#!/usr/bin/env python3
"""Re-skin every embedded CMU Serif Bold / Italic / BoldItalic subset with the
outlines of CMU Serif Roman.

Glyph ids, advance widths (/W, /Widths), clipping, hidden header/footer text and
text positions are untouched, so the layout is identical; only the glyph shapes
change.  Each Roman outline is centred inside the old (wider) Bold advance.

Usage: reskin.py SRC.pdf DST.pdf
"""
import io, re, sys, warnings, collections
warnings.filterwarnings("ignore")
import pymupdf
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen

HERE = __file__.rsplit("/tools/", 1)[0]
ROMAN = TTFont(f"{HERE}/fonts/CMUSerif-Roman.ttf")
RCMAP = ROMAN.getBestCmap()
RGS = ROMAN.getGlyphSet()
RHMTX = ROMAN["hmtx"]
RUPEM = ROMAN["head"].unitsPerEm

LIG = {'fi': '\ufb01', 'fl': '\ufb02', 'ff': '\ufb00', 'ffi': '\ufb03', 'ffl': '\ufb04'}
_SIG = None


def _sig(gs, gn):
    rec = DecomposingRecordingPen(gs)
    gs[gn].draw(rec)
    return tuple(tuple(round(v) for v in a) for _, args in rec.value for a in args if a is not None)


def sig_index():
    """outline signature -> glyph names, from the full Bold/Italic/BoldItalic fonts"""
    global _SIG
    if _SIG is None:
        _SIG = {}
        for fn in ("Bold", "Italic", "BoldItalic"):
            f = TTFont(f"{HERE}/fonts/CMUSerif-{fn}.ttf")
            gs = f.getGlyphSet()
            for gn in f.getGlyphOrder():
                sg = _sig(gs, gn)
                if sg:
                    _SIG.setdefault(sg, []).append(gn)
    return _SIG


STYLE = re.compile(r"CMU ?Serif[- ]?(BoldItalic|Bold|Italic)")


def parse_tounicode(doc, xref):
    """code -> unicode string (first char), from a ToUnicode CMap."""
    k = doc.xref_get_key(xref, "ToUnicode")
    if k[0] != "xref":
        return {}
    tu = int(k[1].split()[0])
    s = doc.xref_stream(tu).decode("latin-1")
    m = {}
    for blk in re.findall(r"beginbfchar(.*?)endbfchar", s, re.S):
        for a, b in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            try:
                m[int(a, 16)] = bytes.fromhex(b).decode("utf-16-be", "ignore")
            except ValueError:
                pass
    for blk in re.findall(r"beginbfrange(.*?)endbfrange", s, re.S):
        for a, b, c in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            a, b = int(a, 16), int(b, 16)
            base = int(c, 16)
            for i in range(a, b + 1):
                m[i] = chr(base + i - a)
    return m


def descriptor_fontfile(doc, fdict_xref):
    """-> (descriptor xref, FontFile2 xref, is_type0)"""
    sub = doc.xref_get_key(fdict_xref, "Subtype")[1]
    if sub == "/Type0":
        arr = doc.xref_get_key(fdict_xref, "DescendantFonts")[1]
        cid = int(re.search(r"(\d+) 0 R", arr).group(1))
        fd = doc.xref_get_key(cid, "FontDescriptor")
    else:
        cid = fdict_xref
        fd = doc.xref_get_key(fdict_xref, "FontDescriptor")
    fdx = int(fd[1].split()[0])
    ff = doc.xref_get_key(fdx, "FontFile2")
    return cid, fdx, int(ff[1].split()[0]), sub == "/Type0"


def reskin_font(doc, fx, stats):
    cid, fdx, ffx, is0 = descriptor_fontfile(doc, fx)
    buf = doc.xref_stream(ffx)
    t = TTFont(io.BytesIO(buf))
    upem = t["head"].unitsPerEm
    s = upem / RUPEM
    glyf, hmtx = t["glyf"], t["hmtx"]
    # glyph name -> unicode
    g2u = {}
    if is0:
        cm = t.getCmap(3, 1) if hasattr(t, "getCmap") else None
        cmt = t["cmap"].getcmap(3, 1) or t["cmap"].getcmap(0, 3)
        for u, gn in cmt.cmap.items():
            g2u[gn] = chr(u)
        # glyphs without a cmap entry (ligatures etc.): CID == GID, use ToUnicode
        tu = parse_tounicode(doc, fx)
        for gn in t.getGlyphOrder():
            if gn not in g2u and gn != ".notdef":
                v = tu.get(t.getGlyphID(gn))
                if v:
                    g2u[gn] = LIG.get(v, v[0])
    else:
        tu = parse_tounicode(doc, fx)
        c10 = t["cmap"].getcmap(1, 0)
        for code, gn in c10.cmap.items():
            if code in tu:
                g2u[gn] = tu[code][0]
    done = skipped = 0
    for gn in t.getGlyphOrder():
        if gn == ".notdef":
            continue
        g = glyf[gn]
        if g.numberOfContours == 0:
            continue  # space / unused
        u = g2u.get(gn)
        rn = RCMAP.get(ord(u)) if u else None
        if rn is None and gn in RGS:  # same glyph name in the Roman font
            rn = gn
        if rn is None:  # contextual alternates etc.: identify by outline in the full font
            for cand in sig_index().get(_sig(t.getGlyphSet(), gn), []):
                if cand in RGS:
                    rn = cand
                    break
        if rn is None:
            skipped += 1
            stats["missing"][u or f"?{gn}"] += 1
            continue
        wb = hmtx[gn][0]
        wr = RHMTX[rn][0] * s
        rec = DecomposingRecordingPen(RGS)
        RGS[rn].draw(rec)
        pen = TTGlyphPen(None)
        rec.replay(TransformPen(pen, (s, 0, 0, s, (wb - wr) / 2, 0)))
        ng = pen.glyph()
        glyf[gn] = ng
        ng.recalcBounds(glyf)
        hmtx[gn] = (wb, getattr(ng, "xMin", 0))
        done += 1
    for tag in ("fpgm", "prep", "cvt "):
        if tag in t:
            del t[tag]
    out = io.BytesIO()
    t.save(out)
    data = out.getvalue()
    doc.update_stream(ffx, data)
    doc.xref_set_key(ffx, "Length1", str(len(data)))
    # honest naming / descriptor
    for x in {fx, cid, fdx}:
        for key in ("BaseFont", "FontName"):
            v = doc.xref_get_key(x, key)
            if v[0] == "name":
                doc.xref_set_key(x, key, STYLE.sub("CMUSerif-Roman", v[1]))
    doc.xref_set_key(fdx, "ItalicAngle", "0")
    doc.xref_set_key(fdx, "FontWeight", "400")
    stats["glyphs"] += done
    stats["skipped"] += skipped


def main():
    src, dst = sys.argv[1:3]
    doc = pymupdf.open(src)
    stats = {"fonts": 0, "glyphs": 0, "skipped": 0, "missing": collections.Counter(), "failed": []}
    for x in range(1, doc.xref_length()):
        try:
            if doc.xref_get_key(x, "Type")[1] != "/Font":
                continue
            bf = doc.xref_get_key(x, "BaseFont")[1]
        except Exception:
            continue
        if not STYLE.search(bf):
            continue
        if doc.xref_get_key(x, "Subtype")[1] not in ("/Type0", "/TrueType"):
            continue
        try:
            reskin_font(doc, x, stats)
            stats["fonts"] += 1
        except Exception as e:  # keep going, report
            stats["failed"].append((x, bf, repr(e)))
    doc.save(dst, garbage=3, deflate=True)
    print("fonts re-skinned:", stats["fonts"], "glyphs:", stats["glyphs"],
          "glyphs without Roman shape:", stats["skipped"])
    print("missing chars:", dict(stats["missing"]))
    print("failed:", stats["failed"][:5], len(stats["failed"]))


if __name__ == "__main__":
    main()
