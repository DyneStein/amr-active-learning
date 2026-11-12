"""Robustness of the temporal comparison to how the 2017 pool is divided into arrival batches.

The released spectra carry no acquisition dates, so the main experiment (E1_temporal) forms the four
arrival batches from a hash of the isolate code. This module repeats the same comparison under other
divisions of the same pool:

  hash      the division used in the paper, md5(code) mod 4 (reproduction check on this machine)
  saltK     an independent division, md5("K:" + code) mod 4, for K = 1, 2, ...
  single    no sequence at all: the whole budget is bought in one round from the whole pool

Train, validation and test sets, the model, its tuned settings and the seeds are those of E1_temporal,
so the only thing that changes is which isolates arrive together and in what order.

Run (from the AMR_AL folder, AMR_AL_ROOT pointing at a folder that holds data/driams_compact and
config/best_params.json):
    python -m amr_al.robust run  --variants salt1,salt2,single,hash,salt3 --budgets 100,400,800
    python -m amr_al.robust table
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

from . import config, data, paths, runner

RULES = ["random", "uncertainty", "diversity", "hybrid"]
EXP = "R1_batching"


def _assign(variant):
    def f(codes, dates, n_rounds):
        if variant == "hash" or variant == "single":
            h = [int(hashlib.md5(c.encode()).hexdigest(), 16) % n_rounds for c in codes]
        else:
            k = variant.replace("salt", "")
            h = [int(hashlib.md5(f"{k}:{c}".encode()).hexdigest(), 16) % n_rounds for c in codes]
        return np.array(h, int), f"robust:{variant}"
    return f


def jobs(variants, budgets, seeds, pairs):
    out = []
    for v in variants:
        for pair in pairs:
            for seed in seeds:
                for b in budgets:
                    for s in RULES:
                        j = dict(exp=f"{EXP}_{v}", setting="temporal", pair=pair, site="DRIAMS-A", seed=seed,
                                 strategy=s, budget=b, variant=v)
                        j["id"] = runner.job_id(j)
                        out.append(j)
    return out


def _out(j):
    return os.path.join(paths.RESULTS, EXP, j["id"] + ".json")


def _on_ac():
    try:
        return "AC Power" in subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True).stdout
    except Exception:
        return True


def run(variants=("salt1", "salt2", "single", "hash", "salt3"), budgets=(100, 400, 800), seeds=None, pairs=None,
        need_ac=True, shard=0, n_shards=1, hours=None):
    """Run the unfinished jobs of this shard. Every job is saved as soon as it ends, so a disconnect loses one job
    at most and running the same call again continues. `hours` stops starting new jobs after that long."""
    seeds = list(config.SEEDS) if seeds is None else seeds
    pairs = list(config.PAIRS) if pairs is None else pairs
    os.makedirs(os.path.join(paths.RESULTS, EXP), exist_ok=True)
    mine = [j for j in jobs(variants, budgets, seeds, pairs) if runner._shard(j["id"], n_shards) == shard]
    todo = [j for j in mine if not os.path.isfile(_out(j))]
    print(f"shard {shard} of {n_shards}: {len(mine)} jobs, {len(mine) - len(todo)} already done, {len(todo)} to run",
          flush=True)
    orig_assign, orig_rounds = data.assign_rounds, config.N_ROUNDS
    t0, done = time.time(), 0
    for j in todo:
        if os.path.isfile(os.path.join(paths.ROOT, "STOP")):
            print("STOP file found, leaving", flush=True)
            break
        if hours is not None and time.time() - t0 > hours * 3600:
            print(f"time budget of {hours} h reached, {len(todo) - done} jobs left for the next run", flush=True)
            break
        if os.path.isfile(_out(j)):          # another session finished it meanwhile
            continue
        while need_ac and not _on_ac():
            time.sleep(60)
        data.assign_rounds = _assign(j["variant"])
        config.N_ROUNDS = 1 if j["variant"] == "single" else orig_rounds
        try:
            res = runner.run_job(j, log=lambda *a: None)
        finally:
            data.assign_rounds, config.N_ROUNDS = orig_assign, orig_rounds
        tmp = _out(j) + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(res, fh, default=runner._jsonable)
        os.replace(tmp, _out(j))
        done += 1
        if done % 10 == 0:
            el = time.time() - t0
            print(f"{time.strftime('%H:%M:%S')} {done}/{len(todo)} done, {el/done:.1f} s per job, "
                  f"about {(len(todo)-done)*el/done/3600:.1f} h left; last {j['id']} auroc {res['final']['auroc']:.4f}", flush=True)


def preflight(pair="ecoli_cro", rule="random", budget=100, seed=0):
    """Runs one job of the paper's own division and compares it with the published E1 record, if that record is in
    results/E1_temporal. A difference means the software versions changed since October, which is harmless here
    because every division, including the paper's own, is rerun in the same environment. Never stops the notebook."""
    try:
        j = jobs(["hash"], [budget], [seed], [pair])
        j = [x for x in j if x["strategy"] == rule][0]
        os.makedirs(os.path.join(paths.RESULTS, EXP), exist_ok=True)
        if os.path.isfile(_out(j)):
            with open(_out(j)) as fh:
                new = json.load(fh)
        else:
            orig = data.assign_rounds
            data.assign_rounds = _assign("hash")
            try:
                new = runner.run_job(j, log=lambda *a: None)
            finally:
                data.assign_rounds = orig
            tmp = _out(j) + ".tmp"
            with open(tmp, "w") as fh:
                json.dump(new, fh, default=runner._jsonable)
            os.replace(tmp, _out(j))
            with open(_out(j)) as fh:
                new = json.load(fh)
        print(f"preflight job ran on {new['device']}: pool {new['sizes']['pool']}, test {new['sizes']['test']}, "
              f"AUROC {new['final']['auroc']:.6f}, versions {new['versions']}")
        old_f = os.path.join(paths.RESULTS, "E1_temporal", f"E1_temporal__{pair}__DRIAMS-A__{rule}__b{budget}__s{seed}.json")
        if os.path.isfile(old_f):
            with open(old_f) as fh:
                old = json.load(fh)
            same = abs(old["final"]["auroc"] - new["final"]["auroc"]) < 1e-9
            print(f"published run: AUROC {old['final']['auroc']:.6f}, versions {old['versions']} -> "
                  + ("reproduced exactly" if same else "not identical (versions differ, see docstring; the rerun is still valid)"))
        else:
            print("published E1 record not found in results/E1_temporal, comparison skipped")
    except Exception as e:                                   # informative only
        print("preflight could not run:", repr(e))


def summary(write=True):
    """One row per finished job, written to tables/R1_batching_runs.csv, and a paired comparison against random
    selection printed per division (mean AUROC difference over the 10 seeds, exact Wilcoxon p)."""
    import csv
    import glob
    import itertools
    from scipy import stats
    rows = []
    for f in sorted(glob.glob(os.path.join(paths.RESULTS, EXP, "*.json"))):
        with open(f) as fh:
            d = json.load(fh)
        j, m = d["job"], d["metrics"][1:]
        rows.append(dict(variant=j["variant"], pair=j["pair"], budget=j["budget"], rule=j["strategy"], seed=j["seed"],
                         auroc=d["final"]["auroc"], vme=d["final"]["vme"], me=d["final"]["me"],
                         threshold=d["final"]["threshold"], labels=d["final"]["labels_total"],
                         op_vme=sum(x["op_vme_count"] for x in m), op_me=sum(x["op_me_count"] for x in m),
                         op_untested=sum(x["op_untested"] for x in m), op_R=sum(x["op_R"] for x in m),
                         pool=d["sizes"]["pool"], device=d["device"]))
    if write and rows:
        os.makedirs(paths.TABLES, exist_ok=True)
        out = os.path.join(paths.TABLES, "R1_batching_runs.csv")
        with open(out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} finished jobs written to {out}")
    key = {(r["variant"], r["pair"], r["budget"], r["rule"], r["seed"]): r for r in rows}

    def exact_p(d):
        d = d[d != 0]
        if len(d) == 0:
            return 1.0
        r = stats.rankdata(np.abs(d)); tot = r.sum(); w = r[d > 0].sum(); st = min(w, tot - w)
        c = sum(1 for sg in itertools.product((0, 1), repeat=len(d))
                if min(np.dot(sg, r), tot - np.dot(sg, r)) <= st + 1e-12)
        return c / 2 ** len(d)

    for v in sorted({r["variant"] for r in rows}):
        print(f"\ndivision {v}: rule minus random, test AUROC on 2018")
        for pair in config.PAIRS:
            for b in sorted({r["budget"] for r in rows if r["variant"] == v}):
                line = f"  {pair:10s} b{b:<4d}"
                for rule in RULES[1:]:
                    seeds = [s for s in config.SEEDS if (v, pair, b, rule, s) in key and (v, pair, b, "random", s) in key]
                    if len(seeds) < 5:
                        line += f"  {rule[:4]} (only {len(seeds)} seeds)"
                        continue
                    d = np.array([key[(v, pair, b, rule, s)]["auroc"] - key[(v, pair, b, "random", s)]["auroc"] for s in seeds])
                    h = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
                    line += f"  {rule[:4]} {d.mean():+.4f} [{d.mean()-h:+.4f},{d.mean()+h:+.4f}] p={exact_p(d):.4f} n={len(d)}"
                print(line)
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "table"])
    ap.add_argument("--variants", default="salt1,salt2,single,hash,salt3")
    ap.add_argument("--budgets", default="100,400,800")
    ap.add_argument("--seeds", default=",".join(map(str, config.SEEDS)))
    ap.add_argument("--pairs", default=",".join(config.PAIRS))
    ap.add_argument("--no-ac-check", action="store_true")
    a = ap.parse_args()
    if a.cmd == "table":
        summary()
    else:
        run(a.variants.split(","), [int(x) for x in a.budgets.split(",")], [int(x) for x in a.seeds.split(",")],
            a.pairs.split(","), need_ac=not a.no_ac_check)
