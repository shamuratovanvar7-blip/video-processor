"""Masala matni/rasmi -> Claude API -> yechim JSON."""
import base64
import json
import os
import re

import anthropic

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

HEAD = """Sen tajribali kimyo va biologiya o'qituvchisan. Foydalanuvchi kimyo yoki biologiya bo'yicha masala
yoki nazariy mavzu yuboradi. Avval fanni aniqla ("subject": "kimyo" yoki "biologiya").
Hech narsa so'ramasdan, darhol bajar va FAQAT bitta JSON obyekt qaytar (markdown, izoh, ``` belgilarisiz).

Til: o'zbek (lotin). Kimyoda formulalarda Unicode indekslarni ishlat: H₂O, Cu(NO₃)₂, Fe²⁺, SO₂↑, →.
Biologiyada (genetika masalalari, hujayra, ekologiya va h.k.) sahna "none" bo'lsin, kimyoviy sahnalarni ishlatma.
"""

PROBLEM_RULES = """MASALA (hisoblash talab qilinadi) bo'lsa: "mode": "problem".
Masalani to'liq va to'g'ri yech, hisob-kitoblarni ikki marta tekshir. 3-7 ta qadam ("1-QADAM", ...),
"problem_text" ga masala matnini yoz, "answers" ga yakuniy javoblarni yoz.
"""

THEORY_RULES = """NAZARIYA (mavzu, tushuncha, qoida tushuntirilishi so'ralsa, masalan "Mol nima", "Alkanlar",
"Oksidlanish-qaytarilish") bo'lsa: "mode": "theory".
Mavzuni o'quvchiga video-dars shaklida tushuntir: 5-8 ta bo'lim ("1-QISM", "2-QISM", ...): ta'rif,
asosiy tushunchalar, formula/qonunlar, misollar, reaksiya tenglamalari, qo'llanilishi.
Har bo'limda 2-5 qisqa qator (<= 50 belgi). Uslub: ta'rif -> "box", atama -> "badge",
formula/tenglama -> "equation", eng muhim qoida -> "result", izoh -> "note".
"problem_text" o'rniga bo'sh qoldir, "answers" bo'sh ro'yxat, "rules" ga 3-5 ta xulosa ("Esda saqlang").

AGAR foydalanuvchi o'zining nazariy MATNINI yuborgan bo'lsa (uzun matn): videoni aynan SHU MATN asosida tuz.
Matndagi ta'rif, qoida, formula, misol va raqamlarni saqla, o'zingdan ziddiyatli yoki yangi ma'lumot qo'shma.
Matnni mantiqiy bo'limlarga bo'l (matn uzunligiga qarab 5-12 bo'lim), ortiqcha takrorni qisqartir,
murakkab gaplarni qisqa, tushunarli qatorlarga aylantir. Matn tartibini imkon qadar saqla.
"""

SCHEMA = """JSON sxemasi:
{
 "mode": "problem | theory",
 "subject": "kimyo | biologiya",
 "title": "mavzu (2-5 so'z)",
 "problem_text": "masala matni (rasm bo'lsa, undan ko'chirib yoz)",
 "steps": [               // masala: 3-7 qadam; nazariya: 5-8 bo'lim
  {
   "label": "1-QADAM yoki 1-QISM",
   "title": "sarlavha (2-5 so'z)",
   "scene": "test_tube | beaker | electrolysis | none",
   "scene_params": {      // ixtiyoriy
     "caption": "qisqa izoh",
     "color": "blue|green|colorless|yellow|brown|red|orange|pink|purple",
     "gas": "SO₂",
     "gas_color": "#D9926B",
     "bubbles": true, "precipitate": "#CD6E3C", "solid": "#C85030",
     "heat": true, "progress": 0.6, "progress_label": "0,9 / 3 mol e"
   },
   "lines": [             // 2-5 qator, har biri qisqa (<= 45-50 belgi)
     {"text": "...", "style": "equation | note | result | badge | box"}
   ]
  }
 ],
 "rules": ["esda saqlash kerak bo'lgan 3-5 ta qoida/xulosa"],
 "answers": [{"label": "so'ralgan kattalik", "value": "qiymat birligi bilan"}]
}

Uslublar: equation = reaksiya/formula (qalin), note = oddiy izoh, result = muhim natija (to'q sariq),
badge = ko'k yorliq (qisqa), box = to'q ko'k quti (ta'rif/xulosa).
Sahna: qizdirish -> test_tube; eritma/gaz/cho'kma -> beaker; elektroliz -> electrolysis; boshqasi -> none.
"""


def _system(mode):
    if mode == "problem":
        return HEAD + PROBLEM_RULES + SCHEMA
    if mode == "theory":
        return HEAD + THEORY_RULES + SCHEMA
    return (HEAD + "Avval so'rov turini aniqla va mos qoidaga amal qil.\n\n"
            + PROBLEM_RULES + "\n" + THEORY_RULES + "\n" + SCHEMA)


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


def solve(problem_text="", image_bytes=None, mode="auto", subject=None, image_mime="image/jpeg"):
    """Sinxron chaqiruv (botda asyncio.to_thread orqali ishlatiladi)."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"].strip())
    content = []
    if image_bytes:
        content.append({"type": "image", "source": {
            "type": "base64", "media_type": image_mime,
            "data": base64.b64encode(image_bytes).decode()}})
    if mode == "theory" and problem_text:
        if len(problem_text) > 250:
            problem_text = ("Quyidagi nazariy matn asosida video-dars tayyorla (matndan chetga chiqma):\n\n"
                            + problem_text)
        else:
            problem_text = "Nazariy mavzu (video-dars): " + problem_text
    if subject:
        problem_text = f"Fan: {subject}.\n" + problem_text
    content.append({"type": "text", "text": problem_text or "Rasmdagi masalani yech."})
    last = None
    total_in = total_out = 0
    for _ in range(2):
        msg = client.messages.create(
            model=MODEL, max_tokens=8000, system=_system(mode),
            messages=[{"role": "user", "content": content}])
        raw = "".join(b.text for b in msg.content if b.type == "text")
        total_in += msg.usage.input_tokens
        total_out += msg.usage.output_tokens
        try:
            data = _validate(_extract_json(raw))
            data["mode"] = mode if mode in ("problem", "theory") else (data.get("mode") if data.get("mode") in ("problem", "theory") else "problem")
            subj = subject or str(data.get("subject", "")).lower()
            data["subject"] = "biologiya" if "bio" in subj else "kimyo"
            data["_usage"] = {"input": total_in, "output": total_out}
            return data
        except Exception as e:  # noqa: BLE001
            last = e
    raise RuntimeError(f"Yechimni o'qib bo'lmadi: {last}")
