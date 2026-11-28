#!/usr/bin/env python3
"""remove_black.py SRC.pdf DST.pdf

"Qora bilan bo'yalgan" bloklarni (matn, rasm, vektor) kitobdan butunlay o'chiradi.
SRC o'zgarmaydi. Bet raqamlari o'zgarmaydi. Idempotent: allaqachon o'chirilgan
blok (anchor matni topilmasa) o'tkazib yuboriladi.

  51-bet : o'ng "Molyar massa" kartochkasi
  52-bet : "1 Ma'nosi" sarlavhasi (pastdagi katak yuqoriga suriladi)
  82-bet : "3 Davr bo'ylab oksid va gidroksidlar ..." bloki
  83-bet : butun "Davr bo'ylab ..." konteyneri (2-davr/3-davr/Qoida, ramka bilan); "4 Umumiy formula" joyida qoladi
  84-bet : 4 ta jadval qatori (Fe2+, Cu2+, Fe3+, Al3+); jadvallar yopiladi, pastdagilar siljiydi
"""
import sys
import pymupdf

TXT = pymupdf.PDF_REDACT_TEXT_REMOVE
IMG = pymupdf.PDF_REDACT_IMAGE_REMOVE
G_COV = pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED
G_TCH = pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED
G_NONE = pymupdf.PDF_REDACT_LINE_ART_NONE
IMG_NONE = pymupdf.PDF_REDACT_IMAGE_NONE
TXT_NONE = pymupdf.PDF_REDACT_TEXT_NONE
R = pymupdf.Rect


def redact(page, rects, text=True, gfx=G_COV, img=IMG):
    for r in rects:
        page.add_redact_annot(R(r), fill=False)
    page.apply_redactions(images=img, graphics=gfx, text=TXT if text else TXT_NONE)


def words_in(page, rect):
    return " ".join(w[4] for w in page.get_text("words", clip=R(rect)))


def has(page, rect, *tokens, any_=False):
    s = words_in(page, rect)
    f = [t in s for t in tokens]
    return any(f) if any_ else all(f)


def snapshot(doc, pno):
    """Bir betli nusxa (doc, 0-bet)."""
    t = pymupdf.open()
    t.insert_pdf(doc, from_page=pno, to_page=pno)
    return t


def strip_source(snap_bytes, clip, w, h):
    """clip'dan tashqaridagi MATN jismonan o'chirilgan nusxa."""
    s = pymupdf.open("pdf", snap_bytes)
    pg = s[0]
    clip = R(clip)
    outside = [R(0, 0, w, clip.y0), R(0, clip.y1, w, h),
               R(0, clip.y0, clip.x0, clip.y1), R(clip.x1, clip.y0, w, clip.y1)]
    outside = [r for r in outside if r.width > 0.01 and r.height > 0.01]
    for r in outside:
        pg.add_redact_annot(r, fill=False)
    pg.apply_redactions(images=IMG_NONE, graphics=G_NONE, text=TXT)
    return s


def compact(doc, pno, y_s, y_e, segs, stamps=(), p0=None):
    """Sahifaning [y_s, y_e] oralig'ini bo'laklarga (segs=(s0,s1,dy)) bo'lib, yuqoriga suradi.
    Oraliqdagi eski kontent (matn, vektor, rasm) jismonan olib tashlanadi, bo'laklar toza
    manbadan (matni chegaradan tashqarida o'chirilgan) qayta quriladi.
    stamps: (clip, dy) -- p0 (asl nusxa)dan olingan kichik bo'lak (chap katak matni/chizig'i)."""
    page = doc[pno]
    W, H = page.rect.width, page.rect.height
    cur = snapshot(doc, pno).tobytes()
    srcs = [(strip_source(cur, (0, s0, W, s1), W, H), (0, s0, W, s1), dy) for s0, s1, dy in segs]
    p0b = p0.tobytes() if p0 is not None else None
    stamp_srcs = [(strip_source(p0b, c, W, H), c, dy) for c, dy in stamps]
    redact(page, [(0, y_s, W, y_e + 1.8)], text=True, gfx=G_COV, img=IMG)
    for s, clip, dy in srcs + stamp_srcs:
        clip = R(clip)
        page.show_pdf_page(R(clip.x0, clip.y0 + dy, clip.x1, clip.y1 + dy), s, 0, clip=clip)


def drop_dark_annots(doc):
    n = 0
    for pno in (50, 51, 81, 82, 83):
        if pno >= len(doc):
            continue
        page = doc[pno]
        for a in list(page.annots() or []):
            fc = a.colors.get("fill") or a.colors.get("stroke")
            if a.type[1] == "Square" and fc and max(fc) < 0.45:
                page.delete_annot(a)
                n += 1
    return n


# ---------------------------------------------------------------- 51
def do51(doc):
    p = doc[50]
    card = (306, 124, 544, 246)
    if not has(p, card, "Molyar", "massa"):
        return False
    redact(p, [(303, 121, 548, 249)])
    return True


# ---------------------------------------------------------------- 52
def do52(doc):
    p = doc[51]
    if not has(p, (51, 518, 150, 542), "nosi"):
        return False
    p0 = snapshot(doc, 51)
    # sarlavha (1 + Ma'nosi) o'chiriladi, pastdagi hamma narsa 25.4 pt yuqoriga suriladi
    band = (519.0, 544.4)
    redact(p, [(50, 517, 152, 543)])
    compact(doc, 51, 500, 781,
            [(500, band[0], 0.0), (band[1], 781, -(band[1] - band[0]))], p0=p0)
    return True


# ---------------------------------------------------------------- 82
def do82(doc):
    p = doc[81]
    if not has(p, (55, 659, 555, 731), "2-davr"):
        return False
    redact(p, [(52, 656, 558, 734)])
    return True


# ---------------------------------------------------------------- 83
def do83(doc):
    p = doc[82]
    box = (36, 67, 545, 657)
    if not has(p, box, "3-davr", "Qoida", any_=True):
        return False
    # "4 Umumiy formula" kartochkasi (y>=670) joyida qoladi
    redact(p, [box])
    return True


# ---------------------------------------------------------------- 84
# a,b : o'chiriladigan gorizontal tasma (chiziq egasi qoidasi: yuqori chiziq qoladi)
BANDS84 = [
    dict(name="Fe2+", band=(307.5, 329.2), row=(57, 307.6, 553, 329.1), tok=("Fe2+", "temir(II)"),
         left=(68.5, 297.5, 157.5, 316.5), left_tok="Fe(OH)2",
         line=(67.5, 328.5, 158.2, 329.2), yref=306.7),
    dict(name="Cu2+", band=(351.0, 373.5), row=(57, 351.1, 553, 373.4), tok=("Cu2+", "mis(II)"),
         left=(68.5, 341.5, 157.5, 360.5), left_tok="Cu(OH)2",
         line=(67.5, 372.7, 158.2, 373.5), yref=350.2),
    dict(name="Fe3+", band=(508.5, 530.2), row=(57, 508.6, 553, 530.1), tok=("Fe3+", "temir(III)"),
         left=(68.5, 486.0, 154.0, 506.0), left_tok="Fe(OH)3",
         line=(67.5, 529.5, 155.2, 530.2), yref=507.7),
    dict(name="Al3+", band=(574.5, 597.0), row=(57, 574.6, 553, 596.9), tok=("Al3+", "alyuminiy"),
         left=(68.5, 553.0, 154.0, 572.0), left_tok="Al(OH)3",
         line=(67.5, 596.2, 155.2, 597.0), yref=573.7),
]
ALL_BANDS84 = [(b["band"][0], b["band"][1]) for b in BANDS84]


def do84(doc):
    p = doc[83]
    present = []
    for b in BANDS84:
        if has(p, b["row"], *b["tok"]) and has(p, b["row"], "qoldig'i"):
            present.append(b)
    if not present:
        return False
    p0 = snapshot(doc, 83)
    # 1) qator matni/katagi jismonan o'chiriladi; chap birlashgan katak matni ham (keyin siljitilib qayta qo'yiladi)
    redact(p, [b["row"] for b in present], text=True, gfx=G_COV, img=IMG_NONE)
    redact(p, [b["left"] for b in present], text=True, gfx=G_NONE, img=IMG_NONE)

    def shift_before(y):  # y dan to'liq yuqorida joylashgan tasmalar yig'indisi
        return sum(b["band"][1] - b["band"][0] for b in present if b["band"][1] <= y + 1e-6)

    y_s, y_e = 218.0, 781.0
    bounds = [y_s]
    segs = []
    for b in present:
        segs.append((bounds[-1], b["band"][0], -shift_before(bounds[-1])))
        bounds.append(b["band"][1])
    segs.append((bounds[-1], y_e, -shift_before(bounds[-1])))
    text_stamps, line_stamps = [], []
    for b in present:
        a, c = b["band"]
        cum_before = shift_before(a)
        # chap ustun matni: yangi katak markazi bo'yicha
        text_stamps.append((b["left"], -(cum_before + (c - a) / 2)))
        # chap ustun pastki chizig'i: ref chiziq (o'ng ustunlarda) yangi o'rniga
        ref_new = b["yref"] - cum_before
        l = b["line"]
        line_stamps.append(((l[0], l[1], l[2], l[3]), ref_new - l[1]))
    stamps = text_stamps + line_stamps  # chiziqlar oxirida (matn kataklari ustiga tushmasin)
    compact(doc, 83, y_s, y_e, segs, stamps=stamps, p0=p0)
    return True


def main(src, dst):
    doc = pymupdf.open(src)
    if len(doc) < 84:
        raise SystemExit("PDF 84 betdan kam")
    res = {"annots": drop_dark_annots(doc)}
    # pastdan yuqoriga emas, betlar mustaqil
    for name, fn in (("51", do51), ("52", do52), ("82", do82), ("83", do83), ("84", do84)):
        res[name] = fn(doc)
    doc.save(dst, garbage=4, deflate=True)
    print(src, "->", dst, res)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
