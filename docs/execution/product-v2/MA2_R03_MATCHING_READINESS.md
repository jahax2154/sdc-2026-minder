# MA2-R03 — measured missing-input match request, owner E/F handoff

F actual Find my matches request on a saved Profile with zero anchored evidence
still times out at12600ms. No model involved. Source catalogue remains available.
A traced that full-catalogue assessments still enrich/validate all910role market
records even though the existing3-skill minimum cannot be met for ANY role.

A now exports PersonalMatchingService.input_readiness(profile):
{global_minimum_possible,distinct_valid_anchored_skills,minimum_assessed_skills,
per_role_minimum_coverage,role_coverage_assessed:false,policy_version,targeted_questions}.
Counts only distinct valid anchored skill inputs; conflicting values don't count.
This is a necessary global minimum, NOT a per-role assessment or changed numerical
policy. Titles/interests/self-report confidence don't fabricate anchored competence.

E OWNED REQUIRED FIX: product_views.career_read, ONLY for global selected_role_ids
absent/None, may call this helper when the actual personal service exposes it. If
false, return promptly with recommendation:null, assessment_readiness:<result>,
integration_mode, statements:[], explicit limitations explaining market enrichment
not run without necessary personal input. Product view status partial, not a failed
service or zero-demand statement. No invented assessed/ranked coverage or source
availability count. Keep all eligible roles in the independent catalogue; no industry
filter/exclusion. Selected-role/skill source reads and Outlook remain available;
>=3necessary inputs use existing full scorer/market policy unchanged. Fixture services
without readiness method keep their existing behavior. Commit focused E refinement.

F OWNED: render returned targeted missing-input message/link to existing anchored
assessment; don't mark service failure or require rating every role. For genuinely
eligible full global computation, retain explicit user Find action and allow a
bounded30s request (actual12.6s exceeded old12s); keep frame/navigation live, manual
retry, no background rank/model call on refresh. Don't enlarge all client timeouts.

A owns only helper/scoring internals/common routes. E/F own their modules; A does
not copy active files or rewrite their work. Verify actual empty/misclassified/
conflicting evidence guard, actual adequate profile still reaches unchanged ranking,
and per-role market source visibility. Do not fake completion with catalogue size.
