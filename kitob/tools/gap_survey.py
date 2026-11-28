#!/usr/bin/env python3
"""Map empty bands inside the body area of every page -> layout/gaps.json"""
import json, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, pymupdf
d = pymupdf.open(sys.argv[1])
BODY_TOP, BODY_BOT = 72.0, 764.0      # between header bar and footer bar (pt)
out = {}
for pn, pg in enumerate(d, 1):
    pix = pg.get_pixmap(dpi=36, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    s = 36 / 72
    x0, x1 = int(36 * s), int(560 * s)
    y0, y1 = int(BODY_TOP * s), int(BODY_BOT * s)
    rows = (a[y0:y1, x0:x1] < 245).any(axis=1)          # row has ink?
    ys = np.where(rows)[0]
    if ys.size == 0:
        out[pn] = {"content": None, "bands": [], "trailing_pt": BODY_BOT - BODY_TOP}
        continue
    first, last = ys[0], ys[-1]
    bands, run = [], None
    for i in range(first, last + 1):
        if not rows[i]:
            run = (i if run is None else run)
        elif run is not None:
            bands.append((run, i)); run = None
    bands = [(round(BODY_TOP + b0 / s, 1), round(BODY_TOP + b1 / s, 1), round((b1 - b0) / s, 1)) for b0, b1 in bands if (b1 - b0) / s >= 24]
    # horizontal extent of each ink run (block row) -> "side holes": tall runs whose ink covers < 62% of the width
    runs, st = [], None
    for i in range(first, last + 2):
        inkrow = i <= last and rows[i]
        if inkrow and st is None:
            st = i
        elif not inkrow and st is not None:
            runs.append((st, i)); st = None
    side = []
    for r0, r1 in runs:
        h = (r1 - r0) / s
        if h < 60:
            continue
        cols = (a[y0 + r0:y0 + r1, x0:x1] < 245).any(axis=0)
        xs = np.where(cols)[0]
        wid = (xs[-1] - xs[0]) / s
        if wid < 0.62 * 524:
            side.append({"y0": round(BODY_TOP + r0 / s, 1), "y1": round(BODY_TOP + r1 / s, 1),
                         "x0": round(36 + xs[0] / s, 1), "x1": round(36 + xs[-1] / s, 1)})
    out[pn] = {"content_top": round(BODY_TOP + first / s, 1), "content_bottom": round(BODY_TOP + last / s, 1),
               "leading_pt": round(first / s, 1), "bands_ge_24pt": bands, "side_holes": side,
               "trailing_pt": round(BODY_BOT - (BODY_TOP + last / s), 1)}
json.dump(out, open("layout/gaps.json", "w"), indent=1)
big = {p: v for p, v in out.items() if v.get("side_holes") or v.get("leading_pt", 0) > 100 or v["trailing_pt"] > 120 or any(b[2] > 40 for b in v.get("bands_ge_24pt", []))}
print("pages with inner gaps >=24pt or trailing blank >120pt:", len(big))
for p, v in big.items():
    print(p, "leading", v.get("leading_pt"), "trailing", v["trailing_pt"], "big-bands", [b[2] for b in v.get("bands_ge_24pt", []) if b[2] > 40], "side-holes", len(v.get("side_holes", [])))
