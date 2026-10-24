# A replacement recommendation contract handoff — N01-R1

A checkpoints: N1.2 `5f8fb31bd322ca0d8d2f6ecb75411cda4e07f81e`,
N1.3 `664b8264d3d229f39beb141329107fd5bef0a1e9`,
reference diagnostics N1.1-R01 `8011c34fd12062ef90a55505f591aa4c0b3d3886`.
Consume committed changes normally; preserve local owner work and checkpoint history.
No sibling working directory was changed. No push/deployment is requested.

Current user delegation supersedes waiting on original N01 for the bounded
provisional implementation. The original proposal is still pending/inactive.
The new policy is `personal-role-fit-v3-provisional`; current-market combination
is `personal-current-cohort-v1`. `PersonalMatchingService(market)` is the new
default. Explicit old `N01-pending` callers still get the preserved old behavior.
Do not claim the original proposal was historically approved.

C consumer paths transferred for A-local integration are listed under N01-R1 in
ownership.v1.json. Intake now offers the source-native anchor protocol through
GET /api/assessment-reference. Public recommendations expose independent rank
groups and measured coverage; selected-role context includes personal evidence
components and industry paths. Current market indices remain internal. Backend
calculates all rankings; chat selects/explains allowlisted facts only. Forecasts
are independent and remain unavailable. Database migrations/actions/worker
approval controls were reused, not rewritten. A's guarded worker-once adapter
uses A artifacts; C's runtime/worker database guards remain intact.

Remaining owner-coordinated consumer cleanup: companies.py explicitly calls the
old pending API and labels its generic company assessment pending. It is outside
the transferred paths and remains unchanged. In a later C checkpoint migrate its
generic occupation-context call to the new tokens or CareerServices, retaining
company-specific qualification/competence unknowns and avoiding any invented
company score. dev.py's historical startup text can be updated alongside it.
This does not block the new main Career Match/personal recommendation service.

Groq secret/model selection and scheduled real-provider acceptance remain
access-dependent. A consumes only its own owner-controlled configuration; no C
secret, database or model metadata was copied. A's real HTTP/Chromium tests passed
with honest provider-unavailable output. Mock/native-tool tests are software
evidence only. Configure and verify access in the intended lane before claiming
real provider success. Deployment stays unauthorised.

B training coordination: N2.1 is a local USD0 policy-distillation control with
provisional labels, not an independent personal-fit job. No paid A job is queued.
Future paid execution remains B-only and requires an immutable compatible target,
source/policy/split hashes, verified access/budget and the standing stop controls.
New B1.1-R03 quantities are preserved as their actual descriptive targets; none
were silently treated as quarterly unique-ad forecasting labels or current rank
inputs. No retraining is requested against incompatible historical targets.
