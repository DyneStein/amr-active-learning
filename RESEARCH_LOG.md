# Research log

Active learning for maintaining MALDI-TOF AMR predictors (DRIAMS).
Newest entries at the top. Each entry: date, what was done, what was observed, what was decided, next step.
Experiment outputs themselves live on the shared Google Drive folder (`results/`, `tables/`, `figures/`);
this log records what they showed and every decision taken because of them.

## Experiment status

| Experiment | Question | Jobs | Done | Notes |
|---|---|---|---|---|
| E1_temporal | RQ1, RQ2 | 660 | 660 | done 4 Oct 2026 |
| E3_routing | RQ5 | 180 | 180 | done 4 Oct 2026 |
| E2_semisup | RQ3 | 390 | 390 | done 4 Oct 2026 |
| E4_crosssite | RQ4 | 880 | 880 | done 4 Oct 2026; S. aureus at D dropped (no labels) |
| E5_recal | threshold ablation | 240 | 239 | 1 job missing from download (kpneu random b100 s3) |
| D1_dev | combination search (dev split) | 510 | 510 | done 5 Oct 2026; search stopped (see log) |
| **Total** | | **2 860** | **2 859** | |

## Checklist

- [x] Plan and literature check (24 Sep 2026)
- [x] Code: `amr_al` package, notebooks 00-04, self-test 17/17 on synthetic data (27 Sep 2026)
- [x] Notebook 00 in every Colab account: self-test 17/17 in all (3 Oct 2026); T4 speed lines still to record
- [x] Dryad API account; token works (200) (3 Oct 2026)
- [x] Notebook 01: DRIAMS-A downloaded and verified (3 Oct 2026)
- [x] Checks before notebook 02: no date column (pseudo-batches); MALDI1/MALDI2 = instrument, almost no duplicates
- [x] Notebook 02: audit tables, tuned settings, premise check (gap per pair) (3 Oct 2026)
- [ ] Supervisor check-in on the premise result (premise holds: gaps 0.042-0.057)
- [x] Notebook 03 workers: E1 -> E3 -> E2 (1 230 jobs, 4 Oct 2026)
- [x] Notebook 01 again with DRIAMS-B/C/D (4 Oct 2026)
- [ ] E4 workers
- [ ] Formal Scopus / PubMed novelty search (queries in `docs/Literature_Check.pdf`)
- [ ] Confirm target-journal impact factors on JCR

---

## 2026-10-05 · Conference paper draft

- `paper/AMR_Paper_Draft.pdf` (14 pp; copy at `Baterial-AMR/AMR_Paper_Draft.pdf`). Single column, Computer Modern,
  booktabs tables, centred page numbers, 11 figures and 4 tables, set to match the format of the submitted
  Risk-Aware Active Learning paper. No LaTeX on this machine, so the look is reproduced in the HTML -> Chrome build;
  see `paper/README.md` for the four commands. Sources in `paper/` (paper.py, pfig.py, pdiag.py, paper_data.py,
  stamp.py, fonts/, fig/).
- First attempt was two-column with coloured headings, callout boxes and reference tier badges; rejected as not
  looking like a submitted paper. Figures were restyled to a muted print palette (checked for colour-blind
  separation), schematics redrawn as monochrome line art, and all decorative chrome removed.
- Framing: label efficiency is a negative result; the positive results are (a) deployment-time error counts and
  (b) calibration decay under drift. Both error types (VME and ME) reported everywhere, after the D1_dev lesson.
- Honest points kept in the draft: uncertainty sampling lowers VMEs in all three pairs but raises MEs for
  K. pneumoniae (+54%) and is flat for S. aureus; the pre-registered D1 rule picked a combination that only traded
  one error for the other, reported as a failure of our rule; E2 reported as invalid by design flaw.
- Open before submission: author affiliation placeholder in the title block; formal Scopus/PubMed novelty search;
  supervisor review; venue choice; statement on code/data release.

## 2026-10-05 · E5 and D1_dev results; combination search stopped, back to the original study

- D1_dev (510/510; 110 jobs ran twice on different machines with identical results -> fully reproducible).
  Pre-registered rule winner: D14 (VME-risk 50% + random 50% + adaptive calibration), then D07. BUT the rule counted
  only missed resistances: D14 gets them down by calling ~2/3 of susceptible isolates resistant (major errors among
  untested isolates x1.95). All re-calibrating combinations trade major errors for very major errors; none improves
  the trade-off. AUROC is flat across all 16 combinations (within +-0.005 of random on average).
  Only uncertainty selection (D02, and D05 = half uncertainty + half random) lowers BOTH error types among untested
  isolates (total -15% / -9% vs random, p < 0.01). Recorded as exploratory; no 2018 confirmation run.
- Decision (user, 5 Oct): stop the combination search and stay with the original research questions.
- E5 (239/240) vs E1, 2018 test, paired by seed: re-calibrating on 25% held-out new labels raises sensitivity toward
  the 90% target (mean E. coli 0.82 -> 0.88, K. pneumoniae 0.64 -> 0.77, S. aureus 0.72 -> 0.79; still short because
  2018 drifts again) but raises the major-error rate (0.37 -> 0.52, 0.27 -> 0.49, 0.26 -> 0.39) and lowers balanced
  accuracy; AUROC slightly lower (fewer training labels). Holm-significant: sensitivity 9/24, major errors 11/24 cells.
  Reading: the old threshold silently drifted to a different operating point; restoring the promised sensitivity
  shows its real cost with models of AUROC ~0.75-0.85.
- Outputs: `Results/extra/` (dev_rank, dev_errors, e5).
- Next: write-up of RQ1-RQ5 (RQ3 reported with the pseudo-label design flaw), supervisor meeting, formal novelty search.

## 2026-10-05 · Combination catalogues and PRE-REGISTERED decision rule for the development search

- Catalogues AL-A..AL-E (`docs/AMR_AL_Catalogues.pdf`): 5 slots (selection S1-S9, budget split B1-B5, retraining
  T1-T4, calibration C1-C5, unlabelled U0-U2); 2 430 combinations, 1 424 valid, 559 robust and affordable; analytic
  ranking; literature check; 16 combinations (D01-D16) + bounds chosen for the development search.
- Development split (2018 never used): train 2015-16, pool = 2017 arrival batches 1-2 (4 rounds), test = 2017
  batches 3-4. Seeds 100-104, budgets 100 and 300, 3 pairs: 510 jobs (`D1_dev`).
- Decision rule, fixed now before any development result:
  1. Non-inferiority on AUROC: mean difference vs D01 (random) over the 6 pair x budget cells >= -0.005, and no
     pair significantly worse (paired Wilcoxon over seeds, Holm p < 0.05).
  2. Among those, rank by (a) missed resistances among untested isolates relative to D01 (mean ratio over cells) and
     (b) calibration error |2017-test sensitivity - 0.90| (mean), with R-class conformal coverage >= 0.85 required.
     Final rank = sum of the two ranks; ties go to the combination with fewer changed parts.
  3. The top 2 combinations (plus the single-change steps between D01 and the winner, as an ablation chain) are run
     once on the real split (2017 -> 2018, seeds 0-9, budgets 100/400/800) and compared with E1 and E5 by seed.
- Code: `amr_al/combo.py` (combination engine), `data.dev_split`, config `COMBOS` and `D1_dev`; E1-E5 unchanged.
  Self-test 22/22 (crash/resume identical for combinations D10, D11, D14).

## 2026-10-05 · Checks on threshold, conformal bounds and pseudo-labels; E5 added

- Threshold: set on 2015-16 validation for 90% sensitivity to resistance. Realised on 2018 (model before retraining):
  80% / 73% / 79% (E. coli / K. pneumoniae / S. aureus). The threshold does not survive the drift.
- Conformal bounds (routing_all): at least 15.5% / 18.9% / 14.3% of 2017 resistant isolates got a confident "S" set,
  above the 10% the method promises (lower bound; empty sets not counted). The guarantee breaks under drift, which
  explains why routing missed more resistances than random.
- Pseudo-labels: 65-95% of each round's isolates were pseudo-labelled; accuracy 87-93%, i.e. 60-240 wrong labels per job.
  Design flaw found: the "susceptible" cut-off (p <= 0.05) lies ABOVE the decision threshold (mean 0.010-0.023), so
  isolates the model itself calls resistant were pseudo-labelled susceptible. E2 as run is not a fair test of
  pseudo-labelling; it must be reported as such or rerun with cut-offs tied to the threshold (decision pending).
- Added E5_recal (240 jobs): 25% of bought labels (fixed per seed) kept out of training and used to re-set the threshold
  and conformal bounds each round (new labels alone once they hold >= 10 resistant isolates, else with validation).
  E1-E4 job ids and behaviour unchanged. Self-test 18/18. Outputs in `Results/extra/`.
- Next: run E5 (notebook 03, EXPERIMENTS = ["E5_recal"]), decide on E2 rerun.

## 2026-10-05 · First look at the results (notebook 04 + extra tests)

- Tables/figures/results downloaded to `Baterial-AMR/Results/` (not in this repo). Extra tests (operational VME vs random,
  E4 tests) in `Results/extra/`.
- E1 (RQ1-2): retraining helps (no retraining -> all 2017 labels: AUROC +0.044 / +0.046 / +0.051 for E. coli / K. pneumoniae /
  S. aureus). No strategy beats random on 2018 AUROC after Holm correction (0 of 45 tests). Pure uncertainty is worse
  (K. pneumoniae, 800 labels: -0.029, Holm p = 0.029). The primary endpoint (labels to close 95% of the gap) is not reached
  within 800 labels by any strategy; random closes 66-77% of the gap at 800.
- Operational safety (pre-specified secondary metric): resistant isolates NOT sent to the lab and called susceptible during
  2017. Uncertainty sampling at 800 labels cuts these vs random: 49.8 -> 33.6, 19.4 -> 5.2, 18.8 -> 9.2 (all Holm p < 0.05).
- E3 (RQ5): conformal routing = random on AUROC; uses fewer labels (routing_all 650 / 522 / 428) but leaves MORE missed
  resistances than random at 800 (78 vs 50, 33 vs 19, 39 vs 19; Holm p < 0.01). Possible cause: conformal bounds calibrated
  on 2015-16 data do not hold under drift (to check: coverage on 2017).
- E2 (RQ3): pseudo-labels hurt. Pseudo-labels alone lower AUROC below no retraining; with labels, 2018 VME rises sharply at
  small budgets (e.g. E. coli random+ssl, 100 labels: VME 0.60 vs 0.19). No significant AUROC gain.
- E4 (RQ4): the DRIAMS-A model transfers poorly to some sites (K. pneumoniae at B: AUROC 0.48; C: 0.59); local labels fix
  most of it with 25-100 isolates. No strategy differs from random (0 of 120 tests); sites are small (low power).
- Caveat: VME at the fixed threshold is high everywhere (0.13-0.45); threshold recalibration is a needed ablation.
- Next: discuss framing with supervisors (negative AL result + positive operational-safety result), check conformal coverage
  and pseudo-label accuracy, then write-up.

## 2026-10-04 · All experiments done (2 110 / 2 110)

- Check run (worker acc9, T4, updated config/runner/analysis on Drive): E4 already 880/880 at start; the last
  2 jobs had been finished by an earlier worker. Worker found 0 jobs to do. All four experiments complete.
- Next: notebook 04 (analysis), then write-up.

## 2026-10-04 · E4 run: 878 / 880 done

- 8 workers ran E4. Status in the one runtime with the new config: 878 done of 880, 2 claims still "running".
- Most runtimes still had the old config (total 990), so they also ran S. aureus-oxacillin at DRIAMS-D.
  Hybrid/diversity jobs there failed (PCA on 0 rows); other strategies wrote results that are meaningless (no labels).
- A failed job keeps its claim, so it shows as "running" until the 3-hour TTL, then as "stale" and is retried.
- Fix: `analysis.load` now keeps only results whose job id is in the current design (`runner.all_jobs`), so
  the skipped S. aureus-D results are ignored. Self-test 17/17.
- Next: one worker with the updated code to finish the last 2 jobs, then status must show E4 880/880.

## 2026-10-04 · Target-site audit for E4

| Pair | DRIAMS-B n (R, %R) | DRIAMS-C n (R, %R) | DRIAMS-D n (R, %R) |
|---|---|---|---|
| ecoli_cro | 213 (45, 21.1%) | 916 (151, 16.5%) | 1 994 (198, 9.9%) |
| kpneu_cro | 152 (18, 11.8%) | 366 (55, 15.0%) | 2 151 (123, 5.7%) |
| saur_oxa | 346 (21, 6.1%) | 738 (41, 5.6%) | **0** |

- DRIAMS-D has no labelled S. aureus–oxacillin isolates → combination removed from E4 (`skip` in config; 110 jobs),
  E4 = 880 jobs. Self-test 17/17 after the change.
- Very few resistant isolates at DRIAMS-B (18-45) and for S. aureus everywhere: after the 50/50 pool/test split the
  test sets hold about 9-23 resistant isolates, so AUROC/VME there are noisy; report with confidence intervals and
  flag as low-power. At B the pool (76-173 isolates) is smaller than the largest budgets, so budgets 200/400 equal
  "label everything".
- The share of resistant isolates differs strongly between hospitals (e.g. K. pneumoniae 5.7% at D vs 13.9% at A in
  2018): label shift is part of the cross-site problem.
- Before relaunching: upload the new `amr_al/config.py` and `amr_al/runner.py` to Drive.

## 2026-10-04 · E1, E3, E2 complete; DRIAMS-B/C/D downloaded

- Status: E1_temporal 660/660, E3_routing 180/180, E2_semisup 390/390 done, 0 stale. One worker: 154 jobs in
  1.72 h (about 40 s per job on a T4).
- E4_crosssite showed 990 "running": workers had reached E4 before the B/C/D data existed, the jobs failed, and their
  claim files remained (they would expire after 3 h). Decision: delete the E4 claim folder, check pair counts at
  B/C/D, then run E4 in all accounts.
- DRIAMS-B/C/D (2018 only), streamed on a CPU runtime:

  | Site | Archive | Stream time | Spectra with labels | Notes |
  |---|---|---|---|---|
  | DRIAMS-B | 3.69 GB | 4.3 min | 2 386 | 3 511 label rows had no spectrum in the archive |
  | DRIAMS-C | 12.43 GB | 15.2 min | 4 696 | 41 spectra had no label row |
  | DRIAMS-D | 42.56 GB | 47.6 min | 10 436 | perfect match |

  No acquisition dates at any site. Whole compact copy (A-D): 1.5 GB. DRIAMS-B is small and 60% of its label
  rows lack a spectrum: report its cross-site results with that caveat.

## 2026-10-04 · Workers started; parallel-safety note

- All 8 workers started (acc1..acc8, SHARD 0..7, N_SHARDS 8, HOURS 11-12). EXPERIMENTS was left at None, so E4
  jobs will fail quickly until DRIAMS-B/C/D are downloaded; their claims expire after 3 h and they rerun later.
- Concurrency design: no locks are held, so no deadlock is possible (a worker skips a claimed job, it never
  waits). Results are written atomically (temp file, then rename). Shards keep workers on separate jobs; overlap
  is only possible at the end, when workers help each other, and Drive's cross-account sync delay can then let two
  workers run the same job. Each job is deterministic, so both write the same numbers; `analysis.load` now counts
  each job id once (commit a5905a2; self-test 17/17). `amr_al/analysis.py` must be re-uploaded to Drive before
  notebook 04.

## 2026-10-03 · Worker plan

- 8 Colab accounts run notebook 03 in parallel: WORKER acc1..acc8, SHARD 0..7, N_SHARDS = 8, HOURS = 3.5.
- EXPERIMENTS = ["E1_temporal", "E3_routing", "E2_semisup"] (1 230 jobs) until DRIAMS-B/C/D are downloaded;
  E4 (990 jobs) added afterwards.
- Expected: about 1 min per job on a T4 → roughly 150 jobs per worker per 3.5 h session; the 1 230 core jobs in
  about one round of sessions across 8 accounts.

## 2026-10-03 · Notebook 02: audit, tuning, premise check (T4)

**Labelled isolates per pair and year (% resistant):**

| Pair | 2015 | 2016 | 2017 (pool) | 2018 (test) |
|---|---|---|---|---|
| ecoli_cro | 97 (27.8%) | 1 384 (24.4%) | 2 094 (22.2%) | 1 386 (18.5%) |
| kpneu_cro | 47 (23.4%) | 765 (19.5%) | 1 273 (14.2%) | 775 (13.9%) |
| saur_oxa | 74 (21.6%) | 1 067 (24.6%) | 1 445 (18.8%) | 1 204 (14.6%) |

The share of resistant isolates falls every year for all three pairs (label shift as well as spectral drift).
For K. pneumoniae the largest budget (800) is 63% of the 2017 pool, so B = 800 is close to "full".

**Tuning** (3-fold CV AUROC on 2015-16 only, 16 combinations, 8-36 s each on T4):

| Pair | colsample_bytree | learning_rate | max_depth | n_estimators | CV AUROC (sd) |
|---|---|---|---|---|---|
| ecoli_cro | 0.3 | 0.05 | 6 | 300 | 0.887 (0.024) |
| kpneu_cro | 0.3 | 0.05 | 4 | 600 | 0.726 (0.025) |
| saur_oxa | 0.1 | 0.05 | 4 | 600 | 0.892 (0.016) |

Differences between the top settings are well inside one standard deviation; learning rate 0.05 wins everywhere.

**Premise check** (seed 0; AUROC):

| Pair | in-period CV 2015-16 | 2018, no retraining | 2018, retrained with all 2017 | gap retraining can close |
|---|---|---|---|---|
| ecoli_cro | 0.881 | 0.824 | 0.872 | +0.048 |
| kpneu_cro | 0.751 | 0.733 | 0.791 | +0.057 |
| saur_oxa | 0.896 | 0.799 | 0.841 | +0.042 |

- All three gaps are above the 0.02 cut-off → **premise holds; E1 goes ahead.**
- Decay 2015-16 → 2018 without retraining: −0.057 (E. coli), −0.018 (K. pneumoniae, weak model to begin with),
  −0.097 (S. aureus). AUPRC drops more (e.g. E. coli 0.75 on 2017 batch 1 → 0.64 on 2018).
- The 2017 pseudo-batches differ by up to ±0.04 AUROC from one another: noise from random batching, not time.
- Observation: the threshold chosen for 90% sensitivity on 2015-16 validation gives VME 0.18-0.34 on 2018
  (sensitivity 66-82%), i.e. the decision threshold drifts too. With full retraining the S. aureus VME even rises
  (0.20 → 0.34) while ME falls (0.44 → 0.17). AUROC/AUPRC are unaffected (threshold-free). To discuss: re-choose
  the threshold on recent labelled data (e.g. bought labels) as an ablation.

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
