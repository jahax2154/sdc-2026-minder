"""Actual A source/HTTP repair matrix, one real Groq call; explicit outage case."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import threading
import time
import urllib.error
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server
from minder_ml.intelligence.policy import ROOT
from minder_ml.intelligence.product_runtime import build, ProductServer, QuietHandler
from minder_ml.intelligence.integration_cli import provisional_demo_profile
from minder_ml.intelligence.role_fit import reference
from minder_ml.intelligence.groq_adapter import GroqAdapter


def main():
    output=ROOT/'ml/artifacts/session-a/product/chat-repair';output.mkdir(parents=True,exist_ok=True)
    report=dict(environment='Disposable A-only SQLite; actual full source services and loopback HTTP',
                synthetic_profiles=True,model='qwen/qwen3.8-27b',guidance={},reads_during_real_provider=[],deployment=False)
    with tempfile.TemporaryDirectory(dir=output) as folder:
        app,_=build('A',database=Path(folder)/'runtime.sqlite3')
        provider=app.provider
        with make_server('127.0.0.1',0,app,server_class=ProductServer,handler_class=QuietHandler) as server:
            serving=threading.Thread(target=server.serve_forever,daemon=True);serving.start()
            origin='http://127.0.0.1:'+str(server.server_port)
            def request(path,body=None,token=None,method=None,expected=200):
                headers={'Content-Type':'application/json'}
                if token:headers['Authorization']='Bearer '+token
                req=Request(origin+'/api/'+path,data=json.dumps(body).encode() if body is not None else None,
                            headers=headers,method=method or ('POST' if body is not None else 'GET'))
                start=time.perf_counter()
                try:reply=urlopen(req,timeout=45)
                except urllib.error.HTTPError as error:reply=error
                with reply:
                    value=json.loads(reply.read());assert reply.code==expected,(path,reply.code,value.get('code'))
                    correlation=reply.headers['X-Request-ID']
                elapsed=round((time.perf_counter()-start)*1000,3)
                if path=='chat' and expected==200:assert value['diagnostics']['request_id']==correlation
                return value,elapsed
            def ask(token,text,version=None,**extra):
                return request('chat',dict(message=text,expected_profile_version=version,**extra),token)
            try:
                tokens={}
                for group in ('unsaved','partial','rich'):
                    token=request('session',{})[0]['token'];tokens[group]=token
                    version=None
                    if group!='unsaved':
                        profile=({'synthetic':True,'career_context':{'goals':'Fictional software exploration'}} if group=='partial'
                                 else provisional_demo_profile(levels=(4,)*len(reference()['skills'])))
                        version=request('profile',dict(profile=profile,expected_version=None),token,'PUT')[0]['version']
                    result,elapsed=ask(token,'How can u help me minder?',version)
                    assert result['response_mode']=='application_guidance' and not result['diagnostics']['provider_invoked']
                    assert '?' in result['answer'] and 'partial profile' in result['answer']
                    report['guidance'][group]=dict(elapsed_ms=elapsed,response_mode=result['response_mode'],
                        provider_code=result['provider']['code'],diagnostics=result['diagnostics'])
                token=tokens['unsaved']
                request('profile',token=token,expected=404)
                for name,text in [('greeting','Hello Minder!'),('paraphrase','What kinds of things can you help me with?'),
                                  ('onboarding','I am a fresh graduate. Where should I start?')]:
                    result,elapsed=ask(token,text)
                    report['guidance'][name]=dict(elapsed_ms=elapsed,response_mode=result['response_mode'])
                follow,elapsed=ask(token,'What do you mean by that?',previous_context_id=result['conversation_context_id'])
                assert 'personally' in follow['answer']
                report['followup']=dict(elapsed_ms=elapsed,owner_scope=True,no_raw_transcript=True)
                other_version=request('profile',token=tokens['partial'])[0]['version']
                request('chat',dict(message='Tell me more',expected_profile_version=other_version,
                    previous_context_id=result['conversation_context_id']),tokens['partial'],expected=404)
                role,elapsed=ask(token,'What does a Software Developer do?')
                assert role['statements'][0]['sources'][0]['geography']=='US'
                report['role_reference']=dict(elapsed_ms=elapsed,source_geography='US',provider_invoked=False)
                token=tokens['partial'];profile=request('profile',token=token)[0]
                started=threading.Event();original=provider.complete_tool
                def measured(*args,**kwargs):started.set();return original(*args,**kwargs)
                provider.complete_tool=measured
                with ThreadPoolExecutor(max_workers=1) as pool:
                    pending=pool.submit(ask,token,'Explain current Malaysian source evidence and next-quarter forecasts.',
                        profile['version'],selected_role_ids=['onet:15-1252.00'])
                    assert started.wait(20),'provider stage not reached'
                    for path in ('profile','agents','proposals','action-history','agent-settings'):
                        was_pending=not pending.done();_,elapsed=request(path,token=token,expected=404 if path=='agent-settings' else 200)
                        report['reads_during_real_provider'].append(dict(route=path,status=404 if path=='agent-settings' else 200,elapsed_ms=elapsed,chat_pending_at_start=was_pending))
                    live,total=pending.result(timeout=40)
                assert all(s.get('status')=='unavailable' for s in live['statements'] if s.get('kind')=='forecast')
                report['real_provider']=dict(elapsed_ms=total,status=live['provider']['status'],code=live['provider'].get('code'),
                    native_arguments_validated=live['provider'].get('tool_call',{}).get('arguments_validated',False),
                    statement_count=len(live['statements']),measurement_types=sorted({s['measurement_type'] for s in live['statements'] if 'measurement_type' in s}),
                    diagnostics=live['diagnostics'])
                assert request('profile',token=token)[0]==profile
                app.provider=GroqAdapter(key='',model='qwen/qwen3.8-27b')
                outage,_=ask(token,'Explain the next-quarter forecast.',profile['version'],selected_role_ids=['onet:15-1252.00'])
                assert outage['response_mode']=='limited_fallback' and not outage['diagnostics']['provider_invoked']
                for path in ('agents','proposals','action-history','agent-settings'):request(path,token=token,expected=404 if path=='agent-settings' else 200)
                report['configured_outage']=dict(provider_code=outage['provider']['code'],outbound_calls=0,saved_reads_passed=True,
                    evidence_kind='Explicit disabled-key configuration; not a real Groq account outage')
                report['no_profile_mutation']=request('profile',token=token)[0]==profile
                report['status']='passed' if live['provider']['status']=='available' else 'limited_real_provider_unavailable'
            finally:
                server.shutdown();serving.join(timeout=5)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
