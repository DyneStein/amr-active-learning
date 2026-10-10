# ICIC 2026 asks for the IEEE conference identifier in the footer of the first page only,
# at 10 pt, and for no page numbers anywhere.
import sys, fitz

ID = "979-8-3195-2818-6/26/$31.00 ©2026 IEEE"
src, dst = sys.argv[1], sys.argv[2]
d = fitz.open(src)
p = d[0]
# bottom of the left column: 0.63 in from the left edge, 0.5 in up from the paper edge
p.insert_text((0.63 * 72, p.rect.height - 0.5 * 72), ID, fontname="tiro", fontsize=10, color=(0, 0, 0))
d.save(dst, deflate=True, garbage=3)
print("pages", len(d), "| identifier stamped on page 1")
