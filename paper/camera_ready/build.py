"""Camera ready build for ICIC 2026 (paper 280): writes main.tex, an IEEEtran A4 conference paper.

The body text is taken from ../ieee.py (the submitted version) so that every sentence that was not
revised stays exactly as submitted. Each revision is an explicit (old, new) pair in revisions.py and
the build stops if an old passage is not found, so the list of changes is complete and auditable.
Run: python3 build.py   then   tectonic main.tex
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ieee          # noqa: E402  the submitted source
import revisions     # noqa: E402

FIGW = {"f1_pipeline": True, "f2_curves": True, "f3_errors": True, "f4_shap": True}
ieee.fig = lambda name, num, cap, wide=False: f"\n@@FIG|{name}|{cap}@@\n"
ieee.table = lambda num, cap, body, wide=False: f"\n@@TAB|{num}|{cap}@@\n"


def inline(s):
    s = s.replace("<wbr>", "")
    s = s.replace("&nbsp;", "~").replace("&rho;", r"$\rho$").replace("&eacute;", r"\'e")
    s = s.replace("&ldquo;", "``").replace("&rdquo;", "''").replace("&lt;", "<").replace("&gt;", ">")
    s = s.replace("%", r"\%").replace("_", r"\_").replace("&amp;", r"\&")
    s = re.sub(r"<i>(.*?)</i>", r"\\textit{\1}", s, flags=re.S)
    s = re.sub(r"<b>(.*?)</b>", r"\\textbf{\1}", s, flags=re.S)
    s = s.replace("p < 0.05", "$p < 0.05$")
    s = re.sub(r"\bp = (0\.\d+)", r"$p = \1$", s)
    s = s.replace("doi:10.5061/dryad.bzkh1899q", r"doi:10.5061/\allowbreak dryad.\allowbreak bzkh1899q")
    s = s.replace("\\textit{et al.}", "\\textit{et al.}")
    assert "<" not in re.sub(r"\$[^$]*\$", "", s) and "&" not in s.replace(r"\&", ""), s[:300]
    return s


def figure(name, cap):
    return ("\\begin{figure*}[!t]\n\\centering\n"
            f"\\includegraphics[width=\\textwidth]{{figures/{name}.pdf}}\n"
            f"\\caption{{{inline(cap)}}}\n\\label{{fig:{name}}}\n\\end{{figure*}}\n")


def body(html):
    out = []
    for part in re.split(r"(@@(?:FIG|TAB)\|.*?@@)", html, flags=re.S):
        if part.startswith("@@FIG|"):
            _, name, cap = part.strip("@").split("|", 2)
            out.append(figure(name, cap))
            continue
        if part.startswith("@@TAB|"):
            _, num, cap = part.strip("@").split("|", 2)
            out.append(revisions.TABLES[num](inline(cap)))
            continue
        for m in re.finditer(r"<h2>(.*?)</h2>|<h3>(.*?)</h3>|<p[^>]*>(.*?)</p>|(@@RAW\|.*?@@)", part, flags=re.S):
            h2, h3, p, raw = m.groups()
            if h2:
                out.append("\\section{%s}\n" % inline(re.sub(r"^[IVX]+\.(&nbsp;)*", "", h2)))
            elif h3:
                out.append("\\subsection{%s}\n" % inline(re.sub(r"^[A-Z]\. ", "", h3)))
            elif p:
                out.append(" ".join(inline(p).split()) + "\n")
            elif raw:
                out.append(revisions.RAW[raw.strip("@").split("|", 1)[1]] + "\n")
    return "\n".join(out)


def revised(name, text):
    text = " ".join(text.split())
    for old, new in revisions.CHANGES.get(name, []):
        old = " ".join(old.split())
        assert text.count(old) == 1, f"{name}: passage not found exactly once: {old[:70]!r}"
        text = text.replace(old, new)
    return text


def main():
    front = revised("FRONT", ieee.FRONT)
    abstract = re.search(r'<p class="abs"><b>Abstract</b>&mdash;(.*?)</p>', front, re.S).group(1)
    keywords = re.search(r'<p class="idx"><b>Keywords</b>&mdash;(.*?)</p>', front, re.S).group(1)
    t1 = "@@TAB|I|Position of this study relative to representative prior work. Explainable artificial " \
         "intelligence (XAI) here means any reported feature attribution.@@"
    secs = [revised("S1", ieee.S1), t1, revised("S2", ieee.S2), revised("S3", ieee.S3()), revised("S4", ieee.S4()),
            revised("S5", ieee.S5()), revised("S6", ieee.S6())]
    refs = re.findall(r"<li>(.*?)</li>", ieee.REFS, re.S)
    assert len(refs) == 20
    bib = "\n".join("\\bibitem{r%d} %s" % (i + 1, " ".join(inline(r).split())) for i, r in enumerate(refs))
    tex = revisions.PREAMBLE + "\\begin{abstract}\n" + " ".join(inline(abstract).split()) + "\n\\end{abstract}\n\n" \
        + "\\begin{IEEEkeywords}\n" + " ".join(inline(keywords).split()) + "\n\\end{IEEEkeywords}\n\n" \
        + "\n".join(body(s) for s in secs) + revisions.ACK \
        + "\\begin{thebibliography}{20}\n" + bib + "\n\\end{thebibliography}\n\\end{document}\n"
    for roman, label in (("V", "robust"), ("IV", "cross"), ("III", "shap"), ("II", "cost"), ("I", "position")):
        tex = re.sub(r"\bTable %s\b" % roman, r"Table~\\ref{tab:%s}" % label, tex)
    tex = re.sub(r"\bFig\. (\d)\b", r"Fig.~\1", tex)
    tex = re.sub(r"(?<![\w\\{])\[(\d{1,2})\]", r"\\cite{r\1}", tex)
    open(os.path.join(HERE, "main.tex"), "w").write(tex)
    words = len(re.sub(r"\\[a-zA-Z]+|[{}$]", " ", inline(abstract)).split())
    print("wrote main.tex,", len(tex) // 1024, "KB; abstract words:", words)


if __name__ == "__main__":
    main()
