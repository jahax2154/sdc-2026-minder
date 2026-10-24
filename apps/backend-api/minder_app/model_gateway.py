"""One bounded provider flight per shared quota group; safe quota metadata only.

File locks coordinate same-host lane processes and workers. Hosted replicas must
share the configured private coordination volume; a local file is not a distributed
quota service. Original transport, daily owner budget and model remain intact.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import urlopen
from minder_ml.intelligence.groq_adapter import GroqAdapter, ProviderError
from .store import uid

POLICY = 'groq-shared-quota-v1'
OPERATIONS = (('GET','/api/product/provider-status'),)
# Local completion ceiling derived from the additional1000-token/minute error,
# with50tokens of headroom for rounding/concurrent legacy callers. It does not
# assert that the8000TPM header changed or authorize a billing/quota increase.
COMPLETION_LIMIT = 950
HEADERS = ('retry-after','x-ratelimit-limit-requests','x-ratelimit-limit-tokens',
    'x-ratelimit-remaining-requests','x-ratelimit-remaining-tokens',
    'x-ratelimit-reset-requests','x-ratelimit-reset-tokens')


def coordination_directory():
    explicit=os.environ.get('MINDER_PROVIDER_COORDINATION_DIR')
    if explicit:return Path(explicit)
    # Preserve the existing macOS lane group; Linux/Replit uses its real writable
    # temp directory rather than attempting to create a privileged /private root.
    root=Path('/private/tmp') if os.path.isdir('/private/tmp') else Path(tempfile.gettempdir())
    return root/('minder-provider-coordination-'+str(os.getuid()))


def duration(value):
    if not isinstance(value,str):return 0
    if re.fullmatch(r'\d+(?:\.\d+)?',value):return float(value)
    parts = re.findall(r'(\d+(?:\.\d+)?)(ms|[smhd])',value)
    if ''.join(n+u for n,u in parts)!=value:return 0
    return sum(float(n)*{'ms':.001,'s':1,'m':60,'h':3600,'d':86400}[u] for n,u in parts)


class QuotaError(ProviderError):
    def __init__(self, code, *, retry_after=0, queue_ms=0, attempts=0, limit_details=None):
        super().__init__(code,uid(),retryable=True)
        self.retry_after,self.queue_ms=retry_after,queue_ms
        self.attempts,self.limit_details=attempts,limit_details
    def public(self):
        return dict(super().public(),retry_after_seconds=round(self.retry_after,3),
            queue_ms=round(self.queue_ms,3),coordination_policy=POLICY,
            transport_attempts=self.attempts,limit_details=self.limit_details)


class CoordinatedGroq(GroqAdapter):
    def __init__(self, *, coordination_dir=None, max_wait=20, opener=urlopen, **kwargs):
        kwargs['retries']=0  # one outbound attempt; no invisible 429 retry bursts
        super().__init__(opener=opener,**kwargs)
        self.transport=opener
        self.opener=self._open
        self.max_wait=max(0,min(20,max_wait))
        root=Path(coordination_dir) if coordination_dir is not None else coordination_directory()
        root.mkdir(parents=True,exist_ok=True,mode=0o700)
        # Same team/model quota group, independent of key spelling. No key hash
        # or credential is written. Operators can separate unrelated accounts.
        group=os.environ.get('MINDER_PROVIDER_QUOTA_GROUP','minder-team-groq')+'|'+str(self.model)
        self.state_path=root/(hashlib.sha256(group.encode()).hexdigest()[:24]+'.json')
        self.lock_path=self.state_path.with_suffix('.lock')
        self.last_headers={}
        self.last_status=None
        self.limit_details=None
        self.http_diagnostics=None
        self.rejected_web_candidate=None

    def _open(self, request, timeout):
        try:
            response=self.transport(request,timeout=timeout)
            self._observe(response.status,response.headers)
            return response
        except HTTPError as error:
            self._observe(error.code,error.headers)
            if error.code==400:
                # Retain only typed diagnostics and visible public-web tool args.
                # Never retain/log upstream messages, request bodies or headers.
                try:
                    payload=json.loads(error.read(16384)).get('error',{})
                    code=payload.get('code','unknown')
                    self.http_diagnostics=dict(http_status=400,native_code=code if isinstance(code,str) and re.fullmatch(r'[a-z_]{1,60}',code) else 'unknown')
                    request_value=json.loads(request.data or b'{}')
                    tools=request_value.get('tools',[])
                    if len(tools)==1 and tools[0].get('function',{}).get('name')=='explain_public_sources':
                        generated=payload.get('failed_generation','')
                        if isinstance(generated,str):
                            candidate=generated.strip()
                            match=re.search(r'<function=explain_public_sources>\s*(\{.*\})\s*</function>',candidate,re.S)
                            if match:candidate=match[1]
                            parsed=json.loads(candidate)
                            if isinstance(parsed,dict):
                                if parsed.get('name')=='explain_public_sources':parsed=parsed.get('parameters',parsed.get('arguments'))
                                if isinstance(parsed,str):parsed=json.loads(parsed)
                                if isinstance(parsed,dict) and 'introduction' in parsed:
                                    self.rejected_web_candidate={k:v for k,v in parsed.items() if k in ('introduction','findings','limitations','advice')}
                except (ValueError,TypeError,AttributeError,KeyError):pass
            if error.code==429:
                # Extract only typed quota numbers. Never log/persist the body,
                # organization ID, raw error message or any credential.
                try:
                    message=json.loads(error.read(8192)).get('error',{}).get('message','')
                    match=re.search(r'(tokens|requests) per (minute|day).*?Limit\s*:?\s*(\d+).*?Used\s*:?\s*(\d+).*?Requested\s*:?\s*(\d+)',message,re.I)
                    if match:
                        self.limit_details=dict(resource=match[1].lower(),period=match[2].lower(),
                            limit=int(match[3]),used=int(match[4]),requested=int(match[5]))
                        state=self._state()
                        state['additional_enforced_limit']=dict(self.limit_details,observed_at=time.time())
                        if match[1].lower()=='tokens' and match[2].lower()=='minute':
                            state['completion_budget']=dict(used=int(match[4]),at=time.time())
                        with self.state_path.open('w') as stream:json.dump(state,stream)
                except (ValueError,TypeError,AttributeError):pass
            raise

    def _observe(self,status,headers):
        self.last_status=status
        self.last_headers={n:headers[n] for n in HEADERS if headers.get(n) and
            re.fullmatch(r'[0-9.smhd]+',str(headers[n])) and len(str(headers[n]))<=40}
        stamp=time.time()
        previous=self._state()
        state=dict(observed_at=stamp,status=status,headers=self.last_headers,
            tokens_reset_at=stamp+duration(self.last_headers.get('x-ratelimit-reset-tokens')),
            retry_at=stamp+duration(self.last_headers.get('retry-after')))
        if previous.get('additional_enforced_limit'):
            state['additional_enforced_limit']=previous['additional_enforced_limit']
        if previous.get('completion_budget'):state['completion_budget']=previous['completion_budget']
        # Lock held throughout the request; readers use the same lock. No prompt,
        # response, owner, provider request headers or personal data is retained.
        descriptor=os.open(self.state_path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        with os.fdopen(descriptor,'w') as stream:json.dump(state,stream)

    def _state(self):
        try:return json.loads(self.state_path.read_text())
        except (OSError,ValueError):return {}

    @contextmanager
    def flight(self,estimated_tokens,completion_reservation=0):
        started=time.monotonic()
        descriptor=os.open(self.lock_path,os.O_RDWR|os.O_CREAT,0o600)
        with os.fdopen(descriptor,'a') as lock:
            while True:
                try:
                    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic()-started>=self.max_wait:
                        raise QuotaError('provider_queue_busy',queue_ms=(time.monotonic()-started)*1000)
                    time.sleep(.05)
            try:
                state=self._state();headers=state.get('headers',{})
                wait=max(0,state.get('retry_at',0)-time.time())
                extra=state.get('additional_enforced_limit',{})
                limit=min(COMPLETION_LIMIT,extra.get('limit',COMPLETION_LIMIT)) if extra.get('resource')=='tokens' and extra.get('period')=='minute' else COMPLETION_LIMIT
                budget=state.get('completion_budget',dict(used=0,at=time.time()))
                used=max(0,budget['used']-(time.time()-budget['at'])*limit/60)
                wait=max(wait,max(0,used+completion_reservation-limit)*60/limit)
                remaining=headers.get('x-ratelimit-remaining-tokens')
                if remaining is not None and float(remaining)<estimated_tokens:
                    wait=max(wait,state.get('tokens_reset_at',0)-time.time())
                if wait>max(0,self.max_wait-(time.monotonic()-started)):
                    raise QuotaError('provider_rate_limited',retry_after=wait,queue_ms=(time.monotonic()-started)*1000)
                if wait:time.sleep(wait)
                state['completion_budget']=dict(used=max(0,used-wait*limit/60)+completion_reservation,at=time.time())
                descriptor=os.open(self.state_path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
                with os.fdopen(descriptor,'w') as stream:json.dump(state,stream)
                yield round((time.monotonic()-started)*1000,3)
            finally:fcntl.flock(lock,fcntl.LOCK_UN)

    def _bounded(self,messages,tool,max_tokens):
        payload=json.dumps(dict(messages=messages,tool=tool))
        if len(payload.encode())>24000:
            raise ProviderError('provider_context_budget_exceeded',uid())
        if not self.key or not self.model:
            return super().complete_tool(messages,tool,max_tokens=max_tokens) if tool else super().complete(messages,max_tokens=max_tokens)
        self.last_headers={};self.last_status=None;self.limit_details=None
        self.http_diagnostics=None;self.rejected_web_candidate=None
        with self.flight(len(payload)//3+max_tokens,max_tokens) as queue_ms:
            try:
                result=super().complete_tool(messages,tool,max_tokens=max_tokens) if tool else super().complete(messages,max_tokens=max_tokens)
            except ProviderError as error:
                if self.http_diagnostics:error.http_diagnostics=dict(self.http_diagnostics)
                if self.rejected_web_candidate is not None:error.rejected_web_candidate=self.rejected_web_candidate
                if error.code=='provider_rate_limited':
                    state=self._state()
                    retry=max(0,state.get('retry_at',0)-time.time())
                    raise QuotaError(error.code,retry_after=retry or max(0,state.get('tokens_reset_at',0)-time.time()),
                        queue_ms=queue_ms,attempts=1,limit_details=self.limit_details) from None
                raise
            state=self._state()
            if state.get('completion_budget') and isinstance(result.get('usage',{}).get('completion_tokens'),int):
                state['completion_budget']['used']=max(0,state['completion_budget']['used']-max_tokens+result['usage']['completion_tokens'])
                with self.state_path.open('w') as stream:json.dump(state,stream)
            return dict(result,queue_ms=queue_ms,coordination_policy=POLICY,transport_attempts=1,
                quota_headers=dict(self.last_headers),quota_header_scope=dict(requests='requests_per_day',tokens='tokens_per_minute'))

    def complete_tool(self,messages,tool,*,max_tokens=1024):
        name=tool['function']['name']
        cap=256 if name=='reply_concisely' else 256 if name=='propose_schedule' else 384 if name=='explain_public_sources' else 640 if name=='propose_guidance' else 384
        return self._bounded(messages,tool,min(max_tokens,cap))

    def complete(self,messages,*,max_tokens=512):
        return self._bounded(messages,None,min(max_tokens,384))


def dispatch(app,owner,method,path,body):
    provider=app.provider
    state=provider._state() if isinstance(provider,CoordinatedGroq) else {}
    return dict(policy_version=POLICY,configured=bool(getattr(provider,'key',None)),
        model=getattr(provider,'model',None),coordinated=isinstance(provider,CoordinatedGroq),
        observed_status=state.get('status'),observed_at=state.get('observed_at'),
        quota_headers=state.get('headers',{}),additional_enforced_limit=state.get('additional_enforced_limit'),
        retry_after_seconds=round(max(0,state.get('retry_at',0)-time.time()),3),
        max_queue_seconds=getattr(provider,'max_wait',0),local_completion_reservation_per_minute=COMPLETION_LIMIT,
        limitation='Same-host processes sharing the coordination directory participate. Other hosts/legacy runtimes do not. No provider call was made.')
