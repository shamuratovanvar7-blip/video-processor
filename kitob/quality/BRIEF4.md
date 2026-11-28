# Rasm sifatini oshirish — talablar

Foydalanuvchi: *"yana 10 ta agent rasmlarning sifatiga qarasin, sifatini oshirsin."* Sening vazifang: oralig'ingdagi HAR BIR rasmning sifatini baholab, yaxshilash mumkin bo'lganlarini yaxshilash.

## Muhim cheklov (foydalanuvchiga ham shunday aytiladi)
Oflayn **sun'iy intellektli super-resolution modeli yo'q** (HuggingFace yopiq, GitHub 403, PyPI'da og'irlik fayllari yo'q). Shuning uchun faqat **klassik usullar**: JPEG/shovqinni chetni saqlab tozalash, Lanczos bilan kattalashtirish, chetga sezgir o'tkirlash, alfa/chet artefaktlarini tozalash, hamda oddiy shakllarni (sharlar, ikonlar) analitik yuqori ruxsatda qayta chizish. Natijani har doim ko'z bilan tekshir; yomonlashtirgan bo'lsa — bu rasmga tegma.

## Fayllar va vositalar (/home/user/video-processor/kitob/)
- BAZA: `Kimyo_1-qism_yakuniy_v4.pdf` (joylashuv bosqichi tugagan, birlashtirilgan). **O'zgartirma**, nusxa ol.
- `tools/enhance.py` (sinalgan): `load(doc, xref)`, `metrics(arr)` (sharpness, noise, blockiness), `enhance(arr, scale, denoise, sharpen)`, `to_png_bytes`, `to_jpeg_bytes`. Almashtirish: `page.replace_image(xref, stream=...)` (joylashuv/hajm o'zgarmaydi; xref ning BARCHA joylashuvlari yangilanadi — bir xref turli betlarda ishlatilsa, boshqa betdagi ko'rinishni ham tekshir; sening oralig'ingdan tashqaridagi betlarda ishlatilgan xrefga TEGMA: `get_image_rects`/boshqa betlarda `get_images` bilan tekshir).
- `tools/spherefix.py` (sharlarni to'ldirish/yuqori ruxsat uchun foydali), `tools/rasterfix.py`.
- Python: pymupdf, numpy, PIL, scipy, cv2 (fastNlMeans, Lanczos, bilateral, guided filter va h.k.).

## Qanday ishlaysan
1. Har bir rasm joylashuvi uchun **samarali dpi** (`piksel / (pt/72)`), `metrics`, va **ko'zdan baholash** (yirik ko'rinishda — rasmni 3–4× kattalashtirib, yoki sahifani `clip` bilan 300–600 dpi render qilib).
2. Qaror:
   - **<300 dpi** va xira/yumshoq: 1.5–2× Lanczos + denoise (h≈2–4) + sharpen (0.4–0.8). Maqsad ≈300–360 dpi, 2× dan oshirma.
   - **≥300 dpi lekin JPEG dog'lari/shovqin/xira chet**: o'lchamini o'zgartirmay denoise + sharpen.
   - **Oddiy sharlar/molekula modellari/ikonlar** (tekis rang, yumshoq gradient): klassik usul yetarli bo'lmasa, analitik qayta chizish (yuqori ruxsatda supersampling) — faqat natija asldan aniq yaxshi bo'lsa.
   - **Allaqachon aniq / kichik ikon / 1×1, 8×8 gradient chiziqlar:** tegma.
   - Fotosurat: haddan tashqari silliqlama (yog'li "plastik" ko'rinish) va halo (oq ramka) paydo qilma.
3. **Fayl hajmi byudjeti**: butun PDF ≤ ~70 MB. Shaffoflik (alfa) kerak bo'lmagan fotosuratlar uchun `to_jpeg_bytes(arr, 92)` (subsampling=0), alfa/tekis grafikalar uchun PNG. 2× kattalashtirish hajmni 4× oshiradi — katta rasmlarni (>600 px) 2× qilma, faqat denoise/sharpen.
4. Alfa (shaffof) rasmlarda chet halo/oq qirra bo'lmasin; yumshoq chet (soya, so'nish) saqlansin. Oldingi bosqichlarda qo'shilgan yumshoq so'nish/to'ldirishlarni buzma.
5. Geometriya (rasm joyi, o'lchami) o'zgarmasin; mazmun (rasmdagi narsa, ranglar) o'zgarmasin: ranglar siljishi, yangi artefakt, "sifat past" ko'rinishi bo'lmasin.

## Natija
- `kitob/parts_q/qK.pdf` — faqat sening betlaringdan (ketma-ket tartibda, aynan shu oraliq).
- `kitob/parts_q/qK_report.md`: har bir yaxshilangan rasm uchun: bet, xref, eski/yangi piksel o'lchami, samarali dpi (oldin→keyin), metrika (oldin→keyin), qo'llangan usul; "tegilmadi" ro'yxati va sababi.
- Oldin/keyin yirik taqqoslash PNG: `kitob/render/qK_before_N.png` / `qK_after_N.png` — Read bilan ko'rib tasdiqla (sifat aniq yaxshilangan bo'lishi kerak).
- O'zgarmagan betlar bazaga piksel jihatdan bir xil bo'lishi shart (rasm ishlatilmagan betlar). Faqat o'z betlaringda ishla; Git'ga tegma.
- Oxirida 150 so'zdan oshmaydigan qisqa xulosa.
