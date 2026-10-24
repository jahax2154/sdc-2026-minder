"""Bounded, credential-free PUBLIC retrieval. No user text enters HTTP queries."""
import concurrent.futures
import csv
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
import io
import re
import socket
import threading
import time
from urllib.parse import urlsplit, urljoin
from urllib.request import Request, HTTPRedirectHandler, build_opener

POLICY = 'public-career-retrieval-v1'
SEEDS = (
    ('dosm-employment', 'https://www.dosm.gov.my/portal-main/release-content/employment-statistics-Q22026',
     'Employment Statistics, Second Quarter 2026', 'MY', 'Registered private-sector establishment survey; aggregate jobs/vacancies, not individual-role hiring.'),
    ('talentcorp-mycol', 'https://www.talentcorp.com.my/mycol/', 'Malaysia Critical Occupations List', 'MY',
     'Critical occupation groups and employer-reported shortages; not a count of jobs or guaranteed individual opportunity.'),
    ('talentcorp-skills', 'https://mynsr.talentcorp.com.my/faqs/', 'Malaysia National Skills Registry FAQs', 'MY',
     'Occupational skills taxonomy/reference; not personal proficiency or measured vacancies.'),
    ('talentcorp-communications', 'https://www.talentcorp.com.my/resources/press-releases/talentcorp-and-mcmc-bring-industry-ecosystem-together-to-strengthen-future-talent/',
     'TalentCorp and MCMC future talent', 'MY', 'Communications and multimedia sector study/context, not a national role forecast.'),
)
HOSTS = frozenset(urlsplit(s[1]).hostname for s in SEEDS)
TOPICS = frozenset('malaysia malaysian jobs job employment vacancies vacancy demand hiring market skills skill software developer data digital cyber cybersecurity engineering engineer finance accounting healthcare nursing shortage occupation talent technology artificial intelligence communications multimedia current latest'.split())
LFS_URL='https://storage.dosm.gov.my/labour/lfs_month.csv'

def labour_rows(raw):
    """Render actual official CSV cells with documented units; never infer jobs."""
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    fields={'date','lf_employed','lf_unemployed','u_rate','p_rate'}
    if not rows or len(rows)>1000 or not fields.issubset(rows[0]):raise RetrievalError('official_labour_csv_schema_invalid')
    rows.sort(key=lambda r:r['date'])
    for row in rows:
        try:
            date=datetime.strptime(row['date'],'%Y-%m-%d').date()
            if date>datetime.now(timezone.utc).date():raise ValueError()
            if not all(0<=float(row[f])<100000 for f in fields-{'date'}):raise ValueError()
        except (ValueError,TypeError):raise RetrievalError('official_labour_csv_value_invalid') from None
    lines=[f"Month {r['date'][:7]}: unemployment rate {r['u_rate']}%; participation rate {r['p_rate']}%; employed persons {r['lf_employed']} thousand; unemployed persons {r['lf_unemployed']} thousand." for r in reversed(rows[-3:])]
    return '\n'.join(lines),rows[-1]['date'][:7]


class RetrievalError(Exception):
    pass


def checked_url(url, *, resolve=True, allowed_hosts=HOSTS):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname not in allowed_hosts or parsed.username or parsed.password
            or parsed.port not in (None, 443) or len(url) > 1500):
        raise RetrievalError('public_source_url_not_allowed')
    if resolve:
        try:
            addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        except OSError:
            raise RetrievalError('public_source_dns_unavailable') from None
        if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):
            raise RetrievalError('nonpublic_destination_rejected')
    return url


class Redirects(HTTPRedirectHandler):
    max_redirections = 3
    def __init__(self,allowed_hosts=HOSTS,resolve=True):
        super().__init__();self.allowed_hosts,self.resolve=allowed_hosts,resolve
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        checked_url(newurl,resolve=self.resolve,allowed_hosts=self.allowed_hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class PageText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.title, self.parts, self.meta, self.links, self.in_title = [], [], [], {}, [], False
        self.structured = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'script' and attrs.get('type','').casefold() == 'application/ld+json':
            self.structured = []
        if tag == 'meta':
            key = attrs.get('property', attrs.get('name', '')).casefold()
            if key in ('article:published_time', 'datepublished', 'date', 'og:title'):
                self.meta[key] = attrs.get('content', '')
        if tag in ('script', 'style', 'nav', 'footer', 'header', 'noscript', 'svg'):
            self.skip.append(tag)
        if tag == 'title':
            self.in_title = True
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if not self.skip and tag in ('p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'tr'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag == 'script' and self.structured is not None:
            try:
                value=json.loads(''.join(self.structured))
                def dates(node,depth=0):
                    if depth>8:return
                    if isinstance(node,dict):
                        if isinstance(node.get('datePublished'),str):self.meta.setdefault('datepublished',node['datePublished'])
                        for child in node.values():dates(child,depth+1)
                    elif isinstance(node,list):
                        for child in node[:30]:dates(child,depth+1)
                dates(value)
            except (ValueError,TypeError):pass
            self.structured=None
        if self.skip and tag == self.skip[-1]:
            self.skip.pop()
        if tag == 'title':
            self.in_title = False
        if not self.skip and tag in ('p', 'div', 'li', 'h1', 'h2', 'h3', 'tr'):
            self.parts.append('\n')

    def handle_data(self, data):
        if self.structured is not None:self.structured.append(data[:30000])
        if self.in_title:
            self.title.append(data)
        elif not self.skip:
            self.parts.append(data)


def published(meta, text):
    value = next((meta[k] for k in ('article:published_time', 'datepublished', 'date') if meta.get(k)), '')
    match = re.search(r'\b(20\d\d-\d\d-\d\d)\b', value)
    if match:
        return match[1]
    # Source-owned JSON-LD sometimes uses RFC-like US date formatting.
    for fmt in ('%a, %m/%d/%Y - %H:%M','%Y-%m-%dT%H:%M:%S%z'):
        try:return datetime.strptime(value,fmt).date().isoformat()
        except ValueError:pass
    match = re.search(r'(?:Latest Release\s*:?|Released by.{0,100}?|KUALA LUMPUR[, ]+)\s*(\d{1,2}\s+[A-Za-z]+\s+20\d\d)', text, re.I | re.S)
    if match:
        try:
            return datetime.strptime(match[1], '%d %B %Y').date().isoformat()
        except ValueError:
            pass
    return None


def plain(raw, content_type):
    if 'html' in content_type or content_type.startswith('text/plain'):
        parser = PageText()
        parser.feed(raw.decode('utf-8', errors='replace'))
        text = '\n'.join(' '.join(part.split()) for part in ''.join(parser.parts).splitlines() if part.strip())
        return text[:80000], parser.meta.get('og:title') or ' '.join(parser.title).strip(), parser.meta, parser.links
    if 'application/pdf' in content_type:
        import io
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        if reader.is_encrypted or len(reader.pages) > 12:
            raise RetrievalError('public_pdf_outside_bounds')
        return '\n'.join(p.extract_text() or '' for p in reader.pages)[:80000], '', {}, []
    raise RetrievalError('public_source_content_type_unsupported')


class PublicRetrieval:
    def __init__(self, *, opener=None, clock=time.monotonic, resolve=True,allowed_hosts=HOSTS,timeout=8):
        self.allowed_hosts,self.timeout=allowed_hosts,max(1,min(8,timeout))
        self.open = opener or build_opener(Redirects(allowed_hosts,resolve)).open
        self.clock, self.resolve = clock, resolve
        self.cache, self.failures, self.lock = {}, {}, threading.Lock()

    def fetch(self, seed):
        source_id, url, fallback_title, geography, scope = seed
        checked_url(url, resolve=self.resolve,allowed_hosts=self.allowed_hosts)
        with self.lock:
            failed = self.failures.get(url)
            if failed and self.clock() - failed < 60:
                raise RetrievalError('public_source_recently_unavailable')
            old = self.cache.get(url)
            if old and self.clock() - old[0] < 300:
                return dict(old[1], cache_status='recent_cache')
        request = Request(url, headers={'User-Agent': 'MinderPrototype/1.0 PublicCareerEvidence',
            'Accept': 'text/html,application/pdf,text/plain', 'Accept-Encoding': 'identity'})
        with self.open(request, timeout=self.timeout) as response:
            http_status=getattr(response,'status',200)
            final_url = response.geturl()
            checked_url(final_url, resolve=self.resolve,allowed_hosts=self.allowed_hosts)
            raw = response.read(786433)
            if len(raw) > 786432:
                raise RetrievalError('public_source_too_large')
            content_type = response.headers.get('Content-Type', '').split(';')[0].casefold()
        observation_period=None
        if url == LFS_URL:
            text,observation_period=labour_rows(raw)
            title,meta,links='DOSM Monthly Principal Labour Force Statistics',{},[]
        else:text, title, meta, links = plain(raw, content_type)
        if len(text.strip()) < 100:
            raise RetrievalError('public_source_has_no_verified_page_text')
        stamp = datetime.now(timezone.utc).isoformat()
        record = dict(id=source_id + ':' + hashlib.sha256(raw).hexdigest()[:16], url=final_url,
            title=(title or fallback_title)[:400], published_at=published(meta, text), retrieved_at=stamp,
            geography=geography, scope=scope, sha256=hashlib.sha256(raw).hexdigest(),
            text=text, cache_status='live_fetched', content_type=content_type,http_status=http_status)
        if observation_period:record['observation_period']=observation_period
        # Only allowlisted actual page links can supply a PDF. No user URL/query.
        record['document_links'] = [urljoin(final_url, link) for link in links
            if '.pdf' in link.casefold() and urlsplit(urljoin(final_url, link)).hostname in HOSTS][:8]
        with self.lock:
            if len(self.cache) >= 24:
                self.cache.pop(next(iter(self.cache)))
            self.cache[url] = self.clock(), record
        return dict(record)

    def retrieve(self, question):
        # Selection uses a fixed public topic vocabulary. Raw private text is
        # never put in a URL/query parameter, header or another website's search.
        topics = set(re.findall(r'[a-z]+', question.casefold())).intersection(TOPICS)
        chosen = [SEEDS[2], SEEDS[1]] if topics.intersection({'skills', 'skill', 'software', 'cyber', 'cybersecurity'}) else [SEEDS[0], SEEDS[1]]
        if topics.intersection({'communications', 'multimedia'}):
            chosen = [SEEDS[3], SEEDS[2]]
        records, failures = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(self.fetch, seed): seed for seed in chosen}
            for future, seed in futures.items():
                try:
                    records.append(future.result())
                except Exception:
                    with self.lock:
                        self.failures.setdefault(seed[1], self.clock())
                        if self.clock() - self.failures[seed[1]] >= 60:
                            self.failures[seed[1]] = self.clock()
                    failures.append(dict(source_url=seed[1], status='unavailable', code='public_source_fetch_unavailable'))
        for record in records:
            candidates = [line for line in record['text'].splitlines() if len(line.split()) >= 6]
            candidates.sort(key=lambda line: -sum(t in line.casefold() for t in topics))
            record['passage'] = '\n'.join(line[:600] for line in candidates[:4])[:2200]
        return dict(policy_version=POLICY, tool='retrieve_public_career_sources',
            status='available' if records else 'unavailable', sources=records, failures=failures,
            limitation='Live public pages from a bounded official source set, not an exhaustive web search. Publication date stays unknown when not supplied. No private query or profile was sent.')
