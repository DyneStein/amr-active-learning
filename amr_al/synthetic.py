"""A small fake DRIAMS archive with the same layout, for testing the pipeline end to end.

Resistant isolates get extra intensity at a few bins; the signal drifts a little
each year and differs between sites, so decay and cross-site shift both exist.
"""
import io
import os
import tarfile
import uuid

import numpy as np
import pandas as pd

from . import config

SPECIES = [("Escherichia coli", 0.35), ("Klebsiella pneumoniae", 0.2),
           ("Staphylococcus aureus", 0.3), ("Enterococcus faecalis", 0.15)]
R_RATE = {"Escherichia coli": 0.2, "Klebsiella pneumoniae": 0.25, "Staphylococcus aureus": 0.2}


def _spectrum(rng, species_i, resistant, year_shift, site_scale):
    x = rng.gamma(0.6, 1.0, config.N_BINS)
    base = 400 + 900 * species_i
    x[base:base + 40] += 30                       # species peak
    if resistant:
        start = 2500 + 7 * species_i + year_shift  # resistance marker drifts with time
        x[start:start + 6] += 14 * site_scale
    x = np.maximum(x, 0)
    return x / x.sum()


def make_archive(path, site, years, n_per_year, seed=0, with_dates=True, extra_dirs=True):
    rng = np.random.default_rng(seed)
    site_scale = {"DRIAMS-A": 1.0, "DRIAMS-B": 0.7, "DRIAMS-C": 0.8, "DRIAMS-D": 0.6}.get(site, 1.0)
    with tarfile.open(path, "w:gz") as tar:
        def add(name, payload):
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))

        for yi, year in enumerate(years):
            rows = []
            for _ in range(n_per_year):
                si = rng.choice(len(SPECIES), p=[w for _, w in SPECIES])
                sp = SPECIES[si][0]
                code = str(uuid.UUID(int=int(rng.integers(1 << 62)) << 64 | int(rng.integers(1 << 62))))
                res = rng.random() < R_RATE.get(sp, 0.1)
                x = _spectrum(rng, si, res, year_shift=3 * yi, site_scale=site_scale)
                body = "bin_index binned_intensity\n" + "\n".join(f"{i} {v:.6g}" for i, v in enumerate(x))
                add(f"{site}/binned_6000/{year}/{code}.txt", body.encode())
                if extra_dirs and rng.random() < 0.1:
                    add(f"{site}/binned_6000_warped/{year}/{code}.txt", b"ignore me")
                    add(f"{site}/raw/{year}/{code}.txt", b"# raw spectrum\n1 2\n")
                lab = "R" if res else "S"
                if rng.random() < 0.05:
                    lab = rng.choice(["I", "-", "R(1)"])
                row = dict(code=code, species=sp, laboratory_species=sp,
                           Ceftriaxone=lab if sp != "Staphylococcus aureus" else "-",
                           Oxacillin=lab if sp == "Staphylococcus aureus" else "-",
                           Meropenem=rng.choice(["S", "S", "-"]))
                if with_dates:
                    row["acquisition_date"] = f"{year}-{rng.integers(1, 13):02d}-{rng.integers(1, 28):02d}"
                rows.append(row)
            df = pd.DataFrame(rows)
            add(f"{site}/id/{year}/{year}_clean.csv", df.to_csv(index=False).encode())
            add(f"{site}/id/{year}/{year}_strat.csv", df.head(5).to_csv(index=False).encode())
    return path
