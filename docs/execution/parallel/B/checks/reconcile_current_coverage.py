"""Read committed A coverage and B evidence; never mutate a sibling checkout."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

from minder_ml.intelligence.data_pipeline import MARKET_DATA, ROOT, encoded, utc_now


def reconcile(a_ref):
    revision=subprocess.check_output(['git','rev-parse',a_ref],text=True).strip()
    source='docs/execution/parallel/A/N3.1.json'
    coverage=json.loads(subprocess.check_output(['git','show',revision+':'+source],text=True))
    roles=coverage['actual_coverage']['current_market']['roles']
    published=json.loads((MARKET_DATA/'published-role-observations.v1.json').read_text())
    context=json.loads((MARKET_DATA/'current-public-evidence.v1.json').read_text())
    rows=[]
    for r in published['observations']:
        latest=r['period']['end']=='2026-06-30'
        rows.append({'source_id':r['source_id'],'source_entity_id':r['entity_id'],'label':r['label'],
            'period':r['period'],'value':r['value'],'unit':r['unit'],'source_url':r['source_url'],
            'published_at':r['published_at'],'available_at':r['available_at'],
            'occupation_code':None,'classification':r['classification'],
            'delivery_status':'awaiting_occupation_mapping_for_canonical_use' if latest else 'historical_context_only',
            'already_callable_as_source_native_context':True,
            'canonical_role_mapping_applied':False,
            'comparison_status':'unsuitable_for_A_Bosch_ad_count_cohort',
            'exact_reasons':['Published offering quantity/source universe/quarter differs from the 155-requisition employer snapshot.',
                'The extracted source entry supplies a label but no verified occupation code; no code inferred from similar titles.',
                'Unique-ad deduplication and positions-per-ad equivalence are unverified.']+
                ([] if latest else ['Older than the latest acquired DOSM Q2 2026 release; missing top-list entries are not zero.'])})
    return {'version':'current-coverage-reconciliation-v1','checked_at':utc_now(),
        'A_reference':{'commit':revision,'report':source,'report_as_of':coverage['actual_coverage']['as_of']},
        'A_four_market_informed_roles':[dict(r,delivery_status='already_integrated_and_usable_under_A_existing_provisional_policy',
            classification_basis='B declared employer-title rules plus exact native O*NET ID aliases; not an official MASCO crosswalk',
            limitations=['Known zero only within the inspected Bosch sample; never low national demand.',
                'New institutional shortage facts do not automatically alter this numeric ordering.']) for r in roles],
        'official_role_observations':rows,
        'official_status_counts':dict(Counter(r['delivery_status'] for r in rows)),
        'other_acquired_evidence':[
            {'source':'MyCOL 2024/2025','distinct_occupation_groups':66,'classification':'MASCO 2020 4-digit',
             'delivery_status':'newly_callable_source_coded_context; awaiting_A_context_integration_and_canonical_code_mapping',
             'comparison_status':'not_an_ad_count_or_rank; designation_not_comparable_to_Bosch_counts',
             'exact_reason':'Shortage classification; subset of six-digit children may be designated; non-listing stays unknown.'},
            {'source':'DOSM latest economic activities','distinct_sector_labels':21,
             'delivery_status':'newly_callable_source_native_current_context; awaiting_A_context_integration',
             'comparison_status':'current_levels_only; no_narrow_role_allocation',
             'exact_reason':'National source marginals, large unclassified count and classification/coverage-review flag; not joint role-sector observations.'},
            {'source':'DOSM latest major occupation groups','distinct_major_groups':9,
             'delivery_status':'newly_callable_broad_current_context; awaiting_A_context_integration',
             'comparison_status':'unsuitable_for_narrow_role_count_comparison',
             'exact_reason':'Broad major group grain cannot be treated as each canonical role; native codes absent from the workbook are left null.'},
            {'source':'JobStreet original 69024-ad corpus','delivery_status':'historical_context_only',
             'comparison_status':'unsuitable_for_live_current_or_complete_quarter_flow_comparison',
             'exact_reason':'Surviving weekly-scrape corpus, dates end May 2025; missing quarters, collection windows, historical availability and per-record country verification.'},
            {'source':'Galaxy public occupational aggregates','source_distinct_six_digit_occupations':3041,
             'source_distinct_four_digit_groups':428,'delivery_status':'public_inspection_completed_bulk_distribution_held',
             'comparison_status':'not_integrated; source_period_and_reuse_conditions_must_be_respected',
             'exact_reason':'Linked terms clauses 4.3/4.4 restrict storage/reproduction/distribution; no separate open licence or permission located. No bulk rows exported.'},
            {'source':'Other pinned references: O*NET/ESCO/ILO, labour force and wages',
             'delivery_status':'reference_or_context_only_for_this_market_expansion',
             'comparison_status':'unsuitable_as_advertisement_demand_counts',
             'exact_reason':'Foreign occupational requirements/crosswalks, technical AI exposure, employment stocks or wages have different geography or quantities. No conversion to MY ad counts.'}],
        'new_application_context_coverage':context['coverage'],
        'privacy':'No CVs/applicant profiles/recruiter contacts acquired; derived context contains only allowlisted aggregate facts.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--a-ref',default='session/a-personal-integration')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/execution/parallel/B/CURRENT_COVERAGE_RECONCILIATION.v1.json')
    args=parser.parse_args();result=reconcile(args.a_ref);args.output.write_text(encoded(result))
    print(encoded({'A_roles':len(result['A_four_market_informed_roles']),
                   'official_status_counts':result['official_status_counts'],
                   'new_context_coverage':result['new_application_context_coverage']}),end='')
