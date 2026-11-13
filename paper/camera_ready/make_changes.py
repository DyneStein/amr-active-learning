"""Writes camera_ready_changes.txt: every passage of the submitted paper that the camera ready version changes,
read directly from revisions.CHANGES, so the list cannot drift from what build.py applies.
Run: python3 make_changes.py
"""
import os
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import revisions  # noqa: E402

NAMES = {"FRONT": "Abstract", "S1": "I. Introduction", "S2": "II. Related Work", "S3": "III. Method",
         "S4": "IV. Experimental Setup", "S5": "V. Results", "S6": "VI. Discussion and VII. Conclusion"}


def plain(h):
    h = re.sub(r"@@RAW\|T4@@", "[new Table I: all 45 temporal effect sizes with 95% confidence intervals]", h)
    h = re.sub(r"<h3>(.*?)</h3>", r"[heading] \1", h)
    h = re.sub(r"<[^>]+>", "", h).replace("&lt;", "<").replace("&nbsp;", " ")
    return " ".join(h.split())


def is_deletion(old, new):
    o, n = plain(old).split(), plain(new).split()
    i = 0
    for w in o:
        if i < len(n) and w == n[i]:
            i += 1
    return i == len(n) and len(n) < len(o)


def wrap(s):
    return textwrap.fill(s, 100, initial_indent="    ", subsequent_indent="    ") if s else "    (nothing)"


out = ["CHANGES IN THE CAMERA READY VERSION (PID280.pdf), paper 280",
       "Every sentence not listed here is exactly as in the submitted paper.",
       "DELETED = submitted words removed to fit 6 pages, nothing reworded.",
       "CHANGED = a correction or an addition for the reviewers (new wording).",
       "",
       "Layout: Table I of the submitted paper (position of this study) and Fig. 4 (SHAP dot matrix) are removed to",
       "fit 6 pages, since Section II-C and Table III carry the same content. A new table of all 45 temporal effect",
       "sizes is added (Reviewer 2, point 1). Tables are renumbered I (new), II (cost), III (SHAP).", ""]
n = d = c = 0
for key, pairs in revisions.CHANGES.items():
    out += ["=" * 100, NAMES[key], "=" * 100, ""]
    for old, new in pairs:
        n += 1
        tag = "DELETED" if is_deletion(old, new) else "CHANGED"
        d += tag == "DELETED"
        c += tag == "CHANGED"
        out += [f"[{n}] {tag}", "  SUBMITTED TEXT:", wrap(plain(old)), "  CAMERA READY TEXT:", wrap(plain(new)), ""]
out.insert(5, f"{n} passages: {d} deletions, {c} changes.")
open(os.path.join(HERE, "camera_ready_changes.txt"), "w").write("\n".join(out) + "\n")
print(f"wrote camera_ready_changes.txt: {n} passages, {d} deletions, {c} changes")
