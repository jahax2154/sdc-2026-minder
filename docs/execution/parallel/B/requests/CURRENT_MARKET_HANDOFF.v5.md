# B1.1-R05 — verified selected six-digit MyCOL scope

Consume B1.1-R04 `f9dcd93`, then the commit containing this refinement. The v4 handoff remains the early delivered checkpoint; this update resolves specific six-digit scope that was unknown in its examples.

Four original MyCOL occupation profiles were inspected from the same acquired public PDF: MASCO 2020 groups **2141**, **2411**, **2512**, **2524**, PDF pages **79**, **113**, **125**, **137**. Their explicit code blocks contain **43** distinct six-digit memberships in total. Nominated-job-title restrictions remain attached. This is positive source evidence, not blanket membership of every child or a code-to-individual-title pairing.

The existing additive query now returns a source fact with `query_scope.relationship=explicitly_enumerated_six_digit_member` for verified codes:

```python
market.current_context(as_of=now, occupation_system="MASCO",
                       occupation_version="2020", occupation_code="2512-01")
```

Examples also verify `2141-03`, `2411-25`, and `2524-01`. A non-matching query such as `2512-99` remains unknown, never low demand. The returned occupation object remains the four-digit parent, with the six-digit query and source page separately identified; no child label or O*NET mapping is fabricated.

`current-context-examples.v2.json` records actual outputs. Source codes are MASCO codes, not A's `onet:*` IDs. Canonical occupation mapping still requires code-backed acceptance; no title-only translation, numerical score or market-count comparison is introduced by B.

Coverage remains **66 four-digit shortage groups**, **21 DOSM sector labels**, **9 major occupation groups**, **1 identified employer feed**. The 43 six-digit memberships are a more precise scope within four of those groups; they are not added to the 66 as a cross-level grand total. Galaxy bulk redistribution remains held under the recorded terms. No forecast history or paid execution blocks this current-context delivery.
