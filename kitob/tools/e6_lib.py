import pymupdf, importlib.util, math
R = pymupdf.Rect
spec = importlib.util.spec_from_file_location("rb", "/home/user/video-processor/kitob/tools/remove_black.py")
rb = importlib.util.module_from_spec(spec); spec.loader.exec_module(rb)
FONT = pymupdf.Font(fontfile="/home/user/video-processor/kitob/fonts/CMUSerif-Roman.ttf")
TEAL = (0.0706, 0.6275, 0.6392)
PALE = (0.8667, 0.9412, 0.9490)
BLACK = (0, 0, 0)
K = 0.5523
PAGE_RECT = [pymupdf.Rect(0, 0, 594.8, 842.2)]

def tl(s, size): return FONT.text_length(s, fontsize=size)

def rrect_path(sh, r, rad):
    x0, y0, x1, y1 = r
    P = pymupdf.Point
    k = rad * K
    sh.draw_line(P(x0 + rad, y0), P(x1 - rad, y0))
    sh.draw_bezier(P(x1 - rad, y0), P(x1 - rad + k, y0), P(x1, y0 + rad - k), P(x1, y0 + rad))
    sh.draw_line(P(x1, y0 + rad), P(x1, y1 - rad))
    sh.draw_bezier(P(x1, y1 - rad), P(x1, y1 - rad + k), P(x1 - rad + k, y1), P(x1 - rad, y1))
    sh.draw_line(P(x1 - rad, y1), P(x0 + rad, y1))
    sh.draw_bezier(P(x0 + rad, y1), P(x0 + rad - k, y1), P(x0, y1 - rad + k), P(x0, y1 - rad))
    sh.draw_line(P(x0, y1 - rad), P(x0, y0 + rad))
    sh.draw_bezier(P(x0, y0 + rad), P(x0, y0 + rad - k), P(x0 + rad - k, y0), P(x0 + rad, y0))

def fill_rrect(page, r, rad, color):
    sh = page.new_shape(); rrect_path(sh, r, rad)
    sh.finish(fill=color, color=None, closePath=True); sh.commit()

def dashed_rrect(page, r, rad=9, width=0.75, dash="[2.25 1.5] 0", color=TEAL, fill=None):
    sh = page.new_shape()
    if fill is not None:
        rrect_path(sh, r, rad); sh.finish(fill=fill, color=None, closePath=True)
    rrect_path(sh, r, rad)
    sh.finish(color=color, fill=None, width=width, dashes=dash, closePath=True, lineCap=0)
    sh.commit()

def solid_rrect(page, r, rad, color=TEAL, width=0.75, fill=(1, 1, 1)):
    sh = page.new_shape(); rrect_path(sh, r, rad)
    sh.finish(color=color, fill=fill, width=width, closePath=True); sh.commit()

def tri(page, x, top, color=(0.0431, 0.4549, 0.502)):
    sh = page.new_shape(); P = pymupdf.Point
    sh.draw_polyline([P(x, top), P(x + 6.8, top + 3.75), P(x, top + 7.5)])
    sh.finish(fill=color, color=None, closePath=True); sh.commit()

SUP, SUB = 0.745, 0.745
# word = list of (text, kind, color) ; kind n/sup/sub
def wlen(word, size):
    w = 0
    for t, k, c in word:
        w += tl(t, size if k == 'n' else size * SUP)
    return w

def W(text, kind='n', color=BLACK): return [(text, kind, color)]

def wrap(words, size, width, first_width=None):
    sp = tl(" ", size)
    lines, cur, cw = [], [], 0
    lim = first_width or width
    for w in words:
        l = wlen(w, size)
        add = l if not cur else sp + l
        if cur and cw + add > lim:
            lines.append(cur); cur, cw = [w], l; lim = width
        else:
            cur.append(w); cw += add
    if cur: lines.append(cur)
    return lines

def draw_line(tw_by_color, x, y, line, size, justify_to=None):
    sp = tl(" ", size)
    cx = x
    for i, w in enumerate(line):
        if i: cx += sp
        for t, k, c in w:
            if k == 'n': s, dy = size, 0
            elif k == 'sup': s, dy = size * SUP, -4.1 * size / 11
            else: s, dy = size * SUB, 2.3 * size / 11
            tw_by_color.setdefault(c, pymupdf.TextWriter(PAGE_RECT[0])).append((cx, y + dy), t, font=FONT, fontsize=s)
            cx += tl(t, s)
    return cx

def para(page, x, y, words, size, width, pitch, center=False, cx=None):
    lines = wrap(words, size, width)
    tws = {}
    for i, ln in enumerate(lines):
        xx = x
        if center:
            lw = sum(wlen(w, size) for w in ln) + tl(" ", size) * (len(ln) - 1)
            xx = cx - lw / 2
        draw_line(tws, xx, y + i * pitch, ln, size)
    for c, tw in tws.items(): tw.write_text(page, color=c)
    return len(lines)

def redact_all(page, rects, gfx=rb.G_COV, img=rb.IMG):
    rb.redact(page, rects, text=True, gfx=gfx, img=img)

def show(page, src_bytes, clip, dy, dx=0):
    W_, H_ = page.rect.width, page.rect.height
    s = rb.strip_source(src_bytes, clip, W_, H_)
    c = R(clip)
    page.show_pdf_page(R(c.x0 + dx, c.y0 + dy, c.x1 + dx, c.y1 + dy), s, 0, clip=c)

def equalize(doc, pno, rc, extra, cuts, shifts, pad=2.6, rad=9, fill_white=True, small=False):
    """rc: dashed-border centerline rect (x0,y0,x1,y1). Extend bottom by `extra`.
    cuts: y's separating groups; shifts: len(cuts)+1 dy values."""
    p = doc[pno]; PAGE_RECT[0] = p.rect
    snap = rb.snapshot(doc, pno).tobytes()
    x0, y0, x1, y1 = rc
    redact_all(p, [(x0 - 1.2, y0 - 1.2, x1 + 1.2, y1 + 1.2)])
    dashed_rrect(p, R(x0, y0, x1, y1 + extra), rad=rad, fill=(1, 1, 1) if fill_white else None)
    cr = rad + 0.3
    if small:
        for i in range(0, 1):
            show(p, snap, (x0 + cr, y0 + pad, x1 - cr, y1 - pad), shifts[0])
        return
    ys = [y0 + pad] + list(cuts) + [y1 - cr]
    for i in range(len(ys) - 1):
        xa = (x0 + cr, x1 - cr) if (i == 0 and shifts[0] != 0) else (x0 + pad, x1 - pad)
        show(p, snap, (xa[0], ys[i], xa[1], ys[i + 1]), shifts[i])

def shift_region(doc, pno, x0, x1, y_start, y_end, cuts, shifts, snap=None):
    """Redact (x0,y_start,x1,y_end) fully and re-show groups split at cuts, each moved by shifts[i]."""
    p = doc[pno]; PAGE_RECT[0] = p.rect
    snap = rb.snapshot(doc, pno).tobytes()
    redact_all(p, [(x0, y_start, x1, y_end)])
    ys = [y_start] + list(cuts) + [y_end]
    for i in range(len(ys) - 1):
        show(p, snap, (x0, ys[i], x1, ys[i + 1]), shifts[i])
