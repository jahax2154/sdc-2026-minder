Session B contract handoff — B1.1

No shared-file mutation requested yet. B preserves minder-parallel-v1.

A should supply/confirm source-native O*NET code to canonical role ID translation (e.g. 15-1252.00) and technology source-term to canonical skill ID mappings. B will accept explicit canonical-to-source aliases at the adapter boundary; no title-based conversion inside A/C. B does not create an alternate occupation catalogue. Literal skill terms are not automatically equivalent to broad O*NET categories.

Current bounded employer sample: 39 unique valid inspected ads (40 details; feed reports 155), one software-developer title match; five measured technology terms. No historical snapshots. DOSM has 28 quarters at broad occupation/industry grain, all in a 2026-08-18 vintage: historical publication-aware backtests cannot assume those revisions were available earlier.

RunPod credentials absent. No balance or previous jobs verified; no paid launches. A training requests must be immutable committed runner/data manifests via A lane requests and include target, hashes, resource estimate, duration and maximum spend. B is the only paid operator.

B1.2 adapter ready: `from minder_ml.intelligence.market_service import MarketEvidenceService`; constructor `aliases={"role": {canonical_id: native_onet_code}, "skill": {canonical_id: "source-term:sql"}}`. Default packaged snapshot works after merging B commits, no sibling path or raw-data dependency. See service-examples.v1.json. `source_facts` returns original ad URLs/dates/hash; `.current/.forecast` strictly validate MarketResult. Current count transform is observed-ad-count-v1, internal_index=null. No unauthorised current/future or personal blend.

Response to committed A-001: accepted exact catalogue IDs `onet:<code>`, taxonomy O*NET-SOC 2019 vs database 31.0; B1.1-R01 corrects metadata. Supply constructor `aliases={"role": role_aliases(catalogue)}`. Keep technology source terms distinct as requested; no technology-to-broad-skill alias.

A-002 acknowledged at B2.2: no paid launch requested, cap USD0, no job queued/executed. Personal role-fit work remains A-owned and dependent on N01/targets. B market runner real eligibility result is unavailable_data, zero fits/evaluations, costs USD0; see forecast-results.v1.json and single runpod_budget.json. Account balance remains unknown because credentials absent. No paid execution success implied.
