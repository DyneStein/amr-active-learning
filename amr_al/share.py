"""Build the folder that gets handed to the supervisors.

Everything a reader needs to check the work: the paper, the exact list of isolates
used, the selection logs, every result file, the SHAP tables, and the code.

    from amr_al import share
    share.build("/content/drive/MyDrive/AMR_Final", spectra=True)
"""
import os
import shutil
import time
import zipfile

import numpy as np

from . import config, data, paths

LAYOUT = ["01_Paper", "02_Dataset", "03_Logs", "04_Results", "05_Explainability_SHAP",
          "06_Code", "07_Answers"]


def manifest(seed=0, site="DRIAMS-A"):
    """Every isolate used by the main study: which split it fell in and what its label was.

    The train/validation division depends on the seed (20% of the training years is held
    out); seed 0 is recorded here. The pool arrival batches are calendar quarters and do
    not depend on the seed.
    """
    import pandas as pd
    have = data.available()
    rows, skipped = [], []
    for pair in config.PAIRS:
        species, ab = config.PAIRS[pair]
        if site not in have:
            skipped.append(f"{pair} at {site}")
            continue
        tr = data.load_pair(site, config.TRAIN_YEARS, species, ab)
        po = data.load_pair(site, [config.POOL_YEAR], species, ab)
        te = data.load_pair(site, [config.TEST_YEAR], species, ab)
        val = data._stratified_split(tr["y"], config.VAL_FRACTION, seed)
        rounds, mode = data.assign_rounds(po["code"], po["date"], config.N_ROUNDS)
        for i in range(len(tr["y"])):
            rows.append((pair, species, ab, site, tr["year"][i], tr["code"][i],
                         "validation" if val[i] else "train", None, int(tr["y"][i])))
        for i in range(len(po["y"])):
            rows.append((pair, species, ab, site, po["year"][i], po["code"][i],
                         "pool", int(rounds[i]) + 1, int(po["y"][i])))
        for i in range(len(te["y"])):
            rows.append((pair, species, ab, site, te["year"][i], te["code"][i],
                         "test", None, int(te["y"][i])))
        for target in config.TARGET_SITES:
            if (pair, target) in [tuple(x) for x in config.EXPERIMENTS["E4_crosssite"].get("skip", [])]:
                continue
            if config.TARGET_YEAR not in have.get(target, []):      # that site was never downloaded
                skipped.append(f"{pair} at {target}")
                continue
            try:
                tg = data.load_pair(target, [config.TARGET_YEAR], species, ab)
            except KeyError:                                        # antibiotic absent at that site
                skipped.append(f"{pair} at {target}")
                continue
            if not len(tg["y"]):
                skipped.append(f"{pair} at {target} (no labelled isolates)")
                continue
            held = data._stratified_split(tg["y"], config.TARGET_TEST_FRACTION, seed + 1000)
            for i in range(len(tg["y"])):
                rows.append((pair, species, ab, target, tg["year"][i], tg["code"][i],
                             "cross_site_test" if held[i] else "cross_site_pool", None, int(tg["y"][i])))
    if skipped:
        print("manifest: not available, so left out: " + ", ".join(sorted(set(skipped))))
    df = pd.DataFrame(rows, columns=["pair", "species", "antibiotic", "site", "year", "isolate",
                                     "split", "arrival_batch", "label"])
    df["label_meaning"] = np.where(df.label == 1, "resistant or intermediate", "susceptible")
    return df


def _copytree(src, dst, pattern=None):
    if not os.path.isdir(src):
        return 0
    os.makedirs(dst, exist_ok=True)
    n = 0
    for root, _, files in os.walk(src):
        rel = os.path.relpath(root, src)
        for f in files:
            if pattern and not f.endswith(pattern):
                continue
            od = os.path.join(dst, rel) if rel != "." else dst
            os.makedirs(od, exist_ok=True)
            shutil.copy2(os.path.join(root, f), os.path.join(od, f))
            n += 1
    return n


def spectra_subset(dst, site_years=None):
    """The spectra of the three studied pairs only, as one .npz per pair and site.

    The full DRIAMS archives are 145 GB; this is the part the study actually read.
    """
    os.makedirs(dst, exist_ok=True)
    total = 0
    for pair, (species, ab) in config.PAIRS.items():
        for site in [config.SOURCE_SITE] + config.TARGET_SITES:
            years = data.available().get(site, [])
            if not years:
                continue
            try:
                d = data.load_pair(site, years, species, ab)
            except KeyError:
                continue
            if not len(d["y"]):
                continue
            f = os.path.join(dst, f"{pair}__{site}.npz")
            np.savez_compressed(f, X=d["X"].astype(np.float32), y=d["y"],
                                isolate=d["code"], year=d["year"])
            total += os.path.getsize(f)
            print(f"  {pair} {site}: {len(d['y'])} spectra")
    return total


def build(dest, spectra=True, paper_pdf=None, zip_results=True, log=print):
    """Assemble the folder. Parts whose inputs are missing are skipped and listed
    in STATUS.md, so this can be run before everything has been produced."""
    for d in LAYOUT:
        os.makedirs(os.path.join(dest, d), exist_ok=True)
    done, missing = [], []

    # 01 paper
    if paper_pdf and os.path.isfile(paper_pdf):
        shutil.copy2(paper_pdf, os.path.join(dest, "01_Paper", os.path.basename(paper_pdf)))
        done.append("01_Paper: " + os.path.basename(paper_pdf))
    else:
        missing.append("01_Paper: no paper PDF was passed to share.build(paper_pdf=...)")

    # 02 dataset (needs the DRIAMS copy; skipped where it is not mounted)
    ds = os.path.join(dest, "02_Dataset")
    open(os.path.join(ds, "README.md"), "w").write(_DATASET_README)
    if not os.path.isdir(data.data_root()):
        missing.append("02_Dataset: manifest and spectra need the DRIAMS copy "
                       f"(looked in {data.data_root()}); run notebook 05 where the data is mounted")
    else:
        try:                                  # never lose the rest of the folder over this step
            log("building the isolate manifest ...")
            m = manifest()
            m.to_csv(os.path.join(ds, "isolate_manifest.csv"), index=False)
            counts = m.groupby(["pair", "site", "split"]).agg(
                isolates=("label", "size"), resistant=("label", "sum")).reset_index()
            counts["resistant_pct"] = (100 * counts.resistant / counts.isolates).round(1)
            counts.to_csv(os.path.join(ds, "isolate_counts.csv"), index=False)
            log(f"  {len(m)} isolates listed")
            done.append(f"02_Dataset: manifest of {len(m)} isolates")
            if spectra:
                log("writing the spectra subset ...")
                size = spectra_subset(os.path.join(ds, "spectra_subset"))
                log(f"  {size/1e6:.0f} MB")
                done.append(f"02_Dataset: spectra subset, {size/1e6:.0f} MB")
        except Exception as e:
            log(f"  dataset step failed: {e!r}")
            missing.append(f"02_Dataset: failed with {type(e).__name__}: {e}")

    # 03 logs
    n_logs = _copytree(paths.LOGS, os.path.join(dest, "03_Logs"))
    (done if n_logs else missing).append(
        f"03_Logs: {n_logs} files" if n_logs else
        f"03_Logs: nothing in {paths.LOGS}; worker logs and the selection log come from notebook 05")

    # 04 results
    res = os.path.join(dest, "04_Results")
    _copytree(paths.TABLES, os.path.join(res, "tables"), ".csv")
    _copytree(paths.FIGURES, os.path.join(res, "figures"))
    if zip_results:
        zf = os.path.join(res, "raw_results_json.zip")
        with zipfile.ZipFile(zf, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(paths.RESULTS):
                for f in files:
                    if f.endswith(".json"):
                        fp = os.path.join(root, f)
                        z.write(fp, os.path.relpath(fp, paths.RESULTS))
        log(f"  raw results zipped: {os.path.getsize(zf)/1e6:.1f} MB")
    else:
        _copytree(paths.RESULTS, os.path.join(res, "results"), ".json")

    # 05 SHAP
    sh = os.path.join(dest, "05_Explainability_SHAP")
    got = []
    for f in ("shap_top_bins.csv", "shap_agreement.csv", "shap_profiles.npz"):
        src = os.path.join(paths.TABLES, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(sh, f))
            got.append(f)
    (done if got else missing).append(
        "05_Explainability_SHAP: " + ", ".join(got) if got else
        "05_Explainability_SHAP: empty; run explain.run() then explain.compare() in notebook 05")

    # 06 code
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    code = os.path.join(dest, "06_Code")
    _copytree(os.path.join(here, "amr_al"), os.path.join(code, "amr_al"), ".py")
    _copytree(os.path.join(here, "notebooks"), os.path.join(code, "notebooks"), ".ipynb")
    for f in ("README.md", "RESEARCH_LOG.md", "requirements.txt"):
        if os.path.isfile(os.path.join(here, f)):
            shutil.copy2(os.path.join(here, f), os.path.join(code, f))

    nt = len([f for f in os.listdir(os.path.join(res, "tables"))]) if os.path.isdir(os.path.join(res, "tables")) else 0
    done.append(f"04_Results: {nt} tables, plus the raw result records")
    done.append("06_Code: amr_al package, notebooks and the research log")
    if not os.listdir(os.path.join(dest, "07_Answers")):
        missing.append("07_Answers: written once the SHAP and selection logs exist")

    open(os.path.join(dest, "README.md"), "w").write(_TOP_README)
    with open(os.path.join(dest, "STATUS.md"), "w") as fh:
        fh.write("# What is in this folder so far\n\nBuilt " + time.strftime("%d %b %Y, %H:%M") + ".\n\n## Ready\n\n")
        fh.write("".join(f"- {x}\n" for x in done) or "- nothing yet\n")
        fh.write("\n## Still to come\n\n")
        fh.write("".join(f"- {x}\n" for x in missing) or "- nothing; the folder is complete\n")
    log(f"\nfolder ready: {dest}")
    for x in done:
        log("  ready    " + x)
    for x in missing:
        log("  pending  " + x)
    return dest


_DATASET_README = """# Dataset

The study uses DRIAMS, a public collection of MALDI-TOF mass spectra of bacterial
isolates with laboratory susceptibility results.

  Weis C. et al., "Direct antimicrobial resistance prediction from clinical MALDI-TOF
  mass spectra using machine learning", Nature Medicine 28, 164-174 (2022).
  Data: Dryad, doi:10.5061/dryad.bzkh1899q, released under CC0 (public domain).

We use the `binned_6000` form: each spectrum is 6000 numbers, one per 3 dalton step
from 2000 to 20000 daltons. Labels follow the DRIAMS authors' encoding, where
resistant and intermediate count as 1 and susceptible counts as 0.

Files here

  isolate_manifest.csv   every isolate the study used: its DRIAMS code, species,
                         antibiotic, site, year, which split it belonged to, which
                         arrival batch (for 2017), and its laboratory result
  isolate_counts.csv     the same thing summarised: how many isolates and what share
                         were resistant, per pair, site and split
  spectra_subset/        the spectra themselves for the three studied pairs, one
                         compressed .npz per pair and site, holding X (spectra),
                         y (labels), isolate (codes) and year

The full archives are about 145 GB; the subset here is the part this study read.
`amr_al/driams_fetch.py` in 06_Code re-downloads it from Dryad and rebuilds the
same files, and `amr_al/data.py` rebuilds the splits from them.
"""

_TOP_README = """# Antimicrobial resistance prediction: active learning study

  01_Paper                 the write-up
  02_Dataset               the exact isolates used, and their spectra
  03_Logs                  worker logs, and the record of every selection decision
  04_Results               one JSON per finished run, plus the summary tables and figures
  05_Explainability_SHAP   which parts of the spectrum each model relies on
  06_Code                  the full code, the notebooks and the research log
  07_Answers               answers to the questions raised in review

Start with 07_Answers, then the paper.
"""
