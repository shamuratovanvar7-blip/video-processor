# Qirqilgan joylarni tuzatish — 2-to'lqin (qat'iy talab)

Foydalanuvchi: **"tuzatsang, barchasini tuzat."** Birinchi to'lqinda agentlar ko'p joyni "ishonchsiz / yolg'on signal / tiklab bo'lmadi" deb o'tkazib yuborgan va shu sabab foydalanuvchining ikki namunasi (4-betdagi suv va CO₂ molekula modellari — sharlarning tepasi tekis kesilgan) tuzatilmay qolgan. Endi:

## Talab
- Har bir nomzod (`cutoff/candidates.json`) va sening betlaringdagi HAR BIR ko'rinadigan kesilish quyidagi 2 holatdan biri bilan yopilishi shart:
  1. **Tuzatildi** (to'liq yoki eng yaqin qabul qilarli ko'rinishda), yoki
  2. **Kesilish emas** — buni aniq dalil bilan yoz (masalan "butun to'rtburchak surat, fotosurat kadri bo'yicha to'ldirilgan" yoki "obyekt to'liq, rasm chetiga faqat oq fon tegadi").
- "Ishonchli tiklab bo'lmadi" — qabul qilinmaydi. Aniq tiklash imkonsiz bo'lsa ham **tekis kesilgan chet qolmasligi kerak**: yumaloq shakl bo'lsa to'liq yumaloq qilib chiz; fotosurat/bulut/tutun/alanga kabi kesilgan bo'lsa chetga yumshoq so'nish (alfa gradient) yoki kengaytirib so'ndirish qo'lla.
- Foydalanuvchi namunalari (ko'rib ol): `/tmp/claude-0/-home-user-video-processor/e38f87eb-8760-5547-8662-11b395051bca/images/1.png` va `.../images/2.png` — kislorod sharining tepasi rasm chetida tekis kesilgan. Natija shu 4-betdagi tuzatilgan holatdagidek bo'lsin (`render/cut/p4_after.png`).
- Avvalgi agentlar tegmagan, endi qayta ochiladigan joylar: 13-bet fotosuratlari; 21–23-bet jihoz suratlari (shtativ, qisqich, kolba qirralari); 25-bet aralashma stakani va molekula belgilari; 26-bet distillash va qizdirish suratlari; 30-bet surat; 34-bet — "yog'ochning yonishi" surati (alanga/tutun tepada tekis kesilgan) va O₂/H₂ molekula rasmlari (tepasi qirqilgan sharlar); 36-bet mayda "bulut" atomlari (NH₃, H₂S, CO₂, CH₄ atrofidagi mayda molekulalar); 17, 19-betlardagi suratlarning chetlari.

## Fayllar (/home/user/video-processor/kitob/)
- `Kimyo_1-qism_yakuniy.pdf` — BAZA (4-bet allaqachon tuzatilgan). **O'zgartirma**, nusxa ol. Yangi yozuv kerak bo'lsa faqat `fonts/CMUSerif-Roman.ttf`.
- `cutoff/candidates.json` — nomzodlar: `page`, `xref`, `bbox` (sahifada, pt), `img_px`, `edges` (qaysi chetda kontent kesilgan ko'rinadi). Nomzodlarda yo'qlari ham bo'ladi: oralig'ingdagi **har bir betni** `page.get_pixmap(dpi=150)` bilan render qilib ko'z bilan tekshir (rasm chetlari uchun kerak bo'lsa clip bilan 300–400 dpi kattalashtir).
- `tools/spherefix.py` — **kesilgan sharlarni to'ldirish** (sinalgan, 4-betda ishladi):
  ```python
  import sys; sys.path.insert(0, "/home/user/video-processor/kitob/tools")
  import pymupdf, spherefix as sf
  d = pymupdf.open("...")                       # nusxa
  arr = sf.load_image(d, xref)                  # H x W x 4 RGBA
  cs = [c for c in sf.detect_circles(arr, rmin, rmax, p2=12) if c[1]-c[2] < 1.5]   # tepasi kesilganlari (cx, cy, r)
  new, off = sf.complete_spheres(arr, cs, "top", pad=14)   # side: top/bottom/left/right
  sf.place(d, page_no, xref, new, "top", 14)    # eski rasm ustiga joylaydi (sahifa fonini avto-moslaydi)
  ```
  `detect_circles` Hough ishlatadi (radius oralig'ini rasmdagi sharga qarab ber; natijani ko'z bilan tekshir, kerak bo'lsa `cs`ni qo'lda yoz). Katta bo'lmagan kesilish uchun `pad` ni 8–20 oralig'ida ber. Sharlar bir-birini yopib turgan bo'lsa ham ishlaydi (faqat qo'shilgan qatorlar bo'yaladi).
- `tools/rasterfix.py` — rasm ichidagi yozuvni almashtirish (ehtiyoj bo'lsa).
- Qolgan hamma narsa uchun: tekis kesilgan alfa-fonli surat → `new = arr` nusxasida chet alfa'sini so'ndir (masalan, chetdan 10–16 px da 0→1 gradient) va `page.replace_image(xref, stream=png_bytes)` bilan almashtir (barcha joylashuvlar yangilanadi; hajm o'zgarmaydi); katak/chegara chizig'i uzilgan bo'lsa shu rasmning boshqa qismidan nusxalab chizig'ini tikla; vektor/yozuv kesilgan bo'lsa joyini/o'lchamini to'g'rila.
- Python: `pymupdf`, numpy, PIL, scipy, opencv (`cv2`) bor.

## Qoidalar
1. Faqat o'z betlaringda ishla; boshqa agentlar boshqa oraliqlarni tahrirlayapti. Git'ga tegma.
2. O'zgarmagan betlar baza bilan piksel jihatdan bir xil bo'lishi shart (tekshir). Boshqa hech narsa o'zgarmasin.
3. Har bir o'zgargan bet uchun oldin/keyin PNG (`kitob/render/dK_before_N.png`, `dK_after_N.png`) — Read bilan ko'rib tasdiqla (chet yumaloq/yumshoq, rang va soya mos, hech qanday ingichka chiziq/to'rtburchak artefakt yo'q).
4. Natija: `kitob/parts_d/dK.pdf` — faqat sening betlaringdan, ketma-ket tartibda (K — sening raqaming).
5. Hisobot `kitob/parts_d/dK_report.md`: har bir nomzod/kesilish uchun bitta qator: bet, xref/joy, qaror (**tuzatildi** / **kesilish emas + dalil**), usul. Oxirida 150 so'zdan oshmaydigan xulosa (nechta tuzatildi, nechta kesilish emas).
