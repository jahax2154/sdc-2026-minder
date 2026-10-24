# MA2-R02 — explicit local worker and runtime revision

A's product CLI now supports --worker only for laneA. It reuses E hosted_worker.run
and A's existing Worker against the same A Store, bounded by the existing provider/
queue/lease/idempotency rules. No second scheduler/backend or other-lane process.
Default commands still start no worker; D/E/F reservations untouched. Shutdown sets
the worker stop event and waits at most5s; no retry of a user write is introduced.

GET health includes runtime_revision from a validated full release/provider SHA or
local Git at process construction. A explicit local worker also reports its actual
thread liveness. Neither field certifies hosted scheduling/durability. Existing
hosted factory/volume/auth guards stay strict; E deployment supervisor still owns
production operation. Invalid revision values are never reflected to browsers.

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane A --worker
```

A private env now selects its isolated3.12 runtime and local-development CV storage;
Qwen key remains in the same0600 ignored server config, no copied key/new subscription.
Explicit --check confirms current model/provider presence/namespace without a model
call or worker start. Actual all-worker/browser-closed local test is separate from
requested hosted acceptance, which still needs Railway/Clerk access.
