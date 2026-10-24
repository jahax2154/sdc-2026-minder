# Revision3 release candidate — 24 October 2026

Functional acceptance revision: `425f0173ab89ad3a1a2b0cecd0d3de5745a4261d`.
MA2 evidence checkpoint: `a2e58066acb490fa8d739438d4f6b5377207e8c1`.
Release-handoff descendants change documentation/checks only. Select the final
verified head of `session/a-personal-integration` for publication; retain this
functional revision as the exact source of the measured runtime results.

**Local integrated product acceptance is established with the limitations below.
The release is not hosted or submission-complete.** No judge URL, live Clerk
accounts, hosted restart/daily-job evidence or actual RunPod GPU fit exists yet.
Prepare/review [release PR#1](https://github.com/jahax2154/sdc-2026-minder/pull/1);
do not merge, rebase or squash it. Main/tag authorization remains separate.

## Integrated ownership and revisions

M0 `719c8731ff54c73065f675267556e04d14c17a96` released D/E/F early with contracts,
exact isolated directories/commands, approved design assets and ownership. Its
initial gaps are historical, not current runtime claims. Current authorities are
[OWNERSHIP.json](OWNERSHIP.json), the actual exported schemas and refinements.

| Owner | Committed handoff included in the candidate | Responsibility |
| --- | --- | --- |
| A | `425f0173ab89ad3a1a2b0cecd0d3de5745a4261d` | Routes, typed model/actions, common runtime, integration, active scorer |
| B | `c8eb09921f6bf583ec30bca636f549628a575d69` | Compulsory bounded GPU experiment; preparation only so far |
| C | `362316351ebe90b31c533eb75cff46a851808314` | Preserved factual-grounder/provider transport work |
| D | `53e154459cf53eb9c2472658d381b85b4ad3302a` | Sole migration owner; identity, state, conversations, private CV storage |
| E | `1669142ade6ac1e8f9790633e3b9e125c97a7aa1` | Managed authentication, hosted supervisor and deployment packaging |
| F | `3c7d105d34e32c291bc7440764390f55a8fb515f` | Entire approved frontend/client and browser acceptance |

All required bootstrap/repair/handoff SHAs are verified ancestors. Normal merges
preserve producer commits and messages. See [full phase/refinement index](MORNING_CHECKPOINTS.json).
Source handoffs remain in D/MD3_MORNING_HANDOFF.md, E/ME2_HANDOFF.md,
E/ME2_R01_AUTOMATION.md, F/MORNING_REV3_HANDOFF.md and
`docs/execution/parallel/B/MB1-PREP.json`.

## Actual runtime and contracts

A root is `/Users/phuahjunhong/sdc-2026-minder-worktrees/session-a`, branch
`session/a-personal-integration`, API8111/UI9111, database
`ml/artifacts/session-a/product/runtime.sqlite3`. Isolated Python3.12.15 is selected
by the ignored `.env.local`. No sibling environment/database was modified.
`qwen/qwen3.8-27b` remains the actual model, with the existing private Groq file.

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane A --worker
```

Only A's explicit `--worker` starts the existing E supervisor; other lane commands
retain their defaults. GET `/api/health` records actual startup revision/thread
liveness. HTTP is bounded concurrent service, not serialized behind provider calls.

- GET `/api/auth/config` exposes allowlisted public configuration; GET
  `/api/auth/session` verifies identity. Local POST `/api/session` creates an
  anonymous development capability. Hosted mode forbids that fallback and requires
  E's maintained Clerk SDK verification plus D's stable issuer/subject mapping.
  Anonymous records are not adopted by the first real user.
- Minder POST/GET/DELETE `/api/product/conversations` or `/conversation` supports
  multiple stored threads. GET `/api/product/mindbot-conversation` atomically obtains
  the user's one continuous Mindbot thread, also enforced by a unique database index.
  Mindbot has no New chat, selector, event chat or forced Minder redirect.
- POST `/api/product/conversation-turn` accepts current Profile version, conversation,
  message and idempotency key. Server owns channel, visible outcome and action refs.
  Provider calls run outside write transactions. Exact retries replay stored results;
  uncertain writes require deliberate receipt recovery, never automatic mutation retry.
- POST `/api/product/generation-accept` accepts stored generation/version/role and
  idempotency key. It creates one canonical proposed plan only after explicit review.
  Activating that plan is separate. Refresh reads the saved plan, not a new generation.
- Profile/preferences/availability and typed task/daily actions use the same validated
  ActionExecutor: ownership, current versions, scope, explicit instruction or concrete
  proposal approval, audit IDs and idempotency. Generated text cannot grant authority
  or certify mastery. Missing essential time/target/capacity asks for clarification.
- `/api/agent-settings` stores enabled/state/timezone/check_time/owned-plan scope,
  next_run and last_result. One existing Worker posts to the same Mindbot history.
  Pause/cancel, current-day catch-up, leases, failure records and deduplication are
  tested. A check authorizes proposals, not arbitrary autonomous plan changes.
- D migrations are additive through schema7 on SQLite. CV/resume PDF/TXT uploads
  require explicit purpose, private owner checks and review before Profile writes.
  Text PDF extraction is bounded; scanned files require manual input. Deletion
  removes original bytes/drafts, preserving already accepted Profile fields.
  Exact retry after a lost review response performs one Profile write.

Exported schemas: `contracts/parallel-services.v1.schema.json`, A generation schemas,
D conversation/generation-state schemas and the [document contract](DOCUMENTS_CONTRACT.md).
Current action additions are in MA1_R06_ACTION_TOOLS.md, MA1_R08_AUTOMATION_TOOLS.md
and MA1_R10_PROFILE_AND_SCOPE.md. F alone owns rendering/client files.

## Acceptance and practical limits

[MA2_ACCEPTANCE.json](MA2_ACCEPTANCE.json) distinguishes actual Qwen/browser/local
storage checks from generated-identity/fault-injection/controlled-clock software tests.
It retains original failures as well as successful refinements. Test totals do not
substitute for required live sign-in and hosted acceptance.

The original roadmap boilerplate came from routing a learning request into the
closed factual-selection ledger and unnecessarily computing full assessment context.
Typed model guidance now reads bounded available Profile/history without requiring
a numerical assessment. F renders the actual answer first. A separately validates
practice advice, empirical evidence and action authority. Trailing incomplete model
fragments may be omitted only after all structural/factual checks, without inventing
completion. Metadata records those adjustments; unusable output still fails honestly.

Sparse-profile global matching originally exceeded the frontend12s bound. Exact
complete-result validation memoization preserves all checks and calculation output:
same-input authenticated dispatch12358.368ms ->6343.235ms; actual frozen browser6572ms,
no timeout, no Profile mutation or generation. Changed payloads must revalidate.
This is local measurement, not a process-cold/hosted performance guarantee.

Real provider availability varies: a rapid contextual follow-up returned actual
`provider_rate_limited`. An explicit50s acceptance gap passed the unchanged browser
journey; there is no production auto-retry or model switch. The daily supervisor
processes one queued event per30s; old local events delayed the first150s timer check.
The repeat actually delivered83.003s after the due minute. This is not a punctual
delivery or hosted-service guarantee.

## Scoring and honest pitch

Active policies remain `personal-role-fit-v3-provisional` and
`personal-current-evidence-v2.1`. Original N01 is not historically approved.
At least3 valid anchored essential skills and30% per-role evidence coverage support
numerical assessment. Optional missing preferences are not dislikes; reset removes
their effect, repeated feedback is idempotent, and skill evidence remains separate.
Preparation time/resources affect feasibility, not competence.

Backend comparable current treatment is .85personal + .15source-specific normalized
activity + bounded shortage context; groups with different measurements/coverage
are not pooled. Sector/forecast ranking weights remain zero. Missing market evidence
is neither zero demand nor established opportunity. Adequate synthetic run:1016
catalogue,910eligible/assessed,5comparable activity ranks,7published support,
7related shortage/0exact-role shortage,907sector context,900personal-only ranks.
Counts overlap. Sparse Profile:910eligible,0assessed/0ranked. See
[pipeline and worked trace](PITCH_PIPELINE.md), not model-invented scores.

Ridge/XGBoost/synthetic experiment history is preserved. No independently validated
career-outcome accuracy, real next-quarter forecast or AI-replacement probability
is established. B's prepared GPU experiment does not yet constitute a GPU fit.

## Judge publication: exact remaining dependencies

E inspected Replit first: the accessible candidate is an older React/Express mockup
with development PostgreSQL, not this Python app. An unfinished durable DB conversion
is the concrete blocker there. The single prepared fallback is Railway, preserving
one Python service, one mounted SQLite/private-file volume and the existing worker.
Do not publish the old mockup or build a second backend.

Required external access: intended existing Railway project/service/credits/volume;
configured Clerk instance and two live test accounts; provider secrets installed
privately in the hosted runtime. No connected Railway capability or existing GitHub
deployment secrets/variables was available. No upgrade or new spend was authorized.
Actual Linux image build and hosted persistent restart checks remain unperformed.

Use [deploy/README.md](../../../deploy/README.md), its pinned dependency/artifact
packaging, environment template and backup/recovery commands. Preserve mounted-path
and managed-auth startup guards. After access: verify existing resources/cost, build
the exact candidate, configure exact origins and server-only keys, run section9
with two real accounts, restart the service, verify private CV/history survival and
one due daily message with browsers closed, then publish its actual SHA/HTTPS URL.
This scoped publication is already authorized; main merge/tag is separately pending.

B separately requires confirmed redeemed credits/key and a usable pinned image/
endpoint. B alone may run the authorized single <=USD2 experiment after those gates,
retrieve GPU-fit/device/metric/cost/shutdown evidence and hand over a committed SHA.
No automatic promotion into runtime scoring or market coverage follows the experiment.

## Five-minute demo and sign-in procedure

Until hosted access is supplied, use local9111 explicitly as a development demo.
Do not give judges localhost as a remote URL or claim real login. Once hosted
acceptance passes, open the verified HTTPS URL, use Clerk Sign in/Sign up or the
privately provisioned judge account, and test logout before sharing access.

1. Save a partial Profile; show that missing numerical assessment does not block chat.
2. Ask the exact ML-engineer roadmap question, then give an unseen project/time reply.
3. Open Careers; distinguish catalogue exploration, assessed ranks and evidence scopes.
4. Select a direction; generate/review/save/activate one plan. Refresh My Path, complete
   one activity, and distinguish recorded activity from verified competence.
5. Open the same Mindbot history; request a scoped change, review a proposal, show the
   persisted daily settings/result and a synthetic CV's explicit extraction review.

Prepare a due event before the walkthrough; do not fake its timestamp during the demo.
Show unavailable forecasts honestly. No synthetic label result should be presented
as independent evaluation or a real nationally representative demand forecast.

Private configs, actual local DB/WAL/uploads, environments, browser screenshots/logs
and thirteen read-only untracked source inputs remain outside Git. D's synthetic
acceptance creates a private database backup; this is not a backup of A's live DB,
CV objects or credentials. No new private-state backup or hosted recovery is claimed.
