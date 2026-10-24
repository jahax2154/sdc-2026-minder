"""Actual catalogue/Qwen/public HTTP/canonical SQLite journey; no browser claim.

Fresh owner, short normal intake only. Never seed anchored evidence or a plan.
No provider fixture, hidden retry, manual quota pause or credential output.
"""
from pathlib import Path
import json
import time
from minder_ml.intelligence.product_runtime import build
from minder_app.store import AppError

ROOT=Path('ml/artifacts/session-a/product/morning')/('native-candidate-'+str(int(time.time())))
ROOT.mkdir(parents=True,exist_ok=False)

def main():
    app,_=build('A',database=ROOT/'next-native-journey.sqlite3')
    session=app.store.session();token=session['token'];owner=session['profile_id']
    report=dict(kind='real-provider canonical application dispatch; not browser/hosted proof',
        steps=[],turns=[],started_at=time.time())
    def call(path,body=None,method=None):
        return app.dispatch(method or ('GET' if body is None else 'POST'),'/api/'+path,body or {},token)
    def save():
        (ROOT/'next-native-journey-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    def step(name,fn):
        try:
            detail=fn();report['steps'].append(dict(name=name,status='pass',detail=detail));save();return detail
        except Exception as error:
            report['steps'].append(dict(name=name,status='fail',error=getattr(error,'code',str(error))[:180]));save();raise
    profile=call('profile',dict(profile=dict(onboarding=dict(stage='studying',objective='fit',context='Computer science',
        interests=['software development'],self_reported_skills=['Python'],experience_state='none_yet'))),'PUT')
    assert profile['evidence']==[] and not profile['constraints']
    starter=call('product/starter-recommendations',{})
    step('normal short intake without CV or anchored rubric',lambda:dict(evidence_count=len(profile['evidence']),
        initial_options=[dict(role_id=o['role_id'],label=o['label'],status=o['status'],personal_assessment=o['personal_assessment']) for o in starter['options']],coverage=starter['coverage']))
    role=next((o for o in starter['options'] if o['label']=='Software Developers'),starter['options'][0])
    direction=call('product/direction',dict(role_id=role['role_id'],plan_id=None,expected_version=None,idempotency_key='select'),'PUT')
    bot=call('product/mindbot-conversation')['conversation']['conversation_id']
    conversation=call('product/conversations',dict(title='Native fresh intake conversation',idempotency_key='chat'))['conversation']['conversation_id']
    def turn(cid,message,key):
        started=time.perf_counter()
        result=call('product/conversation-turn',dict(conversation_id=cid,message=message,
            expected_profile_version=profile['version'],idempotency_key=key))
        response=result['response']
        report['turns'].append(dict(key=key,elapsed_ms=round((time.perf_counter()-started)*1000,3),
            answer=response['answer'],provider=response['provider'],response_mode=response['response_mode'],
            diagnostics=response['diagnostics']))
        (ROOT/('next-native-'+key+'.json')).write_text(json.dumps(result,indent=2)+'\n');save()
        assert response['provider']['status']=='available',response['provider']
        return response
    response=step('real structured proposed plan',lambda:turn(bot,
        'Create a practical learning roadmap for '+role['label']+'. Use my saved background and give concrete learning phases and activities. Do not save or change my plan.','plan'))
    generation=response['generation'];assert generation['advice']['stages']
    accept=dict(draft_id=generation['draft_id'],role_id=role['role_id'],expected_profile_version=profile['version'],
        expected_generation_version=generation['record_version'],idempotency_key='accept')
    saved=call('product/generation-accept',accept);assert call('product/generation-accept',accept)==saved
    plan=saved['plan'];assert len(call('plans')['plans'])==1
    call('product/direction',dict(role_id=role['role_id'],plan_id=plan['plan_id'],expected_version=direction['version'],idempotency_key='activate'),'PUT')
    step('accept saves one canonical plan',lambda:dict(tasks=len(plan['tasks']),duplicate_accept_same_result=True,plans=1))
    views={name:call('product/views/'+name) for name in ('roadmap','tasks','progress','overview')}
    skills=call('role-requirements',{})
    assert len({json.dumps(view['data'],sort_keys=True) for view in views.values()})==4
    assert views['overview']['data']['active_plan']['plan_id']==plan['plan_id']
    step('canonical distinct view data (browser separate)',lambda:dict(views=list(views),skills_source_records=skills['display']['source_record_count'],plan_id=plan['plan_id']))
    task=plan['tasks'][0]
    call('product/task-action',dict(plan_id=plan['plan_id'],task_id=task['task_id'],operation='complete',
        expected_state_version=plan['state_version'],idempotency_key='complete'))
    assert call('product/progress')['completed_count']==1
    app,_=build('A',database=ROOT/'next-native-journey.sqlite3')
    step('task completion persists after app reconstruction',lambda:dict(completed=call('product/progress')['completed_count'],plans=len(call('plans')['plans'])))
    # Ordinary consecutive turns: a two-second natural reading gap, not65seconds.
    for index,message in enumerate(['What small software project could I use to practise debugging?',
        'I only know basic Python. How should I make the first version smaller?',
        'What should I write down when I get stuck, so I can learn from it?']):
        if index:time.sleep(2)
        try:step('ordinary consecutive guidance '+str(index+1),lambda m=message,i=index:turn(conversation,m,'ordinary-'+str(i)))
        except AssertionError:pass  # preserve failure, continue independent checks; never replay this request
    # Availability is collected only when constructing an actual schedule.
    profile=call('profile',dict(profile=dict(onboarding=dict(profile.get('onboarding',{}),weekly_study_hours=6)),expected_version=profile['version']),'PUT')
    plan=call('plans')['plans'][0];task=next(t for t in plan['tasks'] if t['state']=='proposed')
    message='Please reschedule '+task['title']+' to 2026-12-01T15:00:00+08:00.'
    def proposal(key):
        result=turn(conversation,message,key)
        event=next(e for e in call('product/minder-handoffs')['events'] if e['event_id']==result['diagnostics']['handoff']['event_id'])
        assert event['status']=='pending',event.get('clarification_code')
        assert len([n for n in call('product/mindbot-conversation')['messages'] if n['message_id']==event['mindbot_message_id']])==1
        return event
    try:
        event=step('Minder creates one approval-only singleton proposal',lambda:proposal('schedule-reject'))
        before=call('plans')
        rejected=call('product/handoff-decision',dict(event_id=event['event_id'],decision='reject',expected_version=event['version'],idempotency_key='reject'))
        assert not rejected['target_changed'] and call('plans')==before
        step('rejection changes no plan',lambda:dict(target_changed=False))
        event=step('second explicit request produces an approval preview',lambda:proposal('schedule-approve'))
        decision=dict(event_id=event['event_id'],decision='approve',expected_version=event['version'],idempotency_key='approve')
        applied=call('product/handoff-decision',decision);assert call('product/handoff-decision',decision)==applied
        step('approval applies once',lambda:dict(target_changed=applied['target_changed'],replayed_saved_result=True))
        app,_=build('A',database=ROOT/'next-native-journey.sqlite3')
        assert any(e['status']=='approved' for e in call('product/minder-handoffs')['events'])
        step('history proposal and accepted state survive reconstruction',lambda:dict(
            plans=len(call('plans')['plans']),events=len(call('product/minder-handoffs')['events']),completed=call('product/progress')['completed_count']))
    except (AssertionError,AppError):pass  # keep failed handoff evidence; still verify independent public retrieval
    # A separate unsaved owner proves that market questions don't need intake.
    session=app.store.session();token=session['token'];owner=session['profile_id'];profile=dict(version=None)
    cid=call('product/conversations',dict(title='No profile market question',idempotency_key='new'))['conversation']['conversation_id']
    web=step('actual no-profile public-page answer',lambda:turn(cid,
        'Using current Malaysian sources, what does MyCOL occupation shortage evidence tell me and what does it not show?','web'))
    assert web['statements'] and not app.store.list(owner,'profile')
    report['completed_at']=time.time()
    report['gate_passed']=all(s['status']=='pass' for s in report['steps']) and any(s['name']=='approval applies once' for s in report['steps'])
    save();print(json.dumps(dict(gate_passed=report['gate_passed'],steps=[dict(name=s['name'],status=s['status']) for s in report['steps']],
        turns=[dict(key=t['key'],elapsed_ms=t['elapsed_ms'],provider=t['provider']) for t in report['turns']]),indent=2))
    assert report['gate_passed'],'Native gate incomplete; inspect explicit failed or absent steps'

if __name__=='__main__':main()
