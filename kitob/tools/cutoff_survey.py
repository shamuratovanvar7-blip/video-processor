#!/usr/bin/env python3
"""Find raster images whose visible content touches (and is cut by) an image edge."""
import io, json, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, pymupdf

d = pymupdf.open(sys.argv[1])
out, cache = [], {}

def rgba(xref, smask):
    pix = pymupdf.Pixmap(d, xref)
    if pix.colorspace is None or pix.colorspace.n != 3 or pix.alpha:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    arr = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(int)
    a = np.full((pix.height, pix.width), 255)
    if smask:
        m = pymupdf.Pixmap(d, smask)
        ma = np.frombuffer(m.samples, np.uint8).reshape(m.height, m.width)
        if ma.shape != a.shape:
            ma = np.array(pymupdf.Pixmap(m, pix.width, pix.height).samples, np.uint8).reshape(pix.height, pix.width) if False else np.kron(ma, np.ones((a.shape[0] // ma.shape[0] or 1, a.shape[1] // ma.shape[1] or 1), int))[:a.shape[0], :a.shape[1]]
        a = ma
    return arr, a

def edge_report(arr, a):
    bg = (a < 25) | (arr.min(axis=2) > 238)
    H, W = bg.shape
    if H < 20 or W < 20 or bg.mean() < 0.30:
        return None  # photo / full-bleed picture
    res = {}
    for name, band in (("left", bg[:, :2].all(axis=1)), ("right", bg[:, -2:].all(axis=1)),
                       ("top", bg[:2, :].all(axis=0)), ("bottom", bg[-2:, :].all(axis=0))):
        nb = ~band
        frac = nb.mean()
        # longest non-bg run along the edge
        run = best = 0
        for v in nb:
            run = run + 1 if v else 0
            best = max(best, run)
        if best >= 5 and frac < 0.97:
            res[name] = dict(run_px=int(best), frac=round(float(frac), 3))
    return res or None

for pn, pg in enumerate(d, 1):
    for img in pg.get_images(full=True):
        xref, smask = img[0], img[1]
        key = xref
        if key not in cache:
            try:
                arr, a = rgba(xref, smask)
                cache[key] = (edge_report(arr, a), arr.shape[1], arr.shape[0])
            except Exception as e:
                cache[key] = (None, 0, 0)
        rep, w, h = cache[key]
        if rep:
            for r in pg.get_image_rects(xref):
                out.append(dict(page=pn, xref=xref, img_px=[w, h], bbox=[round(v, 1) for v in r], edges=rep))
json.dump(out, open("cutoff/candidates.json", "w"), indent=1)
pages = sorted({o["page"] for o in out})
print("candidates:", len(out), "pages:", pages)
