# The study pipeline, drawn as a full width schematic.
# Writes ifig/f1_pipeline.svg for the paper and AMR_Pipeline.pdf as a standalone file,
# because the reviewers asked for the pipeline on its own as well as inside the paper.
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ifig")
os.makedirs(OUT, exist_ok=True)

W, H = 724, 196
SER = "'Times New Roman',Times,serif"
INK, LINE, MUT = "#111111", "#333333", "#666666"


def box(x, y, w, h, lines, bold_first=True, fill="#ffffff", dash=None):
    """A rounded box with centred lines of text; the first line can carry the label."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" '
         f'stroke="{LINE}" stroke-width="0.9"{d}/>')
    n = len(lines)
    y0 = y + h / 2 - (n - 1) * 5.6 + 3.4
    for i, t in enumerate(lines):
        wt = "600" if (i == 0 and bold_first) else "400"
        s += (f'<text x="{x + w / 2}" y="{y0 + i * 11.2}" font-family="{SER}" font-size="9.2" '
              f'font-weight="{wt}" fill="{INK}" text-anchor="middle">{t}</text>')
    return s


def arrow(pts, label=None, lx=None, ly=None, dash=None, anchor="middle"):
    """A polyline arrow through pts [(x,y), ...] with an optional label."""
    d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(pts))
    da = f' stroke-dasharray="{dash}"' if dash else ""
    s = (f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="0.9"{da} '
         f'marker-end="url(#ah)"/>')
    if label:
        s += (f'<text x="{lx}" y="{ly}" font-family="{SER}" font-size="8.2" fill="{MUT}" '
              f'text-anchor="{anchor}">{label}</text>')
    return s


def build():
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">',
         '<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5.2" '
         f'markerHeight="5.2" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{LINE}"/>'
         '</marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    yt, hb = 18, 44
    b1 = (8, 112); b2 = (136, 112); b3 = (264, 112); b4 = (392, 118); b5 = (578, 138)

    p.append(box(*b1, yt, hb, ["Spectra, 2015 and 2016", "with susceptibility results"]) if False else
             box(b1[0], yt, b1[1], hb, ["Spectra, 2015-2016", "with AST results"]))
    p.append(box(b2[0], yt, b2[1], hb, ["Train classifier", "set threshold t"]))
    p.append(box(b3[0], yt, b3[1], hb, ["Score isolates", "arriving in 2017"]))
    p.append(box(b4[0], yt, b4[1], hb, ["Acquisition rule", "buy B/4 tests"]))
    p.append(box(b5[0], yt, b5[1], hb, ["Evaluate on 2018", "AUROC and TreeSHAP"]))

    for a, b in [(b1, b2), (b2, b3), (b3, b4)]:
        p.append(arrow([(a[0] + a[1], yt + hb / 2), (b[0] - 3, yt + hb / 2)]))
    p.append(arrow([(b4[0] + b4[1], yt + hb / 2), (b5[0] - 3, yt + hb / 2)],
                   "after four rounds", (b4[0] + b4[1] + b5[0]) / 2, yt + hb / 2 - 7))

    # the split: bought or not bought
    xc = b4[0] + b4[1] / 2
    ysp, yr2, h2 = yt + hb + 16, 120, 40
    c1 = (300, 124); c2 = (442, 134)
    p.append(f'<path d="M{xc},{yt + hb} L{xc},{ysp}" fill="none" stroke="{LINE}" stroke-width="0.9"/>')
    p.append(f'<path d="M{c1[0] + c1[1] / 2},{ysp} L{c2[0] + c2[1] / 2},{ysp}" fill="none" '
             f'stroke="{LINE}" stroke-width="0.9"/>')
    p.append(arrow([(c1[0] + c1[1] / 2, ysp), (c1[0] + c1[1] / 2, yr2 - 3)]))
    p.append(arrow([(c2[0] + c2[1] / 2, ysp), (c2[0] + c2[1] / 2, yr2 - 3)]))
    p.append(f'<text x="{c1[0] + c1[1] / 2 - 6}" y="{ysp + 13}" font-family="{SER}" font-size="8.2" '
             f'fill="{MUT}" text-anchor="end">selected</text>')
    p.append(f'<text x="{c2[0] + c2[1] / 2 + 6}" y="{ysp + 13}" font-family="{SER}" font-size="8.2" '
             f'fill="{MUT}" text-anchor="start">not selected</text>')

    p.append(box(c1[0], yr2, c1[1], h2, ["Laboratory AST", "true label obtained"]))
    p.append(box(c2[0], yr2, c2[1], h2, ["Model's call is reported", "very major and major errors"]))

    # feedback: bought labels go back into training
    xf = c1[0] + 16
    p.append(arrow([(c1[0], yr2 + h2 / 2), (36, yr2 + h2 / 2), (36, yt + hb + 3)],
                   "augment training set, retrain, reset t; repeat for four quarterly rounds",
                   44, yr2 + h2 / 2 - 6, anchor="start"))
    p.append("</svg>")
    svg = "\n".join(p)
    open(os.path.join(OUT, "f1_pipeline.svg"), "w").write(svg)
    print("wrote", os.path.join(OUT, "f1_pipeline.svg"))
    return svg


def standalone(svg):
    """A one page PDF of just the pipeline, for submitting separately."""
    html = (f'<!doctype html><meta charset="utf-8"><style>@page{{size:{W/72+0.7:.2f}in '
            f'{H/72+1.65:.2f}in;margin:0.35in;}}body{{margin:0;'
            f'font-family:{SER};}}p{{font-size:9pt;margin:8pt 0 0;color:#222;text-align:justify}}'
            '</style>' + svg +
            '<p><b>Fig. 1.</b> Study pipeline. A classifier is trained on isolates from 2015 and '
            '2016 and a decision threshold is fixed on held out data. Isolates arriving in 2017 are '
            'scored in four quarterly rounds. AST denotes antimicrobial susceptibility testing. '
            'In each round an acquisition rule buys laboratory '
            'susceptibility tests for a fixed share of the budget; those isolates return a true '
            'label and enter the training set, while the remaining isolates are reported using the '
            "model's own call and contribute to the error counts. The maintained model is evaluated "
            'on isolates from 2018.</p>')
    tmp = os.path.join(OUT, "_pipeline.html")
    open(tmp, "w").write(html)
    pdf = os.path.join(HERE, "AMR_Pipeline.pdf")
    subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "file://" + tmp],
                   capture_output=True)
    os.remove(tmp)
    print("wrote", pdf)


if __name__ == "__main__":
    standalone(build())
