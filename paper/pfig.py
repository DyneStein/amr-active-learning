# Figures for the AMR active-learning paper. Writes SVGs into fig/.
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get("AMR_CSV_DIR", os.path.join(HERE, "_data")) + "/"   # tables written by paper_data.py
OUT = os.path.join(HERE, "fig") + "/"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 7.6, "axes.labelsize": 7.8, "axes.titlesize": 8.2, "legend.fontsize": 7.2,
    "xtick.labelsize": 7.2, "ytick.labelsize": 7.2, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none",
    "axes.grid": True, "grid.color": "#e8e8e8", "grid.linewidth": 0.45, "figure.dpi": 110,
    "axes.facecolor": "white", "figure.facecolor": "white", "savefig.facecolor": "white",
})

# validated categorical hues (dataviz validator, light surface, all-pairs PASS)
C = {"uncertainty": "#2a78d6", "diversity": "#eb6834", "hybrid": "#1baf7a", "routing": "#4a3aa7",
     "random": "#52514e", "none": "#a8a7a1", "full": "#0b0b0b"}
VME, ME = "#8f2a2a", "#8a6a1a"            # dark status tones for print
INK, INK2, MUT = "#1a1a1a", "#444444", "#777777"
PAIR = {"ecoli_cro": "E. coli", "kpneu_cro": "K. pneumoniae", "saur_oxa": "S. aureus"}
PAIRFULL = {"ecoli_cro": "E. coli with ceftriaxone", "kpneu_cro": "K. pneumoniae with ceftriaxone", "saur_oxa": "S. aureus with oxacillin"}
DASH = {"random": (4, 2), "none": (1.4, 1.6), "full": (5, 2)}

A = pd.read_csv(S + "all_results.csv")
A["budget"] = A.budget.astype(str)
RND = pd.read_csv(S + "e1_rounds.csv")
RND2 = pd.read_csv(S + "e2_rounds.csv")
RND3 = pd.read_csv(S + "e3_rounds.csv")


def spread(vals, gap):
    """Nudge label positions apart, keeping order."""
    o = np.argsort(vals); v = np.array(vals, float)[o]
    for i in range(1, len(v)):
        if v[i] - v[i - 1] < gap: v[i] = v[i - 1] + gap
    out = np.empty_like(v); out[o] = v; return out


def save(fig, name):
    fig.savefig(OUT + name + ".svg", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print("wrote", name)


def style(ax, xlab="", ylab="", title=""):
    ax.set_axisbelow(True)
    ax.grid(axis="x", visible=False)
    if xlab: ax.set_xlabel(xlab)
    if ylab: ax.set_ylabel(ylab)
    if title: ax.set_title(title, color=INK, pad=3, loc="left", fontweight="bold", fontsize=8.4, style="italic")
    ax.tick_params(colors=INK2)
    for s in ("left", "bottom"): ax.spines[s].set_color("#bbbbbb")


def ci(x):
    x = np.asarray(x, float)
    return 1.96 * x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0


# ---------------------------------------------------------------- F3 drift premise
def f_drift():
    r = RND[(RND.strategy == "none") & (RND["round"] == 0)].groupby("pair").auroc.mean()     # 2018, frozen model
    full = A[(A.exp == "E1_temporal") & (A.strategy == "full")].groupby("pair").auroc.agg(["mean", ci])
    fig, ax = plt.subplots(figsize=(3.5, 1.85))
    pairs = list(PAIR)
    x = np.arange(3)
    w = 0.34
    b1 = ax.bar(x - w / 2, [r[p] for p in pairs], w, color=C["none"], label="no retraining", zorder=3)
    b2 = ax.bar(x + w / 2, [full.loc[p, "mean"] for p in pairs], w, color=C["full"],
                yerr=[full.loc[p, "ci"] for p in pairs], error_kw=dict(lw=0.7, ecolor=INK2, capsize=2),
                label="retrained on all 2017 labels", zorder=3)
    for bb, p in zip(b1, pairs):
        ax.text(bb.get_x() + bb.get_width() / 2, bb.get_height() + .004, f"{r[p]:.3f}", ha="center", va="bottom", fontsize=6.3, color=INK2)
    for bb, p in zip(b2, pairs):
        d = full.loc[p, "mean"] - r[p]
        ax.text(bb.get_x() + bb.get_width() / 2, bb.get_height() + .012, f"+{d:.3f}", ha="center", va="bottom", fontsize=6.5, color=INK, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(["E. coli\nCRO", "K. pneumoniae\nCRO", "S. aureus\nOXA"])
    ax.set_ylim(0.70, 0.95); ax.set_yticks(np.arange(0.70, 0.91, 0.05))
    style(ax, ylab="AUROC on 2018 isolates")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(-0.02, 1.04), handlelength=1.2, labelspacing=0.25, borderpad=0.1)
    save(fig, "f3_drift")


# ---------------------------------------------------------------- F4 learning curves
def f_curves():
    e1 = A[A.exp == "E1_temporal"]
    fig, axes = plt.subplots(1, 3, figsize=(5.25, 1.72), sharey=False, gridspec_kw=dict(wspace=0.34))
    for ax, p in zip(axes, PAIR):
        g = e1[e1.pair == p]
        lo = g[g.strategy == "none"].auroc.mean()
        hi = g[g.strategy == "full"].auroc.mean()
        nfull = g[g.strategy == "full"].labels_total.mean()
        span = hi - lo
        ax.axhline(lo, color=C["none"], lw=1.1, ls=(0, DASH["none"]), zorder=2)
        ax.axhline(hi, color=C["full"], lw=1.1, ls=(0, DASH["full"]), zorder=2)
        ax.text(36, lo - span * 0.015, "no retraining", color=MUT, fontsize=6.1, va="top")
        ax.text(36, hi + span * 0.015, f"retrain on all {nfull:.0f} labels", color=INK, fontsize=6.1, va="bottom")
        ends = []
        for s in ["random", "uncertainty", "diversity", "hybrid"]:
            d = g[g.strategy == s].groupby("budget").auroc.agg(["mean", ci])
            d.index = d.index.astype(int); d = d.sort_index()
            kw = dict(color=C[s], lw=1.6, zorder=5, solid_capstyle="round")
            if s == "random": kw.update(ls=(0, DASH["random"]), zorder=6)
            ax.plot(d.index, d["mean"], marker="o", ms=3.1, mew=0, **kw)
            ax.fill_between(d.index, d["mean"] - d["ci"], d["mean"] + d["ci"], color=C[s], alpha=0.12, lw=0, zorder=3)
            ends.append((d["mean"].iloc[-1], s))
        span = max(hi, max(e[0] for e in ends)) - min(lo, min(e[0] for e in ends))
        _ = span
        ys = spread([e[0] for e in ends], span * 0.085)
        for (y0, s), y in zip(ends, ys):
            ax.plot([800, 980], [y0, y], color=C[s], lw=0.6, zorder=4)
            ax.text(1030, y, s, color=C[s], fontsize=6.3, va="center",
                    fontweight="bold" if s == "random" else "normal")
        ax.set_xscale("log"); ax.set_xticks([40, 100, 200, 400, 800])
        ax.set_xticklabels(["40", "", "200", "", "800"])
        ax.set_xlim(34, 2600)
        ax.set_ylim(min(lo, min(e[0] for e in ends)) - span * 0.12, max(hi, max(e[0] for e in ends)) + span * 0.17)
        style(ax, xlab="labels bought during 2017" if p == "kpneu_cro" else "", ylab="AUROC on 2018" if p == "ecoli_cro" else "", title=PAIR[p])
    save(fig, "f4_curves")


# ---------------------------------------------------------------- F5 forest plot
def f_forest():
    e1 = A[A.exp == "E1_temporal"]
    rows = []
    for p in PAIR:
        for b in ["40", "100", "200", "400", "800"]:
            ref = e1[(e1.pair == p) & (e1.strategy == "random") & (e1.budget == b)].set_index("seed").auroc
            for s in ["uncertainty", "diversity", "hybrid"]:
                x = e1[(e1.pair == p) & (e1.strategy == s) & (e1.budget == b)].set_index("seed").auroc
                d = (x - ref).dropna()
                rows.append(dict(pair=p, budget=int(b), strategy=s, diff=d.mean(), ci=ci(d)))
    R = pd.DataFrame(rows)
    fig, axes = plt.subplots(1, 3, figsize=(5.25, 2.05), sharex=True, gridspec_kw=dict(wspace=0.26))
    for ax, p in zip(axes, PAIR):
        g = R[R.pair == p]
        y = 0; ticks, labs = [], []
        for b in [40, 100, 200, 400, 800]:
            for s in ["uncertainty", "diversity", "hybrid"]:
                r = g[(g.budget == b) & (g.strategy == s)].iloc[0]
                ax.errorbar(r["diff"], y, xerr=r["ci"], fmt="o", ms=3.4, mew=0, color=C[s],
                            ecolor=C[s], elinewidth=1.1, capsize=1.8, zorder=5)
                y -= 1
            ticks.append(y + 2); labs.append(f"{b}")
            y -= 0.6
        ax.axvline(0, color=INK, lw=0.9, zorder=4)
        ax.axvspan(-0.005, 0.005, color="#e6e5e1", alpha=0.75, lw=0, zorder=1)
        ax.set_yticks(ticks); ax.set_yticklabels(labs)
        ax.set_xlim(-0.045, 0.045); ax.set_xticks([-0.04, -0.02, 0, 0.02, 0.04])
        style(ax, xlab="AUROC difference vs random" if p == "kpneu_cro" else "",
              ylab="labels bought" if p == "ecoli_cro" else "", title=PAIR[p])
        ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
    h = [Line2D([], [], color=C[s], marker="o", ms=3.4, lw=1.1, label=s) for s in ["uncertainty", "diversity", "hybrid"]]
    h.append(plt.Rectangle((0, 0), 1, 1, color="#e6e5e1", label="±0.005 (negligible)"))
    axes[0].legend(handles=h, frameon=False, loc="lower left", bbox_to_anchor=(-0.02, -0.03), handlelength=1.2, labelspacing=0.3, borderpad=0.2)
    save(fig, "f5_forest")


# ---------------------------------------------------------------- F6 safety: errors among untested
def f_safety():
    e1 = A[A.exp == "E1_temporal"]
    fig, axes = plt.subplots(1, 3, figsize=(5.25, 1.82), sharey=False, gridspec_kw=dict(wspace=0.32))
    stars = {("ecoli_cro", "800"): "*", ("kpneu_cro", "800"): "*", ("saur_oxa", "800"): "*"}
    for ax, p in zip(axes, PAIR):
        g = e1[e1.pair == p]
        bs = ["100", "200", "400", "800"]
        x = np.arange(len(bs)); w = 0.38
        for k, s in enumerate(["random", "uncertainty"]):
            m = [g[(g.strategy == s) & (g.budget == b)].opvme.mean() for b in bs]
            e = [ci(g[(g.strategy == s) & (g.budget == b)].opvme) for b in bs]
            ax.bar(x + (k - 0.5) * w, m, w, color=C[s], yerr=e, zorder=3,
                   error_kw=dict(lw=0.7, ecolor=INK2 if s == "uncertainty" else "#8a8982", capsize=2),
                   label=s, hatch="" if s == "uncertainty" else "///", edgecolor="white", linewidth=0.6)
        top = 0
        for i, b in enumerate(bs):
            gr = g[(g.strategy == "random") & (g.budget == b)].opvme
            gu = g[(g.strategy == "uncertainty") & (g.budget == b)].opvme
            pct = 100 * (gu.mean() / gr.mean() - 1)
            h = max(gr.mean() + ci(gr), gu.mean() + ci(gu))
            top = max(top, h)
            sig = (p, b) in stars
            ax.text(i, h * 1.04, f"{pct:+.0f}%" + ("*" if sig else ""), ha="center", va="bottom", fontsize=6.4,
                    color=INK if sig else INK2, fontweight="bold" if sig else "normal")
        ax.set_xticks(x); ax.set_xticklabels(bs)
        ax.set_ylim(0, top * 1.24)
        style(ax, xlab="labels bought" if p == "kpneu_cro" else "", ylab="missed resistances during 2017" if p == "ecoli_cro" else "", title=PAIR[p])
    h = [plt.Rectangle((0, 0), 1, 1, facecolor=C["random"], hatch="///", edgecolor="white", lw=0.6, label="random"),
         plt.Rectangle((0, 0), 1, 1, facecolor=C["uncertainty"], label="uncertainty")]
    fig.legend(handles=h, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.54, 1.10),
               handlelength=1.3, columnspacing=1.6, fontsize=7.4)
    save(fig, "f6_safety")


# ---------------------------------------------------------------- F7 calibration failure
def f_calib():
    e1 = A[A.exp == "E1_temporal"]
    fig, axes = plt.subplots(1, 2, figsize=(5.25, 1.80), gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax = axes[0]
    pairs = list(PAIR)
    x = np.arange(3)
    vals = [e1[(e1.pair == p) & (e1.strategy == "none")].sens.mean() for p in pairs]
    errs = [ci(e1[(e1.pair == p) & (e1.strategy == "none")].sens) for p in pairs]
    bars = ax.bar(x, vals, 0.46, color=C["none"], yerr=errs, error_kw=dict(lw=0.7, ecolor=INK2, capsize=2), zorder=3)
    ax.axhline(0.90, color=VME, lw=1.3, ls=(0, (4, 2)), zorder=4)
    ax.text(2.42, 0.903, "promised 0.90", color=VME, fontsize=6.4, ha="right", va="bottom", fontweight="bold")
    for b, v, e in zip(bars, vals, errs):
        cx = b.get_x() + b.get_width() / 2
        ax.text(cx - 0.055, (v + 0.90) / 2, f"{0.90 - v:+.2f}".replace("+", "−"), ha="right", va="center",
                fontsize=6.5, color=VME, fontweight="bold")
        ax.text(cx, 0.615, f"{v:.2f}", ha="center", va="bottom", fontsize=6.6, color="white", fontweight="bold")
        ax.annotate("", xy=(cx, 0.90), xytext=(cx, v + e + 0.006),
                    arrowprops=dict(arrowstyle="->", color=VME, lw=0.9))
    ax.set_xticks(x); ax.set_xticklabels(["E. coli", "K. pneumoniae", "S. aureus"])
    ax.set_ylim(0.6, 0.97)
    style(ax, ylab="sensitivity to resistance on 2018", title="a  The threshold no longer keeps its promise")

    ax = axes[1]
    r3 = RND3[(RND3.strategy == "routing_all") & (RND3["round"] > 0)]
    agg = r3.groupby(["pair", "seed"]).agg(vme=("op_vme_count", "sum"), untestedR=("op_R", "sum"),
                                           boughtR=("R_bought_total", "max")).reset_index()
    agg["mis"] = agg.vme / (agg.untestedR + agg.boughtR)
    mis = agg.groupby("pair").mis.mean(); mis_ci = agg.groupby("pair").mis.apply(ci)
    bars = ax.bar(np.arange(3), [mis[p] for p in pairs], 0.46, color=C["routing"], zorder=3,
                  yerr=[mis_ci[p] for p in pairs], error_kw=dict(lw=0.7, ecolor=INK2, capsize=2))
    ax.axhline(0.10, color=VME, lw=1.3, ls=(0, (4, 2)), zorder=4)
    ax.text(2.42, 0.112, "promised ≤ 0.10", color=VME, fontsize=6.4, ha="right", va="bottom", fontweight="bold")
    for b, p in zip(bars, pairs):
        ax.text(b.get_x() + b.get_width() / 2, mis[p] + mis_ci[p] + 0.005, f"{mis[p]:.3f}", ha="center", va="bottom", fontsize=6.6, color=INK)
    ax.set_xticks(np.arange(3)); ax.set_xticklabels(["E. coli", "K. pneumoniae", "S. aureus"])
    ax.set_ylim(0, 0.25)
    style(ax, ylab="resistant isolates given a confident “S”", title="b  The conformal guarantee breaks too")
    save(fig, "f7_calib")


# ---------------------------------------------------------------- F8 recalibration tradeoff
def f_recal():
    e1, e5 = A[A.exp == "E1_temporal"], A[A.exp == "E5_recal"]
    m = e5.merge(e1, on=["pair", "strategy", "budget", "seed"], suffixes=("_5", "_1"))
    m = m[m.strategy.isin(["random", "uncertainty"])]
    fig, ax = plt.subplots(figsize=(3.6, 2.5))
    for p, mk in zip(PAIR, ["o", "s", "^"]):
        for s in ["random", "uncertainty"]:
            g = m[(m.pair == p) & (m.strategy == s)]
            if not len(g): continue
            x1, y1 = g.me_1.mean(), g.sens_1.mean()
            x5, y5 = g.me_5.mean(), g.sens_5.mean()
            ax.annotate("", xy=(x5, y5), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="-|>", color=C[s], lw=1.1, alpha=0.85,
                                        shrinkA=2.5, shrinkB=2.5))
            ax.plot([x1], [y1], marker=mk, ms=4.6, color="white", mec=C[s], mew=1.1, zorder=5)
            ax.plot([x5], [y5], marker=mk, ms=4.6, color=C[s], mew=0, zorder=5)
    ax.axhline(0.90, color=VME, lw=1.2, ls=(0, (4, 2)), zorder=2)
    ax.text(0.655, 0.905, "target sensitivity 0.90", color=VME, fontsize=6.3, ha="right", va="bottom", fontweight="bold")
    style(ax, xlab="major error rate on 2018  (susceptible called resistant)", ylab="sensitivity to resistance on 2018")
    h = [Line2D([], [], marker=mk, ms=4.6, lw=0, color=MUT, label=PAIR[p]) for p, mk in zip(PAIR, ["o", "s", "^"])]
    h += [Line2D([], [], marker="o", ms=4.6, lw=0, color="white", mec=INK2, mew=1.1, label="old calibration (E1)"),
          Line2D([], [], marker="o", ms=4.6, lw=0, color=INK2, label="recalibrated (E5)"),
          Line2D([], [], lw=1.6, color=C["random"], label="random selection"),
          Line2D([], [], lw=1.6, color=C["uncertainty"], label="uncertainty selection")]
    ax.legend(handles=h, frameon=False, loc="lower right", handlelength=1.0, labelspacing=0.3, borderpad=0.2)
    ax.set_ylim(0.5, 1.0)
    save(fig, "f8_recal")


# ---------------------------------------------------------------- F9 transfer
def f_site():
    e4 = A[A.exp == "E4_crosssite"]
    fig, axes = plt.subplots(1, 3, figsize=(5.25, 1.72), gridspec_kw=dict(wspace=0.30))
    for ax, p in zip(axes, PAIR):
        g = e4[e4.pair == p]
        for site, col in zip(["DRIAMS-B", "DRIAMS-C", "DRIAMS-D"], ["#2a78d6", "#eb6834", "#4a3aa7"]):
            s = g[g.site == site]
            if not len(s): continue
            lo = s[s.strategy == "none"].auroc.mean()
            d = s[s.strategy == "random"].groupby("budget").auroc.agg(["mean", ci])
            d.index = d.index.astype(int); d = d.sort_index()
            ax.plot([0] + list(d.index), [lo] + list(d["mean"]), marker="o", ms=3.0, mew=0, lw=1.5, color=col, zorder=5)
            ax.fill_between(d.index, d["mean"] - d["ci"], d["mean"] + d["ci"], color=col, alpha=0.13, lw=0)
            ax.plot([0], [lo], marker="o", ms=5.2, color="white", mec=col, mew=1.3, zorder=6)
        ax.axhline(0.5, color=MUT, lw=0.8, ls=(0, (1.4, 1.6)))
        ax.text(5, 0.508, "chance", color=MUT, fontsize=6.0, va="bottom")
        ax.set_xscale("symlog", linthresh=25); ax.set_xticks([0, 25, 50, 100, 200, 400])
        ax.set_xticklabels(["0", "25", "", "100", "", "400"])
        ax.set_xlim(-3, 500); ax.set_ylim(0.44, 0.94)
        style(ax, xlab="local labels bought" if p == "kpneu_cro" else "",
              ylab="AUROC at that hospital" if p == "ecoli_cro" else "", title=PAIR[p])
        if p == "ecoli_cro":
            hh = [Line2D([], [], color=c, lw=1.6, marker="o", ms=3.0, label=f"hospital {n}")
                  for n, c in zip("BCD", ["#2a78d6", "#eb6834", "#4a3aa7"])]
            hh.append(Line2D([], [], color=MUT, lw=0, marker="o", ms=5.2, mfc="white", mec=MUT, mew=1.3, label="no local labels"))
            ax.legend(handles=hh, frameon=False, loc="lower right", handlelength=1.2, labelspacing=0.25, borderpad=0.2)
    save(fig, "f9_site")


# ---------------------------------------------------------------- F10 error tradeoff (D1_dev)
def f_tradeoff():
    d = A[(A.exp == "D1_dev") & (~A.strategy.isin(["none", "full"]))]
    g = d.groupby("strategy")[["op_vme_rate", "op_me_rate", "auroc"]].mean()
    ref = g.loc["D01"]
    fig, ax = plt.subplots(figsize=(3.6, 2.55))
    pareto = ["D02", "D05"]
    for s, r in g.iterrows():
        if s == "D01":
            col, z, ms = INK, 7, 6.5
        elif s in pareto:
            col, z, ms = "#2f8f63", 7, 5.6
        else:
            col, z, ms = "#bbbbbb", 4, 4.2
        ax.plot(r.op_me_rate, r.op_vme_rate, "o", ms=ms, color=col, mew=0, zorder=z)
        if s in ["D01"] + pareto + ["D14", "D07", "D04"]:
            dx, dy = (0.012, 0.004) if s != "D14" else (0.012, -0.002)
            ax.annotate(s, (r.op_me_rate + dx, r.op_vme_rate + dy), fontsize=6.4,
                        color=INK if s in ["D01"] + pareto else MUT,
                        fontweight="bold" if s in ["D01"] + pareto else "normal", va="center")
    ax.axvline(ref.op_me_rate, color=MUT, lw=0.7, ls=(0, (1.4, 1.6)), zorder=2)
    ax.axhline(ref.op_vme_rate, color=MUT, lw=0.7, ls=(0, (1.4, 1.6)), zorder=2)
    ax.add_patch(plt.Rectangle((0.18, 0.02), ref.op_me_rate - 0.18, ref.op_vme_rate - 0.02,
                               color="#2f8f63", alpha=0.10, lw=0, zorder=1))
    ax.text(0.215, 0.055, "better on both\nerror types", color=INK, fontsize=6.8, va="bottom")
    ax.annotate("", xy=(0.66, 0.062), xytext=(0.40, 0.175),
                arrowprops=dict(arrowstyle="-|>", color="#bbbbbb", lw=1.4, connectionstyle="arc3,rad=0.25"))
    ax.text(0.60, 0.145, "recalibrating only\nslides along the\ntradeoff", color=MUT, fontsize=6.2, ha="center")
    ax.set_xlim(0.20, 0.78); ax.set_ylim(0.02, 0.26)
    style(ax, xlab="major error rate among untested isolates", ylab="missed resistance rate among untested")
    save(fig, "f10_tradeoff")


# ---------------------------------------------------------------- F11 pseudo label flaw
def f_pseudo():
    r = RND2[(RND2["round"] > 0) & RND2.strategy.str.contains("ssl", na=False)]
    acc = r.groupby("pair").pseudo_acc.mean()
    frac = (r.n_pseudo / r.n_candidates).groupby(r.pair).mean()
    thr = A[(A.exp == "E1_temporal")].groupby("pair").threshold.mean()
    short = {"ecoli_cro": "E. coli", "kpneu_cro": "K. pneu.", "saur_oxa": "S. aureus"}
    fig, axes = plt.subplots(1, 2, figsize=(5.25, 1.78), gridspec_kw=dict(width_ratios=[1, 1.42], wspace=0.40))

    ax = axes[0]
    x = np.arange(3)
    ax.bar(x - 0.19, [frac[p] for p in PAIR], 0.36, color=C["none"], zorder=3, label="pseudo labelled share")
    ax.bar(x + 0.19, [acc[p] for p in PAIR], 0.36, color=C["uncertainty"], zorder=3, label="accuracy of those labels")
    for i, p in enumerate(PAIR):
        ax.text(i - 0.19, frac[p] + .02, f"{frac[p]:.0%}", ha="center", fontsize=6.6, color=INK2)
        ax.text(i + 0.19, acc[p] + .02, f"{acc[p]:.0%}", ha="center", fontsize=6.6, color=INK2)
    ax.set_xticks(x); ax.set_xticklabels([short[p] for p in PAIR], fontsize=6.8)
    ax.set_ylim(0, 1.42); ax.set_yticks([0, .5, 1.0]); ax.set_yticklabels(["0", "50%", "100%"])
    style(ax, title="(a)")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(-0.04, 1.04), handlelength=1.1,
              labelspacing=0.2, fontsize=6.6)

    ax = axes[1]
    for i, p in enumerate(PAIR):
        t = thr[p]
        ax.add_patch(plt.Rectangle((t, i - .20), 0.05 - t, 0.40, color=VME, alpha=0.18, lw=0, zorder=3))
        ax.plot([0, 0.072], [i, i], color="#dddddd", lw=0.7, zorder=2)
        ax.plot([t, t], [i - .25, i + .25], color=VME, lw=1.6, zorder=5)
        ax.plot([0.05, 0.05], [i - .25, i + .25], color=INK2, lw=1.3, zorder=5)
        ax.text(t - 0.0022, i + .30, f"t = {t:.3f}", fontsize=6.4, color=VME, ha="center", va="bottom")
    ax.text(0.05, 2.62, "pseudo \u201csusceptible\u201d cutoff  p \u2264 0.05", fontsize=6.6, color=INK2,
            ha="center", va="bottom")
    ax.annotate("", xy=(0.05, 2.56), xytext=(0.05, 2.34), arrowprops=dict(arrowstyle="->", color=INK2, lw=0.7))
    ax.text(0.030, -0.95, "shaded: called resistant by the model (p \u2265 t),\nbut pseudo labelled susceptible",
            fontsize=6.5, color=VME, ha="center", va="center")
    ax.set_yticks(range(3)); ax.set_yticklabels([short[p] for p in PAIR], fontsize=6.8)
    ax.set_xlim(0, 0.072); ax.set_ylim(-1.45, 3.05)
    ax.set_xlabel("model probability of resistance  p")
    style(ax, title="(b)")
    ax.grid(axis="y", visible=False)
    save(fig, "f11_pseudo")


if __name__ == "__main__":
    f_drift(); f_curves(); f_forest(); f_safety(); f_calib(); f_recal(); f_site(); f_tradeoff(); f_pseudo()
