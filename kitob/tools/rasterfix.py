"""Helpers to replace text that is baked into a raster image of a PDF page.

The picture itself is not edited.  On the page we paint a rectangle in the
local background colour over the old text and write the new text on top in
CMU Serif Roman (vector).  Works only where the background around the text is
flat (labels, pills, captions); it refuses text on photographs / glass / 3D
objects (non-uniform background) and says so.

    import sys; sys.path.insert(0, "/home/user/video-processor/kitob/tools")
    from rasterfix import fix_label
    r = fix_label(doc, 26, xref, quad, "Termometr", bbox, img_px)   # -> dict
"""
import io, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pymupdf
from PIL import Image

HERE = __file__.rsplit("/tools/", 1)[0]
ROMAN = pymupdf.Font(fontfile=f"{HERE}/fonts/CMUSerif-Roman.ttf")
_cache = {}


def image_array(doc, xref):
    key = (id(doc), xref)
    if key not in _cache:
        pix = pymupdf.Pixmap(doc, xref)
        if pix.alpha or pix.colorspace.n != 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        _cache[key] = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")).astype(float)
    return _cache[key]


def analyse(doc, xref, quad, pad=2, ring=2):
    """-> dict(rect_px, bg(0-1 rgb), fg(0-1 rgb), bg_std)"""
    img = image_array(doc, xref)
    H, W, _ = img.shape
    xs = [p[0] for p in quad]
    ys = [p[1] for p in quad]
    x0, x1 = max(0, min(xs) - pad), min(W, max(xs) + pad)
    y0, y1 = max(0, min(ys) - pad), min(H, max(ys) + pad)
    X0, X1, Y0, Y1 = max(0, x0 - ring), min(W, x1 + ring), max(0, y0 - ring), min(H, y1 + ring)
    outer = img[int(Y0):int(Y1), int(X0):int(X1)].copy()
    mask = np.ones(outer.shape[:2], bool)
    mask[int(y0 - Y0):int(y1 - Y0), int(x0 - X0):int(x1 - X0)] = False
    ringpx = outer[mask]
    bg = np.median(ringpx, axis=0)
    bg_std = float(np.mean(np.std(ringpx, axis=0)))
    inner = img[int(y0):int(y1), int(x0):int(x1)].reshape(-1, 3)
    lum = inner @ np.array([0.299, 0.587, 0.114])
    dark = inner[lum <= np.percentile(lum, 8)]
    fg = np.median(dark, axis=0)
    return dict(rect_px=(x0, y0, x1, y1), bg=tuple(bg / 255), fg=tuple(fg / 255), bg_std=bg_std)


def fix_label(doc, page_no, xref, quad, text, bbox, img_px, align="center", max_std=24.0,
              size=None, color=None, grow=1.0, baseline=0.22, force=False):
    """Replace the raster text inside `quad` (image pixel coords) by `text`.

    bbox   : where the image sits on the page (inventory 'bbox')
    img_px : [width, height] of the image in pixels (inventory 'img_px')
    size   : font size in pt (default: fitted to the old text height / width)
    color  : rgb 0-1 for the new text (default: the old text colour)
    force  : paint even when the background is not flat (rarely a good idea)
    returns dict(status='done'|'skipped', reason=..., size=..., rect=...)
    """
    a = analyse(doc, xref, quad)
    if a["bg_std"] > max_std and not force:
        return dict(status="skipped", reason=f"non-uniform background (std {a['bg_std']:.0f})")
    pg = doc[page_no - 1]
    bx0, by0, bx1, by1 = bbox
    sx, sy = (bx1 - bx0) / img_px[0], (by1 - by0) / img_px[1]
    x0, y0, x1, y1 = a["rect_px"]
    rect = pymupdf.Rect(bx0 + x0 * sx, by0 + y0 * sy, bx0 + x1 * sx, by0 + y1 * sy)
    pg.draw_rect(rect, color=None, fill=a["bg"], overlay=True)
    h, w = rect.height, rect.width
    fs = size or min(h * 0.95 * grow, w * grow / max(ROMAN.text_length(text, fontsize=1), 1e-6))
    tl = ROMAN.text_length(text, fontsize=fs)
    x = {"center": rect.x0 + (w - tl) / 2, "left": rect.x0 + 1, "right": rect.x1 - tl - 1}[align]
    y = rect.y1 - baseline * h
    tw = pymupdf.TextWriter(pg.rect, color=color or a["fg"])
    tw.append((x, y), text, font=ROMAN, fontsize=fs)
    tw.write_text(pg)
    return dict(status="done", size=round(fs, 2), rect=[round(v, 1) for v in rect])
