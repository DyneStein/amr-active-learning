# Add centred page numbers in Computer Modern-like serif, as a LaTeX document would.
import sys, fitz
src, dst = sys.argv[1], sys.argv[2]
d = fitz.open(src)
for i, p in enumerate(d):
    n = str(i + 1)
    w = fitz.get_text_length(n, fontname="tiro", fontsize=9.5)
    p.insert_text(((p.rect.width - w) / 2, p.rect.height - 56), n, fontname="tiro", fontsize=9.5, color=(0, 0, 0))
d.save(dst, deflate=True, garbage=3)
print("pages", len(d))
