"""Resume isolated native test state after quota cooldown; trusted service owner.

This is component evidence, NOT a new browser/login acceptance. Existing plan
must originate in the preceding short-intake native journey, never a seeded plan.
No session credential is recovered, exported or fabricated.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from minder_ml.intelligence.product_runtime import build
from minder_app import conversations, handoffs


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--database',type=Path,required=True);args=parser.parse_args()
    database=args.database.resolve()
    root=Path('ml/artifacts/session-a/product/morning').resolve()
    assert database.is_relative_to(root) and database.is_file()
    app,_=build('A',database=database)
    with app.store.connect() as db:
        owners=[r[0] for r in db.execute("SELECT owner FROM documents WHERE kind='plan'")]
    assert len(owners)==1
    owner=owners[0];profile=app.store.get(owner,'profile',owner)
    assert profile['evidence']==[] and profile['onboarding']['experience_state']=='none_yet'
    plan=app.store.list(owner,'plan')[0]
    assert len([g for g in app.store.list(owner,'generation') if g.get('accepted_plan_id')==plan['plan_id']])==1
    events=app.store.list(owner,'minder_handoff')
    assert any(e['status']=='rejected' for e in events)
    origin=events[0]['source_conversation_id'];bot=conversations.Conversations(app.store).mindbot(owner)
    task=next(t for t in plan['tasks'] if t['state']=='proposed')
    cooldown=max(0,app.provider._state().get('retry_at',0)-time.time())
    if cooldown:
        print(json.dumps(dict(status='blocked',retry_after_seconds=cooldown,transport_attempts=0)));return
    message='Please reschedule '+task['title']+' to 2026-12-02T15:00:00+08:00.'
    body=dict(conversation_id=origin,message=message,expected_profile_version=profile['version'],
        idempotency_key='native-approved-after-actual-cooldown')
    started=time.perf_counter()
    result=conversations.dispatch(app,owner,'POST','/api/product/conversation-turn',body)
    response=result['response']
    report=dict(scope='real Qwen + trusted owned canonical services on original isolated short-intake state; not browser/auth proof',
        elapsed_ms=round((time.perf_counter()-started)*1000,3),provider=response['provider'],
        origin_message_saved=True,profile_evidence_count=0,plans_before=1)
    output=database.parent/'next-native-approval-continuation.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    assert response['provider']['status']=='available',response['provider']
    event=next(e for e in app.store.list(owner,'minder_handoff') if e['event_id']==response['diagnostics']['handoff']['event_id'])
    assert event['status']=='pending',event.get('clarification_code')
    assert app.store.get(owner,'plan',plan['plan_id'])==plan
    replay=conversations.dispatch(app,owner,'POST','/api/product/conversation-turn',body)
    assert replay['response']==response
    notices=conversations.Conversations(app.store).mindbot(owner)
    assert len(notices['messages'])==len(bot['messages'])+1
    decision=dict(event_id=event['event_id'],decision='approve',expected_version=event['version'],idempotency_key='native-approve-once')
    before_count=len(app.actions.history(owner))
    applied=handoffs.decide(app,owner,decision)
    assert handoffs.decide(app,owner,decision)==applied
    assert len(app.actions.history(owner))==before_count+1
    saved=app.store.get(owner,'plan',plan['plan_id'])
    changed=next(t for t in saved['tasks'] if t['task_id']==task['task_id'])
    assert changed['state']=='scheduled' and changed['scheduled_at']=='2026-12-02T15:00:00+08:00'
    app,_=build('A',database=database)
    assert app.store.get(owner,'plan',plan['plan_id'])==saved
    assert app.store.get(owner,'minder_handoff',event['event_id'])['status']=='approved'
    report.update(status='passed',one_new_notice=True,turn_replay_no_model_call=True,
        canonical_action_delta=1,approval_replay_same_saved_result=True,restart_persisted=True,
        saved_state=changed['state'],saved_scheduled_at=changed['scheduled_at'],target_changed=applied['target_changed'],
        accepted_plan_preserved=True)
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
