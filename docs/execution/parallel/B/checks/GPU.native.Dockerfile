# Native GitHub build: repository-root context, no local Docker/registry needed.
# COPY only reviewed runtime paths; never COPY the whole repository or .git.
FROM --platform=linux/amd64 nvidia/cuda@sha256:cff3a0d82d2c2b47bab252d67fa9b34a20ef4c50781d98501b5c7367ea9afd10
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 PYTHONPATH=/app/ml/src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip libgomp1 ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ml/src/ /app/ml/src/
COPY contracts/ /app/contracts/
COPY ml/data/market/snapshot.v1.json ml/data/market/mapping.v1.json ml/data/market/published-role-observations.v1.json ml/data/market/current-public-evidence.v1.json ml/data/market/serving-registry.v1.json ml/data/market/forecast-dataset.v1.json /app/ml/data/market/
COPY ml/data/market/synthetic-lab/scenario-spec.v1.json /app/ml/data/market/synthetic-lab/
COPY docs/execution/parallel/source_snapshot.v1.json /app/docs/execution/parallel/
COPY docs/execution/parallel/B/synthetic-results.v1.json docs/execution/parallel/B/synthetic-runpod-job.v1.json docs/execution/parallel/B/synthetic-runpod-requirements.v1.txt /app/docs/execution/parallel/B/
COPY docs/execution/parallel/B/checks/synthetic_market_experiment.py docs/execution/parallel/B/checks/run_synthetic_job.py docs/execution/parallel/B/checks/gpu_synthetic_adapter.py docs/execution/parallel/B/checks/gpu_worker.py docs/execution/parallel/B/checks/gpu-requirements.v1.txt /app/docs/execution/parallel/B/checks/
COPY docs/execution/parallel/B/gpu-runtime-source-manifest.v1.json /app/gpu-image-manifest.json
RUN python3 -m pip install --no-cache-dir -r docs/execution/parallel/B/checks/gpu-requirements.v1.txt && python3 -c "import xgboost; assert xgboost.build_info()['USE_CUDA']"
RUN PYTHONPATH=/app/docs/execution/parallel/B/checks python3 -c "from pathlib import Path; from gpu_worker import verify_manifest; verify_manifest(Path('/app'))"
CMD ["python3", "-u", "docs/execution/parallel/B/checks/gpu_worker.py"]
