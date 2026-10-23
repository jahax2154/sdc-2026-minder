# B1.1-R04 — early MyCOL/DOSM coverage expansion

Integrate the commit containing this handoff. All code/data/reports are B-owned. No root dependency, shared JSON schema, A/C source, score formula or forecast change is included. The additive B context envelope is documented by examples; A coordinates any formal shared-schema/consumer integration.

**New usable native context:** 66 distinct MASCO 2020 four-digit national shortage groups from MyCOL 2024/2025; 21 distinct latest DOSM sector labels; 9 latest major occupation groups. These are different grains and are not summed into one occupation total. The MyCOL landing declares 18 study sectors; this is not an invented 18-sector mapping for every listed occupation. Identified current employers remain **1**, the existing Bosch source: no respondent names or unique employer population is inferred from institutional aggregates.

```python
from datetime import datetime, timezone
from minder_ml.intelligence.market_service import MarketEvidenceService

market = MarketEvidenceService(aliases={"role": role_aliases(catalogue)})
now = datetime.now(timezone.utc).isoformat()
shortage = market.current_context(
    as_of=now, occupation_system="MASCO", occupation_version="2020",
    occupation_code="2512")
sector = market.current_context(
    as_of=now, evidence_ids=["dosm:jmi:2026-q2:sector:manufacturing"])
codes_and_types = market.current_context_catalogue(as_of=now)
```

MyCOL returns an institutional **designation**, not an ad count or score. Non-listing returns unknown, never low demand. Four-digit listing does not imply every six-digit child is critical: the publication can restrict scope to nominated job titles. A six-digit membership query currently returns unknown. The exact publication date/continuous fieldwork window was not verified; records preserve the 2024/2025 edition and explicitly nullable dates, separate from actual acquisition/derived availability. This is the latest linked institutional list, not a claim that its underlying data were measured today.

DOSM levels remain published source-covered job offerings for **2026 Q2**, published **18 August 2026**. Manufacturing is 20,074 offerings at sector grain; it is never allocated to Industrial Engineers or any other narrow role. The large economically unclassified count and coverage-change flags remain visible. The source does not supply native codes for these extracted sector/major-group labels; codes stay null instead of being inferred from titles or row order.

`CURRENT_COVERAGE_RECONCILIATION.v1.json` reconciles A's four actual market-informed roles: Accountants and Auditors, Software Developers, Data Scientists and Industrial Engineers. They retain their existing 0/5/0/0 Bosch count observations and declared provisional title-rule scope. Of the **35** acquired official role-label observations, **5** latest-quarter facts await code-based canonical occupation mapping for A ranking; **30** are historical/context-only. All 35 are already callable as source-native facts. Their quantities, universes, quarters and unverified unique-ad equivalence make them unsuitable for direct comparison with the 155-requisition cohort. No similarly named title is used to invent a crosswalk.

`OFFICIAL_SOURCE_COMPARISON.v1.json` compares the prior audit with all three requested official sources. Galaxy's public occupational API was accessible and inspected, including 3,041 six-digit codes/428 four-digit groups. Its linked terms clauses 4.3/4.4 restrict storage/reproduction/distribution, and no separate Galaxy open-data licence or written permission was located. **Zero Galaxy bulk records are shipped to the application or Git.** Do not equate inspected source breadth with usable application coverage. No candidate, CV, personal-profile or recruiter-contact endpoint was queried.

`current-public-evidence.v1.json` is versioned and checksummed in the serving registry. `current-context-examples.v1.json` contains actual source-coded calls. Only codes, labels, aggregate values/designations, geography, dates and provenance are allowlisted; raw prose, author/recruiter contacts and incidental personal information are excluded. MyCOL code extraction uses source Table7 geometry and a strict 66-unique-code check; no human-label approval is claimed. Raw PDF/OCR/tool dependencies remain ignored/local. Consumer serving requires only committed JSON and existing dependencies.

Current delivery is independent of missing forecast history. Broader **context** is now available; A still needs to consume the additive context interface and accept any genuine code-to-code canonical mapping before expanding its numerical role comparison. No change to A's scoring is inferred by B.
