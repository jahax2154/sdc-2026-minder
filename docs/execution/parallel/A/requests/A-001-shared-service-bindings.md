# A-001 — committed personal/market integration bindings

To B/C via committed lane handoff. A1.1 `915779f`, A1.2 `5ee8acd`, A1.3 `be60d34`,
A1.2-R01 `64dedd8`. Read `../PERSONAL_SERVICE_HANDOFF.md` for concrete constructors.
No change to B/C internals or dependencies requested from A.

`OccupationalCatalogue()` verifies pinned sources and loads 1,016 references,
910 supported for assessment. Canonical role ID is `onet:<source-code>`, e.g.
`onet:15-1252.00`. Taxonomy is O*NET-SOC **2019**; database release is **31.0**.
Do not use 31.0 as the taxonomy edition. All aliases are exact native identity,
not an ESCO/MASCO relation. A's `integration_cli.role_aliases(catalogue)` returns
the canonical-ID -> native-code dictionary from source occupation rows.
Please accept this dict at B's service adapter constructor and publish its exact
constructor in the B handoff. No technology-to-broad-skill aliases are accepted:
keep `source-term:sql`, etc. distinct. Preserve source terms for exploration;
do not map them to an O*NET category based on matching words.

`PersonalMatchingService()` returns real unranked profile-to-role results with
the canonical policy ID `personal-role-fit-v2-proposal`. C1.3's `N01-pending`
token is explicitly supported by A1.2-R01 during this pending state. No scores,
weights, qualification or fit probability are fabricated. `CareerServices` can
inject this directly, with `roles=catalogue.roles()` and
`sources=catalogue.coverage['sources']`. Use all roles for normal exploration;
an explicit selected-role view is supported for bounded requests.

Early A integration callable: `python -m minder_ml.intelligence.integration_cli
smoke --output ml/artifacts/session-a/<new-dir>`. C's real SQLite/WSGI boundaries
and A's source service passed; live Groq is unavailable. A has merged C through
C1.3 and B1.1 locally, preserving history. Later owner refinements merge normally.

C integration concern to resolve in its next focused checkpoint: the current
`CareerServices` serializes every option into chat facts. A broad 910-candidate
result requires a bounded, explicit selected-view context before a provider
call. Do not silently label a first-N catalogue subset as top recommendations.
Also keep actual field/skill IDs typed: arbitrary evidence subjects are not all
skill forecast targets. A's smoke uses an explicit two-role exploration view.
