"""Get DRIAMS from Dryad without storing the huge archives.

Dryad serves each site as one .tar.gz (DRIAMS-A is ~86 GB). Downloads need a
free Dryad API account (ORCID login -> "My account" -> API account), which
gives a client id and secret; a token made from them lasts 10 hours.

We stream the archive once, keep only the pre-binned spectra
(<site>/binned_6000/<year>/<code>.txt) and the label files
(<site>/id/<year>/<year>_clean.csv), and write a compact copy:

    data/driams_compact/<SITE>/<YEAR>/X.npy     float16, spectra * X_SCALE
    data/driams_compact/<SITE>/<YEAR>/meta.csv  one row per spectrum, same order as X
    data/driams_compact/<SITE>/MANIFEST.json    counts and checks
"""
import hashlib
import io
import json
import os
import tarfile
import time

import numpy as np
import pandas as pd

from . import config, paths


# ------------------------------------------------------------------ Dryad API
def get_token(client_id, client_secret):
    import requests
    r = requests.post(config.DRYAD_BASE + "/oauth/token",
                      data=dict(client_id=client_id, client_secret=client_secret,
                                grant_type="client_credentials"), timeout=60)
    r.raise_for_status()
    return r.json()["access_token"]


def test_token(token):
    import requests
    r = requests.get(config.DRYAD_BASE + "/api/v2/test",
                     headers={"Authorization": "Bearer " + token, "Accept": "application/json"}, timeout=60)
    print(r.status_code, r.text[:200])
    return r.status_code == 200


def list_files():
    """Files of the latest DRIAMS version: {name: {size_gb, url}} (public metadata, no token)."""
    import requests
    from urllib.parse import quote
    base = config.DRYAD_BASE
    v = requests.get(f"{base}/api/v2/datasets/{quote(config.DRYAD_DOI, safe='')}/versions", timeout=60).json()
    last = v["_embedded"]["stash:versions"][-1]
    page, files = base + last["_links"]["stash:files"]["href"], {}
    while page:
        r = requests.get(page, timeout=60).json()
        for f in r["_embedded"]["stash:files"]:
            files[f["path"]] = dict(size_gb=f["size"] / 1e9, url=base + f["_links"]["stash:download"]["href"])
        nxt = r.get("_links", {}).get("next", {}).get("href")
        page = base + nxt if nxt else None
    return files


def archive_name(site):
    return site.replace("-", "_") + ".tar.gz"          # "DRIAMS-A" -> "DRIAMS_A.tar.gz"


# ------------------------------------------------------------------ streaming
class _Progress(io.RawIOBase):
    """File-like wrapper that counts bytes and prints progress every `every` seconds."""

    def __init__(self, raw, total, every=60, extra=lambda: ""):
        self.raw, self.total, self.every, self.extra = raw, total, every, extra
        self.n, self.t0, self.last = 0, time.time(), 0.0

    def readable(self):
        return True

    def readinto(self, b):
        data = self.raw.read(len(b))
        if not data:
            return 0
        b[:len(data)] = data
        self.n += len(data)
        now = time.time()
        if now - self.last > self.every:
            self.last = now
            rate = self.n / max(now - self.t0, 1e-9)
            eta = (self.total - self.n) / rate / 60 if self.total else float("nan")
            print(f"  {self.n/1e9:7.2f} / {self.total/1e9:.2f} GB  {rate/1e6:6.1f} MB/s  "
                  f"ETA {eta:5.1f} min  {self.extra()}", flush=True)
        return len(data)


def _open_source(site, token=None, local_path=None):
    """Return (file-like, total_bytes, closer)."""
    if local_path:
        f = open(local_path, "rb")
        return f, os.path.getsize(local_path), f.close
    import requests
    files = list_files()
    name = archive_name(site)
    if name not in files:
        raise FileNotFoundError(f"{name} not in Dryad listing: {sorted(files)}")
    r = requests.get(files[name]["url"], headers={"Authorization": "Bearer " + token},
                     stream=True, allow_redirects=True, timeout=(60, 600))
    if r.status_code != 200:
        raise RuntimeError(f"download failed: HTTP {r.status_code} {r.text[:300]}")
    total = int(r.headers.get("Content-Length", 0)) or int(files[name]["size_gb"] * 1e9)
    r.raw.decode_content = False
    return r.raw, total, r.close


def peek(site, token=None, local_path=None, n=60):
    """Print the first n member names of the archive (downloads only a little)."""
    src, total, close = _open_source(site, token, local_path)
    try:
        with tarfile.open(fileobj=src, mode="r|gz") as tar:
            for i, m in enumerate(tar):
                print(("DIR " if m.isdir() else "    ") + m.name)
                if i + 1 >= n:
                    break
    finally:
        close()


def parse_binned(raw_bytes):
    """Parse one DRIAMS binned spectrum text file -> float32 vector (last column)."""
    if b"#" in raw_bytes:
        raw_bytes = b"\n".join(l for l in raw_bytes.splitlines() if not l.lstrip().startswith(b"#"))
    lines = raw_bytes.split(b"\n", 2)
    first = lines[0].split()
    try:
        [float(t) for t in first]
        body = raw_bytes
    except ValueError:                                  # header line such as "bin_index binned_intensity"
        body = raw_bytes.split(b"\n", 1)[1] if b"\n" in raw_bytes else b""
    first_data = body.split(b"\n", 1)[0].split()
    ncol = max(len(first_data), 1)
    vals = np.array(body.split(), dtype=np.float64)
    return vals.reshape(-1, ncol)[:, -1].astype(np.float32)


def fetch_site(site, token=None, local_path=None, out_root=None, years=None, retries=1):
    """Stream one site's archive and write the compact copy. Returns the manifest dict."""
    out_root = out_root or paths.DATA
    for attempt in range(retries + 1):
        try:
            return _fetch_once(site, token, local_path, out_root, years)
        except (OSError, EOFError, tarfile.TarError, RuntimeError) as e:
            print(f"!! attempt {attempt+1} failed: {e!r}")
            if attempt == retries:
                raise
            print("   retrying from the start in 30 s (a gzip stream cannot resume mid-way)")
            time.sleep(30)


def _fetch_once(site, token, local_path, out_root, years):
    st = config.SPECTRA_TYPE
    spectra = {}          # year -> {code: float16 vector}
    id_files = {}         # year -> {filename: bytes}
    bad = []
    src, total, close = _open_source(site, token, local_path)
    counter = {"n": 0}
    reader = _Progress(src, total, extra=lambda: f"{counter['n']} spectra kept")
    t0 = time.time()
    print(f"streaming {site} ({total/1e9:.1f} GB compressed)")
    try:
        with tarfile.open(fileobj=io.BufferedReader(reader, 4 << 20), mode="r|gz") as tar:
            for m in tar:
                if not m.isfile():
                    continue
                parts = m.name.replace("\\", "/").split("/")
                if st in parts and m.name.endswith(".txt"):
                    i = parts.index(st)
                    if i + 1 >= len(parts) - 1:
                        continue
                    year = parts[i + 1]
                    if years and year not in years:
                        continue
                    code = os.path.splitext(parts[-1])[0]
                    vec = parse_binned(tar.extractfile(m).read())
                    if vec.shape[0] != config.N_BINS or not np.isfinite(vec).all():
                        bad.append(m.name)
                        continue
                    spectra.setdefault(year, {})[code] = (vec * config.X_SCALE).astype(np.float16)
                    counter["n"] += 1
                elif "id" in parts and m.name.endswith(".csv"):
                    i = parts.index("id")
                    year = parts[i + 1] if i + 1 < len(parts) - 1 else "unknown"
                    id_files.setdefault(year, {})[parts[-1]] = tar.extractfile(m).read()
    finally:
        close()
    print(f"stream done in {(time.time()-t0)/60:.1f} min: {counter['n']} spectra, {len(bad)} unreadable")
    return _write_compact(site, spectra, id_files, bad, out_root)


def _pick_id_file(files, year):
    for name in [f"{year}_clean.csv", f"{year}.csv"]:
        if name in files:
            return name
    cands = sorted(k for k in files if "clean" in k) or sorted(files)
    return cands[0] if cands else None


def _write_compact(site, spectra, id_files, bad, out_root):
    manifest = dict(site=site, created=time.strftime("%Y-%m-%d %H:%M"), spectra_type=config.SPECTRA_TYPE,
                    x_scale=config.X_SCALE, dtype="float16", years={}, unreadable=len(bad),
                    unreadable_examples=bad[:5])
    for year in sorted(set(spectra) | set(id_files)):
        spec = spectra.get(year, {})
        files = id_files.get(year, {})
        idname = _pick_id_file(files, year)
        info = dict(n_spectra=len(spec), id_file=idname, id_files_seen=sorted(files))
        if not idname or not spec:
            info["skipped"] = "no id file" if not idname else "no spectra"
            manifest["years"][year] = info
            print(f"  {site} {year}: skipped ({info['skipped']})")
            continue
        meta = pd.read_csv(io.BytesIO(files[idname]), low_memory=False)
        meta["code"] = meta["code"].astype(str)
        n_rows = len(meta)
        meta = meta.drop_duplicates("code")
        have = meta["code"].isin(spec)
        meta = meta[have].reset_index(drop=True)
        X = np.stack([spec[c] for c in meta["code"]]).astype(np.float16)
        out = os.path.join(out_root, site, year)
        os.makedirs(out, exist_ok=True)
        np.save(os.path.join(out, "X.npy"), X)
        meta.to_csv(os.path.join(out, "meta.csv"), index=False)
        info.update(n_id_rows=n_rows, n_matched=len(meta), n_id_without_spectrum=int((~have).sum()),
                    n_spectra_without_id=len(spec) - len(meta),
                    has_acquisition_date="acquisition_date" in meta.columns,
                    columns=list(meta.columns)[:12] + (["..."] if meta.shape[1] > 12 else []),
                    fingerprint=hashlib.sha1("\n".join(sorted(meta["code"])).encode()).hexdigest()[:12])
        manifest["years"][year] = info
        print(f"  {site} {year}: {len(meta)} spectra with labels "
              f"({info['n_id_without_spectrum']} id rows had no spectrum, "
              f"{info['n_spectra_without_id']} spectra had no id row)")
    os.makedirs(os.path.join(out_root, site), exist_ok=True)
    with open(os.path.join(out_root, site, "MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    return manifest


def verify_compact(site, out_root=None, n_check=200):
    """Reload what was written and check shapes, finiteness and float16 round-trip error."""
    out_root = out_root or paths.DATA
    with open(os.path.join(out_root, site, "MANIFEST.json")) as f:
        man = json.load(f)
    ok = True
    for year, info in man["years"].items():
        if "skipped" in info:
            continue
        d = os.path.join(out_root, site, year)
        X = np.load(os.path.join(d, "X.npy"), mmap_mode="r")
        meta = pd.read_csv(os.path.join(d, "meta.csv"), low_memory=False)
        good = X.shape == (len(meta), config.N_BINS) and np.isfinite(np.asarray(X[:n_check], np.float32)).all()
        print(f"  {site} {year}: X {X.shape}, meta {meta.shape}, finite={good}")
        ok &= good
    return ok
