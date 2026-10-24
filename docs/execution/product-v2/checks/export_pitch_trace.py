"""Reproduce active internal scoring with synthetic data; never trains/promotes."""
import hashlib
import json
import math
from pathlib import Path
import tempfile
from minder_ml.intelligence.product_runtime import build
from minder_ml.intelligence.integration_cli import provisional_demo_profile
from minder_ml.intelligence.role_fit import reference
from minder_ml.intelligence.policy import ROOT


def summarize(context):
    rec=context['recommendation'];internal=rec['internal'];role='onet:15-1252.00'
    trace=next(t for t in internal['recommendation_traces'] if t['role_id']==role)
    assessment=next(t for t in internal['personal_assessments'] if t['role_id']==role)
    records=[r for r in internal['evidence_records'] if r['role_id']==role]
    configs={}
    for name in ('personal-role-fit.v3.json','personal-current-evidence.v2_1.json'):
        path=ROOT/'ml/configs/intelligence'/name
        configs[name]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),policy=json.loads(path.read_text()))
    calculation=dict(personal_points=trace['personal_score'],personal_weight=.85,
        activity_index=trace['current_index'],activity_weight=.15,shortage_adjustment=trace['shortage_points'],
        expected_total=min(100,.85*trace['personal_score']+.15*trace['current_index']+trace['shortage_points']))
    assert abs(calculation['expected_total']-trace['final_internal_score'])<1e-7
    return dict(synthetic=True,independent_validation=False,experiment_models_active=False,
        profile_recipe='provisional_demo_profile(levels=(4,)*len(reference()[skills]))',
        policy_configs=configs,coverage=rec['public']['coverage'],overall_ranking_complete=rec['public']['overall_ranking_complete'],
        role_id=role,personal_components=assessment['components'],assessment_coverage=assessment.get('assessment_coverage'),
        trace=trace,calculation=calculation,evidence=records,
        forecasting='Unavailable future forecasts are separate; no forecast value contributes.')


def main():
    out=ROOT/'ml/artifacts/session-a/product/morning';out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out) as folder:
        app,_=build('A',database=Path(folder)/'runtime.sqlite3')
        profile=provisional_demo_profile(levels=(4,)*len(reference()['skills']))
        result=app.services.career_context(profile,expected_profile_version=profile['version'])
        report=summarize(result)
    path=out/'pitch-trace.json';path.write_text(json.dumps(report,indent=2)+'\n');print(path)

if __name__=='__main__':main()
