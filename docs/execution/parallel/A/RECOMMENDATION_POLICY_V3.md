# N01-R1 — provisional recommendation policy v3

Authority: current 23 October 2026 user instruction delegates bounded numerical
choices to A. Policy `personal-role-fit-v3-provisional`, market policy
`personal-current-cohort-v1`. This replaces the original N01 proposal for current
implementation; it does **not** historically approve that proposal. Old N01,
legacy preparation F0/labels and previous evidence remain unchanged. No hiring,
AI-replacement or independently measured personal-fit probability is claimed.

## Measurements and a practical minimum

The acquired O*NET 31.0 essential-skill table covers ten basic skills across 910
occupations. New official level anchors provide examples at levels 2/4/6 for
those same ten native element IDs. Compare only explicit, structured assessments
on the source LV scale, with a matching anchor and a description of the activity
and evidence. Preserve self-report, documented demonstration claims and reviewed
assessments separately; document claims/interests/job titles alone never create
a level. An explicit assessed zero is distinct from unanswered. A review claim
requires human-reviewed provenance and cannot be minted by the public intake.

Minimum: at least **three** usable source-native skill observations and **30%**
of this role's usable positive LV criteria. No employment or role ratings required.
`C = mean(min(observed_level / occupational_level, 1))` over **assessed** criteria,
equal weights; unassessed criteria remain unknown and coverage is reported. This
is a partial essential-skill evidence compatibility index, not full qualification.
Suppressed/not-relevant source rows stay out of the usable requirements. If the
minimum is absent, no personal score: ask for the exact missing skill assessments.

O*NET importance measures do not become person proficiency. Ratio normalization
and the evidence minimum are declared engineering proxies, not calibration.
No milestone, preparation hours or resources enter initial fit.

## Separate optional adjustments

`F = clip(80*C + industry_path_points + role_points + work_style_points, 0, 100)`.

- Role interest: interested `+5`, not interested `-5`, explicit neutral `0`.
  Unanswered/reset contributes no adjustment and retains a null raw preference.
- Each supported industry path has `5*E + 5*(2*U-1)` using only supplied components.
  `E` is an explicit documented transferable-background rubric: 0 = explicitly
  no relevant exposure, .5 = described study/project context, 1 = described
  sustained hands-on domain work. This is context, never demonstrated skill.
  Known current industry alone has no automatic mastery/point assignment.
  Industry interest has the same signed utility convention as role interest.
- Use the **maximum** supported path adjustment, with untouched paths supplying
  no adjustment. This retains alternative industries: disliking one does not
  penalise supported untouched alternatives. Show every path's E/U and selected
  path separately. The compatibility DTO's bounded industry assessment is
  `(path_points+5)/15`, mapping the declared -5..10 point range onto 0..1;
  contributions use path points, never a second application of that display index. Each signal enters once; no extra final penalty.
- Work-style alignment: `5*(2*W-1)`, W the mean explicitly supplied utilities on
  this occupation's sourced positive-impact work-style tags. Absent tags have
  no effect. Preserve the source's AI/Expert provenance; this is stated affinity,
  not personal capability or an independent assessment.

The maximum optional uplift is 20 points (background 5, industry interest 5,
role interest 5, work style 5); preference opposition can lower the result.
Optional absence is omission of an adjustment, not a claimed neutral answer.
Scores with partial evidence expose coverage and assumptions. Reset restores
the prior no-adjustment result; repeated state feedback cannot accumulate points.
Clipping is explicit: contributions still change at endpoints even where the
bounded aggregate cannot move further. No threshold deletes an industry/role.

## Current-market ordering and different coverage

Use current **Malaysian** advertisement evidence only when entity/type, geography,
source universe, cohort version, measurement, units, observation period and
denominator agree. The current source is B1.1-R02’s 155-inspected-ad Bosch feed,
not national demand or verified active hiring. Old source release dates remain visible. Never allocate broad DOSM marginals to detailed roles.

Within a comparable cohort of at least two personally assessed roles:
`M = 100*log1p(role_ad_count)/log1p(valid_inspected_sample_size)`;
`S = .85*F + .15*M`. Require known sample size, 0<=count<=size, valid dates and
source provenance. This explicitly chosen 85/15 rule is **not** inherited 70/30.
It bounds the sparse employer-sample effect to 15 points; changing compatible
counts can change ordering. Zero means zero mapped ads in this inspected sample,
never zero national demand. No percentile denominator is silently invented.

Roles lacking comparable evidence remain in a **separate personal-only group**
ordered by F; singleton market cohorts cannot establish a comparative market
ranking. Groups are labelled and have independent rank scopes. There is no
fabricated common overall rank across unmatched market coverage. Display group
order is not a recommendation between groups. Overall status is partial when
market comparison is unsupported for any assessed role; personal-only fallback
is never full recommendation completion. Unassessed roles remain explorable.
Ties use personal index then native role ID, never random card order.

Next-quarter forecasts stay separate, have zero contribution to this current
ordering and may be unavailable. Backend calculates; the LLM only selects and
explains allowlisted backend facts. Internal market matrices are not public.

## Source grounding, exclusions and learners

Pinned projection `ml/data/reference/role-reference.v3.json` includes ten native
skill anchor sets, 992 exact-code/title industry relationships and 891 sets of
five positive-impact work styles. Twelve source aggregate rows lack native codes and are not joined; their labels
are explicit exceptions. Twenty-four native occupations lack an exact industry
relationship, including 3 otherwise-supported assessment roles. They stay
eligible; optional industry effects remain unsupported rather than fabricated. The industry table covers US top employment sectors for
2025; it is partial and not Malaysian demand. Full source bytes remain ignored
under A artifacts; normalized source-backed reference data and hashes are tracked.
O*NET CC BY 4.0 attribution/change notice is in the projection. Existing thirteen
bootstrap inputs are neither replaced nor regenerated.

Only explicit view restrictions or source-supported hard conflicts exclude.
Initially supported hard restriction: an explicit role allow/deny list. Unknown
geographic/qualification/other occupational constraints are unresolved, not
silently certified or converted into dislike. Eligibility is source support,
not current application qualification. Original preparation feasibility survives.

Baseline remains active and traceable. Preserve Ridge/XGBoost and run bounded
compatible policy-distillation controls with profile-group isolation, frozen
teacher/policy/data/split hashes and same holdout. Such labels are **provisional
policy outputs**, never independent personal-fit validity or promotion evidence.
No live learned-model activation follows teacher agreement. Paid runs remain
B-only; absent external access does not block local service/fixture verification.

## Planned bounded checkpoints

N1.1 source/policy grounding; N1.2 executable assessment/current-market contracts;
N1.3 application/UI plus required demonstrations; N2.1 compatible learner runs;
N3.1 final measured coverage and handoff. Post-checkpoint fixes use linked R IDs.
No push or deployment is authorised by this task.
