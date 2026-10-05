"""All experiment settings in one place.

Edit this file (in the shared Drive folder) to change what runs. Every
Colab account reads the same file, so all workers stay consistent.
"""

# ---------------------------------------------------------------- data
DRYAD_DOI = "doi:10.5061/dryad.bzkh1899q"          # DRIAMS, Weis et al., Nat Med 2022
DRYAD_BASE = "https://datadryad.org"
SPECTRA_TYPE = "binned_6000"                       # 6000 bins, 2000-20000 Da, 3 Da wide
N_BINS = 6000
X_SCALE = 1e4          # spectra are TIC-normalised (~1e-4 per bin); scaled before float16 storage

# species / antibiotic pairs studied (names exactly as in the DRIAMS id files)
PAIRS = {
    "ecoli_cro": ("Escherichia coli", "Ceftriaxone"),
    "kpneu_cro": ("Klebsiella pneumoniae", "Ceftriaxone"),
    "saur_oxa": ("Staphylococcus aureus", "Oxacillin"),
}

# label encoding used by the DRIAMS authors (maldi-learn DRIAMSLabelEncoder):
# resistant and intermediate -> 1, susceptible -> 0, anything else -> dropped
LABEL_MAP = {"R": 1, "I": 1, "S": 0}

# ---------------------------------------------------------------- temporal split (RQ1-RQ3, RQ5)
TRAIN_YEARS = ["2015", "2016"]
POOL_YEAR = "2017"            # arrives in N_ROUNDS batches (quarters if acquisition dates exist)
TEST_YEAR = "2018"
N_ROUNDS = 4
VAL_FRACTION = 0.2            # held out from the training years: threshold + conformal calibration

# ---------------------------------------------------------------- cross-site split (RQ4)
SOURCE_SITE = "DRIAMS-A"
SOURCE_YEARS = ["2015", "2016", "2017", "2018"]
TARGET_SITES = ["DRIAMS-B", "DRIAMS-C", "DRIAMS-D"]
TARGET_YEAR = "2018"
TARGET_TEST_FRACTION = 0.5    # target-site isolates held out for testing
TARGET_LABEL_WEIGHT = 1.0     # sample weight of newly bought target-site labels

# ---------------------------------------------------------------- decision threshold
# threshold chosen on the validation set so that sensitivity for "resistant" >= this;
# keeps very major errors (true R reported as S) low, as a lab would require
TARGET_SENSITIVITY = 0.90

# ---------------------------------------------------------------- model
MODEL = "xgb"                 # "xgb" (GPU if available) or "lr" (logistic regression, CPU)
XGB_DEFAULT = dict(n_estimators=300, max_depth=6, learning_rate=0.1,
                   subsample=0.8, colsample_bytree=0.3, min_child_weight=1,
                   reg_lambda=1.0)
TUNING_GRID = {"max_depth": [4, 6], "learning_rate": [0.05, 0.1],
               "n_estimators": [300, 600], "colsample_bytree": [0.1, 0.3]}
NEW_LABEL_WEIGHT = 1.0        # sample weight for labels bought during active learning

# ---------------------------------------------------------------- selection strategies
PCA_DIM = 50                  # embedding for diversity / hybrid
HYBRID_POOL_FACTOR = 4        # hybrid: take the 4*b most uncertain, then pick b diverse ones
CONFORMAL_ALPHA = 0.10        # RQ5 routing: 90% conformal prediction sets (per class)
SSL_P_HIGH, SSL_P_LOW = 0.95, 0.05   # RQ3 pseudo-label confidence cut-offs
SSL_WEIGHT = 0.5              # sample weight of pseudo-labels

# ---------------------------------------------------------------- experiments
# budgets are TOTAL labels bought over the pool period (split evenly across rounds).
# 0 = never retrain, "all" = label every arriving isolate (full retraining upper bound).
BUDGETS = [40, 100, 200, 400, 800]
SEEDS = list(range(10))

EXPERIMENTS = {
    # RQ1 + RQ2: label efficiency over time, uncertainty vs diversity vs hybrid
    "E1_temporal": dict(setting="temporal", pairs=list(PAIRS),
                        strategies=["random", "uncertainty", "diversity", "hybrid"],
                        budgets=BUDGETS, seeds=SEEDS, include_bounds=True),
    # RQ5: safety routing (test only isolates the model is unsure about) as a selection rule
    "E3_routing": dict(setting="temporal", pairs=list(PAIRS),
                       strategies=["routing_all", "routing"],
                       budgets=BUDGETS, seeds=SEEDS, include_bounds=False),
    # RQ3: paid labels vs free unlabelled spectra (pseudo-labels), alone and combined
    "E2_semisup": dict(setting="temporal", pairs=list(PAIRS),
                       strategies=["ssl_only", "random+ssl", "uncertainty+ssl", "hybrid+ssl"],
                       budgets=[100, 200, 400, 800], seeds=SEEDS, include_bounds=False),
    # RQ4: a hospital adopts a model trained elsewhere; how few local labels close the gap
    "E4_crosssite": dict(setting="crosssite", pairs=list(PAIRS),
                         strategies=["random", "uncertainty", "diversity", "hybrid"],
                         budgets=[25, 50, 100, 200, 400], seeds=list(range(5)),
                         include_bounds=True, sites=TARGET_SITES,
                         # DRIAMS-D has no labelled S. aureus-oxacillin isolates (audit, 4 Oct 2026)
                         skip=[("saur_oxa", "DRIAMS-D")]),
    # Ablation after the first results (5 Oct 2026): the 2015-16 threshold and conformal bounds did not hold on
    # 2017-18. Here a quarter of the bought labels is kept out of training and used, with the validation set,
    # to re-set the threshold and conformal bounds every round. Compared with the same E1 runs (paired by seed).
    "E5_recal": dict(setting="temporal", pairs=list(PAIRS), strategies=["random", "uncertainty"],
                     budgets=[100, 400, 800], seeds=SEEDS, include_bounds=True, recal=True),
    # Combination search on the development split (pool = 2017 batches 1-2, test = 2017 batches 3-4; 2018 untouched).
    # Codes: see COMBOS below and docs/AMR_AL_Catalogues.pdf. Winners are frozen in RESEARCH_LOG before any 2018 run.
    "D1_dev": dict(setting="dev", pairs=list(PAIRS),
                   strategies=["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08",
                               "D09", "D10", "D11", "D12", "D13", "D14", "D15", "D16"],
                   budgets=[100, 300], seeds=[100, 101, 102, 103, 104], include_bounds=True),
}
RECAL_FRACTION = 0.25         # E5: share of bought labels used only for re-calibration
RECAL_MIN_R = 10              # E5: re-calibrate on new labels alone once they hold this many resistant isolates
PSEUDO_ALPHA = 0.05           # combinations: 95% prediction sets for conformal pseudo-labels

# Combinations (catalogue AL-E shortlist). sel / mix / w_new / iw / cal / pseudo are explained in amr_al/combo.py.
COMBO_DEFAULTS = dict(sel="random", mix=0.0, w_new=1.0, iw=False, cal="old", pseudo="none")
COMBOS = {
    "D01": dict(sel="random"),                                              # anchor = E1 random
    "D02": dict(sel="uncertainty"),                                         # anchor = E1 uncertainty
    "D03": dict(sel="random", cal="holdout"),                               # anchor = E5 random
    "D04": dict(sel="vmerisk"),                                             # new selection rule alone
    "D05": dict(sel="uncertainty", mix=0.5),                                # mixing alone
    "D06": dict(sel="uncertainty", mix=0.5, cal="rand_preq"),               # core: mix + prequential re-calibration
    "D07": dict(sel="vmerisk", mix=0.5, cal="rand_preq"),                   # core with VME-risk
    "D08": dict(sel="uncertainty", mix=0.5, cal="rand_hold"),               # random share held out instead
    "D09": dict(sel="uncertainty", mix=0.5, cal="rand_preq", w_new=3.0),    # + recency weight
    "D10": dict(sel="uncertainty", mix=0.5, cal="rand_preq", iw=True),      # + importance weights
    "D11": dict(sel="uncertainty", mix=0.5, cal="rand_preq", pseudo="conformal"),  # + certified pseudo-labels
    "D12": dict(sel="vmerisk", mix=0.5, cal="rand_preq", w_new=3.0),        # VME-risk + recency
    "D13": dict(sel="vmerisk", mix=0.1, cal="weighted"),                    # 90/10 + weighted conformal
    "D14": dict(sel="vmerisk", mix=0.5, cal="aci"),                         # adaptive calibration
    "D15": dict(sel="hybrid", mix=0.5, cal="rand_preq"),                    # hybrid core
    "D16": dict(sel="novelty", mix=0.5, cal="rand_preq"),                   # drift-novelty core
}
# order in which workers pick up experiments (core paper first)
PRIORITY = ["E1_temporal", "E3_routing", "E2_semisup", "E4_crosssite", "E5_recal", "D1_dev"]

# ---------------------------------------------------------------- workers
CLAIM_TTL_HOURS = 3.0         # a claimed-but-unfinished job becomes free again after this
CLAIM_CONFIRM_SECONDS = 2.0   # wait, then re-read the claim to make sure another worker did not take it
