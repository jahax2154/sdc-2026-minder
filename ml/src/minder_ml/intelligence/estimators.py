"""Lazy optional dependencies; bounded CPU learners, no ensemble."""

import os

THREADS = 2
THREAD_ENV = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")


def configure_threads():
    for name in THREAD_ENV:
        os.environ[name] = str(THREADS)


def make_estimator(kind, ridge_l2=1.0):
    configure_threads()
    from sklearn.pipeline import Pipeline
    if kind == "ridge":
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import Ridge
        if ridge_l2 not in (0.1, 1.0, 10.0):
            raise ValueError("ridge_l2 must be one of 0.1, 1, 10")
        return Pipeline([("scaler", StandardScaler()),
                         ("estimator", Ridge(alpha=ridge_l2, solver="svd"))])
    if kind == "xgboost":
        from xgboost import XGBRegressor
        return Pipeline([("estimator", XGBRegressor(
            objective="reg:squarederror", tree_method="hist", device="cpu", n_jobs=2,
            n_estimators=100, max_depth=2, learning_rate=0.05, min_child_weight=5,
            reg_lambda=10, subsample=1.0, colsample_bytree=1.0, random_state=42))])
    raise ValueError("unknown learned scorer")
