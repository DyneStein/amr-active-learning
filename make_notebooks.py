"""Builds the Colab notebooks in notebooks/ (run: python3 make_notebooks.py)."""
import json
import os

SETUP = '''# ---- setup: identical in every notebook ----
FOLDER = "AMR_AL"          # name of the shared folder (or its shortcut) in My Drive

from google.colab import drive
drive.mount("/content/drive")
import os, sys, subprocess
ROOT = f"/content/drive/MyDrive/{FOLDER}"
if not os.path.isdir(os.path.join(ROOT, "amr_al")):
    raise SystemExit(f"{ROOT}/amr_al not found.\\nIn Google Drive open 'Shared with me', right-click {FOLDER} -> "
                     "Organize -> Add shortcut -> My Drive, then run this cell again.")
try:
    import xgboost
    if int(xgboost.__version__.split(".")[0]) < 2:
        raise ImportError
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "xgboost>=2.0"], check=True)
os.environ["AMR_AL_ROOT"] = ROOT
sys.path.insert(0, ROOT)
for m in [k for k in sys.modules if k.startswith("amr_al")]:
    del sys.modules[m]                      # always load the latest code from Drive
from amr_al import config, paths, data, models, runner, audit, analysis, driams_fetch
paths.ensure_dirs()
print("shared folder:", ROOT)
print("compute device for XGBoost:", models.device())'''


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


def nb(cells, gpu=True):
    meta = {"kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"}, "colab": {"provenance": []}}
    if gpu:
        meta["accelerator"] = "GPU"
        meta["colab"]["gpuType"] = "T4"
    return {"nbformat": 4, "nbformat_minor": 0, "metadata": meta, "cells": cells}


NOTEBOOKS = {
"00_Setup_and_T4_Test.ipynb": nb([
    md("""
# 00 · Setup check and T4 test
Run this **once in every Colab account** you will use.

Before running: `Runtime -> Change runtime type -> T4 GPU -> Save`. Then `Runtime -> Run all`.

It checks four things: the shared Drive folder is visible, the GPU works, the whole pipeline runs
end to end on a small synthetic dataset (about 2-4 min, nothing is written to the real data), and how long
one model fit takes on the T4.
"""),
    code(SETUP),
    md("## 1 · GPU"),
    code('''!nvidia-smi --query-gpu=name,memory.total --format=csv
print("XGBoost", xgboost.__version__, "| device:", models.device())
if models.device() != "cuda":
    print("\\n!! Not on a GPU. Runtime -> Change runtime type -> T4 GPU, then Runtime -> Restart and run all.")'''),
    md("## 2 · End-to-end self-test on synthetic data (expect `17/17 checks passed`)"),
    code('''from amr_al import selftest
ok = selftest.run()'''),
    md("## 3 · T4 speed test: one model fit on spectrum-sized data"),
    code('''speed = audit.benchmark()
print(speed)'''),
    md("## 4 · Check this account can write to the shared folder"),
    code('''ACCOUNT = "acc1"          # <- a short name for THIS Colab account (acc1, acc2, ...)
import time, glob
with open(os.path.join(paths.LOGS, f"hello_{ACCOUNT}.txt"), "w") as f:
    f.write(f"{ACCOUNT} {time.ctime()} device={models.device()} speed={speed}\\n")
print("accounts seen so far:", sorted(os.path.basename(p)[6:-4] for p in glob.glob(os.path.join(paths.LOGS, "hello_*.txt"))))'''),
    md("""
**Record:** the self-test summary line, the speed test lines, and anything marked FAIL.
"""),
]),

"01_Get_DRIAMS_Data.ipynb": nb([
    md("""
# 01 · Get the DRIAMS data (run once, in one account)
Streams each DRIAMS archive from Dryad and keeps only the 6000-bin spectra and the label files.
The 86 GB DRIAMS-A archive is never stored; the compact copy on Drive is about 2-4 GB.

**Needs a Dryad API account** (see the PDF, step 3). Put the two values into Colab Secrets
(key icon in the left bar): `DRYAD_CLIENT_ID` and `DRYAD_CLIENT_SECRET`, and switch on notebook access.

A GPU is not needed here: `Runtime -> Change runtime type -> CPU` is fine and saves GPU quota.
Keep the tab open until it finishes (DRIAMS-A: roughly 30-90 min, depending on Colab's network).
"""),
    code(SETUP),
    md("## 1 · Dryad token (valid 10 hours)"),
    code('''try:
    from google.colab import userdata
    cid, secret = userdata.get("DRYAD_CLIENT_ID"), userdata.get("DRYAD_CLIENT_SECRET")
except Exception:
    from getpass import getpass
    cid, secret = getpass("Dryad client id: "), getpass("Dryad client secret: ")
token = driams_fetch.get_token(cid, secret)
assert driams_fetch.test_token(token), "token rejected - check the id/secret"'''),
    md("## 2 · What Dryad has, and a peek inside DRIAMS-A (downloads only a few MB)"),
    code('''files = driams_fetch.list_files()
for name, f in files.items():
    print(f"{f['size_gb']:7.2f} GB  {name}")
driams_fetch.peek("DRIAMS-A", token, n=40)'''),
    md("""
Check the peek: you should see paths like `DRIAMS-A/binned_6000/2015/<code>.txt` and `DRIAMS-A/id/2015/2015_clean.csv`
(the order inside the archive may differ). If the folder names look different, stop here and keep the printed list.
"""),
    md("## 3 · DRIAMS-A (all four years) - needed for everything"),
    code('''if "DRIAMS-A" in data.available():
    print("DRIAMS-A already on Drive:", data.available()["DRIAMS-A"], "- delete data/driams_compact/DRIAMS-A to redo")
else:
    man = driams_fetch.fetch_site("DRIAMS-A", token)
driams_fetch.verify_compact("DRIAMS-A")'''),
    md("## 4 · DRIAMS-B, C, D (only for the cross-site experiment E4; B 3.7 GB, C 12 GB, D 43 GB archives)"),
    code('''GET_OTHER_SITES = False     # set True when you want E4
if GET_OTHER_SITES:
    for site in ["DRIAMS-B", "DRIAMS-C", "DRIAMS-D"]:
        if site in data.available():
            print(site, "already done"); continue
        driams_fetch.fetch_site(site, token)
        driams_fetch.verify_compact(site)'''),
    md("## 5 · Summary"),
    code('''import json
print(data.available())
for site in data.available():
    man = json.load(open(os.path.join(paths.DATA, site, "MANIFEST.json")))
    for y, info in man["years"].items():
        print(site, y, {k: info.get(k) for k in ["n_matched", "n_id_without_spectrum", "has_acquisition_date"]})
!du -sh "{paths.DATA}"'''),
    md("**Record:** the peek list and the summary output."),
], gpu=False),

"02_Data_Audit_and_Tuning.ipynb": nb([
    md("""
# 02 · Data audit, premise check, tuning (run once, T4)
1. What is in the data: isolates and % resistant per pair and year; whether acquisition dates exist
   (if not, the 2017 pool is split into 4 fixed pseudo-batches instead of calendar quarters).
2. **Premise check** - does a 2015-16 model get worse over time, and how much does full retraining recover on 2018?
   If full retraining barely helps, the temporal question (RQ1) is weak and the cross-site question (RQ4) should lead.
3. Hyper-parameter tuning on the training years only (2015-16), saved to `config/best_params.json`.
"""),
    code(SETUP),
    code('''data.stage_to_local(["DRIAMS-A"])      # copy to the fast Colab disk (1-2 min)'''),
    md("## 1 · What is in the data"),
    code('''sites, pairs = audit.summarize()
display(sites)
display(pairs.pivot_table(index=["pair", "site"], columns="year", values=["n", "pct_R"]))'''),
    md("## 2 · Tuning (training years only; roughly 5-15 min per pair on a T4)"),
    code('''import pandas as pd
tuned = pd.concat([audit.tune(pair) for pair in config.PAIRS])
display(tuned.sort_values(["pair", "auroc"], ascending=[True, False]).groupby("pair").head(3))'''),
    md("## 3 · Premise check"),
    code('''prem = pd.concat([audit.premise_check(pair) for pair in config.PAIRS])
prem.to_csv(os.path.join(paths.TABLES, "premise_check.csv"), index=False)
display(prem[["pair", "model", "eval_on", "auroc", "auprc", "vme", "me", "n", "n_R", "rounds_mode"]])
for pair, g in prem.groupby("pair"):
    none = g[(g.model == "no_retrain") & (g.eval_on == config.TEST_YEAR)].auroc.item()
    full = g[g.model == "retrain_with_all_2017"].auroc.item()
    cv = g[g.model == "in_period_5fold_cv"].auroc.item()
    print(f"{pair}: in-period {cv:.3f} | 2018 without retraining {none:.3f} | 2018 with full retraining {full:.3f} "
          f"| gap retraining can close = {full - none:+.3f}")'''),
    md("""
**Record:** both tables and the three `gap` lines. A gap under about 0.02 AUROC means retraining
barely matters for that pair - bring that to the supervisors before running E1 at full size.
"""),
]),

"03_Run_Experiments_Worker.ipynb": nb([
    md("""
# 03 · Experiment worker (run in any account, as often as you like)
Each run picks up unfinished jobs, saves progress after every round, and stops cleanly before the time budget.
Several accounts can run this **at the same time**: give each a different `WORKER` name and `SHARD` number.
If Colab disconnects, just run it again - the job resumes from its last saved round
(a job claimed by a dead session is released after 3 hours).

`Runtime -> Change runtime type -> T4 GPU`, set the four values below, then `Runtime -> Run all`.
"""),
    code('''WORKER = "acc1"        # a different name per Colab account
SHARD = 0              # 0, 1, 2, ... one per account
N_SHARDS = 3           # how many accounts you plan to run in parallel
HOURS = 3.5            # stop starting new jobs after this (free Colab GPU sessions are limited)
EXPERIMENTS = None     # None = all, in priority order E1 -> E3 -> E2 -> E4; or e.g. ["E1_temporal"]'''),
    code(SETUP),
    code('''data.stage_to_local()
runner.status(EXPERIMENTS)'''),
    code('''runner.run_worker(WORKER, shard=SHARD, n_shards=N_SHARDS, experiments=EXPERIMENTS, hours=HOURS)'''),
    code('''runner.status(EXPERIMENTS)
drive.flush_and_unmount()      # make sure every result is written to Drive before the session ends
print("safe to close")'''),
]),

"04_Analyze_Results.ipynb": nb([
    md("""
# 04 · Results (run any time; works on partial results)
Writes tables to `tables/` and figures to `figures/` in the shared folder.
"""),
    code(SETUP),
    code('''runner.status()'''),
    code('''from IPython.display import Image, display
for exp in config.PRIORITY:
    out = analysis.report(exp)
    if not out:
        continue
    if "gap" in out and len(out["gap"]):
        print(exp, "- labels needed to close 95% of the gap between no retraining and full retraining:")
        display(out["gap"].round(3))
    if len(out.get("tests", [])):
        print(exp, "- strategy vs random (paired over seeds, Holm-corrected):")
        display(out["tests"].round(4))
    for f in out["figs"]:
        display(Image(f))'''),
    md("Tables are in `tables/` and figures in `figures/` of the shared folder."),
], gpu=False),

"05_Explain_and_Share.ipynb": nb([
    md("""
# 05 · Feature attributions (SHAP), selection logs, and the folder for the supervisors

Three things, in order. A T4 helps but is not required.

1. **SHAP**: for every species/antibiotic pair, rebuild six models (never retrained, retrained on
   everything, and random / uncertainty at 400 and 800 lab tests) and work out how much each part of
   the spectrum each one relies on. This answers whether active learning and ordinary retraining end
   up using the same peaks.
2. **Selection log**: replay the runs and write down every single decision, one line per isolate per
   round, so a reader can see exactly which isolates were sent for testing and whether they were
   resistant.
3. **Share folder**: collect the paper, the dataset, the logs, the results and the code in one place.

Expect roughly 30 to 60 minutes for step 1 on a T4.
"""),
    code(SETUP),
    code('''
from amr_al import explain
explain.run(seeds=(0, 1, 2, 3, 4))          # resumable: re-run it if the session drops'''),
    code('''
agreement = explain.compare()
tops = explain.top_table()
import pandas as pd
pd.set_option("display.width", 200)
print("Do the models lean on the same parts of the spectrum?")
display(agreement.round(3))
print("\nMost important bins per model:")
display(tops[tops["rank"] <= 8])'''),
    code('''
from amr_al import seltrace
log = seltrace.run(pairs=list(config.PAIRS),
                   strategies=("random", "uncertainty", "diversity", "hybrid"),
                   budgets=(400,), seeds=(0,))
summary = seltrace.summarise(log)
display(summary[summary.pair == "kpneu_cro"])
print("\nThe isolates uncertainty sampling reached for first:")
display(seltrace.examples(log, 10).head(20))'''),
    code('''
# lab tests done against model quality, for the paper and for the supervisors
df = analysis.load("E1_temporal")
cost = analysis.cost_table(df)
cost.to_csv(paths.p("tables", "E1_temporal_cost.csv"), index=False)
display(cost[cost.budget.astype(str).isin(["400", "800"])].round(3))'''),
    code('''
from amr_al import share
PAPER = "/content/drive/MyDrive/AMR_AL/paper/AMR_Paper_Draft.pdf"   # change if it sits elsewhere
share.build("/content/drive/MyDrive/AMR_Final", spectra=True,
            paper_pdf=PAPER if os.path.isfile(PAPER) else None)'''),
    md("`AMR_Final` in My Drive is the folder to share. Right-click it in Drive to download it as a zip."),
], gpu=True),
}

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")
    os.makedirs(out_dir, exist_ok=True)
    for name, book in NOTEBOOKS.items():
        with open(os.path.join(out_dir, name), "w") as f:
            json.dump(book, f, indent=1)
        print("wrote", name)
