"""Bounded offline CPU execution. All fitting requires verified RunPod evidence."""

import csv
import hashlib
import json
from pathlib import Path

from . import artifacts as a
from .estimators import configure_threads, make_estimator
from .evaluation import (read_annotations, compatibility, split_groups, partition,
                         snapshots_hash, predictions, diagnostics, counterfactuals)
from .features import feature_matrix

RELOAD_TOLERANCE = 1e-9


def checked_rows(path):
    rows, report = read_annotations(path)
    if report["errors"]:
        raise ValueError(json.dumps(report))
    return rows, report


def new_run(run_id):
    run = a.run_path(run_id)
    run.mkdir(parents=True, exist_ok=False)
    return run


def save_checked(run, kind, model, timing, x):
    timing["inference"] = a.inference_timing(model, x[:8])
    restored, info = a.save_candidate(run, kind, model, timing)
    before, after = a.predict_raw(model, x), a.predict_raw(restored, x)
    difference = max(abs(x - y) for x, y in zip(before, after))
    if difference > RELOAD_TOLERANCE:
        raise ValueError("save/reload prediction mismatch")
    info["reload_max_absolute_difference"] = difference
    info["reload_tolerance"] = RELOAD_TOLERANCE
    return info


def smoke(run_id, fixture_path, runner_path):
    runner = a.require_runpod(runner_path)
    fixture = json.loads(Path(fixture_path).read_text())
    if fixture.get("data_kind") != "synthetic_math_only":
        raise ValueError("smoke requires explicitly synthetic fixture")
    from .schemas import FeatureSnapshot, FEATURE_VERSION
    rows = [FeatureSnapshot(*x, assessed_requirement_fraction=1,
                            feature_schema_version=FEATURE_VERSION) for x in fixture["x"]]
    x, y = feature_matrix(rows), fixture["y"]
    if len(x) != len(y) or not x:
        raise ValueError("invalid smoke fixture")
    from .schemas import number
    for value in y:
        number(value, "synthetic mathematical target", high=2)
    configure_threads()
    run = new_run(run_id)
    meta = a.metadata_base(runner, {"data_kind": "synthetic_math_only"},
                           {"fixture": a.digest(fixture_path)}, {})
    meta["evaluation_status"] = "synthetic_smoke_only"
    report = {"gate": "B", "data_kind": "synthetic_math_only",
              "empirical_status": "not_evaluated", "rows": len(x), "candidates": {}}
    for kind in ("ridge", "xgboost"):
        model = make_estimator(kind)
        timing = a.fit_timed(model, x, y)
        meta["candidates"][kind] = save_checked(run, kind, model, timing, x)
        report["candidates"][kind] = {"fit_predict_reload": "passed",
                                      "prediction_count": len(a.predict_raw(model, x))}
    a.write_json(run / "metadata.json", meta)
    a.write_json(run / "metrics.json", report)
    return {"run_id": run_id, "report": report, "candidates": meta["candidates"]}


def compare(data_path, run_id, runner_path, split_path=None):
    rows, report = checked_rows(data_path)
    if not rows:
        return {"status": "not_evaluated", "reason": "no independent reviewed labels", "dataset": report}
    supplied = json.loads(Path(split_path).read_text()) if split_path else None
    split = split_groups(rows, supplied)
    dev = partition(rows, split, "development")
    groups = [r["profile_group_id"] for r in dev]
    n_groups = len(set(groups))
    if n_groups < 2:
        return {"status": "not_evaluated", "reason": "fewer than two development groups", "dataset": report}
    runner = a.require_runpod(runner_path)
    configure_threads()
    from sklearn.model_selection import GroupKFold
    run = new_run(run_id)
    # Freeze split before any model comparison. Saved snapshots preserve meaning.
    a.write_json(run / "split.json", split)
    a.write_json(run / "validated_snapshots.json", [
        {k: v for k, v in r.items() if k != "snapshot"} for r in rows])
    meta = a.metadata_base(runner, compatibility(rows), {
        "annotation_csv": a.digest(data_path), "validated_snapshots": snapshots_hash(rows),
        "split": a.digest(run / "split.json")}, split)
    meta["dataset_report"] = report
    meta["scope"] = "reviewed synthetic profile rubric agreement; not employment outcomes"
    x = feature_matrix([r["snapshot"] for r in dev])
    y = [r["relevance_grade"] for r in dev]
    folds = list(GroupKFold(n_splits=min(5, n_groups)).split(x, y, groups))
    metrics = {"evaluation_status": "development_only", "folds": [], "candidates": {}}
    for train, test in folds:
        train_groups = sorted({groups[int(i)] for i in train})
        test_groups = sorted({groups[int(i)] for i in test})
        assert not set(train_groups) & set(test_groups)
        metrics["folds"].append({"training_groups": train_groups, "validation_groups": test_groups})
    for kind in ("baseline", "ridge", "xgboost"):
        raw_oof = [None] * len(dev)
        fold_times = []
        for train, test in folds:
            train_rows, test_rows = [dev[int(i)] for i in train], [dev[int(i)] for i in test]
            model = None
            if kind != "baseline":
                model = make_estimator(kind)
                fold_times.append(a.fit_timed(model,
                    feature_matrix([r["snapshot"] for r in train_rows]),
                    [r["relevance_grade"] for r in train_rows]))
            for index, value in zip(test, predictions(kind, model, test_rows)):
                raw_oof[int(index)] = value
        metrics["candidates"][kind] = diagnostics(dev, raw_oof)
        metrics["candidates"][kind]["fold_fit_timings"] = fold_times
        if kind != "baseline":
            model = make_estimator(kind)
            timing = a.fit_timed(model, x, y)
            meta["candidates"][kind] = save_checked(run, kind, model, timing, x)
        metrics["candidates"][kind]["counterfactuals"] = counterfactuals(kind, model, dev)
    # NDCG first, served-grade MAE next, predeclared baseline preference for ties.
    order = ("baseline", "ridge", "xgboost")
    defined = [k for k in order if metrics["candidates"][k]["mean_ndcg_at_3"] is not None]
    selected = min(defined, key=lambda k: (
        -metrics["candidates"][k]["mean_ndcg_at_3"],
        metrics["candidates"][k]["mae_served_grade"], order.index(k))) if defined else "baseline"
    selection = {"selected_candidate": selected, "ridge_l2": 1.0,
                 "selection_policy": "OOF linear-gain NDCG@3, MAE, baseline-first ties",
                 "split_sha256": a.digest(run / "split.json"),
                 "dataset_sha256": a.digest(data_path),
                 "candidate_pipeline_hashes": {k: v["pipeline_sha256"] for k, v in meta["candidates"].items()}}
    a.write_json(run / "metrics.json", metrics)
    selection["development_metrics_sha256"] = a.digest(run / "metrics.json")
    a.write_json(run / "selection.json", selection)
    meta["selection_sha256"] = a.digest(run / "selection.json")
    meta["selected_candidate"] = selected
    meta["evaluation_status"] = "development_only"
    meta["final_evaluation_scope"] = "frozen holdout" if split["holdout"] else "exploratory grouped validation only"
    a.write_json(run / "metadata.json", meta)
    a.write_json(run / "metrics.json", metrics)
    return {"run_id": run_id, "status": "development_only", "selected_candidate": selected,
            "dataset": report, "development_groups": len(split["development"]),
            "holdout_groups": len(split["holdout"]), "metrics": metrics}


def final_evaluate(data_path, run_id):
    run = a.run_path(run_id)
    meta = json.loads((run / "metadata.json").read_text())
    if meta["evaluation_status"] != "development_only":
        raise ValueError("requires a development-selected run not already evaluated")
    if a.digest(run / "selection.json") != meta["selection_sha256"]:
        raise ValueError("selection changed after freezing")
    selection = json.loads((run / "selection.json").read_text())
    if selection["dataset_sha256"] != a.digest(data_path):
        raise ValueError("dataset changed after development selection")
    if selection["split_sha256"] != a.digest(run / "split.json"):
        raise ValueError("split changed after development selection")
    if selection["development_metrics_sha256"] != a.digest(run / "metrics.json"):
        raise ValueError("development metrics changed after selection")
    rows, report = checked_rows(data_path)
    if snapshots_hash(rows) != meta["dataset_hashes"]["validated_snapshots"]:
        raise ValueError("validated snapshots changed")
    split = split_groups(rows, json.loads((run / "split.json").read_text()))
    hold = partition(rows, split, "holdout")
    if not hold:
        return {"status": "not_evaluated", "reason": "exploratory run has no frozen holdout"}
    selected = selection["selected_candidate"]
    if selected != meta["selected_candidate"]:
        raise ValueError("candidate changed after selection")
    model = None
    if selected != "baseline":
        if meta["candidates"][selected]["pipeline_sha256"] != selection["candidate_pipeline_hashes"][selected]:
            raise ValueError("pipeline changed after development selection")
        model = a.load_pipeline(run, selected, meta)
    # Exclusive persistent marker prevents accidental holdout reuse, including after a failed attempt.
    # No refit/tuning occurs here. The selected model was fit on development only.
    with (run / "holdout_attempt.json").open("x") as stream:
        json.dump({"selected_candidate": selected, "selection_sha256": meta["selection_sha256"]}, stream)
    ledger = a.ARTIFACT_ROOT / "holdout-use"
    ledger.mkdir(exist_ok=True)
    key = hashlib.sha256((selection["dataset_sha256"] + selection["split_sha256"]).encode()).hexdigest()
    with (ledger / (key + ".json")).open("x") as stream:
        json.dump({"run_id": run_id, "selected_candidate": selected,
                   "dataset_sha256": selection["dataset_sha256"], "split": split}, stream)
    metrics = json.loads((run / "metrics.json").read_text())
    metrics["holdout"] = {}
    prediction_rows = []
    for kind in dict.fromkeys(("baseline", selected)):
        raw = predictions(kind, model if kind == selected else None, hold)
        metrics["holdout"][kind] = diagnostics(hold, raw)
        metrics["holdout"][kind]["counterfactuals"] = counterfactuals(kind, model if kind == selected else None, hold)
        from .scoring import learned_score
        for row, value in zip(hold, raw):
            prediction_rows.append({"profile_id": row["profile_id"], "profile_group_id": row["profile_group_id"],
                                    "role_id": row["role_id"], "scorer_kind": kind,
                                    "relevance_grade": row["relevance_grade"], "raw_prediction": value,
                                    "served_index": learned_score(value)})
    with (run / "heldout_predictions.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(prediction_rows[0]))
        writer.writeheader()
        writer.writerows(prediction_rows)
    metrics["evaluation_status"] = meta["evaluation_status"] = "holdout_evaluated"
    a.write_json(run / "metrics.json", metrics)
    a.write_json(run / "metadata.json", meta)
    return {"run_id": run_id, "status": "holdout_evaluated", "selected_candidate": selected,
            "holdout_groups": len(split["holdout"]), "metrics": metrics["holdout"]}
