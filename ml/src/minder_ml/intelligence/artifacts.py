"""Project-controlled artifacts only. Joblib is unsafe for untrusted files."""

from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import time

from .estimators import THREADS, THREAD_ENV, configure_threads
from .schemas import FEATURE_NAMES, FEATURE_VERSION, RUBRIC_VERSION, SCORE_VERSION, RANKING_VERSION

ARTIFACT_ROOT = Path(__file__).resolve().parents[3] / "artifacts" / "intelligence"
PACKAGES = ("numpy", "scipy", "scikit-learn", "xgboost", "joblib", "threadpoolctl")


def versions():
    result = {"python": platform.python_version()}
    for package in PACKAGES:
        try:
            result[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            result[package] = None
    return result


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def run_path(run_id):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", run_id):
        raise ValueError("invalid run ID")
    root = ARTIFACT_ROOT.resolve()
    path = root / run_id
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError("artifact outside controlled root")
    return path


def require_runpod(evidence_path):
    """An operator-supplied attestation, never inferred from hardware or secrets."""
    if not evidence_path:
        raise ValueError("runner_unavailable: RunPod CPU/budget/credit verification required before fitting")
    evidence = json.loads(Path(evidence_path).read_text())
    for field in ("pod_id", "verified_by", "verified_at", "credit_applicability_reference"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            raise ValueError(f"RunPod verification missing {field}")
    if evidence.get("execution_location") != "runpod" or evidence.get("cpu_only") is not True:
        raise ValueError("RunPod CPU execution must be explicitly verified")
    if evidence.get("credit_applicable") is not True:
        raise ValueError("credit applicability must be verified by operator")
    for field in ("agreed_budget_usd", "estimated_run_cost_usd"):
        from .schemas import number
        number(evidence.get(field), field)
    if evidence["estimated_run_cost_usd"] > evidence["agreed_budget_usd"]:
        raise ValueError("estimated cost exceeds agreed budget")
    # Presence of a credential is not verification. Never print credential values.
    if os.environ.get("RUNPOD_POD_ID") != evidence["pod_id"]:
        raise ValueError("must execute within the attested RunPod pod")
    return evidence


def environment(runner):
    return {"execution_location": "runpod", "runner_verification": runner,
            "platform": platform.platform(), "machine": platform.machine(),
            "processor": platform.processor(), "logical_cpu_count": os.cpu_count(),
            "thread_limit": THREADS,
            "thread_environment": {name: os.environ.get(name) for name in THREAD_ENV}}


def fit_timed(model, x, y):
    configure_threads()
    from threadpoolctl import threadpool_limits, threadpool_info
    with threadpool_limits(limits=THREADS):
        wall, cpu = time.perf_counter(), time.process_time()
        model.fit(x, y)
        timing = {"fit_wall_seconds": time.perf_counter() - wall,
                  "fit_process_cpu_seconds": time.process_time() - cpu,
                  "resolved_threadpools": threadpool_info()}
    return timing


def predict_raw(model, x):
    configure_threads()
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=THREADS):
        return [float(v) for v in model.predict(x)]


def inference_timing(model, x, repeats=10):
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        predict_raw(model, x)
        times.append(time.perf_counter() - start)
    return {"batch_size": len(x), "repeats": repeats,
            "wall_seconds_each": times, "mean_wall_seconds": sum(times) / repeats,
            "includes_thread_limit_context": True}


def metadata_base(runner, compatibility, dataset_hashes, split):
    from .policy import load_policy
    _, policy = load_policy()
    return {"created_at": datetime.now(timezone.utc).isoformat(),
            "artifact_schema_version": "minder-learner-artifact-g3-v1",
            "provenance_mode": "unclassified", "promotable": False,
            "policy_id": policy["policy_id"], "policy_version": policy["policy_version"],
            "policy_sha256": policy["policy_sha256"],
            "feature_names": list(FEATURE_NAMES), "feature_schema_version": FEATURE_VERSION,
            "rubric_version": RUBRIC_VERSION, "score_mapping_version": SCORE_VERSION,
            "ranking_policy_version": RANKING_VERSION, "compatibility": compatibility,
            "dataset_hashes": dataset_hashes, "split": split, "seed": 42,
            "package_versions": versions(), "environment": environment(runner),
            "implementation_hashes": {p.name: digest(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
            "evaluation_status": "not_evaluated", "candidates": {}}


def save_candidate(run, kind, model, timing):
    import joblib
    folder = run / kind
    folder.mkdir()
    pipeline = folder / "pipeline.joblib"
    joblib.dump(model, pipeline)
    restored = joblib.load(pipeline)  # Only the file this process just wrote.
    import math
    return restored, {"pipeline_sha256": digest(pipeline), "timing": timing,
                      "hyperparameters": {k: "NaN" if isinstance(v, float) and math.isnan(v) else v
                                          for k, v in model.get_params().items()
                                          if k.startswith("estimator__") or k.startswith("scaler__")}}


def load_candidate(run_id, kind, compatibility):
    if kind not in ("ridge", "xgboost"):
        raise ValueError("not a learned scorer")
    run = run_path(run_id)
    meta = json.loads((run / "metadata.json").read_text())
    if (meta.get("provenance_mode") != "independent_reviewed"
            or meta.get("promotable") is False
            or meta.get("compatibility", {}).get("data_kind") in ("synthetic_math_only", "policy_distillation")):
        raise ValueError("experimental artifacts cannot enter independent serving")
    if meta["evaluation_status"] != "holdout_evaluated" or meta.get("selected_candidate") != kind:
        raise ValueError("artifact not selected and independently holdout-evaluated")
    expected = {"feature_names": list(FEATURE_NAMES), "feature_schema_version": FEATURE_VERSION,
                "rubric_version": RUBRIC_VERSION, "score_mapping_version": SCORE_VERSION,
                "ranking_policy_version": RANKING_VERSION, "compatibility": compatibility}
    for key, value in expected.items():
        if meta.get(key) != value:
            raise ValueError(f"incompatible artifact {key}")
    from .policy import load_policy
    if meta.get("policy_sha256") != load_policy()[1]["policy_sha256"]:
        raise ValueError("artifact policy mismatch")
    return load_pipeline(run, kind, meta)


def load_experiment_candidate(run_id, kind, compatibility, provenance_mode):
    """Explicit research-only path; production load_candidate always rejects it."""
    if kind not in ("ridge", "xgboost"):
        raise ValueError("not a learned scorer")
    if provenance_mode not in ("synthetic_math_only", "policy_distillation"):
        raise ValueError("explicit experiment provenance required")
    run = run_path(run_id)
    meta = json.loads((run / "metadata.json").read_text())
    if meta.get("provenance_mode") != provenance_mode or meta.get("promotable") is not False:
        raise ValueError("experiment provenance mismatch")
    if meta.get("evaluation_status") not in ("synthetic_smoke_only", "policy_distillation_only"):
        raise ValueError("incomplete experiment")
    if ((provenance_mode == "synthetic_math_only") != (meta["evaluation_status"] == "synthetic_smoke_only")):
        raise ValueError("experiment evaluation mode mismatch")
    expected = {"feature_names": list(FEATURE_NAMES), "feature_schema_version": FEATURE_VERSION,
                "rubric_version": RUBRIC_VERSION, "score_mapping_version": SCORE_VERSION,
                "ranking_policy_version": RANKING_VERSION, "compatibility": compatibility}
    for key, value in expected.items():
        if meta.get(key) != value:
            raise ValueError("incompatible experiment " + key)
    from .policy import load_policy
    _, policy = load_policy()
    if meta.get("policy_sha256") != policy['policy_sha256']:
        raise ValueError("experiment policy mismatch")
    return load_pipeline(run, kind, meta)


def load_pipeline(run, kind, meta):
    """Internal loading after run compatibility/status checks by the caller."""
    if kind not in ("ridge", "xgboost"):
        raise ValueError("not a learned scorer")
    if meta["package_versions"] != versions():
        raise ValueError("artifact requires exact recorded Python/package versions")
    if meta["implementation_hashes"] != {
        p.name: digest(p) for p in sorted(Path(__file__).parent.glob("*.py"))
    }:
        raise ValueError("artifact implementation changed; compatibility review required")
    pipeline = run / kind / "pipeline.joblib"
    if not pipeline.resolve().is_relative_to(run.resolve()) or pipeline.is_symlink():
        raise ValueError("pipeline outside controlled run")
    if digest(pipeline) != meta["candidates"][kind]["pipeline_sha256"]:
        raise ValueError("pipeline integrity mismatch")
    import joblib
    from sklearn.pipeline import Pipeline
    from sklearn.utils.validation import check_is_fitted
    model = joblib.load(pipeline)
    expected_steps = ["scaler", "estimator"] if kind == "ridge" else ["estimator"]
    if not isinstance(model, Pipeline) or list(model.named_steps) != expected_steps:
        raise ValueError("artifact is not the expected complete pipeline")
    check_is_fitted(model)
    if model.n_features_in_ != len(FEATURE_NAMES):
        raise ValueError("artifact feature dimension mismatch")
    return model
