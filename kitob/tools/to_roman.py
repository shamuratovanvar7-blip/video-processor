#!/usr/bin/env python3
"""Bold / Italic / Type3-text -> CMU Serif Roman, keeping the layout.

Every character keeps the centre of its original cell, so lines, centred
headings and table cells do not move.  Symbols that CMU Serif lacks are left
untouched.  Usage: to_roman.py SRC.pdf DST.pdf [page numbers (1-based) ...]
"""
import sys, collections, warnings
warnings.filterwarnings("ignore")
import pymupdf

HERE = __file__.rsplit("/tools/", 1)[0]
ROMAN = pymupdf.Font(fontfile=f"{HERE}/fonts/CMUSerif-Roman.ttf")
KEEP_PUNCT = set("‘’ʻʼ'-–—.,:;()[]/+=−·%°")


def span_text(s):
    return "".join(c["c"] for c in s["chars"])


def wants_conversion(s):
    f = s["font"]
    txt = span_text(s)
    if not txt.strip():
        return False
    if f.startswith("CMUSerif") and ("Bold" in f or "Italic" in f):
        pass
    elif f.startswith("Type3"):
        # Type3 text runs are either symbols (▶ ★ ✔ ...) or italic letters/digits
        if not all(ch.isalnum() or ch.isspace() or ch in KEEP_PUNCT for ch in txt):
            return False
    else:
        return False
    # every visible char must exist in Roman, otherwise leave the span alone
    return all(ch.isspace() or ROMAN.has_glyph(ord(ch)) for ch in txt)


def rgb(c):
    return ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)


def convert_page(pg):
    raw = pg.get_text("rawdict")
    spans = [s for b in raw["blocks"] for l in b.get("lines", []) for s in l["spans"]
             if wants_conversion(s)]
    if not spans:
        return 0
    for s in spans:
        size = s["size"]
        oy = s["chars"][0]["origin"][1]
        x0, x1 = s["bbox"][0], s["bbox"][2]
        pg.add_redact_annot(pymupdf.Rect(x0 + 0.15, oy - 0.35 * size, x1 - 0.15, oy - 0.1 * size))
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                        graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                        text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    writers = collections.OrderedDict()
    for s in spans:
        size = s["size"]
        col = rgb(s["color"])
        tw = writers.setdefault(col, pymupdf.TextWriter(pg.rect, color=col))
        for ch in s["chars"]:
            c = ch["c"]
            if c.isspace():
                continue
            wb = ch["bbox"][2] - ch["bbox"][0]
            wr = ROMAN.text_length(c, fontsize=size)
            x = ch["origin"][0] + (wb - wr) / 2
            tw.append((x, ch["origin"][1]), c, font=ROMAN, fontsize=size)
    for tw in writers.values():
        tw.write_text(pg)
    return len(spans)


def main():
    src, dst, *pages = sys.argv[1:]
    d = pymupdf.open(src)
    sel = [int(p) for p in pages] or list(range(1, len(d) + 1))
    done = 0
    for n in sel:
        k = convert_page(d[n - 1])
        done += k
        print(f"page {n}: {k} spans", flush=True)
    if pages:
        d.select([n - 1 for n in sel])
    d.save(dst, garbage=3, deflate=True)
    print("spans converted:", done)


if __name__ == "__main__":
    main()
