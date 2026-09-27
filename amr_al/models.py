"""Base learners. XGBoost (GPU on a T4, CPU otherwise) and logistic regression."""
import json
import os
import warnings

import numpy as np

from . import config, paths

_device = None


def device():
    """'cuda' if XGBoost can train on the GPU here, else 'cpu' (checked once)."""
    global _device
    if _device is None:
        import subprocess
        import xgboost as xgb
        _device = "cpu"
        try:
            has_gpu = subprocess.run(["nvidia-smi"], capture_output=True).returncode == 0
            if has_gpu and xgb.build_info().get("USE_CUDA"):
                m = xgb.XGBClassifier(n_estimators=2, tree_method="hist", device="cuda", verbosity=0)
                m.fit(np.random.rand(64, 8), np.arange(64) % 2)
                _device = "cuda"
        except Exception:
            pass
    return _device


def best_params(pair):
    f = os.path.join(paths.CONFIG_DIR, "best_params.json")
    params = dict(config.XGB_DEFAULT)
    if os.path.isfile(f):
        with open(f) as fh:
            params.update(json.load(fh).get(pair, {}).get("params", {}))
    return params


class XGB:
    def __init__(self, params, seed):
        import xgboost as xgb
        self.m = xgb.XGBClassifier(**params, tree_method="hist", device=device(), random_state=seed,
                                   n_jobs=-1, eval_metric="logloss", verbosity=0)

    def fit(self, X, y, w=None):
        self.m.fit(X, y, sample_weight=w)
        return self

    def predict_proba(self, X):
        if len(X) == 0:
            return np.zeros(0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")        # harmless CPU/GPU input-device notice
            return self.m.predict_proba(X)[:, 1]


class LR:
    def __init__(self, params, seed):
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        self.m = make_pipeline(StandardScaler(), LogisticRegression(
            C=params.get("C", 0.05), max_iter=3000, class_weight="balanced", random_state=seed))

    def fit(self, X, y, w=None):
        self.m.fit(X, y, logisticregression__sample_weight=w)
        return self

    def predict_proba(self, X):
        return self.m.predict_proba(X)[:, 1] if len(X) else np.zeros(0)


def make(pair, seed, kind=None, params=None):
    kind = kind or config.MODEL
    if kind == "xgb":
        return XGB(params or best_params(pair), seed)
    if kind == "lr":
        return LR(params or {}, seed)
    raise ValueError(kind)
