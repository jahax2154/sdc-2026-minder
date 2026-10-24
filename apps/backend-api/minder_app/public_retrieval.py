"""Bounded, credential-free PUBLIC retrieval. No user text enters HTTP queries."""
import concurrent.futures
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
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


class RetrievalError(Exception):
    pass


def checked_url(url, *, resolve=True):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname not in HOSTS or parsed.username or parsed.password
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
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        checked_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class PageText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.title, self.parts, self.meta, self.links, self.in_title = [], [], [], {}, [], False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
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
        if self.skip and tag == self.skip[-1]:
            self.skip.pop()
        if tag == 'title':
            self.in_title = False
        if not self.skip and tag in ('p', 'div', 'li', 'h1', 'h2', 'h3', 'tr'):
            self.parts.append('\n')

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        elif not self.skip:
            self.parts.append(data)


def published(meta, text):
    value = next((meta[k] for k in ('article:published_time', 'datepublished', 'date') if meta.get(k)), '')
    match = re.search(r'\b(20\d\d-\d\d-\d\d)\b', value)
    if match:
        return match[1]
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
    def __init__(self, *, opener=None, clock=time.monotonic, resolve=True):
        self.open = opener or build_opener(Redirects()).open
        self.clock, self.resolve = clock, resolve
        self.cache, self.failures, self.lock = {}, {}, threading.Lock()

    def fetch(self, seed):
        source_id, url, fallback_title, geography, scope = seed
        checked_url(url, resolve=self.resolve)
        with self.lock:
            failed = self.failures.get(url)
            if failed and self.clock() - failed < 60:
                raise RetrievalError('public_source_recently_unavailable')
            old = self.cache.get(url)
            if old and self.clock() - old[0] < 300:
                return dict(old[1], cache_status='recent_cache')
        request = Request(url, headers={'User-Agent': 'MinderPrototype/1.0 PublicCareerEvidence',
            'Accept': 'text/html,application/pdf,text/plain', 'Accept-Encoding': 'identity'})
        with self.open(request, timeout=8) as response:
            final_url = response.geturl()
            checked_url(final_url, resolve=self.resolve)
            raw = response.read(786433)
            if len(raw) > 786432:
                raise RetrievalError('public_source_too_large')
            content_type = response.headers.get('Content-Type', '').split(';')[0].casefold()
        text, title, meta, links = plain(raw, content_type)
        if len(text.strip()) < 100:
            raise RetrievalError('public_source_has_no_verified_page_text')
        stamp = datetime.now(timezone.utc).isoformat()
        record = dict(id=source_id + ':' + hashlib.sha256(raw).hexdigest()[:16], url=final_url,
            title=title or fallback_title, published_at=published(meta, text), retrieved_at=stamp,
            geography=geography, scope=scope, sha256=hashlib.sha256(raw).hexdigest(),
            text=text, cache_status='live_fetched', content_type=content_type)
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
