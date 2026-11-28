"""Classical image-quality enhancement for raster pictures inside the book PDF.

No AI super-resolution model is available offline, so this is: de-JPEG / denoise
(edge-preserving), Lanczos upscaling to a target effective dpi, gentle
edge-aware sharpening, clean alpha.  Verify every result by eye.

    from enhance import load, metrics, enhance, to_png_bytes, to_jpeg_bytes
    arr = load(doc, xref)                        # H x W x 4 float RGBA
    m = metrics(arr)                             # sharpness / noise / blockiness
    out = enhance(arr, scale=2, denoise=4, sharpen=0.6)
    doc[page].replace_image(xref, stream=to_png_bytes(out))   # geometry unchanged
"""
import io
import numpy as np
import cv2
import pymupdf
from PIL import Image


def load(doc, xref):
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
    rgb = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.float32)
    a = np.full(rgb.shape[:2], 255, np.float32)
    if smask:
        m = pymupdf.Pixmap(doc, smask)
        ma = np.frombuffer(m.samples, np.uint8).reshape(m.height, m.width).astype(np.float32)
        if ma.shape == a.shape:
            a = ma
        else:
            a = cv2.resize(ma, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_LINEAR)
    return np.dstack([rgb, a])


def metrics(arr):
    g = cv2.cvtColor(arr[:, :, :3].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    lap = cv2.Laplacian(g, cv2.CV_32F)
    sharp = float(lap.var())
    # noise: median absolute deviation of the high-pass residual in flat areas
    blur = cv2.GaussianBlur(g, (0, 0), 1.0)
    res = g - blur
    noise = float(np.median(np.abs(res)) * 1.4826)
    # 8x8 JPEG blockiness: mean abs step across block borders vs inside blocks
    dx = np.abs(np.diff(g, axis=1))
    h, w = dx.shape
    cols = np.arange(w)
    border = dx[:, (cols % 8) == 7].mean() if w > 16 else 0.0
    inner = dx[:, (cols % 8) != 7].mean() if w > 16 else 1.0
    return dict(size=(arr.shape[1], arr.shape[0]), sharpness=round(sharp, 1), noise=round(noise, 2),
                blockiness=round(float(border / max(inner, 1e-3)), 2))


def enhance(arr, scale=1.0, denoise=3.0, sharpen=0.5, radius=1.0, keep_alpha=True):
    """scale>1 upsamples with Lanczos; denoise = cv2.fastNlMeans strength (0 = off); sharpen = unsharp amount."""
    rgb = arr[:, :, :3].astype(np.uint8)
    a = arr[:, :, 3]
    if denoise and denoise > 0:
        # work on opaque pixels only: fill transparent area with nearest colour to avoid dark halos
        rgb = cv2.fastNlMeansDenoisingColored(rgb, None, denoise, denoise, 5, 15)
    if scale and abs(scale - 1) > 1e-3:
        W, H = int(round(rgb.shape[1] * scale)), int(round(rgb.shape[0] * scale))
        rgb = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_LANCZOS4)
        a = cv2.resize(a, (W, H), interpolation=cv2.INTER_CUBIC)
    if sharpen and sharpen > 0:
        f = rgb.astype(np.float32)
        bl = cv2.GaussianBlur(f, (0, 0), radius * max(scale, 1))
        # edge-aware: sharpen less in flat regions (limits noise boosting)
        d = f - bl
        mag = np.abs(d).mean(axis=2, keepdims=True)
        gate = np.clip((mag - 2) / 10, 0, 1)
        f = f + sharpen * d * gate
        rgb = np.clip(f, 0, 255).astype(np.uint8)
    out = np.dstack([rgb.astype(np.float32), np.clip(a, 0, 255)]) if keep_alpha else np.dstack([rgb.astype(np.float32), np.full(rgb.shape[:2], 255, np.float32)])
    return out


def to_png_bytes(arr):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA" if arr.shape[2] == 4 else "RGB")
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return b.getvalue()


def to_jpeg_bytes(arr, quality=92):
    im = Image.fromarray(np.clip(arr[:, :, :3], 0, 255).astype(np.uint8), "RGB")
    b = io.BytesIO()
    im.save(b, "JPEG", quality=quality, subsampling=0, optimize=True)
    return b.getvalue()
