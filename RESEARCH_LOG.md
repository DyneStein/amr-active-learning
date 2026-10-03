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
- [ ] Notebook 00 in every Colab account (self-test + T4 speed)
- [ ] Dryad API account; notebook 01 downloads DRIAMS-A
- [ ] Notebook 02: audit tables, tuned settings, premise check (gap per pair)
- [ ] Supervisor check-in on the premise result
- [ ] Notebook 03 workers: E1 -> E3 -> E2
- [ ] Notebook 01 again with DRIAMS-B/C/D, then E4
- [ ] Formal Scopus / PubMed novelty search (queries in `docs/Literature_Check.pdf`)
- [ ] Confirm target-journal impact factors on JCR

---

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
