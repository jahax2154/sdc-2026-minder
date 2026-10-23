"""Reproduce final coverage from pinned original inputs and current A/B services.

PYTHONPATH=ml/src python docs/execution/parallel/A/checks/coverage_audit.py --output ml/artifacts/session-a/<new-dir>
Synthetic profiles only; no independent labels or private-profile exports.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from minder_ml.intelligence.policy import ROOT
from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.integration_cli import role_aliases, provisional_demo_profile
from minder_ml.intelligence.market_service import MarketEvidenceService
from minder_ml.intelligence.personal_service import PersonalMatchingService
from minder_ml.intelligence.personal_cli import adapt_original_profile
from minder_ml.intelligence.role_fit import policy
from minder_ml.intelligence.policy_sources import role_reference_v3


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    output=parser.parse_args().output.resolve()
    if not output.is_relative_to((ROOT/'ml/artifacts/session-a').resolve()):raise ValueError('A artifacts required')
    output.mkdir(parents=True,exist_ok=False)
    cat=OccupationalCatalogue();roles=cat.roles();eligible=cat.roles(eligible_only=True)
    market=MarketEvidenceService(aliases={'role':role_aliases(cat)})
    stamp=datetime.now(timezone.utc).isoformat();service=PersonalMatchingService(market,as_of=stamp)
    report=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
        as_of=stamp,policy_id=policy()['policy_id'],reference_version=role_reference_v3()['version'],
        catalogue=dict(references=len(roles),eligible=len(eligible),partial=len(roles)-len(eligible),
            eligible_industry_mapped=sum(bool(r['industry_mappings']) for r in eligible),
            eligible_work_style_mapped=sum(bool(r.get('work_style_mappings')) for r in eligible)),
        profiles=[],current_market={},bootstrap_inputs={},independent_labels=0)
    original_path=ROOT/'ml/data/review/phase2/calibration-v1/profiles.synthetic.json';raw=original_path.read_bytes()
    originals=json.loads(raw)
    cases=[('original-synthetic-calibration',adapt_original_profile(p,raw)) for p in originals]
    cases += [('new-anchored-fresh-graduate',provisional_demo_profile()),
              ('incomplete-one-anchored-skill',provisional_demo_profile('incomplete',(2,)))]
    for kind,profile in cases:
        result=service.assess(profile,roles)
        summary=dict(kind=kind,profile_id=profile['profile_id'],synthetic=profile['synthetic'],
            coverage=result['public']['coverage'],status=result['public']['status'],
            overall_ranking_complete=result['public']['overall_ranking_complete'],
            targeted_questions=result['public']['targeted_questions'])
        report['profiles'].append(summary)
        print(json.dumps(summary),flush=True)
        if kind=='new-anchored-fresh-graduate':
            assert summary['coverage']['assessed']==910 and summary['coverage']['current_comparable_ranked']==4
            report['current_market']['roles']=[dict(role_id=r['entity_id'],count=r['value'],status=r['status'],
                period=r['observation_period'],available_at=r['available_at'],source_ids=r['source_ids'])
                for r in result['internal']['current_market'] if r['status']=='available']
            report['current_market']['role_forecasts_available']=sum(r['status']=='available' for r in result['internal']['forecast_market'])
        else:
            assert summary['coverage']['assessed']==0
    report['current_market']['skills']=[]
    for m in market.mapping['skills']:
        sid=m['source_skill_id'];current=market.current('skill',sid,as_of=stamp);future=market.forecast('skill',sid,issued_at=stamp)
        report['current_market']['skills'].append(dict(skill_id=sid,count=current['value'],status=current['status'],
            forecast_status=future['status'],target_period=future['target_period']))
    report['current_market'].update(inspected_ads=market.snapshot['collection']['accepted_ads'],
        qualifications_observed=market.snapshot['collection']['qualification_observed_ads'],
        source_universe=market.snapshot['source_universe_id'],scope='Observed employer feed; not national demand, verified active hiring or quarterly inflow.')
    snapshot=json.loads((ROOT/'docs/execution/parallel/source_snapshot.v1.json').read_text())
    checked=[]
    for item in snapshot['source_files']:
        p=ROOT/'ml/minder_ml_starter'/item['path']
        matches=hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
        readonly=not p.stat().st_mode & 0o222
        assert matches and readonly
        checked.append(dict(path=item['path'],hash_matches=matches,read_only=readonly))
    report['bootstrap_inputs']=dict(count=len(checked),all_preserved=True,files=checked,
        backup='Existing G0 read-only shared snapshot; no new external backup or input staging.')
    report['original_profiles_sha256']=hashlib.sha256(raw).hexdigest()
    report['limitations']=['Partial essential-skill evidence fit, not qualification or independent accuracy.',
        'No original calibration skill claims reinterpreted as the new anchored rubric.',
        'Unmatched industry/style evidence remains unknown and never fabricates an adjustment.',
        'No forecasts manufactured from new broad/censored/frozen-corpus research quantities.']
    (output/'coverage.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
