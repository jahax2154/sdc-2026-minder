"""Source-verified optional learning library; no automatic gap/mastery mapping."""
import json
from pathlib import Path
from urllib.parse import urlsplit
from minder_ml.intelligence.service_contracts import validate
from .store import AppError


def learning_options(topic_ids=None):
    path = Path(__file__).resolve().parents[1] / "data/learning-resources.v1.json"
    data = json.loads(path.read_text())
    known = {t for r in data["resources"] for t in r["topic_ids"]}
    if topic_ids is not None and (not isinstance(topic_ids, list) or not set(topic_ids).issubset(known)):
        raise AppError("unknown_learning_topic")
    resources = []
    for item in data["resources"]:
        validate("Source", item["source"])
        if urlsplit(item["source"]["uri"]).scheme != "https":
            raise AppError("learning_resource_https_required")
        if topic_ids is None or set(item["topic_ids"]).intersection(topic_ids):
            resources.append(item)
    return dict(version=data["version"], resources=resources,
        limitation="Optional source-verified content, not automatically mapped to occupational criteria. "
                   "Effort, total cost, suitability and demonstrated mastery remain unknown.")
