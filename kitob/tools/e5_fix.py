import pymupdf
R = pymupdf.Rect
SRC = 'Kimyo_1-qism_yakuniy_v3.pdf'
COV = pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED


def snap(doc, n):
    t = pymupdf.open(); t.insert_pdf(doc, from_page=n, to_page=n); return t.tobytes()


def strip(sb, clip, W, H):
    s = pymupdf.open('pdf', sb); pg = s[0]; c = R(clip)
    for r in [R(0, 0, W, c.y0), R(0, c.y1, W, H), R(0, c.y0, c.x0, c.y1), R(c.x1, c.y0, W, c.y1)]:
        if r.width > .01 and r.height > .01:
            pg.add_redact_annot(r, fill=False)
    pg.apply_redactions(images=0, graphics=0, text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    return s


def move(doc, n, rect, items, gfx=COV, between=None):
    """rect ichi tozalanadi; items=(clip,dy) bo'laklar qayta qo'yiladi (matni faqat clip ichida)."""
    p = doc[n]; W, H = p.rect.width, p.rect.height; sb = snap(doc, n)
    srcs = [(strip(sb, c, W, H), R(c), dy) for c, dy in items]
    p.add_redact_annot(R(rect), fill=False)
    p.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE, graphics=gfx, text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    if between:
        between()
    for s, c, dy in srcs:
        p.show_pdf_page(R(c.x0, c.y0 + dy, c.x1, c.y1 + dy), s, 0, clip=c)


def dash_points(page, card):
    card = R(card)
    for dr in page.get_drawings():
        r = dr['rect']
        if dr['type'] == 'f' and len(dr['items']) > 100 and abs(r.x0 - card.x0) < .3 and abs(r.y0 - card.y0) < .3 \
                and abs(r.x1 - card.x1) < .3 and abs(r.y1 - card.y1) < .3:
            pts = []
            for it in dr['items']:
                if it[0] == 'l':
                    pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            return pts
    raise RuntimeError('card not found %s' % (card,))


def side_mids(pts, x_lo, x_hi, y_lo, y_hi):
    ys = sorted({round(y, 2) for x, y in pts if x_lo <= x <= x_hi and y_lo <= y <= y_hi})
    return [(ys[i] + ys[i + 1]) / 2 for i in range(len(ys) - 1) if 1.2 < ys[i + 1] - ys[i] < 1.8]


def extend_card(doc, pno, card, E, n, corner=26):
    """Nuqtali yumaloq ramkaning pastki qismini E pt pastga suradi (yon chiziqlar n davrlik bo'lakdan cho'ziladi)."""
    p = doc[pno]; W, H = p.rect.width, p.rect.height
    x0, y0, x1, y1 = card
    ds = dash_points(p, card)
    sb = snap(doc, pno)
    src = pymupdf.open('pdf', sb)
    pieces = []     # (clip, dest)
    redacts = []
    for side in ('L', 'R'):
        if side == 'L':
            xl, xh = x0 - .5, x0 + 2.6
        else:
            xl, xh = x1 - 2.6, x1 + .5
        mids = side_mids(ds, xl, xh, y0 + 14, y1 - 9)
        mids = [m for m in mids]
        cand = [i for i, m in enumerate(mids) if m <= y1 - 11.5]
        i = cand[-1]; yc = mids[i]; ys = mids[i - n]
        cx0, cx1 = (x0 - 1.5, x0 + corner) if side == 'L' else (x1 - corner, x1 + 1.5)
        redacts.append(R(cx0, yc, cx1, y1 + 1.5))
        pieces.append((R(cx0, yc, cx1, y1 + 1.5), R(cx0, yc + E, cx1, y1 + 1.5 + E)))
        sx0, sx1 = (x0 - 1.5, x0 + 3.5) if side == 'L' else (x1 - 3.5, x1 + 1.5)
        cnt = max(1, round(E / (yc - ys)))
        for j in range(cnt):
            pieces.append((R(sx0, ys, sx1, yc), R(sx0, yc + j * E / cnt, sx1, yc + (j + 1) * E / cnt)))
    mx0, mx1 = x0 + corner, x1 - corner
    redacts.append(R(x0 - 1.5, y1 - 4, x1 + 1.5, y1 + 1.5))
    pieces.append((R(mx0, y1 - 4, mx1, y1 + 1.5), R(mx0, y1 - 4 + E, mx1, y1 + 1.5 + E)))
    for r in redacts:
        p.add_redact_annot(r, fill=False)
    p.apply_redactions(images=0, graphics=COV, text=pymupdf.PDF_REDACT_TEXT_NONE)
    for clip, dest in pieces:
        p.show_pdf_page(dest, src, 0, clip=clip)


if __name__ == '__main__':
    doc = pymupdf.open(SRC)
    # --- 41: chap katak (Ammoniy fosfat) qatorlari o'rta katakdagi sharlar bilan tekislab yoyiladi
    move(doc, 40, (70, 540, 209, 634), [
        ((70, 540, 209, 557.5), 6.0), ((70, 557.5, 209, 574.6), 24.0),
        ((70, 574.6, 209, 591.8), 41.0), ((70, 591.8, 209, 609.6), 58.0),
        ((70, 610.5, 209, 634), 62.0)])
    # --- 42: chap katak (Na2SO4)
    move(doc, 41, (58, 109, 196, 192), [
        ((58, 109, 196, 128.5), 1.0), ((58, 128.5, 196, 145.5), 17.4),
        ((58, 145.5, 196, 163.5), 34.0), ((58, 164.5, 196, 190), 38.0)])
    # --- 44: CO kartasi va Li2C2 kartasi chap qo'shnisi bilan bir xil pastki chegaraga
    extend_card(doc, 43, (293.92, 84.67, 528.07, 186.83), 20.3, 5)
    extend_card(doc, 43, (277.4, 384.7, 528.1, 552.1), 9.0, 2)
    # --- 43: oxirgi qator o'ng kartasi (PH4+) chap karta bilan tenglashtiriladi
    # --- 45: "Misol" kartasi chap ro'yxat balandligigacha cho'ziladi, qatorlar tekis yoyiladi
    move(doc, 44, (372, 391, 540, 443), [
        ((372, 394, 540, 410.5), 15.0), ((372, 410.5, 540, 425.0), 35.0), ((372, 425.0, 540, 443), 54.0)],
        between=lambda: extend_card(doc, 44, (368.9, 367.4, 542.3, 447.1), 72.0, 5, corner=26))
    out = pymupdf.open(); out.insert_pdf(doc, from_page=36, to_page=44)
    out.save('parts_e/e5.pdf', garbage=3, deflate=True)
    for i in range(9):
        out[i].get_pixmap(dpi=110).save(f'render/e5_after_{37+i}.png')
