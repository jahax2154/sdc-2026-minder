"""Bounded local policy-distillation controls; no independent career-fit labels.

Run --output ml/artifacts/session-a/<new-run>. Baseline alone serves users.
Legacy preparation experiments/artifacts and B's paid-training lane are untouched.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import subprocess

from .policy import ROOT, fingerprint
from .role_fit import POLICY_ID, CONFIG, policy, _assessment
from .policy_sources import role_reference_v3
from .catalogue_service import OccupationalCatalogue
from .integration_cli import provisional_demo_profile
from .estimators import make_estimator
from .artifacts import fit_timed, predict_raw, versions
from .service_contracts import validate

FEATURES = ['capability_ratio', 'background_points', 'industry_interest_points', 'role_interest_points', 'work_style_points']
FEATURE_VERSION = 'role-fit-v3-known-components-v1'


def dataset():
    rng = random.Random(20261023)
    cat = OccupationalCatalogue(); ref = role_reference_v3(); p = policy()
    roles = [cat.role(r) for r in ('onet:15-1252.00','onet:15-2051.00','onet:17-2112.00','onet:13-2011.00',
             'onet:11-1011.00','onet:29-1141.00','onet:25-2021.00','onet:27-1024.00',
             'onet:41-2031.00','onet:43-6014.00','onet:49-3023.00','onet:35-1011.00')]
    assert all(r['eligibility']=='supported' for r in roles)
    industries = sorted({m['target_id'] for r in roles for m in r['industry_mappings']})
    styles = sorted(ref['work_style_labels'])
    rows = []
    for family in range(48):
        profile = provisional_demo_profile('distillation-' + str(family), [rng.choice((0,2,4,6)) for _ in range(10)])
        group = 'fictional-profile-family-' + str(family)
        for iid in rng.sample(industries, min(3,len(industries))):
            if rng.random() < .75:
                e=copy.deepcopy(profile['evidence'][0]);method='minder-transferable-background-v1'
                e.update(evidence_id=iid, subject_id=iid, value=rng.choice((0,.5,1)), unit='fraction_0_1', method_id=method,
                    assessment=dict(kind='transferable_background',statement='Fictional explicitly described study or domain work for provisional distillation only.',rubric_version=method))
                profile['evidence'].append(e)
            profile['preferences'].append(dict(entity_type='industry', entity_id=iid,
                state=rng.choice(('interested','neutral','not_interested')), authorizing_request_id='fictional-distillation'))
        for sid in rng.sample(styles, min(8,len(styles))):
            method='minder-work-style-preference-v1';e=copy.deepcopy(profile['evidence'][0])
            e.update(evidence_id=sid,subject_id=sid,value=rng.choice((0,.5,1)),unit='fraction_0_1',method_id=method,
                assessment=dict(kind='work_style_preference',statement='Fictional explicit preference for working conditions; no competence claim.',rubric_version=method))
            profile['evidence'].append(e)
        for r in roles:
            if rng.random()<.7:
                profile['preferences'].append(dict(entity_type='role',entity_id=r['role_id'],state=rng.choice(('interested','neutral','not_interested')),authorizing_request_id='fictional-distillation'))
        validate('Profile', profile)
        for r in roles:
            a=_assessment(profile,r,p,ref,'baseline')
            assert a['score_status']=='scored'
            c=a['components']
            rows.append(dict(profile_group_id=group,role_id=r['role_id'],x=[c[0]['value']]+[v['contribution_points'] for v in c[1:]],
                y=a['score'],label_provenance='provisional_policy_output_not_independent_review'))
    original_count = len(rows)
    first_group = {}
    retained = []
    for row in rows:
        group = first_group.setdefault(tuple(row['x']), row['profile_group_id'])
        if group == row['profile_group_id']:
            retained.append(row)
    rows = retained
    groups=sorted({r['profile_group_id'] for r in rows},key=lambda g:hashlib.sha256(g.encode()).hexdigest())
    split=dict(train=groups[:32],validation=groups[32:40],holdout=groups[40:])
    assert not (set(split['train'])&set(split['validation']) or set(split['train'])&set(split['holdout']) or set(split['validation'])&set(split['holdout']))
    # Also prevent exact component-vector duplication across fictional users.
    vectors={}
    for r in rows:vectors.setdefault(tuple(r['x']),set()).add(r['profile_group_id'])
    assert not any(len(g)>1 for g in vectors.values())
    return rows, split, dict(role_ids=[r['role_id'] for r in roles],
        original_rows=original_count, duplicate_vectors_removed=original_count-len(rows),
        exact_vectors_shared_across_groups=0)


def metrics(y, pred):
    pred=[max(0,min(100,v)) for v in pred]
    return dict(teacher_MAE=sum(abs(a-b) for a,b in zip(y,pred))/len(y),
                teacher_RMSE=math.sqrt(sum((a-b)**2 for a,b in zip(y,pred))/len(y)), count=len(y))


def run(output):
    output=Path(output).resolve()
    if not output.is_relative_to((ROOT/'ml/artifacts/session-a').resolve()):raise ValueError('A artifact root required')
    output.mkdir(parents=True,exist_ok=False)
    rows,split,coverage=dataset()
    (output/'dataset.synthetic.json').write_text(json.dumps(rows,indent=2)+'\n')
    partitions={k:[r for r in rows if r['profile_group_id'] in groups] for k,groups in split.items()}
    x={k:[r['x'] for r in v] for k,v in partitions.items()};y={k:[r['y'] for r in v] for k,v in partitions.items()}
    report=dict(phase_id='N2.1',policy_id=POLICY_ID,policy_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        reference_sha256=policy()['reference_sha256'],feature_names=FEATURES,feature_version=FEATURE_VERSION,
        code_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        implementation_sha256={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
            for name in ('role_fit.py','role_fit_experiments.py','estimators.py','integration_cli.py')},
        runner='local CPU, two threads, USD0; no RunPod launch',created_at=datetime.now(timezone.utc).isoformat(),
        package_versions=versions(),target='provisional_policy_distillation_0_100',independent_personal_fit_labels=0,
        promotable=False,serving_selection='baseline',selection_reason='Exact traceable policy; teacher agreement cannot establish career-fit validity.',
        dataset_sha256=hashlib.sha256((output/'dataset.synthetic.json').read_bytes()).hexdigest(),
        split=split,split_sha256=fingerprint(split),row_counts={k:len(v) for k,v in partitions.items()},coverage=coverage,
        candidates={},limitations=['Synthetic structured profile families; no independent target validity or empirical ranking accuracy.',
            'Holdout groups isolate fictional users; roles repeat deliberately, so unseen-role generalization is not tested.',
            'Unknown optional evidence is represented by its declared zero adjustment, not imputed raw ability.'])
    candidates=[]
    for alpha in (.1,1.,10.):
        model=make_estimator('ridge',ridge_l2=alpha);timing=fit_timed(model,x['train'],y['train'])
        candidates.append((metrics(y['validation'],predict_raw(model,x['validation']))['teacher_MAE'],alpha,model,timing))
    best=min(candidates,key=lambda row:(row[0],row[1]));selected={'ridge':(best[2],best[3])}
    model=make_estimator('xgboost');selected['xgboost']=(model,fit_timed(model,x['train'],y['train']))
    import joblib
    for kind,(model,timing) in selected.items():
        destination=output/(kind+'.joblib');joblib.dump(model,destination)
        original=predict_raw(model,x['holdout'])
        restored=joblib.load(destination)  # Only this process's freshly written, controlled artifact.
        reloaded=predict_raw(restored,x['holdout']);difference=max(abs(a-b) for a,b in zip(original,reloaded))
        assert difference<=1e-9
        report['candidates'][kind]=dict(validation=metrics(y['validation'],predict_raw(model,x['validation'])),
            holdout=metrics(y['holdout'],original),fit=timing,pipeline_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
            reload_max_absolute_difference=difference,live_selected=False)
    report['ridge_validation_search']=[dict(alpha=r[1],teacher_MAE=r[0]) for r in candidates]
    report['selected_ridge_alpha']=best[1];report['bounded_fits']=4
    baseline=[max(0,min(100,80*r['x'][0]+sum(r['x'][1:]))) for r in partitions['holdout']]
    report['candidates']['baseline']=dict(holdout=metrics(y['holdout'],baseline),live_selected=True,
        caveat='Policy teacher identity, not independently measured accuracy')
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(rows=report['row_counts'],candidates={k:v['holdout'] for k,v in report['candidates'].items()},
                         independent_labels=0,selected='baseline',paid_cost_usd=0),indent=2))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)

if __name__=='__main__':main()
