"""Complete spheres (atoms) that are cut off by an image edge.

    from spherefix import load_image, detect_circles, complete_spheres
    arr = load_image(doc, xref)                 # H x W x 4 float RGBA (0..255)
    circles = detect_circles(arr, rmin, rmax)   # [(cx, cy, r), ...] image px (or give them by hand)
    new, off = complete_spheres(arr, circles, side="top", pad=14)
    # `new` is the extended RGBA image; `off` = number of rows/cols added on that side.

The missing cap of each sphere is painted from the shading of the visible part
(polar nearest-neighbour around the sphere's highlight) and the outline ring is
drawn in the sampled rim colour.  Only the *added* rows are painted, so all
original pixels stay as they are.  Added rows are transparent where no sphere
reaches, so the picture can be laid over the old one without a white box.
"""
import io
import numpy as np
import pymupdf
from PIL import Image
from scipy.spatial import cKDTree


def load_image(doc, xref):
    smask = None
    for pg in doc:
        for i in pg.get_images(full=True):
            if i[0] == xref:
                smask = i[1]
                break
        if smask is not None:
            break
    pix = pymupdf.Pixmap(doc, xref)
    if pix.colorspace is None or pix.colorspace.n != 3 or pix.alpha:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    rgb = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(float)
    a = np.full(rgb.shape[:2], 255.0)
    if smask:
        m = pymupdf.Pixmap(doc, smask)
        ma = np.frombuffer(m.samples, np.uint8).reshape(m.height, m.width).astype(float)
        if ma.shape == a.shape:
            a = ma
    return np.dstack([rgb, a])


def detect_circles(arr, rmin, rmax, dp=1.0, p1=80, p2=14, mind=None):
    import cv2
    rgb = arr[:, :, :3].astype(np.uint8)
    # pad so that circles cut by the border are still found
    P = int(rmax)
    big = cv2.copyMakeBorder(rgb, P, P, P, P, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    g = cv2.GaussianBlur(cv2.cvtColor(big, cv2.COLOR_RGB2GRAY), (5, 5), 1.2)
    c = cv2.HoughCircles(g, cv2.HOUGH_GRADIENT, dp, mind or rmin, param1=p1, param2=p2,
                         minRadius=int(rmin), maxRadius=int(rmax))
    return [] if c is None else [(float(x - P), float(y - P), float(r)) for x, y, r in c[0]]


def _rot(a, k):
    return np.rot90(a, k)


def complete_spheres(arr, circles, side="top", pad=14, ring_w=1.5, ring_color=None, clean_edge=2):
    """Extend the canvas on `side` by `pad` px and paint the cut caps. Returns (new_arr, pad)."""
    k = {"top": 0, "right": 1, "bottom": 2, "left": 3}[side]   # np.rot90(k=1) is counter-clockwise: the RIGHT edge becomes the top
    a = _rot(arr, k)                       # work as if the cut were at the top
    H, W, _ = a.shape
    # simple explicit mapping per k
    h0, w0 = arr.shape[:2]
    cs = []
    for cx, cy, r in circles:
        if k == 0:
            cs.append((cx, cy, r))
        elif k == 1:      # left -> top
            cs.append((cy, w0 - 1 - cx, r))
        elif k == 2:      # bottom -> top
            cs.append((w0 - 1 - cx, h0 - 1 - cy, r))
        else:             # right -> top
            cs.append((h0 - 1 - cy, cx, r))
    new = np.zeros((H + pad, W, 4))
    new[:, :, :3] = 255          # transparent rows carry white RGB (no dark fringe when resampled)
    new[pad:] = a
    ss = 4
    for cx, cy, r in cs:
        cy2 = cy + pad                     # in new canvas coordinates
        yy, xx = np.mgrid[0:pad, 0:W]
        d = np.hypot(xx - cx, yy - cy2)
        # observed pixels: inside circle (not on the rim), in the original image area, opaque
        Y, X = np.mgrid[pad:H + pad, 0:W]
        D = np.hypot(X - cx, Y - cy2)
        inner = (D < r - 2.5) & (new[pad:, :, 3] > 200)
        if inner.sum() < max(8, 0.15 * np.pi * r * r):     # too few visible pixels to model the shading
            print(f"spherefix: skipped circle {cx:.0f},{cy:.0f} r={r:.0f} (too little visible)")
            continue
        pts = np.column_stack([X[inner], Y[inner]]).astype(float)
        cols = new[pad:, :, :3][inner]
        # highlight centre = brightest 1% (or greenest) region of the visible disc
        lum = cols @ np.array([0.299, 0.587, 0.114])
        green = cols[:, 1] - 0.5 * (cols[:, 0] + cols[:, 2])
        score = np.where(green.max() > 25, green, lum)
        top = score >= np.percentile(score, 99)
        hx, hy = pts[top].mean(axis=0)
        # polar coords around highlight
        def feat(px, py):
            rho = np.hypot(px - hx, py - hy)
            th = np.arctan2(py - hy, px - hx)
            return np.column_stack([rho, th * max(r * 0.55, 1.0)])
        tree = cKDTree(feat(pts[:, 0], pts[:, 1]))
        miss = (d < r - 0.2)
        mx, my = xx[miss].astype(float), yy[miss].astype(float)
        if mx.size:
            _, idx = tree.query(feat(mx, my), k=4)
            col = cols[idx].mean(axis=1)
            new[:pad][miss, :3] = col
            new[:pad][miss, 3] = 255
        # rim colour
        if ring_color is None:
            ang = np.linspace(0, 2 * np.pi, 720, endpoint=False)
            rx = (cx + r * np.cos(ang)).round().astype(int)
            ry = (cy2 + r * np.sin(ang)).round().astype(int)
            ok = (rx >= 0) & (rx < W) & (ry >= pad) & (ry < H + pad)
            rc = new[ry[ok], rx[ok], :3]
            rim = np.median(rc[rc.sum(axis=1) < np.percentile(rc.sum(axis=1), 40)], axis=0) if ok.any() else np.array([120, 120, 130.0])
        else:
            rim = np.array(ring_color, float)
        # anti-aliased ring, only in the added rows
        sub = np.zeros((pad * ss, W * ss))
        Y2, X2 = np.mgrid[0:pad * ss, 0:W * ss]
        dd = np.hypot((X2 + .5) / ss - (cx + .5), (Y2 + .5) / ss - (cy2 + .5))
        sub[np.abs(dd - r) <= ring_w / 2] = 1
        cov = sub.reshape(pad, ss, W, ss).mean(axis=(1, 3))
        for c3 in range(3):
            new[:pad, :, c3] = new[:pad, :, c3] * (1 - cov) + rim[c3] * cov
        new[:pad, :, 3] = np.maximum(new[:pad, :, 3], cov * 255)
    if clean_edge:        # the old edge rows often carry a grey cut line: whiten them outside the spheres
        Y, X = np.mgrid[pad:pad + clean_edge, 0:W]
        inside = np.zeros(Y.shape, bool)
        for cx, cy, r in cs:
            inside |= np.hypot(X - cx, Y - (cy + pad)) < r + 1.2
        rows = new[pad:pad + clean_edge]
        rows[~inside, :3] = 255
        rows[~inside, 3] = 255
    out = _rot(new, (4 - k) % 4)
    return out, pad


def to_png(arr):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def _page_bg(pg, rect, side, pad_pts):
    """Mean colour / std of a thin strip of the page just outside `rect` on `side`."""
    t = 0.6
    strip = {"top": pymupdf.Rect(rect.x0, rect.y0 - pad_pts - t, rect.x1, rect.y0 - pad_pts),
             "bottom": pymupdf.Rect(rect.x0, rect.y1 + pad_pts, rect.x1, rect.y1 + pad_pts + t),
             "left": pymupdf.Rect(rect.x0 - pad_pts - t, rect.y0, rect.x0 - pad_pts, rect.y1),
             "right": pymupdf.Rect(rect.x1 + pad_pts, rect.y0, rect.x1 + pad_pts + t, rect.y1)}[side]
    pix = pg.get_pixmap(dpi=200, clip=strip & pg.rect, annots=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(-1, pix.n)[:, :3].astype(float)
    return a.mean(axis=0), float(a.std(axis=0).max())


def place(doc, page_no, xref, new_arr, side, pad, fill="auto"):
    """Lay the extended picture over every placement of `xref` on the page (old pixels stay under it).

    fill="auto": the added transparent rows are filled with the page colour next to the picture
    (when that is flat) - this avoids a faint resampling line at the transparent/opaque border."""
    pg = doc[page_no - 1]
    for r in pg.get_image_rects(xref):
        h0 = new_arr.shape[0] - (pad if side in ("top", "bottom") else 0)
        w0 = new_arr.shape[1] - (pad if side in ("left", "right") else 0)
        sx, sy = r.width / w0, r.height / h0
        x0, y0, x1, y1 = r.x0, r.y0, r.x1, r.y1
        add_pts = pad * (sy if side in ("top", "bottom") else sx)
        if side == "top":
            y0 -= add_pts
        elif side == "bottom":
            y1 += add_pts
        elif side == "left":
            x0 -= add_pts
        else:
            x1 += add_pts
        arr = new_arr
        if fill == "auto":
            col, sd = _page_bg(pg, r, side, add_pts)
            if sd < 6:
                a = new_arr[:, :, 3:4] / 255.0
                arr = new_arr.copy()
                arr[:, :, :3] = new_arr[:, :, :3] * a + col * (1 - a)
                arr[:, :, 3] = 255
        pg.insert_image(pymupdf.Rect(x0, y0, x1, y1), stream=to_png(arr), overlay=True)
