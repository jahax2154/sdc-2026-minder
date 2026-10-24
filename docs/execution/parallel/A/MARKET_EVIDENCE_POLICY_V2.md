# I4.3 — personal-current-evidence-v2 (delegated provisional)

Authority: current user instructs A to retain the working personal scorer and
integrate supported, separately typed B evidence with versioned ranking treatments.
No original N01 approval is invented. Personal v3 capability/preference arithmetic,
minimum evidence and baseline/learner selection remain unchanged. Explicit
`personal-current-cohort-v1` calls preserve the earlier four-employer-role behavior.

## Applicability and source scope

`ml/data/reference/market-evidence-links.v1.json` versions A's engineering links.
B 90ebdf1's source data/service is consumed unchanged.

- Software Developers and Accountants and Auditors retain the same named DOSM
  source categories. Chief Executives has a declared functional proxy to the
  combined Managing Directors and Chief Executives category: overall executive
  direction/policy scope overlaps the actual O*NET description. The combined
  source category is never relabelled as an exact native-code count.
- This is **not** a certified MASCO/O*NET whole-taxonomy crosswalk. Record-level
  relationship and scope are displayed. Source-category proxies get their own
  comparison group, distinct from native employer-feed observations.
- Advertising/Marketing Professionals is broader than the linked specialist/
  manager occupations: context only, no count allocation. Public Relations has
  an older 2024 Q4 fact: dated context, not latest-period ranking. Two broad
  administrative labels remain unmapped; no title-based broad allocation.
- Related DOSM sector totals attach through explicit contextual industry links.
  These different national classifications are partial semantic relationships,
  not equal industries or role counts. Sector weight is **zero**. Do not sum
  overlapping totals or allocate them across a role's industries.
- No acquired shortage record is present in the consumed B handoff. The typed
  shortage family returns unavailable/null, never false/zero or an inferred flag.
  A later committed B source/mapping handoff is required to populate real records.

## Ordering treatments

Each assessed role selects its primary compatible activity: latest-period DOSM
occupation-category evidence first, otherwise exact native employer observation.
The official broader-platform source has priority over the narrow one-employer
feed where a declared applicability link exists. Values from both remain visible;
they are **never added together**, averaged as the same measurement, or used as
incompatible forecast targets. Unmapped/older records remain useful context.

Comparisons require at least two personally assessed roles in the same source
universe, measurement, unit, observed period and versioned cohort. Group ranks are
independent; display group order is not a cross-group recommendation.

- Employer `M=100*log1p(mapped requisitions)/log1p(inspected sample size)`.
  Current denominator is 155 actual inspected requisitions; known mapped zero
  means zero within that source feed, not zero national demand.
- Published-category `M=100*log1p(category offerings)/log1p(max observed category
  count in that latest source period)`. The current reference maximum is 40,640
  among five actually numbered 2026 Q2 source categories. Missing/top-list-omitted
  categories are unknown, not zero. The denominator is a declared observed
  reference maximum, not a fabricated national total or vacancy denominator.
  It is frozen by source/period, not by a user's chosen subset.
- Within either compatible group `S=clip(.85*F+.15*M+shortage_adjustment,0,100)`.
  F is unchanged personal v3. This remains separate from legacy 70/30.
- Future supported positive latest-acquired official shortage designation may
  contribute **at most +2 points** through an explicit scoped link. It is a dated
  qualitative signal, not ad frequency, competence or hiring probability. No
  designation/unmapped means unknown/no adjustment, not proof of no shortage.
  The implemented path is exercised only with a named fictional fixture until
  real B evidence arrives; real coverage currently zero.
- Remaining roles are ordered by F plus any supported shortage adjustment.
  Without a supported shortage adjustment they are personal-only. Neither this
  fallback nor contextual sector data constitutes full comparable-market coverage.
  No future forecast or AI-replacement probability is invented or weighted.

Role/industry preference reset and idempotency are unchanged. Market sources are
independent of feedback. An absent optional preference never becomes a dislike.
Internal current indices/final calculation matrices are excluded from ordinary
public results and grounding. Source counts, units, dates, scopes and URLs are
public explanatory facts; personal indices are separately allowed.

## Trace and owner interface

Additive MarketEvidence records preserve measurement type, source entity, actual
value/null, unit/universe/cohort/period, publication/retrieval availability, source
hash/URL, applicability version/relation/scope and ranking eligibility. Internal
RecommendationTrace records link profile-versioned calculation, source IDs,
normalization, group/rank, unknownness and final score. Public trace projection
excludes market arithmetic; trace identity changes when the profile version
changes even when reset restores identical scores and order.

`EvidenceContext.records()` and `RoleFitService.evidence_for()` supply per-role
facts. `evidence_statements()` supplies bounded source-only facts to C grounding;
it includes no raw personal assessment statements/documents. C must keep its
mandatory policy/rank/coverage/uncertainty facts and cannot let LLM selection
reorder backend ranks. A consumes C's committed privacy refinement before any
potential overlapping composition edits. UI/HTTP wiring follows I4.3 service
checkpoint, and A live provider checks await A's private authorised configuration.

## Measured before/after (same fictional anchored profile; actual sources)

| Coverage | v1 before | v2 after |
| --- | ---: | ---: |
| Personally assessed supported roles | 910 | 910 |
| Comparable activity-informed ranks, union | 4 | 5 |
| Employer-feed comparison primary | 4 | 2 |
| Published occupation-category comparison primary | 0 | 3 |
| Dated/scoped published-category facts (includes broader/older context) | 0 integrated | 7 linked roles |
| Real shortage evidence | 0 | 0 (not yet acquired) |
| Related sector context | 0 integrated | 907 |
| Personal-only ranks | 906 | 905 |

The union increase is one **declared executive source-category proxy**. Native
employer evidence remains available for four roles; source precedence moves two
to the published-category comparison. This is not a claim of five exact native
national role series. Sector context does not turn 907 roles into comparable
role-demand measurements. Before/after and tests are in I4.3.json; broader
unsupported market coverage remains an explicit limitation.
