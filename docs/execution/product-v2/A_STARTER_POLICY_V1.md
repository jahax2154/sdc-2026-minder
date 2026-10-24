# A-N1 — starter-exploration-v1

This separately labelled provisional exploration mode serves normal initial
intake. It does not relax, replace or claim to pass the assessed scorer's three-
anchor/coverage minimum. No CV, anchored observation or LLM call is required.
Original N01 and the active provisional assessed policy remain unchanged.

Contract: `POST /api/product/starter-recommendations {limit?:1..5}`; exact DTO
`contracts/starter-recommendation.v1.schema.json`. Read only, authenticated owner,
up to five source-supported catalogue IDs, each with a sourced requirements
presentation and typed current market observations. No numeric fit/proficiency
field. Negative feedback demotes from this shortlist while the role stays in the
full catalogue. Reset restores the prior effect; repeated reads never compound it.

Versioned retrieval choices: all910 supported catalogue roles are considered;
explicit supported role allow/deny constraints filter candidates. Unsupported hard
restrictions return restriction_review_required rather than claiming compliance.
Industry, field and stage never automatically exclude another industry. Weekly
time/budget/horizon remain pathway constraints, not competence or role exclusion.

Tokenise/casefold explicit field, interests, self-reported skill names and
experience; singularise trailing plural s. Interest/context/skill/experience token
multipliers3/2/2/1, occupation title/description/software token multipliers3/1/2;
requirements/accepted industry labels also provide source topics. This is an
internal topical document retrieval order, never an assessment weight or fit
percentage. Inverse document frequency reduces ubiquitous words. Explicit positive
preferences retain priority; negative ones are deprioritised, without deleting
catalogue roles. Study stage informs explanation/planning context, not invented
entry qualifications or competence. When uncertain, source-ID-validated broad
exploration defaults span software, accounting, nursing, engineering and design;
they are explicitly described as starting points rather than verified suitability.

The top24 topical candidates supply current source facts. Activity counts reorder
only their existing slots within an identical measurement/population/vintage/
period/unit cohort, and within the same explicit preference tier. Missing current
evidence does not acquire a zero. Shortage groups/sector context retain their
distinct scope and never become a national role-count leaderboard. Five returned
roles need not have comparable current-market coverage: each option explicitly
reports support/missingness. Forecasts remain separate and are not fabricated.

Normal intake adds optional typed onboarding self_reported_skills, experience_state,
experience_summary, interests_uncertain and weekly_study_hours. They never create
skill-evidence rows. An explicitly changed study-time input maps to the existing
canonical weekly_hours constraint using the same D Profile save/version boundary.
Null resets time. An unrelated full-profile edit cannot restore old onboarding
time after a later explicit availability change. Generation reads canonical
constraints, preventing conflicting stale time metadata in the model context.

Verification: real pinned catalogue, normal intake only, computing vs nursing
personalisation, uncertainty/explicit-none, valid five IDs/source measures,
restriction/negative/reset behaviour, missing-market fallback, canonical time/reset
and no Profile/plan/competence writes. Frontend normal-intake/card journey remains
F-owned and must be proved in A after committed integration; API tests alone do
not close the product journey. No new learner training or paid execution.

Actual A-N1 software verification:177backend checks pass10.773s,0skips;39focused
starter/Profile/generation/orchestration checks pass4.204s. Normal-intake tests
have evidence=[] and explicitly no CV/plan. The first test referenced an obsolete
readiness key; corrected to existing global_minimum_possible, preserving assessed
semantics. Logs remain private under `ml/artifacts/session-a/product/morning/next-starter*`.
F can now integrate this commit and use the exact published schema; source/API
support is implemented, browser product acceptance remains pending F integration.
