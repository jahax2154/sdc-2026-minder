"""Immutable DOSM source parsing, cell round-trip checks and deterministic snapshots."""

from calendar import monthrange
from datetime import date
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile
import html
import time
import io
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urlencode, urlsplit, urlunsplit

from .data_schemas import ROOT, VERSION, SCHEMA_PATH, validate_entity
from .market import build_market_views

PACK = ROOT / "ml/minder_ml_starter"
SNAPSHOTS = ROOT / "ml/data/snapshots"
PIPELINE_VERSION = "dosm-quarterly-cells-v1.1"
REFERENCES = [
    "https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q22026",
    "https://www.oecd.org/en/publications/how-well-do-online-job-postings-match-national-sources-in-large-english-speaking-countries_c17cae09-en.html",
    "https://esco.ec.europa.eu/en/use-esco/download"]

MARKET_DATA = ROOT / 'ml/data/market'
MARKET_ARTIFACTS = ROOT / 'ml/artifacts/session-b'


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def fetch_public(url, destination, *, max_bytes=5_000_000):
    """One bounded public GET, no retries/authentication; raw bytes stay local."""
    request = Request(url, headers={'User-Agent': 'MinderResearch/1.0 (bounded public evidence snapshot)'})
    with urlopen(request, timeout=20) as response:
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError('source exceeds acquisition byte limit')
        resolved=response.url
        if any(token in urlsplit(resolved).query.lower() for token in ('signature=','credential=','token=')):
            parsed=urlsplit(resolved)
            resolved=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,'',''))
        record = {'url': url, 'resolved_url': resolved, 'http_status': response.status,
                  'retrieved_at': utc_now(), 'sha256': hashlib.sha256(body).hexdigest(),
                  'bytes': len(body), 'content_type': response.headers.get('Content-Type')}
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body)
    return body, record


def plain_text(text):
    text = re.sub(r'</(?:li|p|div)>|<br\s*/?>', '\n', text or '', flags=re.I)
    return html.unescape(re.sub(r'<[^>]+>', ' ', text))


def normalize_postings(details, *, retrieved_at, mapping):
    """Count observed ads, not hires. Aliases map to source-native IDs only.

    Required/optional/negated clauses stay distinct. Only positive qualification
    mentions enter skill counts; absence in our dictionary is not absence of skill.
    """
    accepted, rejected, seen = [], [], set()
    fingerprints = {}
    for d in details:
        try:
            if d['location']['country'].lower() != 'my':
                raise ValueError('outside_Malaysia')
            if d.get('active') is False:
                raise ValueError('inactive_advertisement')
            published = d['releasedDate']
            if datetime.fromisoformat(published.replace('Z', '+00:00')) > datetime.fromisoformat(retrieved_at):
                raise ValueError('future_publication')
            ad_id = d['id']
            key = d.get('refNumber') or ad_id
            sections = d.get('jobAd', {}).get('sections', {})
            qualifications = plain_text(sections.get('qualifications', {}).get('text', ''))
            title = d['name'].strip()
            if not title:
                raise ValueError('missing_title')
            signature = hashlib.sha256(json.dumps([title.casefold(), d['location'].get('city'),
                                                  qualifications.casefold()], sort_keys=True).encode()).hexdigest()
            if key in seen:
                raise ValueError('duplicate_native_requisition')
            seen.add(key)
            template_peer = fingerprints.get(signature)
            fingerprints.setdefault(signature, key)
            roles = []
            if not re.search(r'\bintern(ship)?\b', title, re.I):
                roles = [r['source_role_id'] for r in mapping['roles'] if re.search(r['title_pattern'], title, re.I)]
            skills, mentions = [], []
            clauses = re.split(r'[.;\n\r]+', qualifications)
            for skill in mapping['skills']:
                for clause in clauses:
                    if re.search(skill['pattern'], clause, re.I):
                        negated = bool(re.search(r'\b(no|not)\b.{0,30}\b(required|necessary|needed)\b', clause, re.I))
                        optional = bool(re.search(r'\b(preferred|advantage|plus|optional|desirable)\b', clause, re.I))
                        kind = 'negated' if negated else 'preferred' if optional else 'requested'
                        mentions.append({'skill_id': skill['source_skill_id'], 'kind': kind})
                        if kind == 'requested':
                            skills.append(skill['source_skill_id'])
            accepted.append({'ad_id': ad_id, 'requisition_id': key, 'title': title,
                             'url': d.get('postingUrl') or 'https://jobs.smartrecruiters.com/BoschGroup/' + ad_id,
                             'source_id': 'bosch-smartrecruiters-my', 'country': 'MY',
                             'city': d['location'].get('city'), 'published_at': published,
                             # Release date is not an archived first-availability date.
                             'available_at': retrieved_at, 'ingested_at': retrieved_at,
                             'role_ids': sorted(set(roles)), 'skill_ids': sorted(set(skills)),
                             'skill_mentions': mentions, 'content_sha256': signature,
                             'qualifications_status': 'observed' if qualifications.strip() else 'missing',
                             'template_peer_requisition': template_peer,
                             'quality_flags': (['same_template_distinct_native_requisition'] if template_peer else []) +
                                 (['missing_qualifications_not_zero_skills'] if not qualifications.strip() else []) +
                                 (['release_date_older_than_one_year'] if
                                  (datetime.fromisoformat(retrieved_at)-datetime.fromisoformat(published.replace('Z','+00:00'))).days > 365 else []),
                             'validity': 'listed_in_employer_feed_at_collection'})
        except (KeyError, ValueError, TypeError) as exc:
            rejected.append({'ad_id': d.get('id'), 'reason': str(exc)})
    return accepted, rejected


def acquire_market(*, output=MARKET_DATA / 'snapshot.v1.json', max_details=160,
                   reuse_raw=None, reuse_snapshot=None):
    """Reuse pinned DOSM cells and acquire a bounded official employer sample.

    The inspected sample is a snapshot stock, never a quarterly inflow series.
    No writes to bootstrap source hardlinks; raw copyrighted descriptions stay
    in the ignored lane artifact directory and are not exported to Git.
    """
    if not 1 <= max_details <= 160:
        raise ValueError('detail cap must be between 1 and 160')
    now = utc_now()
    raw = MARKET_ARTIFACTS / 'acquisition' / now.replace(':', '-')
    mapping = json.loads((MARKET_DATA / 'mapping.v1.json').read_text())
    observations, quality, provenance = parse_dosm()
    if quality['rejected_rows']:
        raise ValueError('pinned DOSM round-trip failed')
    attempts, details, listings, failures = [], [], [], []
    cached = {}
    if reuse_raw is not None:
        if reuse_snapshot is None:
            raise ValueError('cache_reuse_requires_pinned_snapshot')
        previous = json.loads(Path(reuse_snapshot).read_text())
        for record in previous['acquisition']:
            if '/postings/' not in record['url'] or record.get('http_status') != 200:
                continue
            identifier = record['url'].rsplit('/', 1)[-1]
            file = Path(reuse_raw) / (identifier + '.json')
            if file.is_file() and sha(file) == record['sha256']:
                cached[identifier] = (json.loads(file.read_text()), record)
    # Terms/documentation are evidence of access, not a blanket reuse licence.
    for name, url in [('posting-api', 'https://developers.smartrecruiters.com/docs/posting-api'),
                      ('bosch-careers', 'https://www.bosch.com.my/careers/'),
                      ('bosch-terms', 'https://www.bosch.com.my/terms-of-use/')]:
        try:
            _, record = fetch_public(url, raw / (name + '.html'))
            attempts.append(record)
        except (OSError, ValueError) as exc:
            attempts.append({'url': url, 'status': 'unavailable', 'reason': type(exc).__name__})
    total = None
    for offset in range(0, max_details, 100):
        url = 'https://api.smartrecruiters.com/v1/companies/BoschGroup/postings?' + urlencode(
            {'country': 'my', 'limit': min(100, max_details - offset), 'offset': offset})
        try:
            body, record = fetch_public(url, raw / ('listing-' + str(offset) + '.json'))
            attempts.append(record)
            page = json.loads(body)
            total = page['totalFound']
            listings.extend(page['content'])
            if offset + len(page['content']) >= total:
                break
        except (OSError, ValueError, KeyError) as exc:
            attempts.append({'url': url, 'status': 'unavailable', 'reason': type(exc).__name__})
            failures.append({'url': url, 'reason': type(exc).__name__})
            break
    # Sequential acquisition; max 160 detail requests, no automatic retries.
    reused = 0
    requested = 0
    listed_ids = set()
    for item in listings[:max_details]:
        if item['id'] in listed_ids:
            continue
        listed_ids.add(item['id'])
        url = 'https://api.smartrecruiters.com/v1/companies/BoschGroup/postings/' + item['id']
        if item['id'] in cached and cached[item['id']][0].get('releasedDate') == item.get('releasedDate'):
            detail, record = cached[item['id']]
            details.append(detail)
            attempts.append(dict(record, reused_verified_cache=True,
                                 membership_rechecked_at=utc_now()))
            reused += 1
            continue
        try:
            requested += 1
            body, record = fetch_public(url, raw / (item['id'] + '.json'))
            attempts.append(record)
            details.append(json.loads(body))
        except (OSError, ValueError) as exc:
            attempts.append({'url': url, 'status': 'unavailable', 'reason': type(exc).__name__})
            failures.append({'url': url, 'reason': type(exc).__name__})
        time.sleep(.15)
    collected = utc_now()
    ads, rejected = normalize_postings(details, retrieved_at=collected, mapping=mapping)
    complete_listing = total is not None and len(listed_ids) == total
    complete_details = complete_listing and len(details) == len(listed_ids)
    snapshot = {'version': 'market-snapshot-v1', 'synthetic': False, 'collected_at': collected,
                'mapping_version': mapping['version'], 'mapping_sha256': sha(MARKET_DATA / 'mapping.v1.json'),
                'source_universe_id': 'bosch-my-bounded-inspected-ads-v1',
                'collection': {'reported_feed_total': total, 'listing_rows': len(listings),
                               'detail_cap': max_details, 'detail_responses': len(details),
                               'new_detail_requests': requested, 'reused_verified_details': reused,
                               'accepted_ads': len(ads), 'rejections': rejected,
                               'qualification_observed_ads': sum(a['qualifications_status']=='observed' for a in ads),
                               'qualification_missing_ads': sum(a['qualifications_status']=='missing' for a in ads),
                               'same_template_distinct_requisitions': sum(a['template_peer_requisition'] is not None for a in ads),
                               'release_date_range': {'min':min((a['published_at'] for a in ads),default=None),
                                                      'max':max((a['published_at'] for a in ads),default=None)},
                               'release_year_counts':dict(Counter(a['published_at'][:4] for a in ads)),
                               'listing_ids': len(listed_ids), 'request_failures': failures,
                               'complete_listing': complete_listing,
                               'complete_detail_collection': complete_details,
                               'complete_feed': complete_details,
                               'limit_explanation': '40 was a collector-selected initial request cap, not an API/access limit; expansion cap is explicit.',
                               'window_kind': 'observed_active_snapshot_not_quarterly_inflow'},
                'ads': ads, 'acquisition': attempts,
                'dosm_quality': quality, 'dosm_source': provenance,
                'dosm_observations': [
                    {key: row[key] for key in ('observation_id', 'source_id', 'source_version',
                     'value', 'period_start', 'period_end', 'available_at', 'published_at',
                     'retrieved_at', 'dimension_scope', 'occupation_label', 'industry_label',
                     'group_kind', 'quality_flags', 'source_record')} for row in observations],
                'limitations': ['Employer sample is not the Malaysian labour market.',
                                'No historical employer snapshots or quarterly skill targets.',
                                'DOSM historical cells are one 2026 vintage, not archived historical availability.',
                                'Source-native role mappings require A canonical-ID translation.',
                                'Skill counts exclude preferred/negated mentions; dictionary coverage is partial.',
                                'Raw job descriptions retained locally; redistribution licence not established.']}
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(encoded(snapshot))
    return {'snapshot': str(output.relative_to(ROOT)), 'sha256': sha(output),
            'collection': snapshot['collection'], 'dosm_quality': quality,
            'raw_directory': str(raw.relative_to(ROOT))}


def inspect_csv_bytes(body):
    """Inspect actual rows without exporting job descriptions or inventing dates."""
    text = body.decode('utf-8-sig', errors='replace')
    rows = list(csv.DictReader(io.StringIO(text)))
    fields = list(rows[0]) if rows else []
    dates = {}
    for field in fields:
        if any(t in field.casefold() for t in ('date', 'posted', 'listed', 'published')):
            values = [r[field].strip() for r in rows if r.get(field, '').strip()]
            parsed, unparsed = [], Counter()
            for value in values:
                day = None
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%d %b %Y', '%d %B %Y'):
                    try:
                        day = datetime.strptime(value[:10] if fmt == '%Y-%m-%d' else value, fmt).date().isoformat()
                        break
                    except ValueError:
                        pass
                if day:
                    parsed.append(day)
                else:
                    unparsed[value] += 1
            dates[field] = {'nonempty': len(values), 'parsed_dates': len(parsed),
                            'min': min(parsed, default=None), 'max': max(parsed, default=None),
                            'calendar_quarters': dict(Counter(d[:4] + '-Q' + str((int(d[5:7])-1)//3+1) for d in parsed)),
                            'unparsed_examples': unparsed.most_common(5)}
    id_fields = [f for f in fields if f.casefold() in ('id','job_id','jobid','ad_id','url','job_url','link')]
    return {'format': 'csv', 'row_count': len(rows), 'fields': fields,
            'missing_fields': {f: sum(not (r.get(f) or '').strip() for r in rows) for f in fields},
            'date_fields': dates, 'identity_fields': id_fields,
            'duplicate_identity_rows': {f: len(rows)-len({r.get(f) for r in rows}) for f in id_fields},
            'classification_fields': [f for f in fields if any(t in f.casefold() for t in ('skill','category','class','occupation','title'))],
            'description_fields': [f for f in fields if any(t in f.casefold() for t in ('description','qualification','requirement'))]}


def replay_market_snapshot(input_path, raw_roots, output):
    """Re-normalize pinned acquired bytes without repeating network requests."""
    snapshot=json.loads(Path(input_path).read_text())
    details=[]
    for record in snapshot['acquisition']:
        if '/postings/' not in record['url'] or record.get('http_status')!=200:
            continue
        identifier=record['url'].rsplit('/',1)[-1]
        candidates=[p for root in raw_roots for p in Path(root).rglob(identifier+'.json')]
        path=next((p for p in candidates if sha(p)==record['sha256']),None)
        if path is None:
            raise ValueError('missing_pinned_raw_ad:'+identifier)
        details.append(json.loads(path.read_text()))
    mapping=json.loads((MARKET_DATA/'mapping.v1.json').read_text())
    ads,rejected=normalize_postings(details,retrieved_at=snapshot['collected_at'],mapping=mapping)
    snapshot['ads']=ads
    snapshot['available_at']=utc_now()
    snapshot['normalization_version']='native-requisition-count-and-qualification-coverage-v2'
    snapshot['source_universe_id']='bosch-my-inspected-native-requisitions-v2'
    snapshot['collection'].update(accepted_ads=len(ads),rejections=rejected,
        qualification_observed_ads=sum(a['qualifications_status']=='observed' for a in ads),
        qualification_missing_ads=sum(a['qualifications_status']=='missing' for a in ads),
        same_template_distinct_requisitions=sum(a['template_peer_requisition'] is not None for a in ads),
        release_date_range={'min':min((a['published_at'] for a in ads),default=None),
                            'max':max((a['published_at'] for a in ads),default=None)},
        release_year_counts=dict(Counter(a['published_at'][:4] for a in ads)))
    snapshot['limitations'] += [
        '155 listed source-native requisitions were inspected; current feed membership was rechecked. Old release dates are not newly observed posting flows.',
        'Same text across distinct native requisitions is flagged, not proof of a repost; only repeated native requisition identity is deduplicated.',
        'Missing qualification sections remain unknown and are excluded from skill-count denominator, not dropped from role evidence.']
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True);output.write_text(encoded(snapshot))
    return {'snapshot':str(output.relative_to(ROOT)),'sha256':sha(output),'collection':snapshot['collection']}


def inspect_source_file(path, kind):
    path = Path(path)
    body = path.read_bytes()
    if kind == 'pdf':
        # Optional offline extraction tool lives in the lane's ignored tools.
        # The application serves curated JSON and does not import this parser.
        from pypdf import PdfReader
        reader=PdfReader(io.BytesIO(body))
        return {'format':'pdf','pages':len(reader.pages),'encrypted':reader.is_encrypted,
                'purpose':'Aggregate occupational publication; personal/contact sections excluded from derived output'}
    if kind == 'csv':
        return inspect_csv_bytes(body)
    if kind == 'zip':
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            members = [n for n in archive.namelist() if n.lower().endswith('.csv')]
            if sum(archive.getinfo(n).file_size for n in members) > 250_000_000:
                raise ValueError('uncompressed_CSV_inspection_limit')
            return {'format': 'zip', 'members': {n: inspect_csv_bytes(archive.read(n)) for n in members}}
    if kind == 'xlsx':
        sheets = read_workbook(path)
        return {'format': 'xlsx', 'sheets': {name: {'xml_cell_slots':len(cells),
                 'nonempty_cells':sum(v not in (None,'') for v in cells.values()),
                 'label_cells': {k: v for k, v in cells.items() if re.fullmatch(r'[AB]\d+', k) and v}}
                 for name,cells in sheets.items()}}
    if kind == 'json':
        data = json.loads(body)
        if isinstance(data, list):
            return {'format': 'json', 'records': len(data), 'metadata_records': [
                {k:v for k,v in row.items() if k in ('name','path','size','download_url','ref','title','lastUpdated','licenseName')}
                for row in data[:30] if isinstance(row,dict)]}
        return {'format': 'json', 'keys': list(data), 'metadata': {k:v for k,v in data.items()
                if k in ('title','subtitle','licenseName','licenses','lastUpdated','totalBytes','resources','datasetFiles','files')}}
    text = body.decode('utf-8', errors='replace')
    links = [html.unescape(u) for u in re.findall(r'''(?:href|src)=["']([^"']+)["']''', text)
             if len(u)<1500 and u.startswith(('https://','http://','/')) and not u.startswith('data:')]
    return {'format': 'html', 'title': re.findall(r'<title[^>]*>(.*?)</title>',text,re.S)[:1],
            'data_links': [u for u in links if any(t in u.lower() for t in
                ('csv','xlsx','json','.js','download','release-document','api/','skill','job-profile'))][:100],
            'text_sha256': hashlib.sha256(plain_text(text).encode()).hexdigest()}


def probe_market_sources(plan, output):
    """Finite source plan -> downloaded bytes -> row/field/date evidence ledger."""
    entries = json.loads(Path(plan).read_text())['sources']
    if len(entries) > 20:
        raise ValueError('source_probe_plan_limit_20')
    batch = MARKET_ARTIFACTS / 'investigation' / utc_now().replace(':','-')
    def inspect(entry):
        result = dict(entry)
        file = batch / (entry['source_id'] + '.' + entry['kind'])
        try:
            byte_limit=entry.get('max_download_bytes',30_000_000)
            if not 0 < byte_limit <= 100_000_000:
                raise ValueError('source_probe_download_limit')
            _, record = fetch_public(entry['url'], file, max_bytes=byte_limit)
            result.update(access=record, inspection=inspect_source_file(file,entry['kind']),
                          raw_file=str(file.relative_to(ROOT)), status='inspected_actual_response')
        except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
            result.update(status='unavailable', error=type(exc).__name__,
                          http_status=getattr(exc,'code',None), reason=str(exc))
        return result
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(inspect, entries))
    result = {'version':'market-source-investigation-v1','checked_at':utc_now(),
              'automatic_retries':0,'source_results':records}
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(encoded(result))
    return result


def audit_jobstreet_corpus(path, expected_sha256, output):
    """Real frozen-corpus counts, explicitly not complete historical flows.

    No gap filling, inferred collection dates, language-model labels or fitting.
    Literal mention counts are distinct from conservative request-clause counts.
    """
    path=Path(path)
    if sha(path)!=expected_sha256:
        raise ValueError('corpus_checksum_mismatch')
    mapping=json.loads((MARKET_DATA/'mapping.v1.json').read_text())
    role_patterns=[(r['source_role_id'],re.compile(r['title_pattern'],re.I)) for r in mapping['roles']]
    skill_patterns=[(r['source_skill_id'],re.compile(r['pattern'],re.I)) for r in mapping['skills']]
    counts,locations,missing= {},Counter(),Counter()
    seen=set(); duplicates=0;invalid_dates=0;rows=0;fields=[]
    request=re.compile(r'\b(experience|proficien\w*|knowledge|familiar\w*|skills?|required|must|competenc\w*)\b',re.I)
    optional=re.compile(r'\b(preferred|advantage|plus|optional|desirable)\b|\b(?:no|not)\b.{0,30}\b(?:required|necessary|needed)\b',re.I)
    with zipfile.ZipFile(path) as archive:
        members=[n for n in archive.namelist() if n.endswith('.csv')]
        if len(members)!=1 or archive.getinfo(members[0]).file_size>250_000_000:
            raise ValueError('expected_one_bounded_CSV')
        with archive.open(members[0]) as stream:
            reader=csv.DictReader(io.TextIOWrapper(stream,encoding='utf-8-sig'))
            fields=reader.fieldnames
            for row in reader:
                rows+=1
                if rows>200_000: raise ValueError('corpus_row_cap')
                for field in fields:
                    if not (row.get(field) or '').strip(): missing[field]+=1
                identifier=row['job_id']
                if identifier in seen: duplicates+=1;continue
                seen.add(identifier);locations[row['location']]+=1
                try: day=datetime.strptime(row['listingDate'][:10],'%Y-%m-%d').date()
                except ValueError: invalid_dates+=1;continue
                quarter=f'{day.year}-Q{(day.month-1)//3+1}'
                bucket=counts.setdefault(quarter,{'unique_corpus_ads':0,'role_title_matches':Counter(),
                    'technology_literal_mentions':Counter(),'technology_explicit_request_clauses':Counter()})
                bucket['unique_corpus_ads']+=1
                if not re.search(r'\bintern(ship)?\b',row['job_title'],re.I):
                    bucket['role_title_matches'].update(k for k,p in role_patterns if p.search(row['job_title']))
                text=row['descriptions']
                clauses=re.split(r'[.;\n\r]+',text)
                for skill,pattern in skill_patterns:
                    if pattern.search(text): bucket['technology_literal_mentions'][skill]+=1
                    qualifying=[c for c in clauses if pattern.search(c) and request.search(c) and not optional.search(c)]
                    if skill=='source-term:excel':
                        qualifying=[c for c in qualifying if not re.search(r'\bexcel\s+(in|at|as|within)\b',c,re.I)]
                    if qualifying: bucket['technology_explicit_request_clauses'][skill]+=1
    result={'version':'jobstreet-frozen-corpus-audit-v1','synthetic':False,
        'source_url':'https://www.kaggle.com/datasets/azraimohamad/jobstreet-all-job-dataset',
        'raw_archive_sha256':expected_sha256,'raw_csv':members[0],'rows':rows,'unique_job_ids':len(seen),
        'duplicate_job_ids':duplicates,'invalid_listing_dates':invalid_dates,'fields':fields,'missing_fields':dict(missing),
        'geography':{'source_claim':'Malaysia JobStreet website','country_field_present':False,
                     'distinct_literal_locations':len(locations),'top_locations':locations.most_common(20),
                     'per_record_country_validation':'not_independently_verified; no ISO country field'},
        'classification':{'roles':'conservative source-native title patterns, not broad category allocation',
                          'skills':'five literal technologies; explicit request-clause subset separated from mentions',
                          'mapping_sha256':sha(MARKET_DATA/'mapping.v1.json')},
        'dated_corpus_counts':dict(sorted(counts.items())),
        'measurement':'unique observed frozen-corpus ads grouped by original listing quarter; not complete quarterly source inflows',
        'collection_windows':None,'historical_available_at_by_record':None,
        'eligible_for_approved_forecasting':False,'approved_target_rows':[],
        'limitations':['Uploader describes a current weekly scrape, not a complete historical advertisement archive.',
            'Quarters absent from the acquired corpus remain uncollected/unknown, never zero demand.',
            'Old surviving listings do not identify all ads originally published in their quarter.',
            'No archived source vintages or consistent collection/exposure windows supplied.',
            'Request-clause extraction is conservative partial deterministic evidence, not independently reviewed labels.',
            'Corpus may support descriptive research; no live Malaysian forecast, temporal backtest accuracy or full skill demand claimed.']}
    Path(output).parent.mkdir(parents=True,exist_ok=True);Path(output).write_text(encoded(result))
    return {'output':str(output),'unique_job_ids':len(seen),'dated_quarters':len(counts),
            'eligible_for_approved_forecasting':False,'approved_target_rows':0}


PUBLISHED_ROLE_LABELS = ('Software Developers','Accountants and Auditors',
    'Advertising and Marketing Professionals','Managing Directors and Chief Executives',
    'Administrative Associate Professionals','Administrative Professionals','Public Relations Professionals')


def parse_published_role_counts(body, *, period, source_url, source_id, retrieved_at, document_sha256):
    """Extract only explicit numeric role counts, never top-list absence as zero."""
    text=re.sub(r'\s+',' ',plain_text(body))
    release=re.search(r'Latest Release\s*:\s*(\d{1,2}\s+\w+\s+\d{4})',text)
    if not release: raise ValueError('release_date_not_found')
    published=datetime.strptime(release.group(1),'%d %B %Y').date()
    quarter_words=('First','Second','Third','Fourth')
    expected=f'{quarter_words[int(period[-1])-1]} Quarter of {period[:4]}'
    if expected.casefold() not in text[:release.start()].casefold():
        raise ValueError('release_heading_period_mismatch')
    year,q=int(period[:4]),int(period[-1]);month=3*q-2
    target={'start':date(year,month,1).isoformat(),
            'end':date(year,month+2,monthrange(year,month+2)[1]).isoformat()}
    observed,missing=[],[]
    for label in PUBLISHED_ROLE_LABELS:
        pattern=re.escape(label).replace(r'\ and\ ',r'\s*(?:and|&)\s*')
        matches=re.findall(pattern+r'\s*\(([0-9,]+)\s+job\s+offerings?\)',text,re.I)
        values={int(v.replace(',','')) for v in matches}
        if len(values)>1: raise ValueError('conflicting_explicit_role_counts:'+label)
        identifier='dosm:jmi:published-role-label:'+re.sub('[^a-z0-9]+','-',label.lower()).strip('-')
        if not values:
            missing.append({'entity_id':identifier,'period':target,'reason':'no_explicit_numeric_count_in_release_not_zero'})
            continue
        observed.append({'entity_type':'role','entity_id':identifier,'label':label,'geography':'MY',
            'value':next(iter(values)),'unit':'published job offerings',
            'measurement':'published_online_job_offerings_for_source_role_label',
            'period':target,'published_at':published.isoformat()+'T23:59:59+08:00',
            'publication_precision':'date_only_conservative_end_of_day',
            'available_at':retrieved_at,'availability_basis':'retrieved_release_bytes; original historical byte vintage not independently archived',
            'source_id':source_id,'source_url':source_url,'source_document_sha256':document_sha256,
            'classification':{'system':'DOSM JMI published occupation labels','native_code':None,
                'edition':'not_verified_for_each_release','canonical_role_mapping':'not_applied'},
            'source_universe_id':'dosm-jmi-published-top-occupation-labels',
            'dedup_verified':False,'positions_per_advertisement_verified':False,
            'eligible_for_approved_unique_ad_forecasting':False})
    return observed,missing


def extract_published_role_history(reports, output):
    records,missing,sources=[],[],[]
    for report in reports:
        for source in json.loads(Path(report).read_text())['source_results']:
            if source.get('status')!='inspected_actual_response' or source['kind']!='html': continue
            if source['source_id']=='dosm-jmi-2026q1-page': period='2026-Q1'
            elif source['source_id'].startswith('dosm-release-'): period=source['period']
            else: continue
            body=Path(source['raw_file']).read_bytes()
            if hashlib.sha256(body).hexdigest()!=source['access']['sha256']:
                raise ValueError('release_raw_checksum_mismatch')
            found,absent=parse_published_role_counts(body.decode('utf-8'),period=period,
                source_url=source['url'],source_id=source['source_id'],
                retrieved_at=source['access']['retrieved_at'],document_sha256=source['access']['sha256'])
            records.extend(found);missing.extend(absent)
            sources.append({'source_id':source['source_id'],'url':source['url'],'period':period,
                'sha256':source['access']['sha256'],'retrieved_at':source['access']['retrieved_at'],
                'explicit_numeric_role_counts':len(found),'role_labels_without_numeric_counts':len(absent)})
    result={'version':'dosm-published-role-observations-v1','synthetic':False,'observations':records,
        'missing':missing,'sources':sources,'limitations':[
            'Role-label offering counts are separately reported; they are not allocated from broad-industry totals.',
            'Only explicit numbers are extracted. Absence from a top list is unobserved, not zero.',
            'No skill-request counts occur in these extracted role-label records.',
            'Neither unique-ad deduplication nor positions-per-advertisement equivalence verified from these releases.',
            'Published dates are retained; original historical byte vintages were not independently archived.',
            'No automatic MASCO/O*NET crosswalk or forecast promotion applied.']}
    Path(output).write_text(encoded(result))
    return {'output':str(output),'observations':len(records),'missing':len(missing),'releases':len(sources)}


def clean_aggregate_label(value):
    """Allowlisted occupation/sector labels only; remove incidental contacts."""
    value=plain_text(value)
    value=re.sub(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}','[contact removed]',value,flags=re.I)
    value=re.sub(r'\+\d[\d ()-]{7,}\d','[contact removed]',value)
    return re.sub(r'\s+',' ',value).strip()


def parse_mycol_national_table(ocr_pages):
    """Table 7, PDF spreads 44/45, exactly 66 explicitly coded national groups.

    No forewords, contact sections, respondent identities, historic list tables
    or regional tables enter derived evidence. OCR geometry is preserved.
    """
    result=[]
    for page in ocr_pages:
        number=page['pdf_page']
        if number not in (44,45): continue
        anchors=[r for r in page['lines'] if re.fullmatch(r'\d{4}',r['text'].strip())
                 and (number==44 or r['x']<.5)]
        for anchor in anchors:
            left=anchor['x']<.5
            following=[r['y'] for r in anchors if (r['x']<.5)==left and r['y']<anchor['y']-.005]
            bottom=max(following)+.012 if following else anchor['y']-.025
            titles=[r for r in page['lines'] if anchor['x']+.035<r['x']<(.5 if left else .99)
                    and bottom<r['y']<anchor['y']+.014]
            title=clean_aggregate_label(' '.join(r['text'] for r in sorted(titles,key=lambda r:-r['y'])))
            if not title or '[contact removed]' in title:
                raise ValueError('invalid_or_incidental_contact_in_occupation_label')
            result.append({'code':anchor['text'].strip(),'label':title,'pdf_page':number,
                           'table':'Table 7: national critical occupations',
                           'code_bbox':{k:anchor[k] for k in ('x','y','width','height')}})
    if len(result)!=66 or len({r['code'] for r in result})!=66:
        raise ValueError('national_list_must_have_66_unique_published_codes')
    return sorted(result,key=lambda r:r['code'])


def parse_mycol_six_digit_scope(ocr_pages):
    """Only explicitly enumerated profile codes, not a title-based child join."""
    result={}
    for page in ocr_pages:
        lines=sorted([r for r in page['lines'] if r['x']>.5 and r['y']>.69],key=lambda r:-r['y'])
        combined=' '.join(r['text'] for r in lines)
        parent=re.search(r'MASCO\s*\(4-DIGIT CODE\):\s*(\d{4})',combined,re.I)
        marker=next((r for r in lines if re.search(r'MASCO\s*\(6-DIGIT CODE\)',r['text'],re.I)),None)
        boundary=next((r for r in lines if 'Only the following job titles' in r['text']),None)
        if not parent or not marker or not boundary:
            raise ValueError('explicit_profile_parent_child_scope_and_title_limit_required')
        text=' '.join(r['text'] for r in lines if boundary['y']<r['y']<=marker['y']+.002)
        text=re.sub(r'(\d{4})-\s+(\d{2})',r'\1-\2',text)
        codes=sorted(set(re.findall(r'\b\d{4}-\d{2}\b',text)))
        if not codes or any(not c.startswith(parent.group(1)+'-') for c in codes):
            raise ValueError('profile_child_code_prefix_mismatch')
        if parent.group(1) in result:raise ValueError('duplicate_profile_scope')
        result[parent.group(1)]={'codes':codes,'pdf_page':page['pdf_page'],
            'scope':'Only nominated job titles and explicitly enumerated six-digit codes; no unlisted-child inference',
            'completeness':'positive enumerated codes only; non-matching queries remain unknown'}
    return result


def build_public_current_evidence(ocr_path, acquisition_report, output, scope_ocr_path=None):
    """Code-preserving current context: shortages != offering counts != ads."""
    report=json.loads(Path(acquisition_report).read_text())
    source=next(r for r in report['source_results'] if r['source_id']=='talentcorp-mycol-2024-2025')
    if source.get('status')!='inspected_actual_response' or sha(Path(source['raw_file']))!=source['access']['sha256']:
        raise ValueError('MyCOL_acquired_publication_hash_required')
    groups=parse_mycol_national_table(json.loads(Path(ocr_path).read_text()))
    scopes=parse_mycol_six_digit_scope(json.loads(Path(scope_ocr_path).read_text())) if scope_ocr_path else {}
    if not set(scopes)<={g['code'] for g in groups}:raise ValueError('scope_parent_not_in_national_list')
    available=utc_now();records=[]
    for group in groups:
        records.append({'record_version':'current-public-market-evidence-v1',
            'evidence_id':'mycol:2024-2025:masco2020:'+group['code'],
            'entity_type':'occupation','occupation':{'system':'MASCO','version':'2020',
                'code':group['code'],'level':4,'label':group['label']},
            'geography':{'country_code':'MY','scope':'national'},
            'measurement_type':'institutional_occupation_shortage_designation',
            'value':'listed_in_national_MyCOL','unit':'designation_not_advertisement_count',
            'observation_period':{'label':'MyCOL 2024/2025 edition','start':None,'end':None,
                'basis':'edition, not a verified continuous fieldwork or calendar-flow window'},
            'published_at':None,'publication_date_status':'not_stated_in_inspected_landing_or_verified_report_metadata',
            'available_at':available,'source_available_at':source['access']['retrieved_at'],
            'source':{'source_id':source['source_id'],'publisher':'TalentCorp',
                'url':source['url'],'landing_url':'https://www.talentcorp.com.my/mycol/',
                'sha256':source['access']['sha256'],'pdf_page':group['pdf_page'],
                'table':group['table'],'code_bbox':group['code_bbox']},
            'coverage':{'distinct_national_four_digit_groups':66,'declared_study_sectors':18,
                'sector_coverage_basis':'institutional MyCOL landing statement; not 18 per-occupation sector mappings',
                'employer_count':None,'applies_to_all_six_digit_children':False},
            'comparison_status':'usable_source_coded_context_not_compatible_with_ad_count_ranking',
            'canonical_role_mappings':[],
            'reuse_conditions':{'access':'public official report',
                'licence':'No open-data licence asserted; preserve attribution; raw report/prose not redistributed',
                'terms_url':'https://www.talentcorp.com.my/terms-conditions/'},
            'limitations':['Institutional shortage designation, not number of ads, hires, employment or probability.',
                'Non-listing is unknown and does not imply low demand.',
                'National group designation may cover only nominated six-digit jobs; do not mark every child critical.',
                'Mixed survey/statistical evidence and edition scope are not an October 2026 market snapshot.',
                'No title-only MASCO/O*NET join or numerical recommendation contribution is applied.']})
    snapshot=json.loads((MARKET_DATA/'snapshot.v1.json').read_text())
    for row in snapshot['dosm_observations']:
        if row['period_end']!='2026-06-30' or row['group_kind']!='category':continue
        sector=row['dimension_scope']=='industry'
        label=row['industry_label'] if sector else row['occupation_label']
        identifier=re.sub('[^a-z0-9]+','-',label.casefold()).strip('-')
        entity={'system':'DOSM JMI published economic activities' if sector else 'DOSM JMI published major occupation groups',
                'version':None,'code':None,'label':clean_aggregate_label(label),
                'code_status':'not_supplied_in_acquired_workbook; no code inferred from title or row order'}
        records.append({'record_version':'current-public-market-evidence-v1',
            'evidence_id':'dosm:jmi:2026-q2:'+('sector:' if sector else 'major-occupation:')+identifier,
            'entity_type':'sector' if sector else 'occupation_major_group',
            'sector' if sector else 'occupation':entity,
            'geography':{'country_code':'MY','scope':'published national source coverage'},
            'measurement_type':'published_online_job_offerings', 'value':row['value'],'unit':'published job offerings',
            'observation_period':{'start':row['period_start'],'end':row['period_end'],'label':'2026 Q2','basis':'published quarter'},
            'published_at':'2026-08-18','publication_date_status':'official_release_date; time_of_day_not_asserted',
            'available_at':available,'source_available_at':row['retrieved_at'],
            'source':{'source_id':row['source_id'],'publisher':'Department of Statistics Malaysia',
                'url':'https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q22026',
                'sha256':row['source_version'],'source_cell':row['source_record']},
            'coverage':{'grain':'economic-activity marginal' if sector else 'occupation-major-group marginal',
                'published_total':555509,'economic_activity_unclassified':273024 if sector else None,
                'employer_count':None,'source_representativeness':'not independently verified'},
            'comparison_status':'source_native_current_level_only; not narrow-role allocation or mixed-unit comparison',
            'quality_flags':row['quality_flags'],'canonical_role_mappings':[],
            'reuse_conditions':{'access':'public official aggregate attachment; pinned immutable source reused',
                'licence':'Specific attachment redistribution licence not independently verified; raw workbook not redistributed'},
            'limitations':['Source-covered online offerings, not all Malaysian employment, vacancies or hires.',
                'Separate marginal tables are not joint occupation/sector/employer observations.',
                'Never allocate broad totals to a narrow role or requested skill.',
                'Q2 industry classification/coverage change and large unclassified count limit cross-quarter comparisons.']})
    result={'version':'current-public-market-evidence-v1','synthetic':False,'generated_at':available,
        'records':records,'privacy':'Only code/label, aggregate designation/count, scope, dates and provenance are allowlisted; no applicant, author or recruiter contacts.',
        'coverage':{'mycol_distinct_masco2020_four_digit_groups':66,'dosm_distinct_sector_labels':21,
            'dosm_distinct_major_occupation_groups':9,'distinct_identified_employers_added':0,
            'existing_identified_employer_feed_count':1,'mycol_declared_study_sector_count':18,
            'cross_taxonomy_distinct_occupations':'Not summed across incomparable or unjoined classifications'},
        'galaxy':{'status':'public_aggregate_records_inspected_distribution_held',
            'reason':'Linked MYFutureJobs terms clauses 4.3/4.4 restrict storage/reproduction/distribution; no separate Galaxy open-data licence located.',
            'official_entry':'https://myfuturejobs.gov.my/bm/myfuturejobsgalaxy-2/',
            'terms_url':'https://myfuturejobs.gov.my/wp-content/uploads/2024/03/TermsAndConditions.pdf',
            'source_observed_six_digit_occupations':3041,'source_observed_four_digit_groups':428,
            'records_distributed_to_application':0,'permission_status':'not_granted_or_assumed'}}
    if len(records)!=96:raise ValueError('expected_66_shortage_21_sector_9_major_records')
    for record in records:
        code=record.get('occupation',{}).get('code')
        if code in scopes:
            record['coverage']['explicit_six_digit_codes']=scopes[code]['codes']
            record['coverage']['six_digit_scope_limit']=scopes[code]['scope']
            record['coverage']['six_digit_completeness']=scopes[code]['completeness']
            record['source']['six_digit_scope_pdf_page']=scopes[code]['pdf_page']
    result['coverage']['mycol_profile_groups_with_verified_six_digit_scope']=len(scopes)
    result['coverage']['mycol_explicit_six_digit_memberships']=sum(len(s['codes']) for s in scopes.values())
    result['extraction']={'source_pdf_sha256':source['access']['sha256'],'ocr_sha256':sha(Path(ocr_path)),
        'scope_ocr_sha256':sha(Path(scope_ocr_path)) if scope_ocr_path else None,
        'table_parser':'strict Table7 spread geometry and 66 unique explicit codes',
        'scope_parser':'explicit MASCO parent/six-digit enumeration and nominated-title scope boundary',
        'tool':'Apple Vision local OCR; source extraction, not human-label approval'}
    Path(output).write_text(encoded(result))
    return {'output':str(output),'coverage':result['coverage'],'evidence_records':len(records)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def read_workbook(path):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            for si in ET.fromstring(archive.read("xl/sharedStrings.xml")):
                strings.append("".join(node.text or "" for node in si.iter() if node.tag.endswith("}t")))
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = {}
        for sheet in workbook.findall("m:sheets/m:sheet", ns):
            target = rels[sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]
            member = target.lstrip("/") if target.startswith("/") else str(PurePosixPath("xl") / target)
            cells = {}
            for cell in ET.fromstring(archive.read(member)).findall(".//m:sheetData/m:row/m:c", ns):
                value = cell.find("m:v", ns)
                text = value.text if value is not None else None
                if cell.get("t") == "s" and text is not None:
                    text = strings[int(text)]
                elif cell.get("t") == "inlineStr":
                    text = "".join(n.text or "" for n in cell.findall(".//m:t", ns))
                cells[cell.attrib["r"]] = text
            sheets[sheet.attrib["name"]] = cells
        return sheets


def inspect_pack(pack=PACK):
    pack = Path(pack)
    manifest_path = pack / "sources_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    derived = next(s for s in manifest["derived_files"] if s["id"] == "dosm_jmi_quarterly_long")
    source = next(s for s in manifest["sources"] if s["id"] == derived["source_id"])
    checked = []
    for record in (source, derived):
        path = (pack / record["relative_path"]).resolve()
        if not path.is_relative_to(pack.resolve()):
            raise ValueError("source path escapes source pack")
        checksum = sha(path)
        if checksum != record["sha256"]:
            raise ValueError("source checksum mismatch: " + record["relative_path"])
        checked.append({"relative_path": record["relative_path"], "sha256": checksum})
    return {"source": source, "derived": derived, "checksums": checked,
            "manifest_sha256": sha(manifest_path), "schema_sha256": sha(SCHEMA_PATH), "references": REFERENCES}


def _col_number(text):
    result = 0
    for char in text:
        result = result * 26 + ord(char) - 64
    return result


def parse_dosm(pack=PACK):
    pack = Path(pack)
    provenance = inspect_pack(pack)
    source, derived = provenance["source"], provenance["derived"]
    sheets = read_workbook(pack / source["relative_path"])
    with (pack / derived["relative_path"]).open(newline="") as stream:
        raw_rows = list(csv.DictReader(stream))
    accepted, rejected, seen = [], [], set()
    for row_number, row in enumerate(raw_rows, 2):
        try:
            if row["dimension"] not in ("economic_activity", "occupation_major_group") or row["geography"] != "Malaysia":
                raise ValueError("unsupported source dimension/geography")
            if row["source_id"] != source["id"] or row["file_release_date"] != source["documented_publication_date"]:
                raise ValueError("source provenance mismatch")
            match = re.fullmatch(r"(\d{4})-Q([1-4])", row["period"])
            if not match:
                raise ValueError("not an observed quarterly record")
            year, quarter = map(int, match.groups())
            month = 3 * quarter - 2
            start, end = date(year, month, 1), date(year, month + 2, monthrange(year, month + 2)[1])
            if start.isoformat() != row["period_start"] or row["period"] > source["documented_as_of"]:
                raise ValueError("window or vintage mismatch")
            cells = sheets[row["source_sheet"]]
            ref = re.fullmatch(r"([A-Z]+)(\d+)", row["source_cell"])
            if not ref:
                raise ValueError("invalid source cell")
            column, line = ref.groups()
            if cells.get("B" + line) != row["group_label"] or cells.get(column + "4") != "Q" + str(quarter):
                raise ValueError("source label/quarter header mismatch")
            year_cells = [(_col_number(re.match(r"[A-Z]+", c).group()), v) for c, v in cells.items()
                          if re.fullmatch(r"[A-Z]+3", c) and v and re.fullmatch(r"20\d{2}", v)]
            header_year = max((item for item in year_cells if item[0] <= _col_number(column)), default=(0, None))[1]
            if header_year != str(year):
                raise ValueError("source year header mismatch")
            raw_value = cells.get(row["source_cell"])
            status = row["value_status"]
            if status == "observed":
                value = int(row["online_job_offerings"])
                if value < 0 or raw_value is None or float(raw_value) != value or float(row["source_raw_value"]) != value:
                    raise ValueError("numeric source cell round-trip failed")
            elif status in ("source_dash", "source_blank"):
                value = None
                if row["online_job_offerings"] or (status == "source_dash" and raw_value != "-") or (status == "source_blank" and raw_value not in (None, "")):
                    raise ValueError("missing source cell round-trip failed")
            else:
                raise ValueError("unrecognized source missingness status")
            identity = (row["dimension"], row["group_label"], row["period"])
            if identity in seen:
                raise ValueError("duplicate source series/window")
            seen.add(identity)
            occupation = row["dimension"] == "occupation_major_group"
            flags = ["classification_coverage_review"] if not occupation and row["period"] == "2026-Q2" else []
            record = {
                "schema_version": VERSION, "entity_type": "MarketObservation",
                "observation_id": hashlib.sha256((source["sha256"] + row["source_sheet"] + row["source_cell"]).encode()).hexdigest(),
                "source_id": source["id"], "source_version": source["sha256"], "indicator_id": "online_job_offerings",
                "value": value, "unit": row["unit"], "denominator": None,
                "geography_code": "MYS", "geography_level": "country", "region_code": None,
                "period_start": start.isoformat(), "period_end": end.isoformat(), "frequency": "quarterly",
                "available_at": row["file_release_date"], "published_at": row["file_release_date"], "retrieved_at": source["checked_at_utc"],
                "taxonomy_system": "DOSM JMI published occupation labels" if occupation else "DOSM JMI published economic activity labels",
                "taxonomy_version": None, "occupation_code": None, "occupation_label": row["group_label"] if occupation else None,
                "skill_id": None, "employer_id": None, "industry_id": None, "industry_label": None if occupation else row["group_label"],
                "dimension_scope": "occupation" if occupation else "industry", "group_kind": row["group_kind"],
                "population_coverage": "Published Malaysia online offerings; separate marginal tables, not all vacancies or hires",
                "source_coverage": "DOSM JMI release coverage; provider representativeness not independently verified",
                "measurement_method": "Published online job offering counts", "methodology_version": None,
                "measurement_kind": "observed", "data_quality_status": "missing" if value is None else "review_required" if flags else "valid",
                "quality_flags": flags, "source_record": {"sheet": row["source_sheet"], "cell": row["source_cell"], "raw_value": row["source_raw_value"] or None, "value_status": status}}
            validate_entity(record, "MarketObservation")
            accepted.append(record)
        except (ValueError, KeyError, TypeError) as exc:
            rejected.append({"csv_row": row_number, "reason": str(exc), "source_cell": row.get("source_cell")})
    accepted.sort(key=lambda r: (r["dimension_scope"], r["period_start"], r["occupation_label"] or r["industry_label"]))
    quality = {"input_rows": len(raw_rows), "validated_rows": len(accepted), "rejected_rows": len(rejected), "rejections": rejected,
               "observed_numeric_rows": sum(r["value"] is not None for r in accepted), "missing_rows": sum(r["value"] is None for r in accepted),
               "source_cell_round_trip_rows": len(accepted), "period_min": min((r["period_start"] for r in accepted), default=None),
               "period_max": max((r["period_end"] for r in accepted), default=None),
               "exceptions": source["caveats"] + ["Taxonomy and methodology versions are not supplied: comparability is restricted to the same release and published labels.", "Missing source dates/quarters are not interpolated; skill and employer dimensions remain null."],
               "flagged_classification_rows": sum(bool(r["quality_flags"]) for r in accepted)}
    coverage = []
    for period in ("2026-01-01", "2026-04-01"):
        unclassified = next((r for r in accepted if r["dimension_scope"] == "industry" and r["industry_label"] == "Unclassified" and r["period_start"] == period), None)
        total = next((r for r in accepted if r["dimension_scope"] == "industry" and r["group_kind"] == "overall" and r["period_start"] == period), None)
        if unclassified and total:
            coverage.append({"period_start": period, "unclassified_observed_count": unclassified["value"],
                             "published_total": total["value"], "unclassified_share": unclassified["value"] / total["value"]
                             if unclassified["value"] is not None and total["value"] is not None and total["value"] > 0 else None})
    quality["classification_coverage_diagnostic"] = {"observations": coverage, "status": "requires_review",
                                                    "interpretation": "Observed classification share shift; cause/methodological continuity not established. Industry YoY involving flagged quarter is withheld."}
    return accepted, quality, provenance


def prepare_snapshot(pack=PACK, output_root=SNAPSHOTS):
    rows, quality, provenance = parse_dosm(pack)
    if quality["rejected_rows"]:
        raise ValueError("source rejected rows: " + encoded(quality))
    manifest = {"pipeline_version": PIPELINE_VERSION, "schema_version": VERSION,
                "inputs": provenance["checksums"], "source_manifest_sha256": provenance["manifest_sha256"],
                "schema_sha256": provenance["schema_sha256"]}
    snapshot_id = hashlib.sha256(encoded(manifest).encode()).hexdigest()[:24]
    manifest["snapshot_id"] = snapshot_id
    files = {"observations.jsonl": "".join(json.dumps(r, sort_keys=True, allow_nan=False) + "\n" for r in rows),
             "quality.json": encoded(quality), "source_manifest.json": encoded(provenance),
             "views.json": encoded(build_market_views(rows))}
    manifest["output_sha256"] = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in files.items()}
    files["snapshot.json"] = encoded(manifest)
    target = Path(output_root) / snapshot_id
    if target.exists():
        if any(not (target / name).is_file() or (target / name).read_text() != text for name, text in files.items()):
            raise ValueError("frozen snapshot mismatch; refusing overwrite")
        reused = True
    else:
        target.mkdir(parents=True, exist_ok=False)
        for name, text in files.items():
            with (target / name).open("x") as stream:
                stream.write(text)
        reused = False
    return {"snapshot_id": snapshot_id, "path": str(target), "reused_identical_snapshot": reused,
            "quality": quality, "output_sha256": manifest["output_sha256"]}
