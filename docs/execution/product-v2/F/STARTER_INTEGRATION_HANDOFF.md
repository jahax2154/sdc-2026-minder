# F-STARTER-R01 — urgent starter recommendation integration

Integrated the user-specified A revision42062878914c168752ae058cd4d4f09a37f9b26c normally into F, preserving62fb94f and previous checkpoints. F-only changes in apps/frontend-product; no backend/policy/scorer/provider edit. Read A_N4_R01_PROGRESS_CHECKPOINT, F_STARTER_URGENT_HANDOFF, A_STARTER_POLICY_V1, exact starter schema, plus referenced native handoff/live-web/provider contracts. This bounded repair addresses starter→accepted plan/progress, not the separate complete cross-chat/live-web gate.

## Actual connections

Initial `#careers/matches` automatically calls **POST /api/product/starter-recommendations {limit:5}**. Validates starter-exploration-v1/mode/status/profile_version and null personal_assessment; renders exact backend role IDs/labels/explanations/source/missing-market scope. No assessed score conversion, fake percentage, minimum competency gate or zero-suitable-careers claim. Detailed assessed matching remains explicit at `#careers/assessed`, with absent coverage guarded. Full catalogue and preferences remain available.

Normal optional intake saves interests/uncertainty, self-reported skills, experience/explicit none and optional study time into the same existing Profile save. These create no competency evidence. Backend maps known study time to its canonical availability constraint. Starter response version is checked against the actual saved Profile.

Each starter card has actual View and Choose controls. Choice uses owned structured direction GET/PUT with version/idempotency, then existing My Path→Mindbot generation→review→explicit save→separate activation. Starter/catalogue/saved direction load independently. Optional assessed/market context failure in career details is visible and does not hide valid source requirements or disable choice. Starter unavailable/restriction-review/empty/invalid/error states are distinct and retryable; errors never mean zero suitability.

## Required fresh browser acceptance — PASS

F actual UI http://127.0.0.1:9106/#careers/matches, API8106/same-origin9106, backend health42062878914c168752ae058cd4d4f09a37f9b26c. New local anonymous account (not hosted Clerk proof), actual normal UI studying/fit/Computer science/Python interest/none_yet/3hours intake; **evidence=[] before and after**, no CV, no seed/mock recommendations or manual database edits.

Actual starter POST returned five provisional directions, profile_version equal to the saved onboarding Profile, personal_assessmentnull,910supported considered and0assessed scores. All five returned labels rendered, firstSoftware Developers selected through its card. **Zero requests to assessed matching.**

One actual coordinated Qwen call1525ms, available/generated_guidance, two stages/two tasks. Draft remained unsaved until explicit Save, then separate activation. Skills/Next steps/Roadmap/Progress had four distinct headings and the same accepted plan. Explicit complete changed canonical progress0/2→1/2; refresh retained1/2 and the same plan. No regeneration or additional provider call. No artificial65second pacing/probe.

Complementary real normal-onboarding transport tests (0modelcalls, no mocked recommendation responses): aborted optional career-context/role-evidence reads retain five starter cards; role detail reports optional failure and still saves choice/opens independent My Path. Failed starter request offers working local Retry; failed catalogue read cannot remove valid starter cards. Initial recovery test waited for the previous Careers render; correcting the wait to role-detail controls resolved this test timing issue, not a product change.

Actual endpoint/request/response/rendered-card/selection/accepted-plan/completion evidence: [STARTER_REPAIR_EVIDENCE.json](STARTER_REPAIR_EVIDENCE.json). Full actual starter DTO, accepted canonical plan, request timeline and screenshots are retained under `/private/tmp/minder-f-starter/`, with exact paths/hashes in the evidence. No credential/header/session export. Private artifacts, local env/database/uploads and existing untracked ML raw/derived inputs excluded; no ignore rules added. Existing raw/derived inputs untouched/not backed up.

## A integration

Merge the exact cumulative F handoff normally into A and restart **A's own runtime on9111/8111**. F restarted only its assigned9106/8106 process and no worker. Check served starter-matches.js bytes and health revision before combined browser acceptance. No deployment/main/force push. Backend dependency4206287 contains all starter/profile/generation/provider contracts; no additional migration/config/library dependency added by F.
