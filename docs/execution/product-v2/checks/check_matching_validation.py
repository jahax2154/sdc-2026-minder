import json,tempfile,time
from pathlib import Path
from unittest.mock import patch
from minder_ml.intelligence.product_runtime import build
from minder_ml.intelligence import service_contracts as sc,role_fit,market_evidence,app_context
out=Path('ml/artifacts/session-a/product/morning');out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(dir=out) as tmp:
 app,_=build('A',database=Path(tmp)/'runtime.sqlite3');app.services.personal.as_of='2026-10-24T06:00:00Z'
 token=app.store.session()['token'];app.dispatch('PUT','/api/profile',dict(profile=dict(synthetic=True,onboarding=dict(stage='studying',objective='fit',context='Fictional computing student')),expected_version=None),token)
 def request():
  begin=time.perf_counter();r=app.dispatch('POST','/api/product/views/career-match',{},token)
  return r,round((time.perf_counter()-begin)*1000,3)
 with patch.object(sc,'validate',sc._validate_uncached),patch.object(role_fit,'validate',sc._validate_uncached),patch.object(market_evidence,'validate',sc._validate_uncached),patch.object(app_context,'validate',sc._validate_uncached):
  before,before_ms=request()
 sc._RECOMMENDATION_DIGESTS.clear()
 after,after_ms=request();assert before['data']==after['data']
 report=dict(evidence='Actual source services and authenticated application dispatch, synthetic missing-evidence Profile, no model; source process already initialized',before_ms=before_ms,after_ms=after_ms,public_payload_identical=True,coverage=after['data']['recommendation']['coverage'],validation='Same structural/cross-field checks; only exact fully validated result digest reused between internal/public boundaries')
 (out/'matching-validation-benchmark.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
