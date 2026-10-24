# Explicit Python build avoids selecting the legacy Node/React project runtime.
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/ml/src:/app/apps/backend-api
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY ml/requirements-foundation.txt ml/requirements-foundation.txt
COPY deploy/requirements-hosted.txt deploy/requirements-hosted.txt
COPY deploy/requirements-hosted.lock.txt deploy/requirements-hosted.lock.txt
RUN pip install --no-cache-dir -r deploy/requirements-hosted.lock.txt
COPY ml/src ml/src
COPY ml/configs ml/configs
COPY ml/data ml/data
COPY ml/docs/MINDER_POLICY_REVIEW_v1.md ml/docs/MINDER_POLICY_REVIEW_v1.md
COPY ml/minder_ml_starter/sources_manifest.json ml/minder_ml_starter/sources_manifest.json
COPY contracts contracts
COPY apps/backend-api/minder_app apps/backend-api/minder_app
COPY apps/backend-api/data apps/backend-api/data
COPY apps/frontend-product apps/frontend-product
COPY docs/execution/parallel docs/execution/parallel
COPY docs/execution/product-v2 docs/execution/product-v2
COPY docs/execution/gates/G1A_v2_authorization.json docs/execution/gates/G1A_v2_authorization.json
COPY deploy deploy
RUN python -m deploy.artifacts fetch
CMD ["python", "-m", "deploy.runtime"]
