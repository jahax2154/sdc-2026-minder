# MF2-PAGES-01 — approved Careers / My Path first slice

Dependency: M0 719c8731ff54c73065f675267556e04d14c17a96; preserves F repair
8446ca801de8d8a0163c390f76d2aa609a5fec16 and retry repair57edea4.

Source: docs/minder-approved-product-designs/explore-v1/assets/styles.css and app.js.
Styles are deterministically scoped by frontend tools/import_approved_styles.py;
shared shell remains the repaired72px rail. Explore expands to Careers/My Path;
local tabs follow approved source order. No prototype fixtures or localStorage plans.

Careers uses actual roles, role-requirements, career-context, product/views/career-match
and product/direction. Catalogue remains independently available while match reads
load/fail; failures are visible with retry. Unknown/unsaved profile is explicit.
No illustrative80/100 score or invented forecast. Comparison uses actual occupational
requirements and their limitations. Outlook currently displays supported context;
A's substantive generated outlook contract remains an integration dependency.

My Path reads existing direction/plans/plan-designs/progress without regeneration.
Preview and save are explicit. Activation separately uses owned returned saved plan;
completion/undo uses exact idempotent body/version. Tasks use persisted content;
no fictitious three-milestone/eight-task plan or competence claim. Planned generation
acceptance/typed stages will be integrated after A/D exports; Profile redesign and
broader task edit controls remain pending, not claimed complete by this slice.

Actual test: tests/morning_explore.cjs on http://127.0.0.1:9106 against F lane backend.
Synthetic owner; no successful response mocks. Passed real partial profile save,
career choice, explicit preview/save/activation, completion and refresh, all4 My Path
tabs, two-role comparison, mobile no document overflow,72px rail, no global New chat
on Mindbot, no page errors. Refresh generation calls0; explicit previews1. No provider
call claimed by this page-only check. JS syntax and git diff --check passed.

Screenshots (local, not committed): /private/tmp/minder-f-morning-explore/
careers-desktop.png, careers-compare.png, careers-mobile.png, my-path-next.png,
my-path-roadmap.png, my-path-skills.png, my-path-progress.png.

Observed: partial-profile global matching exceeded client12s deadline; F preserves
catalogue use and renders scoped truthful error. Sent A evidence; backend computation
is A-owned. No scoring/provider changes. Local API/UI8106/9106. No deployment.
