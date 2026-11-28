#!/usr/bin/env python3
"""LiberationSerif-Bold symbols (rho, approx) -> LiberationSerif Regular, same cell."""
import sys, glob, warnings
warnings.filterwarnings("ignore")
import pymupdf
reg = glob.glob("/usr/share/fonts/**/LiberationSerif-Regular.ttf", recursive=True)[0]
F = pymupdf.Font(fontfile=reg)
src, dst = sys.argv[1:3]
d = pymupdf.open(src)
n = 0
for pg in d:
    spans = [s for b in pg.get_text("rawdict")["blocks"] for l in b.get("lines", []) for s in l["spans"]
             if s["font"].split("+")[-1] == "LiberationSerif-Bold" and any(F.has_glyph(ord(c["c"])) for c in s["chars"])]
    if not spans:
        continue
    for s in spans:
        pg.add_redact_annot(pymupdf.Rect(s["bbox"]))
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    for s in spans:
        col = tuple(((s["color"] >> sh) & 255) / 255 for sh in (16, 8, 0))
        tw = pymupdf.TextWriter(pg.rect, color=col)
        for ch in s["chars"]:
            wb = ch["bbox"][2] - ch["bbox"][0]
            wr = F.text_length(ch["c"], fontsize=s["size"])
            tw.append((ch["origin"][0] + (wb - wr) / 2, ch["origin"][1]), ch["c"], font=F, fontsize=s["size"])
            n += 1
        tw.write_text(pg)
d.save(dst, garbage=3, deflate=True)
print("liberation chars redrawn:", n)
