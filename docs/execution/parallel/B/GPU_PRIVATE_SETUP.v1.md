# MB1 preparation — private setup and one bounded GPU experiment

Current continuation: `GPU_NATIVE_BUILD_STATUS.v1.md` / `MB1-R01.json`. Credits/key are now verified; native GitHub build replaces local Docker/registry setup. The latest user instruction permits bounded provider retries within USD2, superseding this historical guide's one-provider-attempt constraint. One client submission remains mandatory.

Revision-3 morning runbook governs this continuation. Reuse SY1–SY3 and `SYNTHETIC_HANDOFF.v1.md`; no source investigation or experiment redesign is needed. **Local preparation is ready; container build, account preflight and actual GPU proof remain pending.** MB2 is compulsory submission work and is not completed by this preparation checkpoint.

## Private credentials

The actual ignored secret file has been created with mode **600**:

`/Users/phuahjunhong/sdc-2026-minder-worktrees/session-b/.env.runpod.local`

Actual supported names:

```dotenv
RUNPOD_API_KEY=
RUNPOD_ENDPOINT_ID=
RUNPOD_IMAGE=
```

Junhong saves **only `RUNPOD_API_KEY` initially**, directly in that file, then confirms that redeemed credits are visible and the key is saved. Do not paste the value into chat, screenshots, commands or Git. B fills `RUNPOD_ENDPOINT_ID` and `RUNPOD_IMAGE` after configuration. The latter must be a final custom-image reference such as `registry/repository@sha256:<64-hex-digest>`, not a base CUDA tag. The controller parses this file without executing shell contents and does not log its values. No account request or billable resource is created by making the template.

Use a new **Restricted** RunPod key. B needs **GraphQL Read/Write during endpoint/template setup and shutdown/deletion**, plus endpoint **Read/Write scoped only to this experiment endpoint** for submit/status/cancel/results. Before an endpoint ID exists, endpoint access may remain None, then be enabled only for that ID. GraphQL Read/Write is account-wide management authority at the provider's documented permission granularity; it is not a narrowly scoped endpoint-only permission. Reduce/revoke it after cleanup. A Read Only key cannot submit jobs or perform cleanup. Do not select an unrestricted All key. These requirements follow [RunPod credentials](https://docs.runpod.io/get-started/credentials) and its [scope explanation](https://www.runpod.io/blog/scoped-api-keys-runpod).

SSH and S3 keys are **not required** for this serverless artifact-return design. A private registry, if chosen, needs separate pull authentication entered in RunPod's container-registry secret interface; it does not belong in the model payload or image. No registry account or repository is assumed. B owns endpoint/image setup, not Junhong's dataset research or a manually rented persistent Pod.

## Image and endpoint requirements

Prepared files are `checks/GPU.Dockerfile`, `checks/gpu-requirements.v1.txt`, `checks/build_gpu_context.py`, and `gpu-runpod-job.v2.json`. The context is an explicit allowlist: code, existing committed snapshots needed by the isolation checks, schemas and scenario specification. It excludes the actual secret file, .git, original 13 raw inputs, environments, private records and model caches. A preview manifest marked uncommitted is rejected by the live handler.

The base image is verified Docker Hub **Linux amd64** CUDA **12.4.1 runtime / Ubuntu 22.04**, platform digest `sha256:cff3a0d82d2c2b47bab252d67fa9b34a20ef4c50781d98501b5c7367ea9afd10`. The GPU profile uses Ubuntu CPython 3.10, retaining the original numerical package versions including **XGBoost 2.1.4**, plus RunPod SDK **1.7.13**. This is an explicit runtime-profile change from the old CPU launcher's CPython 3.9 requirement; the old launcher, its hashes and experiment code remain untouched. No package was installed into the shared team interpreter.

The Linux XGBoost wheel must be the full `manylinux_2_28_x86_64` package, not `xgboost-cpu` or the CPU-only older-glibc variant. Its official wheel SHA-256 is recorded in `gpu-runpod-job.v2.json`. The Dockerfile asserts `xgboost.build_info()['USE_CUDA']`. See the [official installation guide](https://xgboost.readthedocs.io/en/release_2.1.0/install.html) and [GPU parameters](https://xgboost.readthedocs.io/en/release_2.1.0/gpu/index.html).

The custom image must run `gpu_worker.py`, expose the supplied handler to a dedicated RunPod Serverless endpoint named **`minder-b-gpu-once-20261024`**, and have access to **one NVIDIA GPU** with a driver compatible with CUDA 12.4. Actual GPU type, availability and price must be checked after account access; no rate or GPU reservation has been assumed. The final image must be built, inspected, pushed/pullable and pinned by its own digest. **Docker is absent on this Mac**, so only the context/configuration has been validated, not the Linux container. A Docker-capable builder and registry destination (or available provider build integration) remain necessary access/configuration dependencies. Do not create a GPU worker just to build the image.

After the preparation commit, B regenerates the clean context, then on a Docker-capable nonbillable/authorised builder uses:

```sh
python3 docs/execution/parallel/B/checks/build_gpu_context.py
docker build --platform linux/amd64 -t <registry/repository:preparation-SHA> ml/artifacts/session-b/gpu-preparation/context
```

Registry upload/pull and the final digest must be verified; no image publication or remote build occurred in this checkpoint. Capture installed versions and image metadata from that build. The pinned source manifest must identify the actual committed B snapshot, not a fabricated in-container Git history.

Desired endpoint controls: **0 active/minimum workers, maximum 1 worker, 1 GPU**, idle timeout **5 seconds**, endpoint execution timeout **180 seconds**, request execution timeout **180,000 ms**, request TTL **300,000 ms**, no persistent volume and no automatic client retry. Create/configure only after the user's credit/key confirmation; initially retain maximum workers at zero until all spend controls pass. The worker's own experiment subprocess is bounded to **120 seconds / 12 fits**.

**Exact unresolved provider control:** [RunPod's queue-based endpoint documentation](https://docs.runpod.io/serverless/endpoints/endpoint-configurations) describes automatic retries. The [documented request policy](https://docs.runpod.io/serverless/endpoints/send-requests) exposes executionTimeout/ttl, but the inspected material does not establish a zero-requeue setting. No invented `maxRetries=0` field is sent. A local receipt prevents a second client submission and duplicate fitting on the same worker; it cannot certify cross-worker exactly-once execution. B must verify a provider attempt ceiling and a server-side total billing bound (startup, execution, retry, idle, rounding and ancillary costs) before launching. TTL is not claimed to cap all container startup/idle billing. A sleeping-Mac polling loop is not that control. If the provider cannot supply the required bounds, B reports that blocker before any paid submission; no persistent-Pod fallback, repeated campaign, top-up or billing upgrade is allowed.

## Local validation and live operation

```sh
PYTHONPATH=ml/src python3 docs/execution/parallel/B/checks/test_gpu_preparation.py
PYTHONPATH=ml/src python3 docs/execution/parallel/B/checks/gpu_control.py payload
```

The exact immutable request is in `gpu-runpod-job.v2.json`/the controller: the existing dataset checksum, `require_gpu=true`, and one fixed experiment ID. No user code, alternate data, new hyperparameters or extra training jobs are accepted. Copy `gpu-live-preflight.template.v1.json` to the ignored `ml/artifacts/session-b/gpu-live/preflight.json`, then fill it from actual evidence. Default false/null values intentionally fail. Do not turn checks on merely to pass a validator.

Cost bound: verified GPU rate × verified **total** billable duration bound + startup/idle/retry/rounding/ancillary bounds must be **at most USD2**, with sufficient verified credit and no other billable workers. Actual rate, remaining credits and quote are currently unknown. The user's conditional one-run authority becomes active only after they confirm credits are visible and the key is saved. It does not authorise extra campaigns or unlimited provider retries.

After all live checks pass, B uses the following commands with actual IDs and ignored paths:

```sh
python3 docs/execution/parallel/B/checks/gpu_control.py inspect-endpoint
python3 docs/execution/parallel/B/checks/gpu_control.py budget --preflight ml/artifacts/session-b/gpu-live/preflight.json
python3 docs/execution/parallel/B/checks/gpu_control.py submit --preflight ml/artifacts/session-b/gpu-live/preflight.json
python3 docs/execution/parallel/B/checks/gpu_control.py status --job-id <actual-ID>
python3 docs/execution/parallel/B/checks/gpu_control.py retrieve --response ml/artifacts/session-b/gpu-live/status-response.json
```

Submission intent is atomically persisted in the fixed ignored `gpu-live/submission-intent.json` before the sole POST. **Do not delete it or resubmit after a timeout/unknown response.** Retrieve and check the actual job outcome first. The SDK's outer completed status alone does not prove the experiment succeeded: inspect the handler's nested status, GPU fit proofs and artifacts. Catchable worker failures return labelled error logs/partial proofs instead of requesting a retry. Local positive GPU-proof tests use mocked configurations and are not live GPU evidence.

The handler returns a SHA-256-pinned base64 ZIP (maximum 2 MiB) through the retained job result before ephemeral worker cleanup. Retrieval is tested locally, including checksum, expansion and path-traversal rejection; the live provider round trip remains unverified. No S3 key, network volume or credential in the worker is necessary. Fetch results immediately within configured TTL. Preserve failure artifacts and unfavorable metrics as well as successful models.

On failure or deadline, cancellation is available; shutdown must not wait indefinitely for artifacts:

```sh
python3 docs/execution/parallel/B/checks/gpu_control.py cancel --job-id <actual-ID>
python3 docs/execution/parallel/B/checks/gpu_control.py shutdown
python3 docs/execution/parallel/B/checks/gpu_control.py inspect-endpoint
python3 docs/execution/parallel/B/checks/gpu_control.py delete-endpoint
```

Shutdown targets only the exact named endpoint. The [documented management flow](https://docs.runpod.io/sdks/graphql/manage-endpoints) scales min/max to zero before deletion; the client additionally requires no remaining pods before deleting. Provider authentication/control behavior must be verified before spend. Capture final worker state and endpoint absence. Record actual billed charges from the provider; if billing lags, leave cost unknown and mark final reconciliation pending. Do not label scale-to-zero requests as verified shutdown without a subsequent read.

## GPU evidence and handoff

The adapter reuses the exact hashed generator, source checks, splits, features, baselines, tuning grid and experiment runner. Ridge and simple baselines are labelled CPU. XGBoost alone uses `device=cuda:0` and `tree_method=hist`; all five XGBoost fits (one pilot plus four candidate fits) must show USE_CUDA, a successful fitted booster, effective CUDA device, GPU updater and 48 rounds. Seven other fits remain CPU. Device inventory without those fitted-model checks is a failure. No CPU fallback satisfies MB2.

Preserve the previous SY2 validation-selected seasonal method for each family. GPU validation outputs are diagnostic, not a replacement selected on test results. Compare numerical deltas without requiring bitwise GPU identity, and retain adverse results. Archives include fitted configurations, training IDs, UBJ/joblib models, predictions, metrics, UTC job times, source hashes and failure logs. The live controller's submission receipt binds actual endpoint/image digest to the verified preflight. A separate MB2 checkpoint must add actual job/device/image/metric/cost/shutdown evidence.

Observed market evidence, application coverage and real forecasts are unchanged; no model is promoted. A receives the preparation full SHA for coordinated publication. **No worker, account mutation, registry upload or paid job has been made during preparation.** MB1 live and MB2 remain open, not waived as optional submission work.
