# Schematic diagrams for the AMR paper, monochrome line art sized for a 133 mm text measure.
# The viewBox is ~510 units wide, so a font-size of 10 units renders at about 7.4 pt.
OUT = "/tmp/work/project/7fb83f58-8ee1-4d80-abd0-7a5cdba3f0f3/scratchpad/fig/"
K, G, L = "#1a1a1a", "#555555", "#999999"
FILL, SHADE = "#ffffff", "#f1f1f1"
F = 'font-family="Helvetica Neue, Helvetica, Arial, sans-serif"'

HEAD = ('<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" {f} font-size="10">'
        '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
        '<path d="M0,1 L7.4,4 L0,7 z" fill="{k}"/></marker>'
        '<marker id="arg" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
        '<path d="M0,1 L7.4,4 L0,7 z" fill="{g}"/></marker></defs>'
        '<rect width="{w}" height="{h}" fill="#ffffff"/>')


def box(x, y, w, h, title, sub="", fill=FILL, ts=10.5):
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2.5" fill="{fill}" stroke="{K}" stroke-width="0.8"/>'
    lines = [v for v in sub.split("|") if v] if sub else []
    ty = y + h / 2 + 3.6 if not lines else y + h / 2 - 4.6 * len(lines) + 1.5
    o += f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" fill="{K}" font-size="{ts}">{title}</text>'
    for i, s in enumerate(lines):
        o += f'<text x="{x + w / 2}" y="{ty + 11.5 + i * 10.8}" text-anchor="middle" fill="{G}" font-size="9.2">{s}</text>'
    return o


def t(x, y, s, size=9.2, col=G, anchor="middle", it=False):
    i_ = " font-style='italic'" if it else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{col}" font-size="{size}"{i_}>{s}</text>'


def arrow(x1, y1, x2, y2, col=K, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="0.8" fill="none"{d} marker-end="url(#{"ar" if col == K else "arg"})"/>'


def curve(d, col=K, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" stroke="{col}" stroke-width="0.8" fill="none"{da} marker-end="url(#{"ar" if col == K else "arg"})"/>'


def fig1():
    W, H = 510, 236
    b = HEAD.format(w=W, h=H, k=K, g=G, f=F)
    # row 1: arrival -> scoring -> acquisition
    b += box(4, 14, 130, 44, "New isolates", "arrive in round r")
    b += box(174, 14, 136, 44, "Model in service", "scores each: p = P(R)")
    b += box(350, 14, 156, 44, "Acquisition rule", "selects b / R of them")
    b += arrow(134, 36, 172, 36)
    b += arrow(310, 36, 348, 36)
    # split
    b += curve("M398,58 C398,80 240,74 215,94")
    b += curve("M448,58 C448,78 470,80 470,94")
    b += t(300, 80, "acquired", 9.2, K, anchor="end")
    b += t(506, 80, "not acquired", 9.2, K, anchor="end")
    # row 2
    b += box(140, 96, 150, 44, "Laboratory test", "true S / R label")
    b += box(330, 96, 176, 44, "Model's call is used", "resistant if p ≥ t", fill=SHADE)
    b += arrow(290, 118, 328, 118) if False else ""
    # row 3
    b += box(140, 162, 150, 42, "Retrain", "model, t, bounds")
    b += arrow(215, 140, 215, 160)
    b += box(330, 160, 80, 20, "VME", "", ts=9.6)
    b += box(426, 160, 80, 20, "ME", "", ts=9.6)
    b += arrow(400, 140, 378, 158)
    b += arrow(440, 140, 462, 158)
    b += t(370, 194, "resistant reported", 8.6, G)
    b += t(370, 204, "susceptible", 8.6, G)
    b += t(466, 194, "susceptible reported", 8.6, G)
    b += t(466, 204, "resistant", 8.6, G)
    # feedback
    b += curve("M140,183 C60,183 58,70 170,46", G, "4,3")
    b += t(66, 148, "round r + 1", 8.8, G, it=True)
    b += t(255, 228, "four rounds per year; the model is then evaluated on the following year's isolates",
           8.8, G, it=True)
    return b + "</svg>"


def fig2():
    W, H = 510, 262
    b = HEAD.format(w=W, h=H, k=K, g=G, f=F)
    rows = [("E. coli", "ceftriaxone", 1481, 2094, 1386, "213 / 916 / 1 994"),
            ("K. pneumoniae", "ceftriaxone", 812, 1273, 775, "152 / 366 / 2 151"),
            ("S. aureus", "oxacillin", 1141, 1445, 1204, "346 / 738 / none")]
    x0, w1, w2, w3, gap = 118, 86, 176, 86, 7
    xs = [x0, x0 + w1 + gap, x0 + w1 + w2 + 2 * gap]
    for (lab, sub), x, w in zip([("2015 and 2016", "train / validation"), ("2017", "acquisition pool"),
                                 ("2018", "test year")], xs, [w1, w2, w3]):
        b += f'<rect x="{x}" y="10" width="{w}" height="19" fill="{SHADE}" stroke="{K}" stroke-width="0.8"/>'
        b += t(x + w / 2, 23.5, lab, 10.2, K)
        b += t(x + w / 2, 40, sub, 8.8, G)
    for k in range(4):
        xx = xs[1] + 3 + k * 42.5
        b += f'<rect x="{xx}" y="48" width="39" height="12" fill="none" stroke="{L}" stroke-width="0.6"/>'
        b += t(xx + 19.5, 57, f"r{k + 1}", 8.4, G)
    y = 70
    for name, ab, tr, po, te, cross in rows:
        b += t(112, y + 12, name, 9.6, K, anchor="end")
        b += t(112, y + 22, ab, 8.4, G, anchor="end")
        for val, x, w in zip([tr, po, te], xs, [w1, w2, w3]):
            b += f'<rect x="{x}" y="{y}" width="{w}" height="26" fill="none" stroke="{L}" stroke-width="0.6"/>'
            b += t(x + w / 2, y + 17, f"{val:,}".replace(",", " "), 9.6, K)
        y += 32
    b += f'<line x1="{x0}" y1="{y + 3}" x2="{xs[2] + w3}" y2="{y + 3}" stroke="{L}" stroke-width="0.6"/>'
    b += t(112, y + 18, "Other hospitals, 2018", 9.6, K, anchor="end")
    b += t(x0, y + 18, "hospitals B / C / D, each acquiring local labels:", 9, G, anchor="start")
    yy = y + 31
    for name, ab, tr, po, te, cross in rows:
        b += t(x0 + 6, yy, f"{name}: {cross}", 8.8, G, anchor="start")
        yy += 11
    b += t(255, yy + 14, "one isolate = one MALDI-TOF spectrum, 6 000 intensity bins, with a laboratory S/R label",
           8.8, G, it=True)
    return b + "</svg>"


if __name__ == "__main__":
    open(OUT + "f1_loop.svg", "w").write(fig1())
    open(OUT + "f2_data.svg", "w").write(fig2())
    print("wrote f1_loop, f2_data")
