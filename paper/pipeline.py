# The study pipeline, drawn as a full width schematic.
# Writes ifig/f1_pipeline.svg for the paper and AMR_Pipeline.pdf as a standalone file,
# because the reviewers asked for the pipeline on its own as well as inside the paper.
#
# The three years are laid out as bands, the quarterly round is drawn once as the front card of
# a stack of four, and the two bounds (B = 0 and B = all) are dashed arms that bypass the stack,
# so that the reader can see what the acquisition rules are being compared against.
# Height is held at 224 units: at 7.2 in wide that is 2.23 in, which is what lets the figure and
# its caption sit on page 2 of the paper instead of being pushed to page 3.
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ifig")
os.makedirs(OUT, exist_ok=True)

W, H = 724, 224
SER = "'Times New Roman',Times,serif"
INK, LINE, MUT, FAINT = "#111111", "#333333", "#666666", "#9a9a9a"
BAND_END, BAND_MID = "#f4f6f8", "#fbfbfc"   # the 2015-16 and 2018 bands, and the 2017 band
FILL_KEY = "#eceff3"                        # the boxes a reader should land on first


def t(x, y, s, size=9.2, weight="400", anchor="middle", fill=INK, style=""):
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" font-family="{SER}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{st}>{s}</text>')


def box(x, y, w, h, lines, fill="#ffffff", dash=None, lead=10.4, size=9.2, stroke=LINE):
    """A rounded box with centred lines; the first line is the label, the rest are detail."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" '
         f'stroke="{stroke}" stroke-width="0.9"{d}/>')
    n = len(lines)
    y0 = y + h / 2 - (n - 1) * lead / 2 + size / 2 - 1.0
    for i, line in enumerate(lines):
        s += t(x + w / 2, y0 + i * lead, line, size=size if i == 0 else size - 1.0,
               weight="600" if i == 0 else "400", fill=INK if i == 0 else "#2b2b2b")
    return s


def arrow(pts, dash=None, width=0.9, head=True, color=LINE, marker="ah"):
    d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(pts))
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{marker})"' if head else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da}'
            f' stroke-linejoin="round"{mk}/>')


def build():
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">',
         '<defs>'
         '<marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5.0" '
         f'markerHeight="5.0" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{LINE}"/></marker>'
         '<marker id="ag" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="4.6" '
         f'markerHeight="4.6" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{FAINT}"/></marker>'
         '</defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    # ---------------------------------------------------------------- year bands
    bands = [(16, 162, BAND_END, "2015 and 2016"),
             (166, 556, BAND_MID, "2017"),
             (564, 720, BAND_END, "2018")]
    for x0, x1, fill, yr in bands:
        p.append(f'<rect x="{x0}" y="8" width="{x1 - x0}" height="208" rx="4" fill="{fill}"/>')
        p.append(t((x0 + x1) / 2, 26, yr, size=9.4, weight="600"))

    # ---------------------------------------------------------------- the stack of four rounds
    # two part cards behind the front one, so that "four rounds" is shown rather than stated
    for d in (9, 4.5):
        p.append(f'<rect x="{176 + d}" y="{54 - d}" width="370" height="146" rx="4" '
                 f'fill="#ffffff" stroke="{FAINT}" stroke-width="0.7"/>')
    p.append(f'<rect x="176" y="54" width="370" height="146" rx="4" fill="#ffffff" '
             f'stroke="{MUT}" stroke-width="0.8"/>')
    p.append(t(184, 66, "one round of four", size=7.8, anchor="start", fill=MUT, style="italic"))
    p.append(t(184, 75, "about 520 / 320 / 360 isolates arrive per round", size=7.4,
               anchor="start", fill=FAINT))

    # ---------------------------------------------------------------- boxes
    p.append(box(22, 56, 134, 42, ["Training set", "1481 / 812 / 1141 isolates"], fill=FILL_KEY))
    p.append(box(22, 116, 134, 48,
                 ["Gradient boosted trees", "threshold t at 90%", "sensitivity on held out data"]))
    p.append(box(186, 122, 58, 36, ["Score", "f(x)"]))
    p.append(box(258, 84, 124, 44, ["Rank by rule", "random, uncertainty,", "diversity, hybrid"]))
    p.append(box(258, 150, 124, 38, ["Laboratory AST", "on B/4 isolates"]))
    p.append(box(402, 112, 136, 56,
                 ["Reported from f(x) and t", "very major errors (VME)", "major errors (ME)"]))
    p.append(box(572, 100, 140, 56,
                 ["Evaluate on 2018", "1386 / 775 / 1204 isolates", "AUROC and TreeSHAP"],
                 fill=FILL_KEY))

    # ---------------------------------------------------------------- flow arrows
    p.append(arrow([(89, 98), (89, 113)]))
    p.append(arrow([(156, 140), (183, 140)]))
    p.append(arrow([(215, 122), (215, 106), (255, 106)]))
    p.append(t(220, 118, "scores", size=7.4, anchor="start", fill=MUT))

    p.append(arrow([(320, 128), (320, 147)]))
    p.append(t(325, 141, "top B/4", size=7.4, anchor="start", fill=MUT))
    p.append(arrow([(382, 106), (462, 106), (462, 109)]))
    p.append(t(458, 101, "the rest, untested", size=7.4, anchor="end", fill=MUT))

    # the retraining loop, drawn heavier than the rest because it is the thing being studied
    p.append(arrow([(256, 169), (164, 169), (164, 196), (8, 196), (8, 77), (19, 77)], width=1.3))
    p.append(t(28, 182, "bought labels join the training set,", size=7.4, anchor="start", fill=MUT))
    p.append(t(28, 191, "then f and t are refitted", size=7.4, anchor="start", fill=MUT))

    p.append(arrow([(546, 128), (569, 128)]))
    p.append(t(642, 92, "after 4 rounds", size=7.4, fill=MUT, style="italic"))

    # ---------------------------------------------------------------- the two bounds
    p.append(arrow([(156, 66), (162, 66), (162, 39), (600, 39), (600, 97)],
                   dash="3 2.4", color=FAINT, marker="ag"))
    p.append(t(594, 36, "lower bound, B = 0", size=7.4, anchor="end", fill=FAINT))
    p.append(arrow([(320, 188), (320, 208), (656, 208), (656, 159)],
                   dash="3 2.4", color=FAINT, marker="ag"))
    p.append(t(650, 205, "upper bound, B = all", size=7.4, anchor="end", fill=FAINT))

    p.append("</svg>")
    svg = "\n".join(p)
    open(os.path.join(OUT, "f1_pipeline.svg"), "w").write(svg)
    print("wrote", os.path.join(OUT, "f1_pipeline.svg"))
    return svg


CAPTION = (
    "Study pipeline. A gradient boosted classifier is fitted to the isolates of 2015 and 2016 and a "
    "decision threshold t is fixed on held out data at 90% sensitivity. The 3 counts in each box are "
    "the isolates available for <i>E. coli</i>, <i>K. pneumoniae</i> and <i>S. aureus</i> at DRIAMS-A. "
    "The card drawn in the 2017 band is one of 4 identical rounds, in which the model scores the "
    "isolates that arrived, the acquisition rule ranks them, a quarter of the annual budget B is spent "
    "on laboratory susceptibility testing (AST), and those labels join the training set before the "
    "model and the threshold are refitted. Every isolate that is not bought is reported from the model "
    "output alone, and those reports are where the very major and major errors of the pool year "
    "accumulate. The dashed arms bypass the loop and carry the 2 bounds the rules are compared "
    "against, namely never retraining (B = 0) and testing every arriving isolate (B = all).")


def standalone(svg):
    """A one page PDF of just the pipeline, for submitting separately."""
    html = (f'<!doctype html><meta charset="utf-8"><style>@page{{size:{W / 72 + 0.7:.2f}in '
            f'{H / 72 + 1.95:.2f}in;margin:0.35in;}}body{{margin:0;'
            f'font-family:{SER};}}p{{font-size:9pt;margin:8pt 0 0;color:#222;text-align:justify}}'
            'i{font-style:italic}</style>' + svg + f'<p><b>Fig. 1.</b> {CAPTION}</p>')
    tmp = os.path.join(OUT, "_pipeline.html")
    open(tmp, "w").write(html)
    pdf = os.path.join(HERE, "AMR_Pipeline.pdf")
    subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "file://" + tmp], capture_output=True)
    os.remove(tmp)
    print("wrote", pdf)


if __name__ == "__main__":
    s = build()
    if "--svg-only" not in sys.argv:
        standalone(s)
