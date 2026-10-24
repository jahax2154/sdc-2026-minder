"""Documented anonymous Mwmbl v2 page discovery; no private query or paid key.

Search results identify candidates only. Actual fetched pages are evidence.
"""
from contextlib import contextmanager
from datetime import datetime,timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
from urllib.error import HTTPError
from urllib.parse import urlencode,urlsplit,urlunsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler
from .model_gateway import coordination_directory
from .public_retrieval import PublicRetrieval,SEEDS,TOPICS,RetrievalError

POLICY='public-page-discovery-v1'
ENDPOINT='https://api.mwmbl.org/api/v2/search/'
PROFESSIONAL=('talentcorp.com.my','mynsr.talentcorp.com.my','mdec.my','hays.com.my','randstad.com.my',
    'michaelpage.com.my','jobstreet.com.my','mycen.com.my','coursera.org','dataquest.io','github.blog',
    'roadmap.sh','techwireasia.com','rawsec.com','knightfrank.com','roberthalf.com','towardsdatascience.com')
ROLE_TERMS=((r'\b(data analyst|data analytics)\b','data analyst skills'),
    (r'\b(data scien\w*|machine learning)\b','data science skills'),
    (r'\b(software|programmer|coding|python)\b','software developer skills'),
    (r'\b(cyber\w*|information security)\b','cybersecurity skills'),
    (r'\b(nurs\w*|healthcare)\b','nursing skills'),
    (r'\b(account\w*|finance|financial)\b','accounting skills'),
    (r'\b(engineer\w*|manufactur\w*)\b','engineering skills'))


def public_queries(question):
    # A fixed public vocabulary, not an excerpt of the user message/profile/CV.
    for pattern,topic in ROLE_TERMS:
        if re.search(pattern,question,re.I):return ['Malaysia '+topic.replace(' skills',''),topic]
    if re.search(r'\b(skills?|qualifications?)\b',question,re.I):return ['Malaysia skills demand']
    return ['Malaysia labour market']


def candidate_url(value):
    try:
        parsed=urlsplit(value)
        host=(parsed.hostname or '').lower()
        if parsed.scheme not in ('http','https') or parsed.username or parsed.password or parsed.port not in (None,80,443):return None
        if not (host.endswith('.gov.my') or any(host==d or host=='www.'+d for d in PROFESSIONAL)):return None
        if re.search(r'\.(?:exe|zip|tar|gz|js|css|png|jpe?g)(?:$|\?)',parsed.path,re.I):return None
        return urlunsplit(('https',parsed.netloc.replace(':80',''),parsed.path,parsed.query,''))
    except (TypeError,ValueError):return None


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise RetrievalError('search_provider_redirect_rejected')


class MwmblSearch:
    def __init__(self,*,opener=None,state_root=None,clock=time.time):
        self.open=opener or build_opener(NoRedirect()).open
        self.root=Path(state_root) if state_root else coordination_directory()
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.clock=clock;self.cache={};self.lock=threading.Lock()

    @contextmanager
    def budget(self):
        descriptor=os.open(self.root/'public-search.lock',os.O_CREAT|os.O_RDWR,0o600)
        with os.fdopen(descriptor,'a') as handle:
            started=time.monotonic()
            while True:
                try:
                    fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                except BlockingIOError:
                    if time.monotonic()-started>=4:raise RetrievalError('public_search_queue_busy')
                    time.sleep(.05)
            try:
                path=self.root/'public-search.json';month=datetime.now(timezone.utc).strftime('%Y-%m')
                try:state=json.loads(path.read_text())
                except (OSError,ValueError):state={}
                if state.get('month')!=month:state=dict(month=month,attempts=0,last_at=0)
                if state['attempts']>=900:raise RetrievalError('public_search_local_monthly_limit')
                wait=max(0,1.1-(self.clock()-state['last_at']))
                if wait:time.sleep(min(wait,1.1))
                state.update(last_at=self.clock(),attempts=state['attempts']+1)
                fd=os.open(path,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
                with os.fdopen(fd,'w') as output:json.dump(state,output)
                yield
            finally:fcntl.flock(handle,fcntl.LOCK_UN)

    def search(self,query):
        with self.lock:
            cached=self.cache.get(query)
            if cached and self.clock()-cached[0]<(300 if cached[1]['status']=='available' else 30):return dict(cached[1],cache_status='recent_search_cache')
        started=time.perf_counter();stamp=datetime.now(timezone.utc).isoformat()
        record=dict(provider='mwmbl',endpoint=ENDPOINT,query=query,searched_at=stamp,results=[],
            status='unavailable',cache_status='live_search',credentials_required=False)
        try:
            with self.budget():
                request=Request(ENDPOINT+'?'+urlencode({'q':query}),headers={
                    'User-Agent':'MinderPublicEvidencePrototype/1.0','Accept':'application/json'})
                with self.open(request,timeout=5) as response:
                    raw=response.read(262145)
                    if response.status!=200 or len(raw)>262144:raise RetrievalError('search_response_not_supported')
                    value=json.loads(raw)
                rows=value.get('results') if isinstance(value,dict) else None
                if not isinstance(rows,list):raise RetrievalError('search_response_shape_invalid')
                record.update(status='available',results=[dict(url=row['url'],title=str(row.get('title',''))[:300])
                    for row in rows[:10] if isinstance(row,dict) and isinstance(row.get('url'),str)],
                    result_count=value.get('number_of_results',len(rows)),
                    provider_monthly_usage=value.get('monthly_usage'),provider_monthly_limit=value.get('monthly_limit'))
        except HTTPError as error:
            record['code']='public_search_rate_limited' if error.code==429 else 'public_search_http_unavailable'
            error.close()
        except Exception as error:
            record['code']=str(error) if isinstance(error,RetrievalError) else 'public_search_unavailable'
        record['elapsed_ms']=round((time.perf_counter()-started)*1000,3)
        with self.lock:
            if len(self.cache)>=32:self.cache.pop(next(iter(self.cache)))
            self.cache[query]=(self.clock(),record)
        return record


class SearchRetrieval:
    def __init__(self,*,search=None,fetcher_factory=PublicRetrieval,predefined=None):
        self.search=search or MwmblSearch();self.fetcher_factory=fetcher_factory
        self.fetchers={};self.lock=threading.Lock()
        self.predefined=predefined or PublicRetrieval(timeout=4)

    def fetcher(self,host):
        with self.lock:
            if host not in self.fetchers:
                if len(self.fetchers)>=24:self.fetchers.pop(next(iter(self.fetchers)))
                sibling=host[4:] if host.startswith('www.') else 'www.'+host
                self.fetchers[host]=self.fetcher_factory(allowed_hosts=frozenset((host,sibling)),timeout=4)
            return self.fetchers[host]

    def retrieve(self,question):
        import concurrent.futures
        queries=public_queries(question);discovery=[self.search.search(q) for q in queries]
        candidates=[];seen=set()
        for result in discovery:
            for row in result['results']:
                url=candidate_url(row['url'])
                if not url or url in seen:continue
                seen.add(url);candidates.append((url,row['title']))
        # Official pages precede professional context. No snippet is an evidence passage.
        role=queries[-1].removesuffix(' skills').casefold()
        def relevant(title,url):return role in re.sub(r'[^a-z0-9]+',' ',(title+' '+url).casefold())
        candidates.sort(key=lambda row:(0 if urlsplit(row[0]).hostname.endswith('.gov.my') else 1,
            0 if relevant(row[1],row[0]) else 1))
        jobs=[]
        for url,title in candidates[:3]:
            host=urlsplit(url).hostname
            malaysia=host.endswith('.gov.my') or host.endswith('.com.my') or host=='mdec.my'
            seed=('discovered-'+hashlib.sha256(url.encode()).hexdigest()[:12],url,title,
                'MY' if malaysia else 'global; Malaysian applicability not established',
                'Discovered official Malaysian page; preserve its measurement and date scope.' if host.endswith('.gov.my') else
                'Discovered professional/editorial context; not proof of Malaysian hiring demand or individual proficiency.')
            jobs.append((self.fetcher(host),seed,'search_discovered'))
        # Available live official context survives a failed/irrelevant discovery.
        topics=set(re.findall(r'[a-z]+',question.casefold()))
        demand=bool(re.search(r'\b(demand|hiring|market|grow\w*|increas\w*|shortage|vacanc\w*|sought)\b',question,re.I))
        seed=SEEDS[2] if not demand and topics.intersection({'skill','skills','qualification','qualifications'}) else SEEDS[1]
        if seed[1] not in seen:jobs.append((self.predefined,seed,'predefined_official'))
        records=[];failures=[]
        def fetch(job):
            engine,seed,origin=job;started=time.perf_counter()
            try:
                record=engine.fetch(seed)
                record.update(origin=origin,fetch_elapsed_ms=round((time.perf_counter()-started)*1000,3))
                return record,None
            except Exception as error:
                if hasattr(engine,'failures'):
                    with engine.lock:engine.failures[seed[1]]=engine.clock()
                status=getattr(error,'code',None) if isinstance(error,HTTPError) else None
                code=str(error) if isinstance(error,RetrievalError) else 'public_source_timeout' if isinstance(error,TimeoutError) else 'public_source_fetch_unavailable'
                if isinstance(error,HTTPError):error.close()
                return None,dict(source_url=seed[1],origin=origin,status='unavailable',http_status=status,
                    code=code,fetch_elapsed_ms=round((time.perf_counter()-started)*1000,3))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures=[(executor.submit(fetch,job),job) for job in jobs]
            for future,job in futures:
                try:
                    record,failure=future.result()
                    if record:records.append(record)
                    if failure:failures.append(failure)
                except Exception:failures.append(dict(source_url=job[1][1],origin=job[2],status='unavailable',code='public_source_fetch_unavailable'))
        terms=set(re.findall(r'[a-z]+',' '.join(queries))).intersection(TOPICS|{'analyst','analysts','cybersecurity','python','sql','labour','skills'})
        for record in records:
            lines=[line for line in record['text'].splitlines() if len(line.split())>=6]
            lines.sort(key=lambda line:-sum(t in line.casefold() for t in terms))
            record['passage']='\n'.join(line[:600] for line in lines[:4])[:2200]
        # Limit model context; retain the complete discovered-page fetch ledger.
        records.sort(key=lambda r:(0 if urlsplit(r['url']).hostname.endswith('.gov.my') else 1 if r['origin']=='predefined_official' else 2,
            0 if relevant(r['title'],r['url']) else 1))
        selected=records[:3]
        found=any(r['origin']=='search_discovered' for r in selected)
        return dict(policy_version=POLICY,tool='search_then_fetch_public_pages',
            mode='search_and_fetch' if found else 'predefined_fetch_after_search',
            status='available' if selected else 'unavailable',sources=selected,failures=failures,
            discovery=discovery,fetched_pages=[{k:r[k] for k in ('url','title','retrieved_at','cache_status','origin','fetch_elapsed_ms','http_status') if k in r} for r in records],
            limitation='Mwmbl anonymous general web search has limited index coverage. Search snippets are discovery only. '
                'Cited facts use actual fetched page text; predefined official context is labelled separately. '
                'Retrieval time is not publication time. Global skills advice is not measured Malaysian demand. No private search query is sent.')
