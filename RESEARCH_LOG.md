# Research log

Active learning for maintaining MALDI-TOF AMR predictors (DRIAMS).
Newest entries at the top. Each entry: date, what was done, what was observed, what was decided, next step.
Experiment outputs themselves live on the shared Google Drive folder (`results/`, `tables/`, `figures/`);
this log records what they showed and every decision taken because of them.

## Experiment status

| Experiment | Question | Jobs | Done | Notes |
|---|---|---|---|---|
| E1_temporal | RQ1, RQ2 | 660 | 0 | runs first |
| E3_routing | RQ5 | 180 | 0 | |
| E2_semisup | RQ3 | 390 | 0 | |
| E4_crosssite | RQ4 | 990 | 0 | needs DRIAMS-B/C/D |
| **Total** | | **2 220** | **0** | |

## Checklist

- [x] Plan and literature check (24 Sep 2026)
- [x] Code: `amr_al` package, notebooks 00-04, self-test 17/17 on synthetic data (27 Sep 2026)
- [x] Notebook 00 in every Colab account: self-test 17/17 in all (3 Oct 2026); T4 speed lines still to record
- [x] Dryad API account; token works (200) (3 Oct 2026)
- [x] Notebook 01: DRIAMS-A downloaded and verified (3 Oct 2026)
- [x] Checks before notebook 02: no date column (pseudo-batches); MALDI1/MALDI2 = instrument, almost no duplicates
- [ ] Notebook 02: audit tables, tuned settings, premise check (gap per pair)
- [ ] Supervisor check-in on the premise result
- [ ] Notebook 03 workers: E1 -> E3 -> E2
- [ ] Notebook 01 again with DRIAMS-B/C/D, then E4
- [ ] Formal Scopus / PubMed novelty search (queries in `docs/Literature_Check.pdf`)
- [ ] Confirm target-journal impact factors on JCR

---

## 2026-10-03 · DRIAMS-A downloaded

- Streamed 86.16 GB in 100.8 min (about 13-14 MB/s) on a CPU runtime; 111 257 binned spectra kept, 0 unreadable.
- Per year (spectra with labels; 0 label rows without a spectrum and 0 spectra without a label row in every year):

  | Year | Spectra | meta columns |
  |---|---|---|
  | 2015 | 3 198 | 81 |
  | 2016 | 34 868 | 90 |
  | 2017 | 43 122 | 90 |
  | 2018 | 30 069 | 87 |

- All arrays finite, shape (n, 6000). Compact copy on Drive: 1.3 GB.
- `has_acquisition_date` = False for every year: the label files carry no dates, so the 2017 pool is split into
  4 fixed pseudo-random batches (hash of the isolate code), not calendar quarters. Time shift between the
  training years, the pool year and the test year is unaffected; only the order inside 2017 is not real.
  To state in the paper. Checked: the only non-antibiotic columns are `code`, `species`, `laboratory_species`
  (no date anywhere) → decision: keep the 4 hash pseudo-batches for the 2017 pool.
- Isolate codes end in `_MALDI1` (e.g. `6a690054-..._MALDI1`): possibly several spectra (technical replicates)
  per isolate. Checked (spectra / distinct isolates / suffix counts):
  2016: 34 868 / 34 868 / no suffix · 2017: 43 122 / 43 110 / MALDI1 39 781, MALDI2 3 341 ·
  2018: 30 069 / 30 006 / MALDI1 12 670, MALDI2 17 399.
- Reading: the suffix marks the MALDI-TOF instrument, not repeated measurements. Only 12 (2017) and 63 (2018)
  isolates were measured twice, and none in the training years, so the train/validation split and tuning folds
  are unaffected. Decision: no code change.
- Finding for the paper: a second instrument (MALDI2) appears in 2017 (8%) and measures most isolates in 2018
  (58%). Weis et al. (2022) attribute part of DRIAMS's temporal decay to instrument changes. Planned extra
  analysis: test metrics split by instrument (MALDI1 vs MALDI2) in 2018, and the share of MALDI2 spectra each
  strategy buys from the 2017 pool.
- 2015 is small (3 198 spectra); training data is mostly 2016.

## 2026-10-03 · Dryad access and archive layout

- Dryad API account created; keys reset after being shown once on screen; stored only in Colab Secrets.
  Token test: HTTP 200.
- Dryad listing: DRIAMS_A.tar.gz 86.16 GB, DRIAMS_B 3.69 GB, DRIAMS_C 12.43 GB, DRIAMS_D 42.56 GB, README.md.
- Peek (first 40 members of DRIAMS_A): `DRIAMS-A/raw/2016/<uuid>.txt` — layout `<site>/<type>/<year>/<code>.txt`,
  as the fetch code expects. Raw spectra come first in the archive and are skipped; `binned_6000/` and `id/`
  are read when the stream reaches them (order does not matter: everything is matched by code at the end).
- Decision: go ahead with the DRIAMS-A download.

## 2026-10-03 · Notebook 00 in all accounts

- Self-test passed 17/17 in every Colab account.
- All accounts were run with `ACCOUNT = "acc1"`, so `logs/hello_acc1.txt` only holds the last account's line.
  This affects only that check file, not the experiments. For notebook 03 every account must use a
  different `WORKER` name and `SHARD` number (claims are tied to the worker name).
- To record: T4 speed (`XGBoost fit on cuda: ... s`) per account.

## 2026-10-03 · Log started, documents added

- Added `docs/Research_Plan.pdf`, `docs/Literature_Check.pdf`, `docs/Study_Guide.pdf` (17-page explanation of
  every part of the design: data, splits, model, threshold, strategies, conformal routing, pseudo-labels,
  metrics, seeds, ablations).
- No experiments run yet. Next: notebook 00 in each account, then notebooks 01 and 02.

## 2026-10-01 · Study guide

- Wrote the study guide matching `config.py` exactly. Suggested extra ablations (not scheduled):
  learner (xgb vs lr), number of rounds, label weights, PCA size, hybrid pool factor, sensitivity target,
  conformal alpha, pseudo-label cut-offs. Rule: add them as new experiment names, never edit `config.py`
  while workers are running.

## 2026-09-27 · Code and Colab workflow

- `amr_al`: Dryad streaming download (keeps only `binned_6000` spectra and `*_clean.csv` labels),
  temporal and cross-site splits, XGBoost (GPU) / logistic regression, strategies (random, uncertainty,
  k-center diversity, hybrid, conformal routing), pseudo-labels, metrics, resumable job runner with claim
  files and per-round checkpoints, analysis (mean +- 95% CI, labels to close 95% of the gap, Wilcoxon + Holm).
- Self-test on synthetic data: 17/17 checks passed, including crash and resume giving identical results.
- Not yet tested: real Dryad download, real T4 timings.

## 2026-09-24 · Plan and literature check

- Data: DRIAMS only (MALDI-TOF spectra + S/I/R labels). BV-BRC genomes dropped from the core study.
- Split: train DRIAMS-A 2015-16 (20% validation), pool 2017 in 4 batches, test 2018; DRIAMS-B/C/D 2018 for
  cross-site.
- Pairs: E. coli-ceftriaxone, K. pneumoniae-ceftriaxone, S. aureus-oxacillin.
- Quick search found no work using active learning to choose which isolates to phenotype for retraining;
  temporal decay on DRIAMS is already published (Weis et al., Nat Med 2022), so it is motivation, not a
  contribution. Formal database search still to do.
