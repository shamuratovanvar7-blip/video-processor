"""Masala matni/rasmi -> Claude API -> yechim JSON."""
import base64
import json
import os
import re

import anthropic

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

SYSTEM = """Sen tajribali kimyo o'qituvchisan. Foydalanuvchi kimyo masalasini yuboradi.
Hech narsa so'ramasdan, darhol masalani to'liq va to'g'ri yech va FAQAT bitta JSON obyekt qaytar
(markdown, izoh, ``` belgilarisiz).

Til: o'zbek (lotin). Formulalarda Unicode indekslarni ishlat: H₂O, Cu(NO₃)₂, Fe²⁺, SO₂↑, →.
Hisob-kitoblarni ehtiyotkorlik bilan bajar va natijalarni ikki marta tekshir.

JSON sxemasi:
{
 "title": "masala mavzusi (2-5 so'z)",
 "problem_text": "masala matni (agar rasm bo'lsa, undan ko'chirib yoz)",
 "steps": [               // 3-7 ta qadam, har biri qisqa
  {
   "label": "1-QADAM",
   "title": "qadam sarlavhasi (2-5 so'z)",
   "scene": "test_tube | beaker | electrolysis | none",
   "scene_params": {      // ixtiyoriy
     "caption": "qisqa izoh",
     "color": "blue|green|colorless|yellow|brown|red|orange|pink|purple",
     "gas": "SO₂",        // ajralgan gaz formulasi (bo'lsa)
     "gas_color": "#D9926B", // rangli gaz uchun (NO₂ = #D9926B)
     "bubbles": true, "precipitate": "#CD6E3C", "solid": "#C85030",
     "heat": true, "progress": 0.6, "progress_label": "0,9 / 3 mol e"
   },
   "lines": [             // 2-5 qator, har biri bitta qisqa gap/tenglama (<= 45 belgi ideal)
     {"text": "...", "style": "equation | note | result | badge | box"}
   ]
  }
 ],
 "rules": ["esda saqlash kerak bo'lgan 3-4 ta qoida"],
 "answers": [{"label": "so'ralgan kattalik", "value": "qiymat birligi bilan"}]
}

Uslublar: equation = reaksiya/formula (qalin), note = oddiy izoh, result = muhim natija (qizil),
badge = sariq yorliq (qisqa), box = to'q yashil quti (xulosa).
Sahna tanlash: qizdirish -> test_tube; eritma/gaz/cho'kma -> beaker; elektroliz -> electrolysis;
hisob-kitob qadamlari uchun -> none. Savollarga javob bermagan qadam qoldirma."""


def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    a, b = text.find("{"), text.rfind("}")
    if a < 0 or b < 0:
        raise ValueError("JSON topilmadi")
    return json.loads(text[a:b + 1])


def _validate(d):
    if not isinstance(d, dict) or not d.get("steps"):
        raise ValueError("steps yo'q")
    for st in d["steps"]:
        if not isinstance(st.get("lines"), list) or not st["lines"]:
            raise ValueError("qadamda lines yo'q")
    return d


def solve(problem_text="", image_bytes=None, image_mime="image/jpeg"):
    """Sinxron chaqiruv (botda asyncio.to_thread orqali ishlatiladi)."""
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY muhit o'zgaruvchisidan
    content = []
    if image_bytes:
        content.append({"type": "image", "source": {
            "type": "base64", "media_type": image_mime,
            "data": base64.b64encode(image_bytes).decode()}})
    content.append({"type": "text", "text": problem_text or "Rasmdagi masalani yech."})
    last = None
    for _ in range(2):
        msg = client.messages.create(
            model=MODEL, max_tokens=8000, system=SYSTEM,
            messages=[{"role": "user", "content": content}])
        raw = "".join(b.text for b in msg.content if b.type == "text")
        try:
            return _validate(_extract_json(raw))
        except Exception as e:  # noqa: BLE001
            last = e
    raise RuntimeError(f"Yechimni o'qib bo'lmadi: {last}")
