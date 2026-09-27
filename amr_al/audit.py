"""Before the experiments: what is in the data, does the premise hold, and tuned settings."""
import itertools
import json
import os
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

from . import config, data, metrics, models, paths


def summarize():
    """Counts per site/year, and per pair: labelled isolates and % resistant."""
    rows, pair_rows = [], []
    for site, years in data.available().items():
        for year in years:
            X, meta = data.load_site_year(site, year)
            dates = meta["acquisition_date"] if "acquisition_date" in meta.columns else None
            rows.append(dict(site=site, year=year, spectra=len(meta),
                             species=meta["species"].nunique(),
                             with_dates=float(pd.to_datetime(dates, errors="coerce").notna().mean()) if dates is not None else 0.0))
            for pair, (sp, ab) in config.PAIRS.items():
                if ab not in meta.columns:
                    pair_rows.append(dict(pair=pair, site=site, year=year, n=0, n_R=0, pct_R=np.nan, note=f"no {ab} column"))
                    continue
                y = data.encode(meta.loc[meta["species"] == sp, ab]).dropna()
                pair_rows.append(dict(pair=pair, site=site, year=year, n=len(y), n_R=int(y.sum()),
                                      pct_R=round(100 * y.mean(), 1) if len(y) else np.nan, note=""))
    a, b = pd.DataFrame(rows), pd.DataFrame(pair_rows)
    os.makedirs(paths.TABLES, exist_ok=True)
    a.to_csv(os.path.join(paths.TABLES, "audit_sites.csv"), index=False)
    b.to_csv(os.path.join(paths.TABLES, "audit_pairs.csv"), index=False)
    return a, b


def premise_check(pair, seed=0):
    """Does a 2015-16 model decay, and how much does full retraining recover?

    no_retrain: train 2015-16 -> test on each 2017 batch and on 2018
    retrain:    train 2015-17 -> test on 2018 (upper bound of what labels can buy)
    in_period:  5-fold CV AUROC inside 2015-16 (how good the model is on its own period)
    """
    sp = data.temporal_split(pair, seed)
    m = models.make(pair, seed).fit(sp["X_tr"], sp["y_tr"])
    t = metrics.threshold_for_sensitivity(sp["y_val"], m.predict_proba(sp["X_val"]), config.TARGET_SENSITIVITY)
    rows = []
    for r in range(sp["n_rounds"]):
        idx = sp["round_pool"] == r
        rows.append(dict(model="no_retrain", eval_on=f"{config.POOL_YEAR} batch {r+1}",
                         **metrics.evaluate(sp["y_pool"][idx], m.predict_proba(sp["X_pool"][idx]), t)))
    rows.append(dict(model="no_retrain", eval_on=config.TEST_YEAR,
                     **metrics.evaluate(sp["y_te"], m.predict_proba(sp["X_te"]), t)))
    X_full = np.concatenate([sp["X_tr"], sp["X_pool"]])
    y_full = np.concatenate([sp["y_tr"], sp["y_pool"]])
    m2 = models.make(pair, seed).fit(X_full, y_full)
    t2 = metrics.threshold_for_sensitivity(sp["y_val"], m2.predict_proba(sp["X_val"]), config.TARGET_SENSITIVITY)
    rows.append(dict(model="retrain_with_all_2017", eval_on=config.TEST_YEAR,
                     **metrics.evaluate(sp["y_te"], m2.predict_proba(sp["X_te"]), t2)))
    X_in = np.concatenate([sp["X_tr"], sp["X_val"]])
    y_in = np.concatenate([sp["y_tr"], sp["y_val"]])
    aucs = []
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X_in, y_in):
        mm = models.make(pair, seed).fit(X_in[tr], y_in[tr])
        aucs.append(metrics.evaluate(y_in[te], mm.predict_proba(X_in[te]), 0.5)["auroc"])
    rows.append(dict(model="in_period_5fold_cv", eval_on="2015-16", auroc=float(np.mean(aucs))))
    df = pd.DataFrame(rows)
    df.insert(0, "pair", pair)
    df["rounds_mode"] = sp["rounds_mode"]
    return df


def tune(pair, grid=None, folds=3, seed=0, max_combos=None):
    """Grid search on the training years only (never the pool or test years)."""
    grid = grid or config.TUNING_GRID
    sp = data.temporal_split(pair, seed)
    X = np.concatenate([sp["X_tr"], sp["X_val"]])
    y = np.concatenate([sp["y_tr"], sp["y_val"]])
    keys = sorted(grid)
    combos = [dict(zip(keys, v)) for v in itertools.product(*[grid[k] for k in keys])]
    if max_combos:
        combos = combos[:max_combos]
    results = []
    for c in combos:
        params = dict(config.XGB_DEFAULT, **c)
        t0, aucs = time.time(), []
        for tr, te in StratifiedKFold(folds, shuffle=True, random_state=seed).split(X, y):
            m = models.make(pair, seed, kind="xgb", params=params).fit(X[tr], y[tr])
            aucs.append(metrics.evaluate(y[te], m.predict_proba(X[te]), 0.5)["auroc"])
        results.append(dict(params=c, auroc=float(np.mean(aucs)), sd=float(np.std(aucs)), sec=time.time() - t0))
        print(f"  {pair} {c}  AUROC {results[-1]['auroc']:.4f}  ({results[-1]['sec']:.0f}s)", flush=True)
    best = max(results, key=lambda r: r["auroc"])
    f = os.path.join(paths.CONFIG_DIR, "best_params.json")
    allp = {}
    if os.path.isfile(f):
        with open(f) as fh:
            allp = json.load(fh)
    allp[pair] = dict(params=dict(config.XGB_DEFAULT, **best["params"]), cv_auroc=best["auroc"],
                      tuned=time.strftime("%Y-%m-%d %H:%M"), grid=grid)
    os.makedirs(paths.CONFIG_DIR, exist_ok=True)
    with open(f, "w") as fh:
        json.dump(allp, fh, indent=1)
    return pd.DataFrame([dict(pair=pair, **r["params"], auroc=r["auroc"], sd=r["sd"], sec=r["sec"]) for r in results])


def benchmark(n=8000, d=None, n_estimators=300):
    """Time one XGBoost fit on spectrum-sized random data (the 'T4 test')."""
    d = d or config.N_BINS
    rng = np.random.default_rng(0)
    X = rng.gamma(1.0, 1.0, size=(n, d)).astype(np.float32)
    y = (X[:, :50].sum(1) + rng.normal(0, 5, n) > 50).astype(int)
    out = {}
    for dev in (["cuda", "cpu"] if models.device() == "cuda" else ["cpu"]):
        import xgboost as xgb
        m = xgb.XGBClassifier(**dict(config.XGB_DEFAULT, n_estimators=n_estimators), tree_method="hist",
                              device=dev, n_jobs=-1, verbosity=0)
        t0 = time.time()
        m.fit(X, y)
        out[dev] = round(time.time() - t0, 1)
        print(f"  XGBoost fit on {dev}: {out[dev]} s  ({n} x {d}, {n_estimators} trees)", flush=True)
    return out
