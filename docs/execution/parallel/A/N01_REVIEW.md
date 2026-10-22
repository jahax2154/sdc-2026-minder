# N01 review — existing proposal located, no approval or activation

This is a review of the existing pending proposal, not a second policy or a new
decision. Authority remains `../NUMERICAL_POLICY_MAP.md`, section “One
substantive decision N01 — PENDING”, beginning at line 19. Version:
`personal-role-fit-v2-proposal`. Machine projection:
`ml/configs/intelligence/role-fit.v2.proposed.json`, `status=pending`,
`active=false`, SHA-256
`70ab3eb062e68d67dcdf5117feccf352e6812e98ec9e1837a757a617fcf91d99`.
The proposal was introduced by G0.2 `d26bd704ee798c0ab4c9522ae66ce2378d2680d9`;
`G0.2.json`, `G0.3.json`, `LAUNCH.md` and later A phase records all retain N01
as pending. The general `docs/DECISION_LOG.md` has no N01 entry. No missing
proposal was inferred and no replacement was silently adopted.

## Current proposal

The canonical section specifies these definitions:

1. `C_role`: equal-weight mean anchored evidence coverage against supported
   required occupational skills; `Q=1` across positive-weight criteria. Source
   importance and narrative interests never establish proficiency. Missing
   requirement-to-person rubric means unknown.
2. `A_j=.5 E_j+.5 U_j`: anchored transferable industry background and explicit
   preference remain separate. Interested=`1`, not interested=`0`, explicit
   neutral=`.5`, skipped/reset=unknown. Students do not receive fabricated zero
   background or a paid-employment prerequisite.
3. `P=.5 U_role+.5 mean(A_j)` over supported many-to-many mappings, equal
   industry weights. Missing required utility/background/mapping means unknown;
   no implicit imputation or reweighting.
4. `F_role=100(.60 C_role+.25 P+.15 W_role)`, a role-fit index, not a hiring
   probability. Time/resource feasibility belongs to later pathways. Preferences
   enter once; dislike never excludes an occupation. Explicit hard constraints
   remain separate.
5. Personal-only recommendation mode until a separately approved compatible
   market-period combination exists. Current and forecast evidence stay
   separate; no invented blend.

The canonical wording also explicitly requires demonstrating audience/mapping
coverage before acceptance and prohibits converting legacy milestone labels to
the changed target. Independent human review is not a launch dependency;
generated labels still are not independent validity evidence.

## Product decision versus engineering work

The decision is whether this replacement index expresses initial role fit
appropriately **and** whether its conservative no-score behaviour is acceptable.
The latter includes losing a numerical result when optional feedback is reset
or when background/mappings are unknown. Those are observable product semantics.
Replacing them with neutral defaults or silently redistributing missing weights
would require an explicit revised contract.

Recommendation given to the user: accept the package only as a provisional,
versioned, evidence-complete baseline if that no-score behaviour is acceptable.
Retain unknowns instead of inventing proficiency or neutral feedback. The
proposed coefficient package is an engineering recommendation, not measured
optimality, and does not need separate questions for every coefficient. Numeric
calibration, deterministic aggregation, source-ID joins, validation, fixtures,
artifact compatibility and sensitivity testing are engineering work within the
accepted measurement.

Initial matching before preparation planning, no hidden industry-exclusion
threshold, scoped/idempotent negative feedback, and exploration outside prior
industry are already confirmed product decisions. They need not be reopened.
Keeping market periods separate while their combination is unresolved is a
safe existing boundary, not a request for arbitrary new market weights.

No user decision has been recorded in this review. Approval of arithmetic alone
would not manufacture an occupational assessment rubric, supported industry
mapping or empirical labels. Current evidence: 1,016 runtime references, 910
with source measurement support, zero accepted occupation-to-person rubrics or
source-grounded industry mappings in A's runtime. All five existing synthetic
profiles and all five audience demonstrations therefore have zero numerical
role-fit scores. This limitation must remain visible after any later approval.

## Worked examples (proposal arithmetic only)

| Case | Derivation | Result |
| --- | --- | --- |
| Complete hypothetical evidence | `C=.6, E=.8, U_industry=1, U_role=1, W=.7`; `A=.9`, `P=.95` | `F=70.25` |
| Same evidence, role not interested | `U_role=0`, `P=.45`; capability/work style/market unchanged | `F=57.75` |
| Repeat negative feedback | Stored preference remains the same state | `F=57.75`, no accumulated penalty |
| Reset role preference | Required utility becomes unknown | No numeric score |
| Student with known skill evidence, unknown anchored background | Required `E_j` unknown | No numeric score |
| Synthetic many-industry illustration | `A_1=.9`, `A_2=.4`, `U_role=1`, same `C/W`; mean `A=.65`, `P=.825` | `F=67.125`, both industries retained |

These are mathematical examples, not actual profile results, independent labels
or evidence that the proposed weighting is optimal. Exact decimal checks of
the first/negative examples reproduce `70.25` and `57.75` without invoking or
activating the runtime scorer.

## Numerical rules reusable within their existing meaning

- Unknown differs from known zero; completeness and provenance remain explicit.
  Reuse anchored `0/.5/1` utilities and equal positive criterion weights where
  the new source/rubric semantics are compatible. O*NET IM/LV ratings cannot be
  converted directly to those personal utilities.
- Keep the legacy preparation formula unchanged:
  `100(.40 C+.20 I+.20 T+.10 R+.10 W)`. Its reference vector
  `[.6,.8,.5,1,.7]` still yields `67`. It is not the new role-fit formula.
- Keep legacy pathway time/resource rules in pathway feasibility; no mandatory
  milestone, hours or resource completion for initial catalogue consideration.
- Retain existing broad-market `100(.6 percentile(share)+.4 percentile(YoY))`
  only for its supported source grain and frozen comparable cohort of at least
  five entities. It cannot become narrow-role demand or a forecast by relabeling.
- Retain the old `.7 F+.3 D` only for compatible legacy measurements. It is not
  authorised for this changed F or a current/future blend.
- Profile-group isolation, train-only preprocessing, target-bound artifacts
  and separation of provisional versus independent labels remain reusable.
  The old grade-to-index mapping applies only to a compatible target/rubric.

The exact historical projection remains `ml/configs/intelligence/policy.v1.json`
with its canonical policy document; this review changes neither file.
