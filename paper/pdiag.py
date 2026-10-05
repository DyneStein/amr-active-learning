# Schematic diagrams (hand-written SVG) for the AMR paper: Fig 1 maintenance loop, Fig 2 data and splits.
OUT = "/tmp/work/project/7fb83f58-8ee1-4d80-abd0-7a5cdba3f0f3/scratchpad/fig/"
INK, INK2, MUT, LINE = "#0b0b0b", "#52514e", "#8a8982", "#c9c8c2"
BLU, ORA, AQU, VIO = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
VME, ME_, SURF = "#e34948", "#eda100", "#fcfcfb"
F = 'font-family="Helvetica Neue, Helvetica, Arial, sans-serif"'

HEAD = ('<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" {f} font-size="9.5">'
        '<defs>'
        '<marker id="ar" markerWidth="7" markerHeight="7" refX="6.2" refY="3.5" orient="auto">'
        '<path d="M0,0.6 L6.4,3.5 L0,6.4 z" fill="{ink2}"/></marker>'
        '<marker id="arR" markerWidth="7" markerHeight="7" refX="6.2" refY="3.5" orient="auto">'
        '<path d="M0,0.6 L6.4,3.5 L0,6.4 z" fill="{vme}"/></marker>'
        '<marker id="arA" markerWidth="7" markerHeight="7" refX="6.2" refY="3.5" orient="auto">'
        '<path d="M0,0.6 L6.4,3.5 L0,6.4 z" fill="{aqu}"/></marker>'
        '</defs><rect width="{w}" height="{h}" fill="{s}"/>')


def box(x, y, w, h, title, sub="", col=INK2, fill=SURF, r=5, ts=10, bold=True):
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{col}" stroke-width="1"/>'
    lines = [l for l in sub.split("|") if l] if sub else []
    ty = y + (h / 2 + 3.4) if not lines else y + h / 2 - 4.2 * len(lines) + 2
    bw_ = " font-weight='bold'" if bold else ""
    o += f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" fill="{INK}" font-size="{ts}"{bw_}>{title}</text>'
    for i, l in enumerate(lines):
        o += f'<text x="{x + w / 2}" y="{ty + 11 + i * 10.5}" text-anchor="middle" fill="{INK2}" font-size="8.6">{l}</text>'
    return o


def txt(x, y, s, size=8.8, col=INK2, anchor="middle", bold=False, it=False):
    bw_ = " font-weight='bold'" if bold else ""
    it_ = " font-style='italic'" if it else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{col}" font-size="{size}"{bw_}{it_}>{s}</text>' 


def arrow(x1, y1, x2, y2, col=INK2, mk="ar", dash=None, w=1.1):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="{w}" fill="none"{d} marker-end="url(#{mk})"/>'


def curve(d, col=INK2, mk="ar", dash=None, w=1.1):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="none"{da} marker-end="url(#{mk})"/>'


# ---------------------------------------------------------------- Fig 1: the maintenance loop
def fig1():
    W, H = 980, 352
    b = HEAD.format(w=W, h=H, s=SURF, f=F, ink2=INK2, vme=VME, aqu=AQU)
    # spine
    b += box(14, 108, 118, 62, "New isolates", "arrive during|the year (2017)", col=LINE)
    b += box(166, 108, 120, 62, "Model in use", "scores each one:|p = P(resistant)", col=VIO)
    b += box(320, 108, 132, 62, "Selection rule", "picks b of them|(the lab budget)", col=BLU)
    b += arrow(132, 139, 164, 139); b += arrow(286, 139, 318, 139)
    # top: lab
    b += box(500, 22, 150, 58, "Laboratory test", "true S / R label|(slow, expensive)", col=AQU)
    b += curve("M452,124 C476,124 480,60 498,52", AQU, "arA")
    b += txt(468, 92, "tested", 8.6, AQU, bold=True)
    # bottom: untested -> patient
    b += box(500, 196, 150, 58, "Model's call is used", "for the patient:|resistant if p ≥ t", col=VME)
    b += curve("M452,154 C476,154 480,218 498,226", VME, "arR")
    b += txt(466, 188, "not tested", 8.6, VME, bold=True)
    # errors
    b += box(688, 180, 128, 34, "Very major error", "", col=VME, fill="#fdecec", ts=9.2)
    b += txt(752, 209, "resistant called susceptible", 8.0, VME)
    b += box(688, 228, 128, 34, "Major error", "", col="#b9780a", fill="#fdf4e1", ts=9.2)
    b += txt(752, 257, "susceptible called resistant", 8.0, "#8a5c08")
    b += arrow(650, 210, 686, 201, VME, "arR"); b += arrow(650, 232, 686, 241, "#b9780a", "ar")
    # retrain
    b += box(700, 22, 126, 58, "Retrain", "model, threshold t|conformal bounds", col=VIO)
    b += arrow(650, 51, 698, 51, AQU, "arA")
    b += box(858, 22, 108, 58, "Next round", "of arrivals", col=LINE)
    b += arrow(826, 51, 856, 51)
    b += curve("M912,80 C912,290 240,300 226,176", INK2, "ar", dash="5,3")
    b += txt(530, 292, "the updated model scores the next batch   ·   4 rounds per year", 8.8, MUT, it=True)
    # end of year
    b += box(858, 180, 108, 82, "End of year", "evaluate on|the next year’s|isolates (2018)", col=INK, ts=9.6)
    b += arrow(826, 221, 856, 221)
    b += txt(14, 332, "What the paper measures: model quality on 2018 (AUROC) and the errors made on untested isolates during the year.",
             8.8, INK2, anchor="start")
    return b + "</svg>"


# ---------------------------------------------------------------- Fig 2: data and splits
def fig2():
    W, H = 980, 336
    b = HEAD.format(w=W, h=H, s=SURF, f=F, ink2=INK2, vme=VME, aqu=AQU)
    counts = {"ecoli_cro": dict(n="E. coli – ceftriaxone", tr=1481, po=2094, te=1386, B=213, C=916, D=1994),
              "kpneu_cro": dict(n="K. pneumoniae – ceftriaxone", tr=812, po=1273, te=775, B=152, C=366, D=2151),
              "saur_oxa": dict(n="S. aureus – oxacillin", tr=1141, po=1445, te=1204, B=346, C=738, D=0)}
    x0, bw = 150, 150
    # header band
    for i, (lab, sub, col, x) in enumerate([("2015–2016", "train (80%) + validation (20%)", VIO, x0),
                                            ("2017", "arrives in 4 rounds · the label budget is spent here", BLU, x0 + bw + 10),
                                            ("2018", "held out: the test year", INK, x0 + 2 * bw + 250)]):
        w = bw if i != 1 else bw + 230
        b += f'<rect x="{x}" y="24" width="{w}" height="26" rx="4" fill="{col}" fill-opacity="0.12" stroke="{col}"/>'
        b += txt(x + w / 2, 41, lab, 10, col, bold=True)
        b += txt(x + w / 2, 62, sub, 8.4, INK2)
    # four round ticks
    for k in range(4):
        xx = x0 + bw + 20 + k * 92
        b += f'<rect x="{xx}" y="72" width="84" height="15" rx="3" fill="{BLU}" fill-opacity="0.18"/>'
        b += txt(xx + 42, 83, f"round {k + 1}", 7.8, "#1a5490")
    # rows per pair
    y = 100
    for key, d in counts.items():
        b += txt(140, y + 17, d["n"], 9.2, INK, anchor="end", bold=True)
        for lab, x, w, col in [(d["tr"], x0, bw, VIO), (d["po"], x0 + bw + 10, bw + 230, BLU), (d["te"], x0 + 2 * bw + 250, bw, INK)]:
            b += f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="4" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-opacity="0.55"/>'
            b += txt(x + w / 2, y + 17, f"{lab:,} isolates", 9, INK)
        y += 40
    b += txt(x0 - 10, y + 2, "single hospital (DRIAMS-A)", 8.6, MUT, anchor="end", it=True)
    # cross-site block
    b += f'<rect x="{x0}" y="{y + 16}" width="{bw * 3 + 240}" height="62" rx="6" fill="{ORA}" fill-opacity="0.07" stroke="{ORA}" stroke-dasharray="4,3"/>'
    b += txt(x0 + 14, y + 34, "Cross-site: the 2015–16 model is moved to three other hospitals (2018 isolates), which buy their own labels",
             8.8, "#a8431a", anchor="start", bold=True)
    for k, (site, col) in enumerate(zip("BCD", [BLU, ORA, VIO])):
        xx = x0 + 14 + k * 200
        vals = ", ".join(f"{counts[p][site]:,}" for p in counts if counts[p][site])
        b += txt(xx, y + 52, f"hospital {site}:", 8.6, col, anchor="start", bold=True)
        b += txt(xx + 56, y + 52, vals + " isolates", 8.6, INK2, anchor="start")
    b += txt(x0 + 14, y + 68, "(S. aureus has no labelled isolates at hospital D, so that pair is not run there)", 8.2, MUT, anchor="start", it=True)
    b += txt(150, 326, "Each isolate is one MALDI-TOF mass spectrum (6 000 intensity bins) with a laboratory S/R label. "
                       "I and R are both treated as resistant, as in the DRIAMS reference code.", 8.6, INK2, anchor="start")
    return b + "</svg>"


if __name__ == "__main__":
    open(OUT + "f1_loop.svg", "w").write(fig1())
    open(OUT + "f2_data.svg", "w").write(fig2())
    print("wrote f1_loop, f2_data")
