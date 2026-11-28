#!/usr/bin/env python3
"""List text found inside raster images: ocr/inventory.json"""
import io, json, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, pymupdf
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

ocr = RapidOCR()
d = pymupdf.open(sys.argv[1])
inv, cache = [], {}
for pn, pg in enumerate(d, 1):
    for im in pg.get_image_info(xrefs=True):
        if im["width"] < 120 or im["height"] < 40 or not im["xref"]:
            continue
        x = im["xref"]
        if x not in cache:
            pix = pymupdf.Pixmap(d, x)
            if pix.alpha or pix.colorspace.n != 3:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
            res, _ = ocr(img)
            cache[x] = [dict(text=t, conf=round(float(c), 2), box=[[round(float(a)) for a in p] for p in b])
                        for b, t, c in (res or []) if float(c) >= 0.5]
        if cache[x]:
            inv.append(dict(page=pn, xref=x, img_px=[im["width"], im["height"]],
                            bbox=[round(v, 1) for v in im["bbox"]], texts=cache[x]))
    print(pn, sum(len(i["texts"]) for i in inv if i["page"] == pn), flush=True)
json.dump(inv, open("ocr/inventory.json", "w"), ensure_ascii=False, indent=1)
print("images with text:", len(inv), "detections:", sum(len(i["texts"]) for i in inv))
