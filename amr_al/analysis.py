"""Turn finished job results into tables and figures (saved to Drive tables/ and figures/)."""
import glob
import json
import os

import numpy as np
import pandas as pd

from . import config, paths


def load(exp):
    from . import runner
    valid = {j["id"] for j in runner.all_jobs([exp])}   # drops results of skipped jobs (e.g. saur_oxa at DRIAMS-D)
    rows, seen = [], set()
    for f in sorted(glob.glob(os.path.join(paths.RESULTS, exp, "*.json"))):
        with open(f) as fh:
            r = json.load(fh)
        j = r["job"]
        jid = j.get("id") or f
        if jid in seen or jid not in valid:  # duplicate (rare Drive sync race) or no longer part of the design
            continue
        seen.add(jid)
        for rec in r["metrics"]:
            rows.append(dict(exp=j["exp"], pair=j["pair"], site=j["site"], strategy=j["strategy"],
                             budget=str(j["budget"]), seed=j["seed"], final=rec["round"] == r["final"]["round"],
                             rounds_mode=r.get("rounds_mode"), **rec))
    return pd.DataFrame(rows)


def final_table(df):
    """Final-round metrics: mean and 95% CI over seeds."""
    f = df[df["final"]]
    cols = ["auroc", "auprc", "vme", "me", "labels_total"]
    g = f.groupby(["pair", "site", "strategy", "budget"])
    out = g[cols].mean().add_suffix("_mean")
    for c in ["auroc", "vme"]:
        out[c + "_ci95"] = g[c].agg(lambda s: 1.96 * s.std(ddof=1) / np.sqrt(len(s)) if len(s) > 1 else np.nan)
    out["op_vme_total_mean"] = df.groupby(["pair", "site", "strategy", "budget"])["op_vme_count"].sum() / g.size()
    out["seeds"] = g.size()
    return out.reset_index()


def labels_to_close_gap(df, frac=0.95, n_boot=1000, seed=0):
    """Labels needed for the final AUROC to close `frac` of the gap between
    no retraining (strategy 'none') and full retraining (strategy 'full').
    Linear interpolation between budgets; 95% CI by resampling seeds."""
    f = df[df["final"]].copy()
    out = []
    rng = np.random.default_rng(seed)
    for (pair, site), g in f.groupby(["pair", "site"]):
        piv = g.pivot_table(index="seed", columns=["strategy", "budget"], values="auroc")
        if ("none", "0") not in piv.columns or ("full", "all") not in piv.columns:
            continue
        seeds = piv.index.values
        for strat in sorted({s for s, _ in piv.columns} - {"none", "full"}):
            budgets = sorted({int(b) for s, b in piv.columns if s == strat and b not in ("all", "None")})
            if not budgets:
                continue

            def solve(rows):
                sub = piv.loc[rows]
                lo, hi = sub[("none", "0")].mean(), sub[("full", "all")].mean()
                target = lo + frac * (hi - lo)
                xs = [0] + budgets
                ys = [lo] + [sub[(strat, str(b))].mean() for b in budgets]
                for i in range(1, len(xs)):
                    if ys[i] >= target:
                        if ys[i] == ys[i - 1]:
                            return xs[i]
                        return xs[i - 1] + (target - ys[i - 1]) * (xs[i] - xs[i - 1]) / (ys[i] - ys[i - 1])
                return np.nan                    # not reached within the largest budget

            est = solve(seeds)
            boots = [solve(rng.choice(seeds, len(seeds), replace=True)) for _ in range(n_boot)]
            boots = np.array([b for b in boots if np.isfinite(b)])
            out.append(dict(pair=pair, site=site, strategy=strat, labels_needed=est,
                            ci_low=np.percentile(boots, 2.5) if len(boots) > 20 else np.nan,
                            ci_high=np.percentile(boots, 97.5) if len(boots) > 20 else np.nan,
                            reached_in_boot=len(boots) / n_boot,
                            auroc_none=piv[("none", "0")].mean(), auroc_full=piv[("full", "all")].mean()))
    return pd.DataFrame(out)


def vs_random(df, metric="auroc"):
    """Paired (by seed) Wilcoxon test of each strategy against random at each budget, Holm-corrected per pair."""
    from scipy.stats import wilcoxon
    f = df[df["final"]]
    rows = []
    for (pair, site, budget), g in f.groupby(["pair", "site", "budget"]):
        piv = g.pivot_table(index="seed", columns="strategy", values=metric)
        if "random" not in piv.columns:
            continue
        for s in piv.columns:
            if s in ("random", "none", "full"):
                continue
            d = (piv[s] - piv["random"]).dropna()
            if len(d) < 5:
                continue
            p = wilcoxon(d).pvalue if (d != 0).any() else 1.0
            rows.append(dict(pair=pair, site=site, budget=budget, strategy=s, n_seeds=len(d),
                             mean_diff=d.mean(), p=p))
    out = pd.DataFrame(rows)
    if len(out):
        out["p_holm"] = out.groupby(["pair", "site"])["p"].transform(_holm)
    return out


def _holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    m, running = len(p), 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj


def plot_curves(df, exp, metric="auroc", fname=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    f = df[df["final"]]
    keys = list(f.groupby(["pair", "site"]).groups)
    fig, axes = plt.subplots(1, len(keys), figsize=(4.2 * len(keys), 3.4), squeeze=False)
    for ax, (pair, site) in zip(axes[0], keys):
        g = f[(f.pair == pair) & (f.site == site)]
        for strat, gs in g.groupby("strategy"):
            if strat in ("none", "full", "routing_all", "ssl_only"):
                continue
            s = gs[gs.budget.str.isdigit()].copy()
            s["b"] = s.budget.astype(int)
            agg = s.groupby("b")[metric].agg(["mean", "std", "count"]).reset_index()
            ci = 1.96 * agg["std"] / np.sqrt(agg["count"])
            ax.plot(agg.b, agg["mean"], marker="o", ms=3, lw=1.5, label=strat)
            ax.fill_between(agg.b, agg["mean"] - ci, agg["mean"] + ci, alpha=0.15)
        for strat, ls in (("none", ":"), ("full", "--"), ("ssl_only", "-."), ("routing_all", (0, (1, 3)))):
            v = g[g.strategy == strat][metric]
            if len(v):
                ax.axhline(v.mean(), ls=ls, color="k", lw=1, label=strat)
        ax.set_xscale("log")
        ticks = sorted({int(b) for b in g.budget if str(b).isdigit() and int(b) > 0})
        if ticks:
            from matplotlib.ticker import NullFormatter
            ax.set_xticks(ticks)
            ax.set_xticklabels([str(t) for t in ticks], fontsize=7)
            ax.xaxis.set_minor_formatter(NullFormatter())
        if metric in ("auroc", "auprc", "vme", "me"):
            ax.set_ylim(0, 1.02)
        ax.set_title(f"{pair} ({site})", fontsize=9)
        ax.set_xlabel("lab tests bought (total)")
        ax.set_ylabel(metric.upper())
        ax.spines[["top", "right"]].set_visible(False)
    axes[0][0].legend(fontsize=7, frameon=False)
    fig.suptitle(exp, fontsize=10)
    fig.tight_layout()
    os.makedirs(paths.FIGURES, exist_ok=True)
    out = os.path.join(paths.FIGURES, fname or f"{exp}_{metric}.png")
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


BASELINE_EXP = "E1_temporal"


def report(exp):
    """Everything for one experiment: tables to tables/, figures to figures/.

    E2 and E3 have no bounds or plain random of their own; the matching E1 runs
    (none, full, random, uncertainty, hybrid) are added so they can be compared.
    """
    df = load(exp)
    if df.empty:
        print(f"{exp}: no results yet")
        return {}
    n_own = int(df["final"].sum())
    if config.EXPERIMENTS[exp]["setting"] == "temporal" and exp != BASELINE_EXP:
        base = load(BASELINE_EXP)
        if not base.empty:
            base = base[base.strategy.isin(["none", "full", "random", "uncertainty", "hybrid"])
                        & base.pair.isin(df.pair.unique()) & base.seed.isin(df.seed.unique())]
            df = pd.concat([df, base], ignore_index=True)
    os.makedirs(paths.TABLES, exist_ok=True)
    out = {"final": final_table(df)}
    out["final"].to_csv(os.path.join(paths.TABLES, f"{exp}_final.csv"), index=False)
    if {"none", "full"} <= set(df.strategy):
        out["gap"] = labels_to_close_gap(df)
        out["gap"].to_csv(os.path.join(paths.TABLES, f"{exp}_labels_to_close_95pct_gap.csv"), index=False)
    out["tests"] = vs_random(df)
    out["tests"].to_csv(os.path.join(paths.TABLES, f"{exp}_vs_random.csv"), index=False)
    out["figs"] = [plot_curves(df, exp, m) for m in ("auroc", "vme")]
    modes = df["rounds_mode"].dropna().unique()
    print(f"{exp}: {n_own} finished jobs; arrival batches = {list(modes)}")
    return out
