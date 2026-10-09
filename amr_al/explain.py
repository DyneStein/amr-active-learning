"""Which parts of the spectrum each model actually uses, and whether the models
built by active learning use the same parts as the ones built by ordinary retraining.

Attributions are exact TreeSHAP values, computed by XGBoost itself
(`pred_contribs=True`), so no extra package is needed. For one isolate the SHAP
value of a bin is that bin's share of the distance between the model's output for
that isolate and the model's average output; the sign says which way it pushed.
Averaging the absolute value over the test isolates gives how much the model leans
on that bin overall.

Bins: 6000 bins, 2000 to 20000 Da, 3 Da wide (config.SPECTRA_TYPE), so bin i covers
2000 + 3i to 2003 + 3i Da.
"""
import json
import os

import numpy as np

from . import config, paths, runner

# model conditions compared for every pair
CONDITIONS = [
    ("no retraining", "none", 0),
    ("retrain on everything", "full", "all"),
    ("random 400", "random", 400),
    ("uncertainty 400", "uncertainty", 400),
    ("random 800", "random", 800),
    ("uncertainty 800", "uncertainty", 800),
]
TOP_K = 20                 # size of the "prominent features" list the comparison uses


def mz_centre(i):
    """Centre mass of bin i, in daltons."""
    return 2001.5 + 3.0 * np.asarray(i)


def bin_label(i):
    lo = 2000 + 3 * int(i)
    return f"{lo}-{lo + 3} Da"


def _job(exp, pair, strategy, budget, seed, site="DRIAMS-A"):
    return dict(exp=exp, setting="temporal", pair=pair, site=site, seed=seed,
                strategy=strategy, budget=budget,
                id=f"{exp}__{pair}__{site}__{strategy}__b{budget}__s{seed}")


def profile(j, max_test=2000, log=print):
    """Mean |SHAP| and mean signed SHAP per bin for the final model of one job."""
    res = runner.run_job(j, log=log, want_model=True)
    m, X_te = res["model_object"], res["X_te"]
    rng = np.random.default_rng(0)
    rows = np.arange(len(X_te))
    if len(rows) > max_test:
        rows = np.sort(rng.choice(rows, max_test, replace=False))
    import xgboost as xgb
    booster = m.m.get_booster()
    booster.set_param({"device": "cpu"})                   # contributions are a CPU path
    sv = booster.predict(xgb.DMatrix(np.asarray(X_te[rows], np.float32)), pred_contribs=True)
    sv = np.asarray(sv, np.float64)[:, :config.N_BINS]     # last column is the bias term
    return dict(mean_abs=np.abs(sv).mean(0), mean_signed=sv.mean(0),
                auroc=res["final"].get("auroc"), vme=res["final"].get("vme"),
                labels_total=res["final"].get("labels_total", 0), n_explained=int(len(rows)))


def run(pairs=None, seeds=(0, 1, 2, 3, 4), conditions=None, exp="E1_temporal",
        site="DRIAMS-A", out_name="shap_profiles.npz", log=print):
    """Compute a SHAP profile for every pair / condition / seed and save them.

    Saved to tables/shap_profiles.npz as one array per (pair, condition), averaged over seeds.
    Re-running skips what is already in the file, so it can be stopped and resumed.
    """
    pairs = list(pairs or config.PAIRS)
    conditions = conditions or CONDITIONS
    os.makedirs(paths.TABLES, exist_ok=True)
    out_path = os.path.join(paths.TABLES, out_name)
    store = dict(np.load(out_path, allow_pickle=True)) if os.path.isfile(out_path) else {}
    meta = json.loads(str(store.pop("meta_json", "{}"))) if "meta_json" in store else {}
    for pair in pairs:
        for label, strategy, budget in conditions:
            key = f"{pair}|{label}"
            if key + "|abs" in store:
                log(f"skip {key} (already done)")
                continue
            abs_acc, sgn_acc, info = [], [], []
            for seed in seeds:
                j = _job(exp, pair, strategy, budget, seed, site)
                log(f"SHAP {key} seed {seed}")
                pr = profile(j, log=lambda *_: None)
                abs_acc.append(pr["mean_abs"])
                sgn_acc.append(pr["mean_signed"])
                info.append(dict(seed=seed, auroc=pr["auroc"], vme=pr["vme"],
                                 labels_total=pr["labels_total"]))
            store[key + "|abs"] = np.mean(abs_acc, 0)
            store[key + "|sgn"] = np.mean(sgn_acc, 0)
            store[key + "|abs_per_seed"] = np.array(abs_acc)
            meta[key] = dict(pair=pair, condition=label, strategy=strategy, budget=budget,
                             seeds=list(seeds), runs=info)
            np.savez_compressed(out_path, meta_json=json.dumps(meta), **store)
            log(f"saved {key}")
    return out_path


# ------------------------------------------------------------------ comparison
def top_bins(v, k=TOP_K):
    return np.argsort(v)[::-1][:k]


def jaccard(a, b):
    sa, sb = set(a.tolist()), set(b.tolist())
    return len(sa & sb) / len(sa | sb) if (sa | sb) else float("nan")


def compare(out_name="shap_profiles.npz", k=TOP_K):
    """For every pair, how similar the feature rankings of the conditions are.

    overlap_topk : share of the top-k bins the two models have in common (Jaccard)
    spearman     : rank correlation over all 6000 bins
    """
    import itertools

    import pandas as pd
    from scipy.stats import spearmanr
    z = np.load(os.path.join(paths.TABLES, out_name), allow_pickle=True)
    meta = json.loads(str(z["meta_json"]))
    rows = []
    pairs = sorted({m["pair"] for m in meta.values()})
    for pair in pairs:
        conds = [m["condition"] for key, m in meta.items() if m["pair"] == pair]
        for a, b in itertools.combinations(conds, 2):
            va, vb = z[f"{pair}|{a}|abs"], z[f"{pair}|{b}|abs"]
            rows.append(dict(pair=pair, model_a=a, model_b=b,
                             overlap_topk=jaccard(top_bins(va, k), top_bins(vb, k)),
                             spearman=float(spearmanr(va, vb).statistic),
                             top1_a=bin_label(top_bins(va, 1)[0]), top1_b=bin_label(top_bins(vb, 1)[0])))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(paths.TABLES, "shap_agreement.csv"), index=False)
    return out


def top_table(out_name="shap_profiles.npz", k=TOP_K):
    """The top-k bins of every pair / condition, as a table."""
    import pandas as pd
    z = np.load(os.path.join(paths.TABLES, out_name), allow_pickle=True)
    meta = json.loads(str(z["meta_json"]))
    rows = []
    for key, m in meta.items():
        v = z[key + "|abs"]
        sg = z[key + "|sgn"]
        for rank, i in enumerate(top_bins(v, k), 1):
            rows.append(dict(pair=m["pair"], condition=m["condition"], rank=rank, bin=int(i),
                             mz_centre=float(mz_centre(i)), mz_range=bin_label(i),
                             mean_abs_shap=float(v[i]),
                             pushes_towards="resistant" if sg[i] > 0 else "susceptible"))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(paths.TABLES, "shap_top_bins.csv"), index=False)
    return out
