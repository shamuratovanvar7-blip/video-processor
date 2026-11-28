import sys; sys.path.insert(0,'/home/user/video-processor/kitob/tools')
from e6_lib import *
def do51(doc, pno=50):
    p = doc[pno]; Wp, Hp = p.rect.width, p.rect.height; PAGE_RECT[0] = p.rect
    snap = rb.snapshot(doc, pno).tobytes()
    size = 11
    BL = (0.0, 0.4549, 0.502); MOL = (0.0431*0+0.7176*0, 0, 0)
    molc = (0xb7/255*0+0x0b/255, 0x74/255, 0x80/255)
    X0, X1 = 67.5, 541.5
    cx = (X0 + X1) / 2
    # --- layout
    pale_x0, pale_x1 = X0 + 6.75, X1 - 6.75
    tx = 84.2; tw_ = pale_x1 - 10 - tx
    words_pale = [W("Mol", 'n', molc), W("—"), W("modda"), W("miqdorining"), W("birligi."), W("1"), W("mol"), W("moddada"),
        [("6,02", 'n', BLACK)], W("·"), [("10", 'n', BLACK), ("23", 'sup', BLACK)], W("ta"), W("zarra"), W("(atom,"), W("molekula,"), W("ion)"), W("bo‘ladi.")]
    pale_lines = wrap(words_pale, size, tw_)
    top = 126.0
    box_top = 159.8
    box_bot = box_top + 14.2 + 15 * (len(pale_lines) - 1) + 8.25
    bw = X1 - 14 - 86.9
    b1 = [W("Bu"), W("son"), W("Avogadro"), W("doimiysi"), W("deyiladi:"), [("N", 'n', BLACK), ("A", 'sub', BLACK)], W("="), W("6,02"), W("·"),
          [("10", 'n', BLACK), ("23", 'sup', BLACK)], [("mol", 'n', BLACK), ("−1", 'sup', BLACK), (".", 'n', BLACK)]]
    b2 = [W(t) for t in "1 mol — 0,012 kg (12 g) uglerod-12 dagi atomlar soniga teng zarralar tutuvchi modda miqdori.".split()]
    b3 = [W(t) for t in "Modda miqdori n harfi bilan belgilanadi, birligi — mol.".split()]
    # fix '6,02' '·' merging for b1 handled as separate words
    y = box_bot + 14.3
    items = []
    for b in (b1, b2, b3):
        ls = wrap(b, size, bw)
        items.append((y, ls))
        y += 14.5 * (len(ls) - 1) + 17.3
    last_base = items[-1][0] + 14.5 * (len(items[-1][1]) - 1)
    bot = last_base + 14.2
    delta = 333.0 - bot
    print("pale lines", len(pale_lines), "bottom", bot, "delta", delta)
    # --- remove & rebuild
    redact_all(p, [(0, 62, Wp, 781)])
    show(p, snap, (0, 62, Wp, 125.0), 0)
    sideh = 125.0 + (210.0 - delta)
    show(p, snap, (50, 125.0, 64, sideh), 0)
    show(p, snap, (546, 125.0, 560, sideh), 0)
    show(p, snap, (0, 334.5, Wp, 781), -delta)
    # card
    dashed_rrect(p, R(X0, top, X1, bot), rad=9, fill=(1, 1, 1))
    pw = 90.8; pill = R(cx - pw / 2, 132.8, cx + pw / 2, 151.5)
    fill_rrect(p, pill, 9.35, PALE)
    tws = {}
    draw_line(tws, pill.x0 + 11.7, 145.5, [W("Mol nima?")], 12.5) if False else None
    t = pymupdf.TextWriter(p.rect); t.append((pill.x0 + 11.7, 145.5), "Mol nima?", font=FONT, fontsize=12.5); t.write_text(p, color=(0x14/255, 0x20/255, 0x6a/255))
    fill_rrect(p, R(pale_x0, box_top, pale_x1, box_bot), 9, PALE)
    tws = {}
    for i, ln in enumerate(pale_lines):
        draw_line(tws, tx, 174.0 + 15 * i, ln, size)
    for c, tw in tws.items(): tw.write_text(p, color=c)
    tws = {}
    for yy, ls in items:
        tri(p, 74.2, yy - 6.8)
        for i, ln in enumerate(ls):
            draw_line(tws, 86.9, yy + 14.5 * i, ln, size)
    for c, tw in tws.items(): tw.write_text(p, color=c)
    return delta
if __name__ == "__main__":
    doc = pymupdf.open("/home/user/video-processor/kitob/Kimyo_1-qism_yakuniy_v3.pdf")
    do51(doc)
    doc[50].get_pixmap(dpi=110).save("/tmp/w/a51.png")
