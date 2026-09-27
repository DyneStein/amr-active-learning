"""Where everything lives.

ROOT is the shared Drive folder (default /content/drive/MyDrive/AMR_AL).
Set the environment variable AMR_AL_ROOT to use another location
(the local tests do this).
"""
import os

ROOT = os.environ.get("AMR_AL_ROOT", "/content/drive/MyDrive/AMR_AL")
LOCAL_CACHE = os.environ.get("AMR_AL_LOCAL", "/content/amr_local")   # fast Colab disk, not shared


def p(*parts):
    return os.path.join(ROOT, *parts)


DATA = p("data", "driams_compact")          # compact spectra + labels (shared)
CONFIG_DIR = p("config")                    # tuned hyper-parameters, data audit
RESULTS = p("results")                      # one JSON per finished job
CHECKPOINTS = p("checkpoints")              # per-round progress of unfinished jobs
CLAIMS = p("claims")                        # which worker is running which job
LOGS = p("logs")
FIGURES = p("figures")
TABLES = p("tables")


def ensure_dirs():
    for d in [DATA, CONFIG_DIR, RESULTS, CHECKPOINTS, CLAIMS, LOGS, FIGURES, TABLES]:
        os.makedirs(d, exist_ok=True)


def set_root(root, local_cache=None):
    """Point the package at a different root (used by tests)."""
    global ROOT, DATA, CONFIG_DIR, RESULTS, CHECKPOINTS, CLAIMS, LOGS, FIGURES, TABLES, LOCAL_CACHE
    ROOT = root
    if local_cache:
        LOCAL_CACHE = local_cache
    DATA = p("data", "driams_compact"); CONFIG_DIR = p("config"); RESULTS = p("results")
    CHECKPOINTS = p("checkpoints"); CLAIMS = p("claims"); LOGS = p("logs")
    FIGURES = p("figures"); TABLES = p("tables")
