# B1.2-R01 — explicit official role facts plus complete employer evidence

Integrate `b8478a3` (complete employer feed), `ee4096c` (actual historical-source audit/data), then the commit containing this handoff (callable official facts). All files are B-owned; no shared-schema/root-dependency change is requested. A/C source files were not edited.

The existing constructor and canonical alias contract remain unchanged:

```python
market = MarketEvidenceService(aliases={"role": role_aliases(catalogue)})
# Use the actual timezone-aware current issue timestamp, not a frozen midnight.
market.current("role", "onet:15-1252.00", as_of=issued_at)
market.current("skill", "source-term:sql", as_of=issued_at)
```

The full accessible Bosch feed contains 155 distinct native requisitions, with 154 observed qualification sections. Current software-developer count is 5; requested technology counts are Excel 27, SQL 11, C++ 8, Python 6 and Java 4. Older surviving listings and five identical-template/different-requisition cases are flagged. The single missing qualification section is unknown, not zero skills. See v2 handoff and coverage JSON for acquisition, deduplication, dates and limitations.

Additional source-native official evidence is now callable:

```python
source_label = "dosm:jmi:published-role-label:software-developers"
market.current("role", source_label, as_of=issued_at)
market.source_facts("role", source_label)
market.published_role_observations(as_of=issued_at)
market.forecast("role", source_label, issued_at=issued_at)
```

The latest Software Developer fact is **19,899 published online job offerings for 1 April–30 June 2026**, published by DOSM on **18 August 2026**. The other acquired explicit point is 20,089 for 2026 Q1. Thirty-five explicit numeric observations across seven source labels are packaged; 42 source-label/quarter cells remain missing. A name in a top list without a number is not a zero.

These records use `measurement=published_online_job_offerings_for_source_role_label`, `unit=published job offerings`, and a separate source universe. Do not add them to the five Bosch requisitions or pass them as dedup-verified unique-ad targets. Native codes/edition and unique-ad/positions-per-ad equivalence were not independently verified for every release. No automatic canonical crosswalk is applied: A can expose these as source-linked facts while retaining its canonical role catalogue and numerical policy.

`service-examples.v3.json` demonstrates validated actual calls, original source dates/URLs/hashes and forecast unavailability. Published dates are distinct from retrieved byte availability. Queries before retrieval cannot assume independently archived historical bytes. In particular, an A integration fixed at `2026-10-23T00:00:00Z` predates the expanded employer and acquired official evidence; use a genuine current issue time when testing the new snapshot.

The forecast stays unavailable with precise unique-ad/history reasons. Source facts retain original scope, classification and missingness. No new market index, fit arithmetic, current/future weight or model promotion is introduced by B.

The original 69,024-ad JobStreet corpus has been inspected and compiled separately under `ml/data/market/research/`. Its source describes a current weekly scrape, with no complete historical windows or per-record historical availability. Literal mentions and conservative explicit-request clauses are distinguished. These are dated frozen-corpus research counts, not live-current evidence or approved quarterly flow targets. `HISTORICAL_SOURCE_AUDIT.v1.md/json` records all 33 endpoint attempts and the exact remaining data gaps. B retains ownership of that investigation; no dataset research is delegated to the user or A.
