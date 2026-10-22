"""G1A policy projection. The review document remains the single policy authority."""
import copy
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from .schemas import FEATURE_NAMES
from .scoring import BASELINE_WEIGHTS

ROOT = Path(__file__).resolve().parents[4]
POLICY_DOCUMENT = ROOT / 'ml/docs/MINDER_POLICY_REVIEW_v1.md'
POLICY_CONFIG = ROOT / 'ml/configs/intelligence/policy.v1.json'


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


@lru_cache(maxsize=8)
def _validated(config_bytes, document_bytes, authorization_bytes):
    config = json.loads(config_bytes)
    authorization = json.loads(authorization_bytes)
    if authorization.get('authorized_scope') != 'G1A deterministic feature/policy implementation and local verification only':
        raise ValueError('execution authorization scope mismatch')
    match = re.search(r'## config/intelligence/policy.v1.json\s+```json\n(.*?)\n```',
                      document_bytes.decode(), re.S)
    if not match or config != json.loads(match.group(1)):
        raise ValueError('policy projection differs from canonical document')
    f = config['features']
    if (f['order'] != list(FEATURE_NAMES) or f['weights'] != list(BASELINE_WEIGHTS)
            or f['symbols'] != list('CITRW') or f['assessment_completeness_required'] != 1
            or f['silent_imputation'] or f['silent_reweighting']
            or f['criterion_anchor_values'] != [0, .5, 1]
            or any(f[k] != 1 for k in ('required_criterion_weight_default',
                'interest_tag_weight_default', 'resource_group_weight_default',
                'work_style_tag_weight_default'))):
        raise ValueError('unsupported personal-fit policy; explicit migration required')
    return config, {'policy_id': config['policy_id'], 'policy_version': config['schema_version'],
                    'policy_sha256': hashlib.sha256(config_bytes).hexdigest(),
                    'canonical_document_sha256': hashlib.sha256(document_bytes).hexdigest(),
                    'authorization': {'version': authorization['version'],
                                      'effective_instruction_sha256': authorization['effective_instruction_sha256'],
                                      'path': 'docs/execution/gates/G1A_v2_authorization.json',
                                      'scope': authorization['authorized_scope']},
                    'historical_approval': config['approval']}


def load_policy():
    # Re-read bytes to detect edits; validation happens once per unchanged content.
    return copy.deepcopy(_validated(POLICY_CONFIG.read_bytes(), POLICY_DOCUMENT.read_bytes(),
                                    (ROOT / 'docs/execution/gates/G1A_v2_authorization.json').read_bytes()))
