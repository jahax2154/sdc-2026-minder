"""CL3 live C HTTP/provider acceptance. Prints booleans only; no response dumps."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import uuid

ROOT=Path(__file__).resolve().parents[3]
BASE='http://127.0.0.1:9103/api/'
FAMILIES=('employer_observation','published_offering_activity','occupation_shortage','sector_context')

def main():
    checks={}
    token=''
    def api(path,body=None,method=None,override=None):
        request=Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,
            method=method or ('POST' if body is not None else 'GET'),
            headers={'Content-Type':'application/json','Authorization':'Bearer '+(token if override is None else override)})
        with urlopen(request,timeout=45) as response:
            return json.loads(response.read())
    try:
        session=api('session',{})
        token,owner=session['token'],session['profile_id']
        profile=dict(profile_id='new',profile_group_id='new',version='new',synthetic=True,evidence=[],
            preferences=[],current_fields=[],constraints=[],timezone='Asia/Kuala_Lumpur')
        profile=api('profile',dict(profile=profile,expected_version=None),'PUT')
        role='onet:15-1252.00'
        evidence=api('role-evidence',dict(role_id=role))
        canonical={p['canonical_passage']:p for p in evidence['passages']}
        reply=api('chat',dict(message='Explain all four evidence families and their limitations: employer observations, published offering activity, related occupation shortage group and broader sector context.',
            expected_profile_version=profile['version'],selected_role_ids=[role]))
        provider_diagnostics={code:reply['provider'].get('code')==code for code in
            ('provider_http_error','provider_tool_response_invalid','provider_rate_limited','provider_network_or_timeout')}
        for family in FAMILIES:
            selected=[c for c in reply['statements'] if c.get('measurement_type')==family and c['status']=='available']
            checks[family+'_real_selection_success']=bool(selected) and reply['provider']['status']=='available'
            checks[family+'_source_meaning_match']=bool(selected) and all(c['text'] in canonical and
                c['sources']==[canonical[c['text']]['record']['source']] and
                c['mapping']==canonical[c['text']]['record']['mapping'] and
                c['period']==canonical[c['text']]['record']['observation_period'] for c in selected)
            checks[family+'_native_tool_success']=(reply['provider'].get('model')=='openai/gpt-oss-20b' and
                reply['provider'].get('tool_call',{}).get('arguments_validated') is True)
        attack=reply
        forecasts=[c for c in attack['statements'] if c.get('kind')=='forecast']
        checks['unavailable_forecast_preserved']=bool(forecasts) and all(c['status']=='unavailable' and 'No value is inferred' in c['text'] for c in forecasts)
        checks['unsupported_scope_and_false_success_withheld']=('999999' not in json.dumps(attack) and
            attack['action_status']=='no_mutation_requested_or_executed' and api('profile')==profile and api('action-history')['history']==[])
        assert checks['unavailable_forecast_preserved'] and checks['unsupported_scope_and_false_success_withheld']
        def make_plan(task_id):
            task=dict(task_id=task_id,state='proposed',activity_completion=False,mastery_verified=False,
                prerequisite_task_ids=[],locked=False,scheduled_at=None,estimated_hours=None,evidence_ids=[])
            plan=dict(plan_id='new',profile_id=owner,selected_role_id=role,state_version='new',previous_version=None,
                task_ids=[task_id],tasks=[task],progress_event_ids=[],constraints=[])
            return api('plans',dict(plan=plan,idempotency_key=str(uuid.uuid4())))['plan']
        def request(plan):
            return dict(kind='complete_task',target_id=plan['plan_id'],expected=plan['state_version'],
                diff=[dict(path='/tasks/'+plan['task_ids'][0]+'/state',before='proposed',after='completed')],
                reason='Specific fictional-user acceptance instruction')
        plan=make_plan('direct')
        command=dict(request=request(plan),idempotency_key=str(uuid.uuid4()))
        result=api('direct-action',command)
        checks['direct_persisted_and_idempotent']=result==api('direct-action',command) and result['target']['tasks'][0]['activity_completion'] and result['action']['approval_state']=='not_required_direct'
        other=api('session',{})['token']
        try:
            api('direct-action',command,override=other)
            checks['cross_user_blocked']=False
        except HTTPError as exc:
            checks['cross_user_blocked']=exc.code==404
        plan=make_plan('proactive')
        req=request(plan)
        read=lambda:next(p for p in api('plans')['plans'] if p['plan_id']==plan['plan_id'])
        proposal=api('proposals',dict(request=req))
        checks['proactive_no_mutation']=read()==plan
        decision=dict(proposal_id=proposal['preview']['proposal_id'],decision='reject',preview_hash=proposal['preview_hash'],expected_state_version=plan['state_version'])
        rejected=api('proposal-decision',decision)
        checks['rejection_preserves_target']=rejected['status']=='rejected' and read()==plan
        proposal=api('proposals',dict(request=req))
        stale=api('proposals',dict(request=req))
        decision.update(proposal_id=proposal['preview']['proposal_id'],decision='approve',preview_hash=proposal['preview_hash'])
        approved=api('proposal-decision',decision)
        checks['approval_persisted_once']=approved==api('proposal-decision',decision) and read()==approved['target']
        decision.update(proposal_id=stale['preview']['proposal_id'],preview_hash=stale['preview_hash'])
        try:
            api('proposal-decision',decision)
            checks['stale_approval_blocked']=False
        except HTTPError as exc:
            checks['stale_approval_blocked']=exc.code==409
        # Existing actual wall-clock scheduler acceptance is not repeated. Check
        # the NEW CLI evidence path on a real persisted completion event only.
        subprocess.run([sys.executable,'-m','minder_app.worker','--once','--owner',owner],cwd=ROOT,
            check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        notices=api('agents')['notices']
        checks['actual_worker_new_evidence_path']=any({c['measurement_type'] for c in n.get('statements',[])
            if c.get('kind')=='market_evidence' and c['status']=='available'}==set(FAMILIES) for n in notices)
        checks['worker_no_unapproved_change']=read()==approved['target'] and all(n.get('proposal_only') is True for n in notices)
        checks['all_checks_passed']=all(checks.values())
    except Exception:
        checks['all_checks_passed']=False  # no secrets, response/error bodies or traceback locals
    record=dict(backend_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        recorded_at=datetime.now(timezone.utc).isoformat(),synthetic_user=True,real_provider=True,
        real_source_services=True,wall_clock_scheduler_repeated=False,checks=checks,
        provider_diagnostics=locals().get('provider_diagnostics',{}))
    target=ROOT/'ml/artifacts/session-c/live-evidence-bridge.json'
    target.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(checks,sort_keys=True))
    return 0 if checks.get('all_checks_passed') else 1

if __name__=='__main__':
    sys.exit(main())
