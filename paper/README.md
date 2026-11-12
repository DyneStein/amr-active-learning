# Paper build

Two builds live here. `paper.py` makes the long single column version for a journal, and
`ieee.py` makes the six page IEEE two column version for ICIC 2026 (`Conf_ICIC26_Asif.pdf`).

## Conference version

    python ../../../..  # nothing to install; see the venv note below
    python ifig.py            # data figures  -> ifig/f2_curves.svg, f3_errors.svg, f4_shap.svg
    python pipeline.py        # schematic     -> ifig/f1_pipeline.svg and AMR_Pipeline.pdf
    python ieee.py            # -> ieee.html  (set IEEE_OUT to write it elsewhere)
    ANON=1 python ieee.py     # same paper with an anonymous author block, for a blind copy
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
        --no-pdf-header-footer --print-to-pdf=ieee_raw.pdf file://$PWD/ieee.html
    python stamp_icic.py ieee_raw.pdf Conf_ICIC26_Asif.pdf   # IEEE identifier, page 1 only

`ifig.py` reads `all_results.csv` (written by `paper_data.py` from `Results/results`) and the
two SHAP tables. Both paths are overridable with `AMR_CSV_DIR` and `AMR_SHAP_DIR`. The system
python has no pandas or matplotlib, so make a venv for `ifig.py` and `paper_data.py`;
`ieee.py`, `pipeline.py` and `stamp_icic.py` run on `/usr/bin/python3`.

## Single column version

    python paper_data.py; python pfig.py; python pdiag.py; python paper.py
    ... --print-to-pdf=paper_raw.pdf ...; python stamp.py paper_raw.pdf AMR_Paper_Draft.pdf

## House style, kept deliberately

No em dashes in the body (the two in `Abstract&mdash;` and `Keywords&mdash;` are required by the
ICIC template), no en dashes, no hyphenation at line breaks, no colour chrome in the body.
Figure colours were checked for colour blind separation before use. Sentences never open with a
numeral, which is why a few small numbers are spelled out where the rest of the paper uses digits.

## Prose

Rewritten 24 Oct 2026 against the Human Writing Kit. The twelve measures the paper deliberately
holds away from the middle of the human range are listed at the top of `ieee.py`. Numbers,
claims and the twenty references were checked against the previous build by diffing numeric
tokens. Three deliberate changes were made at that point:

- The resistant share of what uncertainty sampling bought at a 400 test budget is now the mean
  over ten seeds (14.9%, 9.7%, 10.8%) rather than the seed 0 figures from the selection log
  (17.2%, 10.2%, 12.8%) that the earlier draft quoted.
- The claim that major errors did not rise to compensate was wrong for *K. pneumoniae*, where
  they rose from 123.7 to 190.1 at a budget of 800. The result section and the discussion now
  report all three pairs, and Fig. 3 shows both error types.
- The references were rendering at body size because the `refs` class carried curly quotes in
  the HTML. They are now 8 pt as IEEE requires, and the list is numbered `[1]` with a hanging
  indent through a CSS counter rather than the browser's own `1.` from the `<ol>`.

## Venue limits (ICIC 2026)

Full paper deadline 25 Oct 2026 (extended twice, from 25 Sep and 11 Oct). Notification 13 Nov,
camera ready notification 20 Nov, registration 25 Nov, conference 2 and 3 Dec at UMT Lahore.
6 pages, 20 references, abstract under 250 words (currently 248), no page numbers, IEEE
identifier on page 1 only. The build asserts none of this, so check it after any edit.

Review is **single blind**: the Author Guidelines page says only "blind peer review", the
template mandates author metadata blocks, and the required filename
`Conf_ICIC26_<first author surname>` carries the surname, so an anonymous submission is not
possible. The author block stays. `ANON=1` exists only for venues that do ask for a blind copy;
the body has no self-citations, acknowledgements or funding note, so nothing else needs hiding.
