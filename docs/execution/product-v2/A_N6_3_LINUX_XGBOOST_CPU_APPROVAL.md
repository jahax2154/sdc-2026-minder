# A-N6.3 — bounded CPU distribution approval for Replit hosting

E's requested substitution is approved as a routine hosted dependency choice:
Linux hosted runtime may use xgboost-cpu==3.4.1, while macOS keeps xgboost==3.4.1.
Preserve existing baseline/Ridge/XGBoost artifacts, model version, scoring policy
and all other resolved dependency pins. No training, GPU provisioning, new cloud
resources, library/model upgrade or numerical product-policy change is authorized.

Verified primary sources on this turn:
- https://xgboost.readthedocs.io/en/stable/install.html documents the CPU-only
  distribution as the supported smaller installation without GPU algorithms.
- https://pypi.org/pypi/xgboost-cpu/3.4.1/json reports version3.4.1, Python>=3.12,
  numpy/scipy ordinary dependencies and a Linuxx86_64 manylinux2_28 wheel of
  5796137bytes, SHA256
  1f16331f5c6beb2b40fbd4bf2834333062d93c9eb38b76186a5c206841dc1809.
  No NVIDIA dependency is listed for that distribution. Use the actual detected
  target architecture/glibc wheel; metadata inspection is not Linux execution.

## E implementation boundary

E owns deploy/requirements-hosted*.txt/build wrappers. Do NOT alter the shared
ml/requirements-foundation.txt to remove Linux generic XGBoost: B may need its GPU
training distribution. Keep the hosted CPU substitution separate from training.
Because an unconditional -r foundation would still require generic xgboost on
Linux, use the canonical foundation as CONSTRAINTS (-c) and explicitly request its
ordinary dependencies (numpy,scipy,scikit-learn,joblib,threadpoolctl,jsonschema,pypdf),
then mutually exclusive platform-marked xgboost-cpu==3.4.1 on Linux and
xgboost==3.4.1 elsewhere. Preserve resolved pins for all other packages in the hosted
lock, including the specifically approved Clerk/PG/object-storage dependencies.
Equivalent explicit hosted-only resolution is acceptable if the canonical ranges
remain enforced. Do not install both overlapping distributions in one environment.
No A foundation, another lane or existing local environment is edited by this
approval. E should commit and hand off its exact reviewed dependency/runtime slice.

## Verification needed before hosted acceptance

E must show the Linux marker/wheel resolution, existing pinned dependency
compatibility and actual Linux xgboost3.4.1 import/artifact load/CPU prediction smoke
when the existing target is accessible. Compare the compatible artifact's expected
predictions with the baseline; report unavailable artifacts/targets explicitly.
Do not retrain, claim Linux execution from a Mac resolver, invent forecasts or
substitute models to obtain a passing result. Existing missing-data/forecast status
and numerical policy remain unchanged. No paid job or NCCL/CUDA installation is
needed for this approved CPU-hosted option. Final functional/hosted acceptance is
still gated on D/E/F committed handoffs and the complete required browser journey.

F reports one coordinated real-provider normal-onboarding journey is in progress.
A will not run a duplicate provider verification during that window. This approval
uses public metadata and does not consume model quota or change any live service.
