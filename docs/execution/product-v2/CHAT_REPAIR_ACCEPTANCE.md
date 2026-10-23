# A targeted chat/Mindbots repair acceptance

Local integrated repair of CHAT-01/PANEL-01/STATUS-01/BOT-01/NAV-01. Frontend
F8446ca801de8d8a0163c390f76d2aa609a5fec16 (product code aeb3e08); backend
A12e7496 plus bounded runtime19b19e0. The containing A integration checkpoint
preserves these full histories. No reset/squash/main merge/deployment.

## Causes and resulting behavior

CHAT-01 had two verified layers. The old backend forced a selection from policy/
proposal/limitation records with no application capability vocabulary; the provider
could not produce a useful app answer even though its real call succeeded. F also
blocked unsaved profiles locally and prefixed content with a generic heading.
The repaired backend distinguishes verified application guidance, grounded empirical
evidence and limited fallback; F renders the actual answer first. Greetings,
capability variants, onboarding and a focused follow-up need no complete Profile
or provider. No implicit Profile save or guessed competence. Saved versions and
owner-scoped prior context are validated. Empirical requests retain the existing
closed factual grounder. Pinned role descriptions are exact US O*NET quotations,
not Malaysian demand or user competence. Conversation-routing-v1 versions this
distinction; grounding-privacy-v1 is retained for empirical claims.

The screenshot's0 recorded personal evidence items was not proof of a broken key
or a requirement to complete a Profile. The old provider saw a closed generic ledger,
not an application-capability answer. New application guidance intentionally sends
no facts to a provider; external source facts and Profile evidence are different
counts. Diagnostics.evidence_count means rendered verified statements, not claimed
personal mastery or number of private Profile records.

BOT-01 was measured HTTP head-of-line blocking, compounded by frontend sequencing.
Old single-request WSGI held GET profile behind a pending provider call. Saved reads
afterward were fast. Both product listeners now use16 bounded request workers with
45s socket bound; provider2-slot/budget and existing SQLite per-request connections,
atomic versions/approval/idempotency remain. No automatic write retry. F draws the
frame before profile/section completion, fetches independent sections, masks private
content on auth failure, cancels obsolete view reads and exposes bounded manual
recovery. Read/write/chat client bounds are8/12/45s. Opening Mindbots invokes no model
or agent job. A concurrent identical direct action still applies exactly once.

F supplies explicit Context Close/toggle/Escape/focus behavior, retained draft/
messages/scroll/width, mobile modal behavior, Working… terminal states and compact
72px navigation with mouse/focus/touch labels. Overview/Explore page bodies were
not redesigned. Screenshots were visually inspected in A after actual UI execution.

## Actual local measurements

Mac local source services/SQLite, synthetic owners. Navigation samples are warm/
initial page navigation, not process-cold or production latency guarantees. Baseline
and guidance now perform different work: guidance explicitly skips a provider;
these numbers do not establish that Qwen itself became faster.

| Case | Sample count / mode | Observed |
| --- | --- | --- |
| F baseline exact capability question |2, real Qwen included |15969/16561ms, only disclaimer/limitations |
| F baseline Mindbots during pending chat |1, real provider |16595ms usable; profile GET16519ms, later reads2–10ms |
| A exact capability UI |1, application guidance/no model |27ms; unsaved, useful answer and question |
| A capability HTTP unsaved/partial/rich |1 each, no model |11.606/4.728/3.317ms |
| A real factual HTTP |1, Qwen available/native validated |1139.759ms total,989.487ms provider;4 measurement families |
| A saved HTTP reads during that call |5, provider still pending |0.923–2.993ms; settings404 is explicit absent state |
| A browser Mindbots during real forecast chat |1, Qwen available |109ms saved ready before chat788.23ms finished; provider618.349ms |
| A browser provider intentionally absent |3 initial/repeated navigation, actual HTTP |frame1ms; saved32/24/24ms; zero added chat calls |
| Controlled serial/threaded HTTP |3 each, explicit0.4s software delay |median413.144ms ->2.933ms; not real Groq evidence |

Actual unsaved empirical follow-up after a role quotation also returned Qwen
available in1526.368ms with5 source entries and unavailable forecast preserved.
One screenshot-only empirical call returned limited_fallback without retaining
its reason; it was not counted as successful live interpretation. The separately
captured same unsaved source flow succeeded. Provider/output availability can vary;
no account outage, reason, model switch or universal success is inferred.

## Evidence and reproducible checks

- Final A combined backend90 passed7.024s. Latest routing-specific conversation/
  chat/grounding20 passed1.152s; F final handoff records its own90 and8 focused.
- Actual A browser repair_integrated passes unsaved/partial/paraphrase/follow-up,
  no implicit save, pinned US source, focused assessment input, real pending chat/
  saved workspace overlap, unavailable forecasts, direct actions, exact proactive
  reject/approve/repeat/stale and foreign context404, zero page errors.
- Actual A configured-key-absent browser passes truthful fallback/manual prefill,
  three saved navigations and zero added model calls. This is an explicit isolated
  configuration, not a live Groq outage and not a mocked browser response.
- Explicit intercepted UI/workspace fixtures pass close/toggle/focus/width/draft/
  scroll, success/error/cancel/timeout, pending duplicate prevention, optional error/
  retry, late-response isolation, auth masking and startup recovery. Their compressed
  45s->80ms/8s->100ms deadlines are software checks, not provider performance.
- A real shell/navigation checks pass72px rail/hover/focus/phone/coarse touch/route
  access. Source F's final20 route/console/assets smoke is retained in its handoff.
- First A100ms compressed read fixture failed an optional ready assertion; unchanged
  repeat passed with other responses2–4ms. Original log retained; no production
  timeout/assertion was weakened. Two earlier HTTP harness expectations were fixed
  (valid own Profile version before foreign lookup, and absent settings404); neither
  was a backend defect. Logs remain private artifacts with report hashes.

From A's existing environment, no build/setup/credential copy:

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane A
# Local UI http://127.0.0.1:9111/#minder and /#mindbots; API8111 or same-origin /api.
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m unittest discover -s apps/backend-api/tests
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/checks/check_chat_repair.py
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/checks/check_repair_provider_off.py
```

Browser scripts accept MINDER_PRODUCT_BASE_URL. A adapters change only report/
screenshot paths, retain upstream assertions and source hashes, and write under
ml/artifacts/session-a/product/chat-repair-final-browser. F's canonical committed
handoff and full phase/dependency SHA table are F/repairs/HANDOFF.md.

## Limits and preserved state

Verified qwen/qwen3.8-27b and private credential remain unchanged. Normal A storage
is disabled; no document work was required. Prior F-DOC-REVIEW-R01 is deferred outside
this brief, not silently closed. Conversations are temporary/in-memory displays with
owner-scoped intent metadata, not stored/restored transcripts or unrestricted model
prose. No verified hosting, continuous scheduler, real future forecast accuracy or
independent suitability validation follows these checks. Scorer/source scopes and
action authority are preserved. No GPU/training/deployment or paid job launched.
Read-only raw/derived inputs remain untracked and unchanged. Private credentials,
DBs/WAL/uploads and browser artifacts remain outside Git, without a new backup claim.
