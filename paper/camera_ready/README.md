# Camera ready version (ICIC 2026, paper 280)

- `build.py` takes the text of the submitted paper (`../ieee.py`) and applies only the passages listed in
  `revisions.py`, then writes `main.tex` (IEEEtran, A4). Compile with `tectonic main.tex` or pdfLaTeX.
- `PID280.pdf` is the compiled paper and `PID280_latex.zip` the LaTeX project (main.tex, IEEEtran.cls, figures).
- `response.tex` / `response.pdf` is the reply to the reviewers.
- `stats/` holds the recomputation of the paired tests (`camera_ready_stats.py`) and the analysis of the
  robustness rerun (`camera_ready_robust.py`, input `R1_batching_runs.csv` from notebook 06), with their outputs.
