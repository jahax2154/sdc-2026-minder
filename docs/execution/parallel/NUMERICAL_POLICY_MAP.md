# G0 numerical mapping and migration boundary

Canonical product update: `docs/MINDER_AI_ML_DECISION_CONTEXT.md`, revision 5. Technical historical authority: `ml/docs/MINDER_POLICY_REVIEW_v1.md`, exact projection `ml/configs/intelligence/policy.v1.json`. This index supersedes conflicting product meaning without editing old policies or claims of historical approval. G0 freezes interfaces; N01 below remains pending. No new scorer is activated.

| Existing definition | Unit / missingness / source | Treatment |
| --- | --- | --- |
| C skill coverage; Q assessed required weight | 0–1; unknown != zero, Q=1 required; anchored profile evidence vs accepted milestone criteria | Preserve legacy. Occupational requirement coverage must use versioned source-native requirements, never O*NET importance as user competence. New C needs N01 semantics. |
| I interest utilities | Equal tag weights; explicit 0/.5/1; unknown prevents complete legacy score | Preserve legacy; new role/industry states are scoped/idempotent, not click penalties. |
| T preparation time | horizon default 12 weeks, remaining effort hours, explicit hours/week; source/accepted estimate basis; unknown not zero | Keep in later plan feasibility. Not initial occupational-fit feature. |
| R resource feasibility | Equal resource-group means, alternatives within group; known 0/1 versus unknown | Keep plan-specific resources. Only sourced hard occupational constraints may exclude initial options; no title inference. |
| W work-style alignment | Equal tags with explicit 0/.5/1 utilities; unknown distinct | Reuse compatible evidence semantics; new occupation tags need valid mapping. |
| F0 = 100 dot([.4,.2,.2,.1,.1],[C,I,T,R,W]) | Legacy preparation index, 0–100, not hiring probability; [0.6,.8,.5,1,.7] -> 67 | Unchanged in scoring.py/inference.py. Do not call this new personal role fit; separate measurement field and policy version. |
| Learned grade mapping | 100 clip(raw/2,0,1); grouped profiles, train-only preprocessing; explicit model_not_ready | Legacy labels/models remain target-bound. No automatic migration to role fit, no provisional-to-gold promotion. |
| User–industry stage | New D03 product requirement; history and preference traces distinct; valid many-to-many mappings | Preserve as explicit component in new contract. No automatic threshold exclusion. New numeric contribution pending N01. |
| D = 100(.6 P(share)+.4 P(YoY)) | MY source-native broad published offering activity; frozen comparable cohorts N>=5; no missing-indicator reweight | Existing market_indexes.py reusable at supported grain only. Not narrow-role demand, unique-ad count or forecast. B owns explicit target/scope reconciliation. |
| S = .7 F + .3 D | Legacy compatible comparison only; entire-set personal-fit fallback when missing/incomparable D | Preserve old implementation, not authorised for changed F or an unstated current/future blend. New DTO uses personal_only_pending_market_policy, no combined values. |
| Forecast | New approved target unique valid observed ads by role / ads requesting skill, MY; next full calendar quarter | Separate arrays, issue/available dates, source universe, denominator/unit. October 2026 -> Jan–Mar 2027. No averaging with current indexes. B implements only supported series or explicit unavailable. |

## One substantive decision N01 — PENDING

Proposed version `personal-role-fit-v2-proposal`, not accepted, not executable as a score in G0:

- C_role = equal-weight mean anchored evidence coverage against supported required occupational skills; Q=1 across required positive-weight criteria. Neither importance ratings nor narrative interests establish proficiency. Without a valid requirement-to-evidence rubric return unknown, not inferred mastery.
- For each supported industry j, E_j is anchored transferable background evidence on [0,1] and U_j is explicit preference utility: interested=1, not_interested=0, explicit neutral=.5; skipped/reset=unknown. A_j = .5 E_j + .5 U_j. A student has unknown background until supported evidence exists; no paid-employment requirement and no fabricated zero. Preserve E and U traces.
- Role preference P = .5 U_role + .5 mean(A_j) over supported many-to-many industry mappings, equal industry weights. Never infer a mapping from title. Missing required U/E/mapping support returns unknown; no silent reweighting. This intentionally conservative completeness may limit score coverage and needs an explicit decision rather than hidden defaults.
- F_role = 100(.60 C_role + .25 P + .15 W_role). T/R move to pathway feasibility; they are not silently dropped and weights renormalized. Preference enters once through P. Hard explicit constraints are separate exclusions; an ordinary negative interest never removes a role.
- Initial recommendation mode remains personal-only until a separately approved compatible market-period combination exists. Current and forecast evidence remain available separately; no hidden average or new market weight.

Concrete example (synthetic arithmetic only): C=.6, E=.8, U_industry=1, U_role=1, W=.7 -> A=.9, P=.95, F_role=70.25. Mark role not interested -> P=.45 and F_role=57.75, delta=-12.5 without changing C, W, market evidence or catalogue eligibility. Repeating the state has delta=0; reset makes the role utility unknown and score unavailable under this conservative proposal. For multiple industries use the declared mean; do not delete a cross-industry role. This is a proposed scale/meaning, not empirical validation or an approved production result.

Sensitivity example at fixed C/W: increasing the proposed preference weight by .05 while reducing C weight by .05 changes F by 5(P-C), bounded [-5,5]. The coefficient choice is not established by these arithmetic checks. Before acceptance, A must demonstrate audience/mapping coverage and actual source/rubric applicability; if changed, version the proposal and fixtures.

Decision requested: approve or revise this one explicit replacement measurement and conservative missingness rule before numeric new-role-fit ranking/model-target creation. A1.2 numeric ranking and A2 compatible targets depend on N01; A1.1 catalogue loading, typed intake/preferences, B ingestion/forecasting, C provider/persistence/action work proceed independently. Do not translate old milestone labels to new labels. Independent human review is not a launch prerequisite under D06; independent validity still requires genuinely independent evidence, and generated labels remain provisional.

Other supersessions: milestone/effort is no longer an initial catalogue prerequisite (legacy service retained); old three-role pilot is calibration only, not the new runtime catalogue limit; old forecast-not-in-v1 scope does not prevent B's new separate forecast contract; D09 direct specific requests authorise scoped writes, inferred/proactive changes need prior approval. No old files or numeric constants were deleted.
