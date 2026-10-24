# Session B — actual GPU execution handoff to A

MB2 passes actual GPU execution, artifact retrieval and cleanup. Final billing settlement remains pending. Publish the commit containing `MB2.json`, this handoff, `gpu-results.v1.json` and `gpu-artifact-manifest.v1.json` through the authorised coordinated procedure in closure file06. B has not pushed. Preparation checkpoint: `40e6a8e5ae20e64f0ca98e7276d1ac0907885a4f`.

One client submission, job **`d7731076-6f21-47a0-a217-04eb0769ac96-e1`**, completed on endpoint `0387furb08gke2`, worker `foovsurpt6stj7`. Provider execution time was2.529seconds after10.339seconds queue delay; the experiment child measured0.695seconds. Device: NVIDIA RTX A4500, driver595.91.07,20470MiB. Five actual XGBoost2.1.4 fits each report `cuda:0`, `grow_gpu_hist` and48boostedrounds; seven Ridge fits and both baseline methods ran on CPU. This proves CUDA fitting, without establishing a speed advantage on this small workload.

RunPod automatically completed descendant build `d443b1c9-aa7f-493d-b420-180c2cd5fa9d` from `4668be8196215d7aa8fe73e47c8756c4b81f7092` before startup observation. B issued no rebuild. The native image tag ends in`:4668be819`; successful supported worker pull logs report digest `sha256:a7bc4356f2634105c183faa4d2356310b549be258205ce25574a4185d6e427cc`. All66 runtime hashes remain pinned to `c8eb09921f6bf583ec30bca636f549628a575d69`. The generic verifier's registry401 was not an actual native worker pull failure. Historical reconstructed-digest worker failure remains unexplained; it was not bypassed or represented as successful.

The unchanged fictional dataset SHA is `b7aa327d30220b27a2236476b5c51d45d04deb16d9bfb009cc2fcca81a01880b`. Train/validation/test/robustness counts remain156/24/34/14, with whole scenario groups separated and publication-date controls intact. All912 returned predictions independently reproduce32 family/method/split metric sets; GPU training IDs belong only to the training split. Original13 read-only source hashes also pass.

| Method | Device | Role test MAE | Skill test MAE |
| --- | --- | ---: | ---: |
| Last value | CPU | 1.470588 | 1.529412 |
| Seasonal | CPU | 2.176471 | 1.882353 |
| Ridge | CPU | 10.469243 | 5.787942 |
| XGBoost | CUDA | 29.025003 | 15.713215 |

Each family has17 test examples. Full MAE/RMSE/WAPE, validation trials, scenarios, robustness results and fitted configurations are committed in `gpu-results.v1.json`. XGBoost performs substantially worse on the test set. The previous validation-selected seasonal choice is preserved, without test reselection or application promotion. Small GPU/CPU floating-point differences are recorded. These are **synthetic outcomes, not Malaysian demand observations or real forecast accuracy**. Real forecasts remain unavailable, and observed market coverage is unchanged.

The190139-byte returned archive passed SHA256 `e138ab157a819fdd3d97392accef07f15c88f6051f7999de3f76f56565e626e8`. Both XGBoost UBJ/joblib models, Ridge artifacts, predictions, generated examples/data, model metadata and complete job record are retained under ignored `ml/artifacts/session-b/gpu-live/artifacts/`. The committed artifact manifest records their individual hashes. Model weights, generated rows and credentials are excluded from Git. These local artifacts have no newly created external backup; A can use the committed numerical report/config proofs directly.

USD2 remains the total authority. The conservative preflight upper estimate wasUSD0.645: USD0.58/hour ×900seconds plusUSD0.50 ancillary/rounding reserve. Shared provider TTL300seconds, container timeout150seconds with5second kill grace, idle5seconds and maximum1worker/GPU bound execution/retry exposure; worker count alone is not a dollar cap. No top-up, billing upgrade or standalone Pod was used. Actual provider retries:0.

Final cleanup checks show endpoint min/max0/0, no Pods/workers, every worker health counter0, queue/in-progress0 and completed1. Current spend isUSD0/hour. Endpoint/template/image metadata are retained, with no persistent volume. Billing API HTTP200 returned no posted records as of2026-10-24T13:30:21Z; balance still readsUSD25. **Final settled cost is unknown**, not confirmed zero. The only follow-up is a read-only billing reconciliation for this endpoint/job, followed by a focused evidence refinement. No new submission, retry campaign or model promotion is authorised. The fixed submission-intent receipt must remain intact.

Resume instructions are superseded by the MB2 completion note in `RUNPOD_RESUME.v1.md`: inspect the existing job/billing state and never resubmit this experiment.
