# Resume after user disconnection — do not submit while paused

The user explicitly requested **no new paid job until they return**. This is an operational hold, not completion of the compulsory GPU experiment. The ignored `ml/artifacts/session-b/gpu-live/PAUSED_BY_USER.json` marker makes `gpu_control.py submit` fail before any network I/O. Do not remove it merely because time elapsed.

Verified at **2026-10-24T10:46:36.766910+00:00**:

| Item | Saved actual state |
| --- | --- |
| Endpoint | `0387furb08gke2` |
| Template | `nre3pphy75` |
| Native build | `a0f51622-0ece-4989-9855-183a70410f5a` — **COMPLETED** |
| Build source | `939dcd2a819248d67476dc01a789504b4cbdfa07`, published and verified |
| Frozen experiment runtime | `c8eb09921f6bf583ec30bca636f549628a575d69`; original data/runner unchanged |
| Image | `registry.runpod.net/jahax2154-sdc-2026-minder-session-b-market-docs-execution-parallel-b-checks-gpu-native-dockerfile:939dcd2a8` |
| Exported OCI manifest | `sha256:4198df1c4cdbe78f0ab0fa5e0549c97574a84dbf9b300de159cec8539ba40b0d` — build-export evidence, not a verified digest pull |
| Experiment job ID | **None — never submitted** |
| Job counters | Completed/failed/queued/in-progress/retried **all 0** |
| Workers | Min **0**, max **0**, no Pods; every health worker counter **0** |
| Credit / current spend | **USD25 / USD0 per hour**; automatic payments disabled |

The native image build ran successfully and its Docker steps verified CUDA-enabled XGBoost and all frozen source hashes. It did **not** train XGBoost. Image prefetch became unhealthy after selecting the exported digest. The native managed tag was restored, but healthy provider pull/prefetch was not established before the stop. Generic `verifyImage` returns registry401 for these private managed references; do not call that an actual successful pull. Source logs/configurations are preserved under ignored `ml/artifacts/session-b/gpu-live/`.

Shutdown was performed and then verified by fresh account/endpoint/health reads. No running build or paid job needs this Mac to monitor it. Endpoint/template/image metadata are intentionally retained for resumption. There is no network volume or persistent worker. Current template command is `/usr/bin/timeout --signal=TERM --kill-after=5s 150s python3 -u /app/docs/execution/parallel/B/checks/gpu_worker.py`. Endpoint execution timeout is180seconds. **The shutdown operation reset idleTimeout to10seconds**; explicitly restore/reverify5seconds before applying the intended timing budget. Do not equate worker-count settings with a dollar spending cap.

When the user returns:

1. Verify this branch/status and read `MB1-R04.json`; preserve the original raw/derived inputs and private secret file.
2. Read actual endpoint health, account credit/spend, endpoint repo/builds/template, and any remote job state. Inspect the fixed local `submission-intent.json` receipt. None existed at the stop, but a future resume must still check. If a job exists, recover its ID/status/artifacts rather than submit again.
3. Reuse the completed build above. Do not rebuild or retrigger a campaign without a diagnosed reason. Resolve the image-prefetch failure and confirm the actual runnable image identity/access.
4. Revalidate the existing USD2 **total** bound, including initialization, tests, provider retries, idle, storage/rounding and cleanup. The shared-TTL/container-timeout budget mode has local regression coverage; live preflight was **not passed** and must not be set to true by assumption.
5. Only after the user's return and actual live preflight passes, remove the local pause marker as part of the explicit resume, retain one exclusive submission intent, submit the unchanged synthetic experiment once, and track its returned job ID. Keep CPU baselines labelled and require actual fitted CUDA XGBoost proof.
6. Retrieve model/predictions/metrics/config/device/artifacts and actual billing; scale to zero/clean up and verify. Commit actual GPU evidence separately as MB2 and give A its full SHA. No real forecast activation or observed-coverage increase.

The key remains only in the mode600 ignored `.env.runpod.local`. No credentials or model weights are in this checkpoint. New artifacts/logs remain local without a new external backup; committed metadata and code preserve the reproducible state. A coordinates publication of the containing checkpoint; B has not pushed.

## Explicit return — MB1-R05 supersedes the pause above

The user explicitly resumed on24October2026. The private pause marker is archived, no prior submission exists, and supported native worker logs establish a successful pull/startup (worker92ff41nk2xxwjq, digest `sha256:a7bc4356f2634105c183faa4d2356310b549be258205ce25574a4185d6e427cc`). RunPod automatically completed descendant build `d443b1c9-aa7f-493d-b420-180c2cd5fa9d` from `4668be8196215d7aa8fe73e47c8756c4b81f7092` before startup observation; the experiment runtime remains manifest-pinned to c8eb099. No B rebuild or push was issued. Capacity returned to0/0, idle timeout5, balanceUSD25 and spendUSD0/hour verified. Proceed through final live preflight and the exclusive submission receipt; actual run remains a separate MB2 checkpoint. See MB1-R05.json for precise verifier/pull distinctions.

## MB2 completed — never resubmit

Single job `d7731076-6f21-47a0-a217-04eb0769ac96-e1` completed with five proven CUDA fits and all artifacts retrieved/checksummed. Its exclusive submission receipt remains in place. Fresh provider health reports one completed job, zero retries, zero queued/running jobs and every worker counter zero; endpoint min/max0/0 and idle5. See MB2.json and GPU_HANDOFF.v1.md. Only final posted billing reconciliation remains: HTTP200 billing history currently returns no records, balanceUSD25/current spendUSD0/hour. This is not proof of a final free run. No further experiment is authorised; status/billing reads must reuse the existing ID.
