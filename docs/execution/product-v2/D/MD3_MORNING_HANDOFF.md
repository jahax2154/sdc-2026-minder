# D morning Revision3 — persistence and CV handoff

D-owned backend implementation delivered; full hosted MD1/MD2 acceptance remains
blocked by external Railway/Clerk/volume configuration. No PostgreSQL conversion
is claimed. Actual engine is SQLite, schema versions1–7. The selected single-instance
Railway volume adapter/runtime candidate was agreed with E after its verified
Replit mockup/runtime blocker; no account resources or billing were provisioned.

## Preserved history and bounded checkpoints

| Phase | Actual output | Checkpoint |
| --- | --- | --- |
| MD0 | Revision3 audit, preserved D library; actual SQLite/source inspection | f49e1205b9e6fcd7fad9d4e2d2a2d740a3b6400c |
| M0 consumed | A ownership/base and approved assets, no reset | 719c8731ff54c73065f675267556e04d14c17a96 |
| MD1.1 | Verified owner mapping; Minder multiple histories, atomic singleton Mindbot; ordered server outcomes/retries | bbe4e1b1e248fd41a1cc621ac9b30d1860622941 |
| MD1.2 | Actual mount guard/private volume; online DB snapshot; notice reconciliation | c24c100353275dd010ea100910ea3c0a0cb07f7d |
| MD2 | CV/resume purpose; bounded text PDF/TXT extraction and existing review; onboarding metadata/retry regression | ab0a8f852171553074c990e80e6722e6b75af656 |
| MD1.3 | Versioned generated/accepted canonical plan; daily schedule/run references | 3299176066dcee3e2f5244986e04affc19994c8f |
| MD1.2-R01 | Portable snapshot first-read fix, source WAL unchanged | 24f0061cf4413a5fafc8a583ffe9bf9208cfdee0 |
| MD3 | Local acceptance/restart runner, actual D migration/backup evidence, final dependency handoff | commit containing this record |

Exact method/body/DTO/error contracts are MD1_CONVERSATION_CONTRACT.md,
MD1.2_VOLUME_AND_RECOVERY.md, MD2_CV_LIBRARY.md and
MD1.3_GENERATION_AUTOMATION.md. A alone registered shared routes/hooks; E owns
managed verification/host wrapper; F owns all frontend. No A/E/F source was edited
by D; their named committed handoffs were normally merged, preserving checkpoints.

## Implemented behavior and integration

E VerifiedIdentity issuer+subject maps atomically to a newly allocated stable owner;
raw client mappings are rejected. Anonymous/dev records stay under their original
owners, never assigned to the first real account. A managed middleware fails closed
without configured verification; real login is not replaced with local capabilities.

Minder supports create/list/open/delete/continue with persisted ordered visible
messages. Mindbot exposes one continuous singleton history per owner;24 concurrent
first loads resolved to one ID. SQLite unique index enforces it. No New chat/branch/
delete path for Mindbot. Browser open uses POST read alias because fetch forbids
GET bodies. Reopen does not execute provider/tools. Server callback runs after turn
reservation commits, then actual final visible DTO/source/action references are
saved. Exact retries return saved outcome; pending/uncertain never auto-reexecute.
Unknown/private reasoning is rejected, not stored. Context is bounded and scoped.

A's real typed generation is stored through record_generation; explicit acceptance
revalidates Profile/draft versions and calls A's materializer outside transactions,
then existing create_plan once. Generated/accepted metadata references canonical
PlanProgress/history/plan_design, no second authoritative graph. Acceptance does not
activate direction implicitly. Changed input supports new reviewed draft, not a
silent overwrite. Immutable source profiles, model/policy, fact IDs and assumptions
remain traceable. Task completion does not certify mastery.

Daily settings/run results reuse agent_settings/agent_events/notices. Scope is owned
plan IDs; saved timezone independent of Profile; next_run,last_result are server
state. Pause/cancel invalidates in-flight leases and pending scope; actual Worker
is A's existing implementation. Due notice appends atomically to SAME Mindbot;
unique owner/event prevents duplicates. E startup reconciles saved missing notices
without rerunning jobs. A handles latest-day catch-up, bounded retry/failure and
actual scoped proposal/action authority; no second scheduler or browser timer.

CV/resume-only new uploads require declared purpose cv|resume, bounded PDF/TXT type,
size/count/user quota. Declaration is not independently verified document semantics.
Legacy files are unclassified, never silently promoted. Private bytes remain separate
from metadata, in the current adapter. TXT/text-PDF extraction produces one existing
review draft, never profile changes. User explicitly chooses corrected fields for
existing intake-correction. The frozen uncertain editor fix is F's committed repair;
D verifies post-commit response-loss exact receipt,409 changed scope, one correction.

PDF limits: installed pypdf, max20 pages/64KiB text, bounded2-slot child process,
12s wall/5s CPU/Linux384MiB memory, no inherited server credentials. Scanned/encrypted,
malformed/oversized/busy/parser-unavailable states remain explicit with manual entry.
No OCR or automatic whole-document Groq submission. Actual source bytes/text remain
untrusted input and cannot authorize an action. Private server-only fields and
files are excluded from public history metadata/logs/Git.

Delete quarantines first, purges linked drafts, removes bytes before success and
retains a retryable deleting state on storage failure. Pending parsed data cannot
resurrect after deletion. Already applied Profile/history/authority records remain;
no account-erasure or SQLite free-page/WAL/backups sanitization claim.

## Actual D verification and local operator state

- Preserved baseline73 tests passed before M0.
- MD1.1:10 focused; integrated102/98passed/4SDKskips under legacy3.9.
- MD1.2:27 focused; integrated116/112passed/4SDKskips.
- MD2: actual pypdf6.21.2 synthetic text/scanned/encrypted/page-limit checks enabled;
  integrated121/117passed/4SDKskips. Shared read-only3.9 environment unchanged.
- MD1.3:9 focused; integrated127/123passed/4SDKskips.
- Same127 D tests then ALL passed under E's published Python3.12 environment,
  read-only with PYTHONDONTWRITEBYTECODE=1, including maintained SDK/PDF tests.
- Backup refinement:8 focused storage/migration tests passed, including initial
  read-only snapshot before a normal SQLite open.
- check_morning_persistence.py passed using actual configured local filesystem
  bytes, canonical state/action executor and existing Worker, followed by a NEW
  Python process reading file/profile/history/run result. Two software verified-
  identity fixtures, anonymous owner not claimed,16 concurrent singleton opens,
  exact action retry/no replay, private snapshot, CV deletion and retained applied
  Profile passed. Identity/model fixture parts are labeled, not live auth/provider.
- Real reserved D DB was privately backed up before migration5->7. It contains0
  canonical documents; no anonymous/user dataset was imported or reassigned.
  Original schema1–5 snapshot verified intact; new schema1–7 snapshot's first
  read-only open succeeded with DELETE journal and0600 permissions. Private copies:
  ml/artifacts/session-d/product/backups/pre-md1-20261024T064325694643Z.sqlite3 and
  post-md1-20261024T064613436737Z.sqlite3. Separate file bytes are NOT backed up.
- Actual D runtime --check passed: local_source_services,8104/9104, provider disabled,
  preserved qwen/qwen3.8-27b configuration, deployment false. No server left running.

A/F real-provider evidence remains separately attributed: F conversation/action
retry and F178a7a8 generated-path acceptance reports actual Qwen, one canonical plan
after lost response, explicit activation, refresh with0new generations and changed
weekly-time follow-up preserving saved plan. These are local A/F observations, not
D software generation fixtures or hosted login/durability proof.

Reproduce local file/new-process acceptance (no external model/network required):
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python docs/execution/product-v2/D/check_morning_persistence.py
```
The interpreter is E's published temporary environment, read-only, not a deploy
path. The runner creates/cleans disposable state only under D's product directory.
For deployed/local runtime install approved dependencies and use its own interpreter.

## Exact remaining hosted dependency

E/A still need actual existing Railway resource/credit access and an attached
persistent volume, plus managed Clerk provisioning and two live accounts. Required
server configuration: MINDER_ENV=production, MINDER_DATA_ROOT=/data,
RAILWAY_VOLUME_MOUNT_PATH=/data, MINDER_DB_PATH=/data/minder/runtime.sqlite3,
MINDER_DOCUMENT_STORAGE=private-volume,
MINDER_DOCUMENT_STORAGE_ROOT=/data/minder/documents. E AUTH_HANDOFF/ME2_HANDOFF
name exact issuer/origins/public key/server secret/JWT verification configuration;
enter credentials via approved secret interfaces, never Git/chat/browser bundles.

Store(path,volume_root=/data) verifies actual canonical mount every connection;
private-volume uses same mount. A plain directory or env URL cannot fake this.
Current evidence is mount-guard software tests + real local-files/process restart,
NOT actual hosted volume/redeploy/backup/scheduler acceptance. Actual hosted tests
must prove two-account isolation, logout/expiry, CV access, same Mindbot after browser
closure and worker due event, mounted DB/file restart/redeploy survival and backups.
No publish, spend, billing upgrade, main merge or data migration was performed by D.

Excluded state: unchanged untracked ml/minder_ml_starter/{raw,derived}, .env.local,
DB/WAL/backups/uploads/caches and D ignored PDF dependency directory. Raw sources,
credentials and private file bytes are NOT backed up/exported by these commits;
only the named D DB snapshots exist locally. All reviewed task source/tests/reports
are committed on the assigned D branch, with final full remote SHA returned to A/F.

## Final combined verification update

Consumed immutable E1669142ade6ac1e8f9790633e3b9e125c97a7aa1, including A's
9a69058 real failed/retry result hook and F178a7a8 reviewed-path acceptance. E's
coherent-clock refinement preserves the next_run guard; it does not weaken due
semantics. D independently reran ALL146 backend tests with zero skips under the
published read-only3.12 SDK/PDF environment, then4 deploy candidate checks and the
fresh-process local persistence runner: all passed. The first candidate command
omitted repository root from PYTHONPATH; corrected invocation below passed4/4.

E's7 actual existing-Worker checks pass: queued/inflight cancellation yields no
phantom action/notice; schedule timezone independent of Profile; latest-day catch-up;
persisted next_run and failed last_result after3attempts; owned-plan scope exclusion;
same singleton history/message reference after reopen/dedupe. This closes the local
worker integration finding; it does not close hosted browser-closed scheduling.
E records exact evidence in E/ME2_R01_AUTOMATION.md. No A/E test files were edited by D.

Final reproducible combined commands:
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python -m unittest discover -s apps/backend-api/tests
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python deploy/test_candidate.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ml/src:apps/backend-api /private/tmp/minder-e-auth-py312/bin/python docs/execution/product-v2/D/check_morning_persistence.py
```

No new D implementation remains pending. MD1/MD2 hosted acceptance is explicitly
limited/blocked_external until actual resource/managed-login access is supplied.
No local disabled capability, unit fixture or test total is substituted for that
proof. A/F receive the final cumulative D SHA after remote verification.
