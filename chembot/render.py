"""Kimyo "video yechim" renderer: JSON yechim -> MP4 (3:4, 810x1080).

Fon: assets/template.png (ko'k to'lqinli "Masala yechimi" shabloni).
Faqat Pillow + ffmpeg ishlatiladi (brauzer kerak emas).
"""
import math
import os
import random
import re
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "assets", "template.png")

W, H = 810, 1080
FPS = 12
SPEED = float(os.getenv("VIDEO_SPEED", "1.0"))  # >1 tezroq, <1 sekinroq
FRAME = (18, 119, 791, 975)  # shablondagi ramka (x0, y0, x1, y1)
CONTENT_W = 690

TEACHERS = [t.strip() for t in os.getenv("TEACHERS", "Shamuratov Anvar|Jo'rayev Ahror").split("|") if t.strip()]
BRAND_HANDLE = os.getenv("BRAND_HANDLE", "").strip()

NAVY = (16, 58, 110)
INK = (16, 42, 84)
INK_SOFT = (62, 82, 112)
ACCENT = (214, 84, 32)
LIGHT = (200, 226, 250)
MINT = (200, 236, 224)
SAND = (255, 236, 170)
WHITE = (255, 255, 255)

_FD = "/usr/share/fonts/truetype/dejavu/"
_CMU = os.path.join(HERE, "assets", "fonts")
# CMU Serif Roman / Bold (loyiha ichida), yo'q belgilar uchun DejaVu zaxira
_FONT_FILES = {
    "sans": [os.path.join(_CMU, "cmunrm.ttf"), "/usr/share/fonts/truetype/cmu/cmunrm.ttf", _FD + "DejaVuSerif.ttf"],
    "sans_b": [os.path.join(_CMU, "cmunbx.ttf"), "/usr/share/fonts/truetype/cmu/cmunbx.ttf", _FD + "DejaVuSerif-Bold.ttf"],
    "serif_b": [os.path.join(_CMU, "cmunbx.ttf"), "/usr/share/fonts/truetype/cmu/cmunbx.ttf", _FD + "DejaVuSerif-Bold.ttf"],
    "fb": [_FD + "DejaVuSerif.ttf", _FD + "DejaVuSans.ttf"],
    "fb_b": [_FD + "DejaVuSerif-Bold.ttf", _FD + "DejaVuSans-Bold.ttf"],
}
FS = 1.16  # CMU belgilari DejaVu'ga qaraganda kichikroq, shuning uchun biroz kattalashtiramiz
_font_cache = {}


def font(kind, size):
    key = (kind, size)
    if key not in _font_cache:
        px = size if kind.startswith("fb") else int(round(size * FS))
        for p in _FONT_FILES[kind]:
            if os.path.exists(p):
                _font_cache[key] = ImageFont.truetype(p, px)
                break
        else:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


# ---------------------------------------------------------------- matn
_SUB = str.maketrans("0123456789+-=()", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")
_SUP = str.maketrans("0123456789+-=()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")


def fix_text(s):
    """_{2} va ^{2+} belgilarini Unicode indekslarga aylantiradi."""
    s = str(s)
    s = re.sub(r"_\{([^}]*)\}", lambda m: m.group(1).translate(_SUB), s)
    s = re.sub(r"\^\{([^}]*)\}", lambda m: m.group(1).translate(_SUP), s)
    s = s.replace("->", "→")
    return s


_SUBM = dict(zip("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎", "0123456789+-=()"))
_SUPM = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾", "0123456789+-=()"))
_FALLBACK = set("≈≠≤≥′⇄⇌↔⚗")


def to_runs(text):
    """Matnni (belgi, rejim, zaxira) bo'laklariga ajratadi: rejim n/sub/sup."""
    runs = []
    for ch in text:
        if ch in _SUBM:
            c, mode = _SUBM[ch], "sub"
        elif ch in _SUPM:
            c, mode = _SUPM[ch], "sup"
        else:
            c, mode = ch, "n"
        fb = ch in _FALLBACK
        if runs and runs[-1][1] == mode and runs[-1][2] == fb:
            runs[-1][0] += c
        else:
            runs.append([c, mode, fb])
    return runs


def _run_font(kind, size, mode, fb):
    sz = size if mode == "n" else max(int(size * 0.68), 10)
    k = ("fb" if kind == "sans" else "fb_b") if fb else kind
    return font(k, sz)


def rich_width(text, kind, size):
    return sum(_run_font(kind, size, m, fb).getlength(c) for c, m, fb in to_runs(text))


def rich_draw(d, x, top, text, kind, size, fill):
    """Indeksli matnni chizadi (CMU Serif'da indeks raqamlari yo'qligi uchun qo'lda)."""
    base = font(kind, size)
    baseline = top + base.getmetrics()[0]
    for c, m, fb in to_runs(text):
        f = _run_font(kind, size, m, fb)
        dy = 0 if m == "n" else (int(size * 0.20) if m == "sub" else -int(size * 0.34))
        d.text((x, baseline + dy), c, font=f, fill=fill, anchor="ls")
        x += f.getlength(c)
    return x


def wrap(text, kind, size, maxw):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            t = (cur + " " + w).strip()
            if rich_width(t, kind, size) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def text_strip(text, kind, size, fill, align="center", maxw=CONTENT_W, pad=0, line_gap=1.38):
    lines = wrap(text, kind, size, maxw)
    lh = int(size * line_gap)
    h = lh * len(lines) + pad * 2
    im = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        tw = rich_width(ln, kind, size)
        x = (W - tw) / 2 if align == "center" else (W - maxw) / 2
        rich_draw(d, x, pad + i * lh, ln, kind, size, fill)
    return im


def chip_strip(text, size, bg, fg=INK, kind="sans_b", maxw=CONTENT_W, padx=22, pady=10, radius=16, tilt=0.0):
    lines = wrap(text, kind, size, maxw - 2 * padx)
    lh = int(size * 1.38)
    tw = max(rich_width(l, kind, size) for l in lines)
    bw, bh = int(tw + 2 * padx), lh * len(lines) + 2 * pady
    chip = Image.new("RGBA", (bw + 8, bh + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(chip)
    d.rounded_rectangle((4, 7, bw + 4, bh + 7), radius, fill=(10, 40, 90, 40))  # soya
    d.rounded_rectangle((4, 4, bw + 4, bh + 4), radius, fill=bg)
    for i, ln in enumerate(lines):
        rich_draw(d, 4 + (bw - rich_width(ln, kind, size)) / 2, 4 + pady + i * lh, ln, kind, size, fg)
    if tilt:
        chip = chip.rotate(tilt, expand=True, resample=Image.BICUBIC)
    strip = Image.new("RGBA", (W, chip.height + 4), (0, 0, 0, 0))
    strip.alpha_composite(chip, ((W - chip.width) // 2, 2))
    return strip


def make_strip(item, size, left=False):
    style = item.get("style", "note")
    text = fix_text(item.get("text", ""))
    al = "left" if left else "center"
    if style == "equation":
        return text_strip(text, "sans_b", size, INK, al)
    if style == "result":
        return text_strip(text, "sans_b", size, ACCENT, al)
    if style == "badge":
        return chip_strip(text, max(size - 6, 18), LIGHT)
    if style == "box":
        return chip_strip(text, max(size - 6, 18), NAVY, WHITE)
    return text_strip(text, "sans", max(size - 5, 18), INK_SOFT, al)


def layout_items(items, y0, y1, size=40, gap=24, left=False):
    """Elementlarni [y0,y1] oraliqqa sig'diradigan shriftda joylashtiradi."""
    while True:
        strips = [make_strip(it, size, left) for it in items]
        total = sum(s.height for s in strips) + gap * max(len(strips) - 1, 0)
        if total <= (y1 - y0) or size <= 18:
            break
        size -= 2
    y = y0
    out = []
    for s in strips:
        out.append((s, y))
        y += s.height + gap
    return out


# ---------------------------------------------------------------- fon
_bg_cache = {}


def background():
    if "bg" not in _bg_cache:
        im = Image.open(TEMPLATE).convert("RGB").resize((W, H), Image.LANCZOS)
        _bg_cache["bg"] = im
    return _bg_cache["bg"].copy()


def credits(im):
    if not TEACHERS:
        return
    d = ImageDraw.Draw(im)
    txt = "Ustozlar: " + "  ·  ".join(TEACHERS)
    rich_draw(d, (W - rich_width(txt, "sans_b", 22)) / 2, 1026, txt, "sans_b", 22, INK_SOFT)


def dots(im, n, cur):
    if n <= 0:
        return
    d = ImageDraw.Draw(im)
    gap, r = 28, 6
    total = (n - 1) * gap + 34
    x = (W - total) / 2
    y = 1000
    for i in range(n):
        if i == cur:
            d.rounded_rectangle((x - 2, y - r, x + 30, y + r), r, fill=NAVY)
            x += 34 + (gap - 16)
        else:
            d.ellipse((x, y - r, x + 2 * r, y + r), fill=NAVY if i < cur else WHITE, outline=NAVY, width=2)
            x += gap


def static_base(label=None, title=None, n_dots=0, cur_dot=0, title_size=38):
    im = background()
    credits(im)
    y = 150
    if label:
        chip = chip_strip(fix_text(label), 24, NAVY, WHITE, tilt=0, padx=22, pady=7, radius=18)
        im.paste(chip, (0, y), chip)
        y += chip.height + 6
    if title:
        s = text_strip(fix_text(title), "serif_b", title_size, NAVY, "center", maxw=700)
        while s.height > 110 and title_size > 26:
            title_size -= 2
            s = text_strip(fix_text(title), "serif_b", title_size, NAVY, "center", maxw=700)
        im.paste(s, (0, y), s)
    dots(im, n_dots, cur_dot)
    return im


# ---------------------------------------------------------------- sahnalar
# Sahnalar 720x430 tuvalga chizilib, keyin bo'sh joyga moslab kichraytiriladi.
SW, SH = 720, 430
SCENE_BOX = (0, 255, W, 665)

_COLORS = {
    "blue": (110, 165, 232), "green": (150, 214, 170), "colorless": (214, 232, 240),
    "yellow": (245, 230, 140), "brown": (190, 140, 100), "red": (230, 120, 110),
    "orange": (240, 170, 100), "pink": (245, 175, 200), "purple": (180, 150, 220),
}


def col(v, default=(110, 165, 232)):
    if not v:
        return default
    if isinstance(v, str):
        if v.startswith("#") and len(v) == 7:
            return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))
        return _COLORS.get(v.lower(), default)
    return default


def caption(d, text, cy):
    if not text:
        return
    text = fix_text(text)
    tw = rich_width(text, "sans_b", 27)
    x = (SW - tw) / 2
    d.rounded_rectangle((x - 16, cy - 6, x + tw + 16, cy + 40), 10, fill=(255, 255, 255, 235), outline=LIGHT + (255,), width=2)
    rich_draw(d, x, cy, text, "sans_b", 27, INK)


def bubbles(d, t, x0, x1, ybot, ytop, n=14, seed=1, r=(3, 7), speed=0.35):
    rnd = random.Random(seed)
    for i in range(n):
        px = rnd.uniform(x0, x1)
        ph = rnd.random()
        sp = speed * rnd.uniform(0.7, 1.4)
        rr = rnd.uniform(*r)
        f = (t * sp + ph) % 1.0
        y = ybot - f * (ybot - ytop)
        x = px + math.sin(t * 3 + i) * 4
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(255, 255, 255, 230), width=2)


def gas_cloud(d, t, cx, cy, color, scale=1.0, seed=3):
    rnd = random.Random(seed)
    c = col(color, (217, 146, 107))
    for i in range(9):
        ox, oy = rnd.uniform(-40, 40), rnd.uniform(0, 50)
        f = (t * 0.25 + i / 9) % 1.0
        r = (22 + 26 * f) * scale
        y = cy - f * 120 * scale - oy * 0.3
        a = int(150 * (1 - f))
        x = cx + ox + math.sin(t * 2 + i) * 8
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (a,))


def draw_beaker(d, cx, top, bw, bh, level, liquid, t, p, seed=1):
    x0, x1, bot = cx - bw // 2, cx + bw // 2, top + bh
    ly = bot - int(bh * level)
    d.rectangle((x0 + 3, ly, x1 - 3, bot - 3), fill=liquid + (235,))
    d.line((x0 + 3, ly, x1 - 3, ly), fill=(255, 255, 255, 200), width=2)
    prec = p.get("precipitate")
    if prec:
        k = min(t / 2.0, 1.0)
        th = int(26 * k)
        d.rectangle((x0 + 4, bot - 3 - th, x1 - 4, bot - 3), fill=col(prec, (200, 100, 60)) + (255,))
    solid = p.get("solid")
    if solid:
        rnd = random.Random(seed + 5)
        for _ in range(26):
            sx = rnd.uniform(x0 + 12, x1 - 12)
            d.ellipse((sx - 5, bot - 14 - rnd.uniform(0, 8), sx + 5, bot - 6), fill=col(solid, (190, 80, 50)) + (255,))
    if p.get("bubbles", True) and level > 0.2:
        bubbles(d, t, x0 + 14, x1 - 14, bot - 10, ly + 6, seed=seed)
    g = (70, 90, 100, 255)
    d.line((x0, top - 10, x0, bot), fill=g, width=4)
    d.line((x1, top - 10, x1, bot), fill=g, width=4)
    d.line((x0, bot, x1, bot), fill=g, width=4)
    d.line((x0 - 8, top - 10, x0 + 6, top - 10), fill=g, width=4)
    d.line((x1 - 6, top - 10, x1 + 8, top - 10), fill=g, width=4)


def scene_beaker(d, t, p):
    cx, top = SW // 2, 70
    draw_beaker(d, cx, top, 250, 240, float(p.get("level", 0.62)), col(p.get("color")), t, p)
    if p.get("gas_color") or p.get("gas"):
        gas_cloud(d, t, cx, top + 20, p.get("gas_color") or "#D9926B")
    if p.get("gas"):
        rich_draw(d, cx + 120, top - 34, fix_text(str(p["gas"])) + "↑", "sans_b", 34, INK)
    caption(d, p.get("caption"), top + 270)


def scene_test_tube(d, t, p):
    base_y = SH - 70
    d.rectangle((70, base_y, 430, base_y + 12), fill=(80, 90, 96, 255))
    d.rectangle((92, 60, 102, base_y), fill=(80, 90, 96, 255))
    d.rectangle((92, 128, 190, 138), fill=(120, 80, 50, 255))
    tw, th = 64, 260
    tube = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
    td = ImageDraw.Draw(tube)
    td.rounded_rectangle((10, 10, 10 + tw, 10 + th), 30, fill=(235, 245, 250, 150), outline=(70, 90, 100, 255), width=4)
    rnd = random.Random(7)
    for i in range(30):
        sx, sy = rnd.uniform(20, 10 + tw - 10), rnd.uniform(th - 60, th - 8)
        c = (200, 60, 40, 255) if i % 3 else (40, 35, 35, 255)
        td.ellipse((sx - 5, sy - 5, sx + 5, sy + 5), fill=c)
    ang = 50
    rot = tube.rotate(ang, expand=True, resample=Image.BICUBIC)
    ccx, ccy = 260, 150
    d.ov.alpha_composite(rot, (int(ccx - rot.width / 2), int(ccy - rot.height / 2)))
    r_ = th / 2
    bx = ccx + r_ * math.sin(math.radians(ang))
    by = ccy + r_ * math.cos(math.radians(ang))
    mx = ccx - r_ * math.sin(math.radians(ang))
    my = ccy - r_ * math.cos(math.radians(ang))
    d.rectangle((bx - 18, by + 40, bx + 18, base_y), fill=(55, 60, 64, 255))
    if p.get("heat", True):
        fl = 1 + 0.18 * math.sin(t * 14) + 0.1 * math.sin(t * 23)
        for sc, c in ((1.0, (255, 150, 40, 230)), (0.62, (255, 215, 90, 240)), (0.34, (90, 150, 255, 255))):
            h = 62 * fl * sc
            d.polygon([(bx - 14 * sc, by + 40), (bx, by + 40 - h), (bx + 14 * sc, by + 40)], fill=c)
    if p.get("gas"):
        gas_cloud(d, t, mx - 10, my - 5, (200, 200, 205), 0.8, seed=9)
        rich_draw(d, mx + 30, my - 104, fix_text(str(p["gas"])) + "↑", "sans_b", 34, INK)
    caption(d, p.get("caption"), SH - 52)


def scene_electrolysis(d, t, p):
    cx, top, bw, bh = SW // 2, 100, 360, 190
    liquid = col(p.get("color"), (120, 170, 225))
    draw_beaker(d, cx, top, bw, bh, 0.72, liquid, t, {"bubbles": False})
    ex_c, ex_a = cx - 80, cx + 80
    ytop, ybot = top - 40, top + bh - 28
    d.rectangle((ex_c - 11, ytop, ex_c + 11, ybot), fill=(150, 150, 155, 255))
    k = min(t / 3.0, 1.0) * float(p.get("progress", 0.6))
    cw = int(12 * k + 2)
    d.rectangle((ex_c - 11 - cw, top + 60, ex_c + 11 + cw, ybot), fill=(205, 110, 60, 255))
    d.rectangle((ex_a - 11, ytop, ex_a + 11, ybot), fill=(45, 45, 50, 255))
    bubbles(d, t, ex_a - 14, ex_a + 14, ybot - 5, top + 62, n=8, seed=4, r=(2, 5))
    bubbles(d, t, ex_c - 14, ex_c + 14, ybot - 5, top + 62, n=4, seed=8, r=(2, 4), speed=0.2)
    d.rounded_rectangle((cx - 40, 8, cx + 40, 42), 6, fill=(40, 40, 44, 255))
    rich_draw(d, cx - 28, 8, "–", "sans_b", 26, WHITE)
    rich_draw(d, cx + 12, 8, "+", "sans_b", 26, WHITE)
    d.line((cx - 30, 8, cx - 30, 2, ex_c, 2, ex_c, ytop), fill=(40, 40, 44, 255), width=3)
    d.line((cx + 30, 8, cx + 30, 2, ex_a, 2, ex_a, ytop), fill=(40, 40, 44, 255), width=3)
    rich_draw(d, ex_c - 56, top + bh + 6, "KATOD (–)", "sans_b", 24, INK_SOFT)
    rich_draw(d, ex_a - 52, top + bh + 6, "ANOD (+)", "sans_b", 24, INK_SOFT)
    py = top + bh + 52
    d.rounded_rectangle((90, py, SW - 90, py + 28), 14, fill=(255, 255, 255, 230), outline=NAVY + (255,), width=3)
    frac = min(t / 4.0, 1.0) * float(p.get("progress", 0.6))
    if frac > 0.02:
        d.rounded_rectangle((92, py + 2, 92 + int((SW - 184) * frac), py + 26), 12, fill=ACCENT + (255,))
    if p.get("progress_label"):
        lbl = fix_text(str(p["progress_label"]))
        rich_draw(d, (SW - rich_width(lbl, "sans_b", 28)) / 2, py + 34, lbl, "sans_b", 28, INK)


SCENES = {"beaker": scene_beaker, "test_tube": scene_test_tube, "electrolysis": scene_electrolysis}


def draw_scene(frame, name, t, params):
    fn = SCENES.get(name)
    if not fn:
        return
    ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    dr.ov = ov
    fn(dr, t, params or {})
    bw, bh = SCENE_BOX[2] - SCENE_BOX[0], SCENE_BOX[3] - SCENE_BOX[1]
    k = min(bw / SW, bh / SH)
    ov = ov.resize((int(SW * k), int(SH * k)), Image.LANCZOS)
    frame.paste(ov, (SCENE_BOX[0] + (bw - ov.width) // 2, SCENE_BOX[1]), ov)


# ---------------------------------------------------------------- slaydlar
class Slide:
    def __init__(self, base, items, scene=None, params=None, hold=2.5, reveal=None):
        self.base, self.items = base, items  # items: [(strip, y)]
        self.scene, self.params = scene, params or {}
        self.hold = hold
        self.reveal = reveal  # har element uchun soniya


def _states(base, items):
    states = [base]
    cur = base
    for strip, y in items:
        nxt = cur.copy()
        nxt.paste(strip, (0, y), strip)
        states.append(nxt)
        cur = nxt
    return states


def slide_frames(sl: Slide):
    states = _states(sl.base, sl.items)
    fade = 3
    frame_i = 0

    def emit(img, t):
        f = img.copy()
        if sl.scene:
            draw_scene(f, sl.scene, t, sl.params)
        return f

    for _ in range(int(0.5 / SPEED * FPS)):
        yield emit(states[0], frame_i / FPS)
        frame_i += 1
    for k in range(1, len(states)):
        dur = max(sl.reveal[k - 1] if sl.reveal else 1.0, 0.5)
        for j in range(fade):
            f = (j + 1) / fade
            yield emit(Image.blend(states[k - 1], states[k], f), frame_i / FPS)
            frame_i += 1
        for _ in range(max(int(dur * FPS) - fade, 0)):
            yield emit(states[k], frame_i / FPS)
            frame_i += 1
    for _ in range(int(sl.hold / SPEED * FPS)):
        yield emit(states[-1], frame_i / FPS)
        frame_i += 1


def reading_time(text, base=0.55, per_char=0.018):
    return (base + per_char * len(text)) / SPEED


def build_slides(data):
    steps = data.get("steps", [])
    n = len(steps)
    slides = []

    # 1. Masala sahifasi (sukut bo'yicha o'chiq: video to'g'ridan-to'g'ri yechimdan boshlanadi)
    if os.getenv("SHOW_PROBLEM", "0") == "1" and data.get("problem_text"):
        base = static_base("MASALA", data.get("title"), 0, 0, title_size=34)
        ptxt = fix_text(data.get("problem_text", ""))
        items = layout_items([{"text": ptxt, "style": "note"}], 270, 955, size=34, left=True)
        slides.append(Slide(base, items, hold=max(3.0, 0.04 * len(ptxt)), reveal=[1.0]))

    # 2. Qadamlar
    for i, st in enumerate(steps):
        base = static_base(st.get("label", f"{i + 1}-QADAM"), st.get("title"), n, i)
        scene = st.get("scene") if st.get("scene") in SCENES else None
        y0 = 690 if scene else 300
        items = layout_items(st.get("lines", []), y0, 955)
        reveal = [reading_time(fix_text(l.get("text", ""))) for l in st.get("lines", [])]
        slides.append(Slide(base, items, scene, st.get("scene_params"), hold=1.0, reveal=reveal))

    # 3. Qoidalar
    rules = data.get("rules") or []
    if rules:
        base = static_base("QOIDALAR", "Esda saqlang!", n, max(n - 1, 0))
        strips, y = [], 310
        for i, r in enumerate(rules[:6]):
            s = chip_strip(f"{i + 1}  " + fix_text(r), 31, [LIGHT, MINT, SAND][i % 3], maxw=CONTENT_W, pady=16)
            strips.append((s, y))
            y += s.height + 24
        slides.append(Slide(base, strips, hold=1.8,
                            reveal=[reading_time(fix_text(r), 0.7, 0.022) for r in rules[:6]]))

    # 4. Javoblar
    answers = data.get("answers") or []
    if answers:
        base = static_base("JAVOBLAR", "Natijalar", n, max(n - 1, 0))
        strips, y = [], 310
        for a in answers[:6]:
            val = wrap(fix_text(a.get("value", "")), "sans_b", 34, CONTENT_W - 60)
            ch = 52 + 46 * len(val) + 14
            card = Image.new("RGBA", (W, ch + 12), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            x0, x1 = (W - CONTENT_W) // 2, (W + CONTENT_W) // 2
            cd.rounded_rectangle((x0, 6, x1, 6 + ch), 12, fill=WHITE, outline=NAVY, width=3)
            rich_draw(cd, x0 + 20, 12, fix_text(a.get("label", "")), "sans", 22, INK_SOFT)
            for j, ln in enumerate(val):
                rich_draw(cd, x0 + 20, 44 + 46 * j, ln, "sans_b", 34, INK)
            strips.append((card, y))
            y += card.height + 20
        slides.append(Slide(base, strips, hold=2.5, reveal=[0.9 / SPEED] * len(strips)))

    # 5. Ustozlar sahifasi
    base = background()
    d = ImageDraw.Draw(base)
    # shablon sarlavhasidagi kolba ikonkasini kattalashtirib qo'yamiz
    icon = background().crop((172, 26, 242, 102))
    icon = icon.resize((int(icon.width * 2.3), int(icon.height * 2.3)), Image.LANCZOS)
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, icon.width - 1, icon.height - 1), fill=255)
    base.paste(icon, ((W - icon.width) // 2, 240), mask)
    items = [(text_strip("Ustozlar", "serif_b", 30, INK_SOFT), 430)]
    y = 490
    for name in TEACHERS:
        s = text_strip(name, "serif_b", 48, NAVY, maxw=700)
        items.append((s, y))
        y += s.height + 14
    if BRAND_HANDLE:
        items.append((chip_strip(BRAND_HANDLE, 34, ACCENT, WHITE, radius=26, padx=30, pady=12), y + 20))
    slides.append(Slide(base, items, hold=1.8, reveal=[0.5] + [0.5] * (len(items) - 1)))
    return slides


# ---------------------------------------------------------------- video
def render_video(data, out_path):
    slides = build_slides(data)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "24",
        "-movflags", "+faststart", out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for sl in slides:
            for frame in slide_frames(sl):
                proc.stdin.write(frame.convert("RGB").tobytes())
    finally:
        proc.stdin.close()
        rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg xatolik bilan tugadi (kod {rc})")
    return out_path


if __name__ == "__main__":
    import json
    import sys

    src = sys.argv[1] if len(sys.argv) > 1 else "sample.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "out.mp4"
    render_video(json.load(open(src, encoding="utf-8")), dst)
    print("tayyor:", dst)
