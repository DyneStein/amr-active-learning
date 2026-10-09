"""End-to-end test on a small synthetic DRIAMS, in a temporary folder (never touches Drive data).

Checks: archive streaming + compact files, audit, tuning, premise check, every
experiment type, crash-and-resume giving identical results, the worker loop,
and the analysis tables/figures.  Run:  from amr_al import selftest; selftest.run()
"""
import copy
import os
import shutil
import tempfile
import time

import numpy as np

from . import analysis, audit, config, data, driams_fetch, paths, runner, synthetic

_OVERRIDES = dict(
    XGB_DEFAULT=dict(n_estimators=20, max_depth=3, learning_rate=0.3, subsample=0.9,
                     colsample_bytree=0.3, min_child_weight=1, reg_lambda=1.0),
    CLAIM_CONFIRM_SECONDS=0.0,
)


def _small_experiments():
    E = copy.deepcopy(config.EXPERIMENTS)
    E["E1_temporal"].update(budgets=[8, 16], seeds=[0, 1])
    E["E3_routing"].update(budgets=[8], seeds=[0])
    E["E2_semisup"].update(budgets=[8], seeds=[0])
    E["E4_crosssite"].update(budgets=[5, 10], seeds=[0], sites=["DRIAMS-B"])
    E["E5_recal"].update(budgets=[8], seeds=[0])
    E["D1_dev"].update(budgets=[8], seeds=[0])
    return E


def run(tmp=None, keep=False):
    t0 = time.time()
    tmp = tmp or tempfile.mkdtemp(prefix="amr_selftest_")
    saved = {k: copy.deepcopy(getattr(config, k)) for k in list(_OVERRIDES) + ["EXPERIMENTS"]}
    old = (paths.ROOT, paths.LOCAL_CACHE)
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok)))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}", flush=True)

    try:
        paths.set_root(os.path.join(tmp, "drive"), os.path.join(tmp, "local"))
        paths.ensure_dirs()
        data.clear_cache()
        runner._pca_cache.clear()
        runner._init_cache.clear()
        for k, v in _OVERRIDES.items():
            setattr(config, k, v)
        config.EXPERIMENTS = _small_experiments()

        print("1. synthetic archives + streaming extraction")
        arch = {
            "DRIAMS-A": synthetic.make_archive(os.path.join(tmp, "A.tar.gz"), "DRIAMS-A",
                                               ["2015", "2016", "2017", "2018"], 170, seed=1),
            "DRIAMS-B": synthetic.make_archive(os.path.join(tmp, "B.tar.gz"), "DRIAMS-B", ["2018"], 160,
                                               seed=2, with_dates=False),
        }
        for site, path in arch.items():
            man = driams_fetch.fetch_site(site, local_path=path)
            n = sum(v.get("n_matched", 0) for v in man["years"].values())
            check(f"fetch {site}", n > 0 and driams_fetch.verify_compact(site), f"({n} spectra)")
        check("warped/raw folders ignored", all(
            len(os.listdir(os.path.join(paths.DATA, "DRIAMS-A"))) and
            not os.path.isdir(os.path.join(paths.DATA, "DRIAMS-A", "binned_6000_warped")) for _ in [0]))
        data.stage_to_local()
        check("staged to local disk", data.data_root().startswith(paths.LOCAL_CACHE))

        print("2. audit, tuning, premise check")
        sites, pairs = audit.summarize()
        check("audit tables", len(sites) == 5 and (pairs.n > 0).any())
        for pair in config.PAIRS:
            audit.tune(pair, grid={"max_depth": [2, 3]}, folds=2)
        check("best_params.json written", os.path.isfile(os.path.join(paths.CONFIG_DIR, "best_params.json")))
        prem = audit.premise_check("ecoli_cro")
        check("premise check", len(prem) == config.N_ROUNDS + 3 and prem.rounds_mode.iloc[0] == "calendar_quarter")

        print("3. crash and resume give identical results")
        job = [j for j in runner.all_jobs(["E1_temporal"])
               if j["strategy"] == "hybrid" and j["budget"] == 16 and j["seed"] == 0 and j["pair"] == "ecoli_cro"][0]
        straight = runner.run_job(job, log=lambda *_: None)
        try:
            os.remove(runner._f("ckpt", job))
        except OSError:
            pass
        try:
            runner.run_job(job, log=lambda *_: None, _stop_after=2)
        except runner._SimulatedCrash:
            pass
        check("checkpoint written at crash", os.path.isfile(runner._f("ckpt", job)))
        resumed = runner.run_job(job, log=print)
        same = [a.get("auroc") for a in straight["metrics"]] == [b.get("auroc") for b in resumed["metrics"]] and \
               [a["labels_total"] for a in straight["metrics"]] == [b["labels_total"] for b in resumed["metrics"]]
        check("resumed == uninterrupted", same)
        os.remove(runner._f("ckpt", job))
        for code in ("D11", "D14", "D10"):          # combinations keep more state (random share, pseudo, adaptive levels)
            cj = [j for j in runner.all_jobs(["D1_dev"]) if j["strategy"] == code and j["pair"] == "ecoli_cro"][0]
            straight = runner.run_job(cj, log=lambda *_: None)
            try:
                os.remove(runner._f("ckpt", cj))
            except OSError:
                pass
            try:
                runner.run_job(cj, log=lambda *_: None, _stop_after=2)
            except runner._SimulatedCrash:
                pass
            resumed = runner.run_job(cj, log=lambda *_: None)
            check(f"combination {code}: resumed == uninterrupted",
                  [a.get("auroc") for a in straight["metrics"]] == [b.get("auroc") for b in resumed["metrics"]]
                  and [a.get("threshold") for a in straight["metrics"]] == [b.get("threshold") for b in resumed["metrics"]])
            os.remove(runner._f("ckpt", cj))

        print("4. worker runs every job")
        runner.run_worker("selftest", hours=2, log_file=True)
        st = runner.status(verbose=True)
        check("all jobs finished", all(r["done"] == r["total"] for r in st.values()))
        res = runner._read(runner._f("result", job))
        check("result has 5 rounds of metrics", res and len(res["metrics"]) == config.N_ROUNDS + 1)
        full = [runner._read(runner._f("result", j)) for j in runner.all_jobs(["E1_temporal"])
                if j["strategy"] == "full" and j["seed"] == 0 and j["pair"] == "ecoli_cro"][0]
        check("full retraining labels every pool isolate",
              full["final"]["labels_total"] == full["sizes"]["pool"])

        print("5. selection log and SHAP")
        from . import explain, seltrace
        tjobs = seltrace.jobs_for(pairs=["ecoli_cro"], strategies=("random", "uncertainty"),
                                  budgets=[config.EXPERIMENTS["E1_temporal"]["budgets"][-1]], seeds=(0,))
        tdf = seltrace.trace_jobs(tjobs, log=lambda *_: None)
        check("selection log has one row per isolate per round",
              len(tdf) > 0 and tdf.groupby(["job", "round", "isolate"]).size().max() == 1)
        bought = tdf[tdf.sent_for_testing]
        # in every round where the budget did not cover all arrivals, uncertainty must buy
        # exactly the isolates nearest the threshold, i.e. ranks 0 .. tested-1
        exact, checked = True, 0
        for (_, rnd), g in tdf[tdf.strategy == "uncertainty"].groupby(["job", "round"]):
            got = g[g.sent_for_testing]
            if len(got) < len(g):
                checked += 1
                exact &= sorted(got.uncertainty_rank) == list(range(len(got)))
        check("uncertainty buys exactly the isolates nearest the threshold",
              exact and checked > 0, f"({checked} partially-bought rounds)")
        check("logged labels match the run",
              all(bought[bought.job == j["id"]].shape[0] ==
                  runner._read(runner._f("result", j))["final"]["labels_total"] for j in tjobs))
        prof = explain.profile(explain._job("E1_temporal", "ecoli_cro", "full", "all", 0),
                               log=lambda *_: None)
        top = explain.top_bins(prof["mean_abs"], 10)
        # synthetic.py plants the resistance marker at bins 2500 + 7*species_index + year drift
        check("SHAP finds the planted resistance marker",
              sum(1 for i in top if 2490 <= i <= 2530) >= 3,
              f"({sum(1 for i in top if 2490 <= i <= 2530)}/10 bins in the marker window)")

        print("6. analysis")
        for exp in config.PRIORITY:
            out = analysis.report(exp)
            check(f"report {exp}", "final" in out and len(out["final"]) > 0)
        check("figures written", len(os.listdir(paths.FIGURES)) >= 4)
    finally:
        for k, v in saved.items():
            setattr(config, k, v)
        paths.set_root(*old)
        data.clear_cache()
        runner._pca_cache.clear()
        runner._init_cache.clear()
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)
    n_ok = sum(ok for _, ok in checks)
    print(f"\nSELFTEST: {n_ok}/{len(checks)} checks passed in {time.time()-t0:.0f} s"
          + ("" if n_ok == len(checks) else "  <-- note the FAIL lines"))
    return n_ok == len(checks)
