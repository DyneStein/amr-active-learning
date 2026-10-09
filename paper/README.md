# Paper build

Single-column, Computer Modern, LaTeX-style PDF produced without a TeX installation.

    python paper_data.py     # caches the result tables from Results/results
    python pfig.py           # data figures  -> fig/f3..f11.svg
    python pdiag.py          # schematics    -> fig/f1_loop.svg, fig/f2_data.svg
    python paper.py          # -> paper.html (set PAPER_OUT to write it elsewhere)
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
        --no-pdf-header-footer --print-to-pdf=paper_raw.pdf file://$PWD/paper.html
    python stamp.py paper_raw.pdf AMR_Paper_Draft.pdf   # centred page numbers

`fonts/` holds the Computer Modern faces (KaTeX_Main), embedded as base64 in the HTML so the
build is self-contained; `fig/` holds the figures. Both are found relative to this folder, so the
build works from any working directory. Figure colours were checked for colour blind separation
before use.

House style, kept deliberately: no em dashes, no en dashes, no line-break hyphenation, and no
colour chrome in the body. The prose was rewritten on 9 Oct 2026 to match the voice of the group's
earlier submission rather than the even cadence it had before; the numbers were checked afterwards
and every figure in the old draft still appears in the new one.
