# Active learning for maintaining MALDI-TOF AMR predictors

Experiments on the DRIAMS dataset (Weis et al., *Nature Medicine* 2022). A model that
predicts antibiotic resistance from MALDI-TOF spectra loses accuracy over time and
across hospitals. The question: when a lab can only afford a limited number of
phenotypic tests, which new isolates should it test so that the retrained model
recovers as much accuracy as possible?

## Experiments

| ID | Question | Setting | Varies | Jobs |
|---|---|---|---|---|
| E1_temporal | RQ1, RQ2: labels needed over time; uncertainty vs diversity vs hybrid | DRIAMS-A: train 2015–16, pool 2017 (4 batches), test 2018 | 4 strategies × 5 budgets × 10 seeds, plus no-retraining and full-retraining bounds | 660 |
| E3_routing | RQ5: testing only isolates the model is unsure about (conformal sets) | as E1 | capped and uncapped routing | 180 |
| E2_semisup | RQ3: paid labels vs pseudo-labels on untested spectra | as E1 | 3 strategies + pseudo-labels, pseudo-labels alone | 390 |
| E4_crosssite | RQ4: a model trained at DRIAMS-A deployed at B, C, D | train A (2015–18); target 2018 split 50/50 into pool and test | 4 strategies × 5 budgets × 5 seeds, plus bounds | 990 |

Pairs: *E. coli*–ceftriaxone, *K. pneumoniae*–ceftriaxone, *S. aureus*–oxacillin.
Model: XGBoost (GPU when available), with hyper-parameters tuned on 2015–16 only.
Metrics: AUROC, AUPRC, very major error rate (resistant reported as susceptible),
major error rate, and error counts among isolates that were not sent for testing.
All settings are in `amr_al/config.py`.

## Layout

```
amr_al/          package: data download, splits, models, strategies, job runner, analysis
notebooks/       00 setup and GPU test · 01 data · 02 audit and tuning · 03 worker · 04 results
docs/            Colab setup guide (PDF)
make_notebooks.py  regenerates notebooks/
```

## Running

The experiments run on Google Colab from a Google Drive folder shared between
several accounts. Every job saves its progress after each round, so a disconnected
session resumes where it stopped, and several accounts can work through the job list
at the same time. Step-by-step instructions: `docs/Colab_Setup_Guide.pdf`.

## Data

DRIAMS on Dryad, doi:10.5061/dryad.bzkh1899q (CC0). Downloading needs a free Dryad
API account. Notebook 01 streams each archive once and keeps only the 6000-bin spectra
and the label files (DRIAMS-A: 86 GB archive, about 2–4 GB kept). Labels follow the
dataset authors' encoding: R and I are resistant, S is susceptible.

Weis C, Cuénod A, Rieck B, et al. Direct antimicrobial resistance prediction from
clinical MALDI-TOF mass spectra using machine learning. *Nat Med* 28, 164–174 (2022).
doi:10.1038/s41591-021-01619-9

## Test without real data

```
pip install -r requirements.txt
python -c "from amr_al import selftest; selftest.run()"
```

This builds a small synthetic dataset in the DRIAMS layout and runs the whole pipeline
(download path, audit, tuning, all four experiments, crash and resume, analysis).
