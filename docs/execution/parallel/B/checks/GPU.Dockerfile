FROM --platform=linux/amd64 nvidia/cuda@sha256:cff3a0d82d2c2b47bab252d67fa9b34a20ef4c50781d98501b5c7367ea9afd10
# Docker Hub verified base: 12.4.1-runtime-ubuntu22.04 amd64. GPU driver is
# supplied by the provider. Final built image digest must be recorded separately.
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 PYTHONPATH=/app/ml/src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip libgomp1 ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY runtime/ /app/
RUN python3 -m pip install --no-cache-dir -r docs/execution/parallel/B/checks/gpu-requirements.v1.txt && python3 -c "import xgboost; assert xgboost.build_info()['USE_CUDA']"
CMD ["python3", "-u", "docs/execution/parallel/B/checks/gpu_worker.py"]
