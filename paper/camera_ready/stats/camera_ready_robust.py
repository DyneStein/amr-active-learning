"""Robustness of the temporal comparison to the division of the 2017 pool into arrival batches (13 Nov 2026).

Input: tables/R1_batching_runs.csv (notebook 06; one row per run) and results/E1_temporal (the published runs).
One row (salt2, E. coli, 400, diversity, seed 0) was missing from the CSV written on Colab although its result file
is on Drive; it was read from Drive and appended by hand (AUROC 0.84767, record finished 2026-11-12 18:29:12).
Run: /usr/bin/python3 camera_ready_robust.py <Results dir>
"""
import sys, os, csv, json, glob, itertools
import numpy as np
from scipy import stats

R = sys.argv[1]
rows = list(csv.DictReader(open(os.path.join(R, "tables", "R1_batching_runs.csv"))))
K = {(r["variant"], r["pair"], int(r["budget"]), r["rule"], int(r["seed"])): r for r in rows}
PAIRS, BUD, RULES, VAR = ["ecoli_cro", "kpneu_cro", "saur_oxa"], [100, 400, 800], ["uncertainty", "diversity", "hybrid"], ["hash", "salt1", "salt2", "salt3", "single"]
print("runs", len(rows), "unique", len(K), "expected", 5 * 3 * 3 * 4 * 10)


def exact_p(d):
    d = np.asarray(d, float); d = d[d != 0]
    if len(d) == 0:
        return 1.0
    r = stats.rankdata(np.abs(d)); tot = r.sum(); w = r[d > 0].sum(); st = min(w, tot - w)
    return sum(1 for sg in itertools.product((0, 1), repeat=len(d)) if min(np.dot(sg, r), tot - np.dot(sg, r)) <= st + 1e-12) / 2 ** len(d)


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); a = np.empty_like(p); run = 0.0
    for k, i in enumerate(o):
        run = max(run, (len(p) - k) * p[i]); a[i] = min(1.0, run)
    return a


def ci(d):
    d = np.asarray(d, float); h = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return d.mean(), d.mean() - h, d.mean() + h


# 1. does the rerun of the paper's own division reproduce the published runs?
diffs = []
for (v, p, b, ru, s), r in K.items():
    if v != "hash":
        continue
    f = os.path.join(R, "results", "E1_temporal", f"E1_temporal__{p}__DRIAMS-A__{ru}__b{b}__s{s}.json")
    old = json.load(open(f))["final"]
    om = json.load(open(f))["metrics"][1:]
    diffs.append((abs(old["auroc"] - float(r["auroc"])), abs(sum(x["op_vme_count"] for x in om) - int(r["op_vme"])),
                  abs(sum(x["op_me_count"] for x in om) - int(r["op_me"]))))
diffs = np.array(diffs)
print(f"\n1. paper's own division rerun vs published E1: {len(diffs)} runs, identical AUROC in {(diffs[:,0] < 1e-12).sum()}, "
      f"max AUROC difference {diffs[:,0].max():.2e}, operational counts identical in {((diffs[:,1] == 0) & (diffs[:,2] == 0)).sum()}")

# 2. paired comparison per division
print("\n2. rule minus random, test AUROC, per division (27 comparisons each: 3 pairs x 3 budgets x 3 rules)")
allc = {}
for v in VAR:
    comp = []
    for p in PAIRS:
        for b in BUD:
            for ru in RULES:
                d = np.array([float(K[(v, p, b, ru, s)]["auroc"]) - float(K[(v, p, b, "random", s)]["auroc"]) for s in range(10)])
                m, lo, hi = ci(d)
                comp.append(dict(v=v, pair=p, budget=b, rule=ru, mean=m, lo=lo, hi=hi, p=exact_p(d), d=d))
    for p in PAIRS:
        idx = [i for i, c in enumerate(comp) if c["pair"] == p]
        for i, a in zip(idx, holm([comp[i]["p"] for i in idx])):
            comp[i]["holm_pair"] = a
    for c, a in zip(comp, holm([c["p"] for c in comp])):
        c["holm_all"] = a
    allc[v] = comp
    raw_neg = sum(c["p"] < 0.05 and c["mean"] < 0 for c in comp); raw_pos = sum(c["p"] < 0.05 and c["mean"] > 0 for c in comp)
    print(f"  {v:7s} mean diff {min(c['mean'] for c in comp):+.4f} to {max(c['mean'] for c in comp):+.4f}; negative means {sum(c['mean'] < 0 for c in comp)}/27; "
          f"raw p<0.05: {raw_neg} against the rule, {raw_pos} for it; Holm within pair <0.05: {sum(c['holm_pair'] < 0.05 and c['mean'] < 0 for c in comp)} against, "
          f"{sum(c['holm_pair'] < 0.05 and c['mean'] > 0 for c in comp)} for; Holm across 27 <0.05: {sum(c['holm_all'] < 0.05 for c in comp)}; "
          f"CI above 0: {sum(c['lo'] > 0 for c in comp)}, below 0: {sum(c['hi'] < 0 for c in comp)}")
    for c in comp:
        if c["p"] < 0.05 and c["mean"] > 0:
            print(f"      for the rule: {c['pair']} b{c['budget']} {c['rule']} {c['mean']:+.4f} [{c['lo']:+.4f},{c['hi']:+.4f}] p {c['p']:.4f} holm_pair {c['holm_pair']:.3f}")

# 3. per pair and rule, averaged over the 3 budgets: each division
print("\n3. mean difference over the 3 budgets (seed level, 95% CI), per division")
for p in PAIRS:
    for ru in RULES:
        line = f"  {p:10s} {ru:11s}"
        for v in VAR:
            d = np.mean([[float(K[(v, p, b, ru, s)]["auroc"]) - float(K[(v, p, b, "random", s)]["auroc"]) for s in range(10)] for b in BUD], axis=0)
            m, lo, hi = ci(d)
            line += f" | {v} {m:+.4f} [{lo:+.4f},{hi:+.4f}]"
        print(line)

# 4. the two published losses and the uncertainty rule at 800, in every division
print("\n4. uncertainty minus random at 800 labels, per division")
for p in PAIRS:
    line = f"  {p:10s}"
    for v in VAR:
        c = [c for c in allc[v] if c["pair"] == p and c["budget"] == 800 and c["rule"] == "uncertainty"][0]
        line += f" | {v} {c['mean']:+.4f} [{c['lo']:+.4f},{c['hi']:+.4f}] p {c['p']:.3f}"
    print(line)

# 5. operational errors, uncertainty vs random, per division
print("\n5. operational errors over the pool year, uncertainty minus random (mean over 10 seeds, 95% CI)")
for b in (400, 800):
    for p in PAIRS:
        line = f"  b{b} {p:10s}"
        for v in VAR:
            dv = np.array([int(K[(v, p, b, 'uncertainty', s)]["op_vme"]) - int(K[(v, p, b, 'random', s)]["op_vme"]) for s in range(10)])
            dm = np.array([int(K[(v, p, b, 'uncertainty', s)]["op_me"]) - int(K[(v, p, b, 'random', s)]["op_me"]) for s in range(10)])
            rv = np.mean([int(K[(v, p, b, 'random', s)]["op_vme"]) for s in range(10)]); uv = np.mean([int(K[(v, p, b, 'uncertainty', s)]["op_vme"]) for s in range(10)])
            line += f" | {v} VME {rv:.1f}->{uv:.1f} ({100*(uv-rv)/rv:+.0f}%) [{ci(dv)[1]:+.1f},{ci(dv)[2]:+.1f}] ME {ci(dm)[0]:+.1f} [{ci(dm)[1]:+.1f},{ci(dm)[2]:+.1f}]"
        print(line)

# 6. share of the reachable gain under random selection, per division (bounds from E1)
print("\n6. AUROC of random selection per division (mean over 10 seeds)")
for p in PAIRS:
    for b in BUD:
        print(f"  {p:10s} b{b:<4d}" + "".join(f" | {v} {np.mean([float(K[(v, p, b, 'random', s)]['auroc']) for s in range(10)]):.4f}" for v in VAR))

# table for the paper: per division, range of mean differences and counts
json.dump({v: [{k: (c[k] if k != "d" else None) for k in c if k != "d"} for c in allc[v]] for v in VAR},
          open(os.path.join(R, "extra", "camera_ready_robust_comparisons.json"), "w"), indent=1)
