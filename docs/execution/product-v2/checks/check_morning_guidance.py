"""Actual current A HTTP + Qwen; synthetic inputs, no credential output or mocks."""
import argparse
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from minder_ml.intelligence.integration_cli import provisional_demo_profile
from minder_ml.intelligence.role_fit import reference


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',choices=('unsaved','partial','rich'),required=True)
    parser.add_argument('--base',default='http://127.0.0.1:9111');parser.add_argument('--followup',action='store_true')
    parser.add_argument('--followup-delay-seconds',type=float,default=0)
    args=parser.parse_args();assert 0<=args.followup_delay_seconds<=60;token=None
    def call(path,body=None,method=None):
        headers={'Content-Type':'application/json'}
        if token:headers['Authorization']='Bearer '+token
        data=json.dumps(body).encode() if body is not None else None
        with urlopen(Request(args.base+'/api/'+path,data=data,headers=headers,
                     method=method or ('POST' if body is not None else 'GET')),timeout=50) as reply:
            return json.load(reply)
    token=call('session',{})['token'];version=None
    if args.case!='unsaved':
        profile=({'synthetic':True,'career_context':{'goals':'Become a machine-learning engineer',
            'experience':'Built a small Python notebook; model evaluation remains unclear'}} if args.case=='partial'
            else provisional_demo_profile(levels=(4,)*len(reference()['skills'])))
        version=call('profile',dict(profile=profile,expected_version=None),'PUT')['version']
    conversation=call('product/conversations',dict(idempotency_key='synthetic-create'))['conversation']
    cid=conversation['conversation_id']
    body=dict(conversation_id=cid,message='now based on my profile, recommend the roadmap to become eML engineer',
              idempotency_key='synthetic-roadmap',expected_profile_version=version)
    report=dict(case=args.case,environment=args.base,synthetic=True,mocked=False,results=[])
    def ask(body):
        start=time.perf_counter();result=call('product/conversation-turn',body)
        response=result.get('response',{});generation=response.get('generation')
        report['results'].append(dict(status=result['turn']['status'],elapsed_ms=round((time.perf_counter()-start)*1000,3),
            answer=response.get('answer'),provider=response.get('provider'),diagnostics=response.get('diagnostics'),
            generation=generation,action_status=response.get('action_status')))
        return result
    first=ask(body)
    if args.followup and first.get('response',{}).get('generation'):
        if args.followup_delay_seconds:time.sleep(args.followup_delay_seconds)
        ask(dict(body,message='I can study six hours a week. My Python notebook predicts bus delays, but I cannot tell whether it generalizes. How should the first milestone change?',idempotency_key='synthetic-unseen-followup'))
    replay=call('product/conversation-turn',body)
    assert replay.get('response')==first.get('response'),'exact replay changed'
    loaded=call('product/conversation',dict(conversation_id=cid))
    report['stored_message_count']=len(loaded['messages'])
    report['replayed_without_new_message']=len(loaded['messages'])==2*len(report['results'])
    report['plan_count']=len(call('plans')['plans'])
    report['status']='passed' if all(r.get('generation') and r['provider']['status']=='available' for r in report['results']) else 'provider_or_validation_unavailable'
    folder=Path('ml/artifacts/session-a/product/morning');folder.mkdir(parents=True,exist_ok=True)
    target=folder/('guidance-'+args.case+'-'+str(time.time_ns())+'.json')
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    assert report['status']=='passed',report['status']
    assert report['replayed_without_new_message'] and report['plan_count']==0

if __name__=='__main__':main()
