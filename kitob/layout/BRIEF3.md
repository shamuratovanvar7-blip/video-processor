# Bo'sh joylarni yopish (joylashuvni zichlash) — talablar

Foydalanuvchi 51-betni ko'rsatdi: "7 Atomning moli" blokida chapda "Mol nima?" kartasi turibdi, o'ng tomonda esa o'chirilgan "Molyar massa" kartochkasidan qolgan **katta bo'sh joy**. U so'radi: *"bu bo'sh qolgan joyga siljimaydimi? ochiq joylarni boshqattan ko'rib chiq."* Sening vazifang: oralig'ingdagi HAR BIR betda shunday ochiq (bo'sh qolgan) joylarni topib, mazmunni siljitib/kengaytirib yopish. Hech narsa kitobdan olib tashlanmaydi, faqat joyi o'zgaradi.

## Qanday bo'sh joylar qidiriladi
1. **Yon tomondagi teshik:** yonma-yon joylashgan bloklardan biri o'chirilgan/qisqa bo'lib, yonida bo'sh joy qolgan (51-bet). Tuzatish: qolgan blokni konteyner kengligiga **kengaytir** va matnni qayta joyla (qayta o'ra), yoki markazla, yoki pastdagi mazmundan mos blokni shu joyga ko'tar. Eng yaxshisi: kartani to'liq kenglikka kengaytirib matnni qayta o'rash — shunda balandligi kamayadi va pastdagi hamma narsa yuqoriga siljiydi, konteyner ramkasi qisqaradi.
2. **Vertikal bo'shliq:** bloklar orasida standart oraliqdan (≈26–28 pt) ancha katta bo'shliq (o'chirilgan bloklar, rasm o'lchami o'zgargan joylar). Tuzatish: pastdagi mazmunni yuqoriga siljit, ramkalarni moslab qisqartir. (Bu 52 va 84-betlarda allaqachon bajarilgan — `tools/remove_black.py` ning ishlash usuli: redaction bilan olib tashlash + betning pastki qismini `show_pdf_page(..., clip=...)` bilan siljitib qayta qurish; kodni o'qib, ishlatsa bo'ladi.)
3. **Sahifa ichidagi ochiq joylar:** kichik rasm atrofidagi, katak ichidagi, jadval yonidagi keraksiz bo'sh joylar. Faqat aniq nuqson bo'lsa tuzat.
4. Sahifaning **pastki bo'sh qismi** (oxirgi blokdan keyin): tabiiy, tegma. Faqat hisobotga yoz: bet, bo'sh balandlik (pt) va keyingi betning birinchi bloki balandligi (u sig'adimi). Boshqa betdan blok ko'tarish **taqiqlangan** (faqat 10-agentga ruxsat, quyida).

`layout/gaps.json` (`tools/gap_survey.py` natijasi) yordam beradi, lekin yon tomondagi teshiklarni topa olmaydi — **betni dpi=110–150 da render qilib ko'z bilan ko'r**.

## Texnik talablar
- BAZA: `kitob/Kimyo_1-qism_yakuniy_v3.pdf` (o'zgartirma, nusxa ol). Python: `pymupdf`, numpy, PIL, scipy, cv2.
- Mazmun (matn, formulalar, rasmlar) o'zgarmasin; hamma yozuv **CMU Serif Roman** (`fonts/CMUSerif-Roman.ttf`). Matnni qayta joylasang: avval eski matnni redaction bilan olib tashla (faqat shu matn to'rtburchagi, qo'shnilarga tegmasdan), so'ng `TextWriter` bilan yoz: o'lcham, rang (mavjud span'lardan ol), so'z ranglari (masalan "Mol" va "g/mol" teal rangli, qalin emas), yuqori/pastki indekslar (`6,02 · 10²³`, `N_A`) — shriftda ² ₃ glyphlari yo'q, shuning uchun kichik (≈70%) belgini siljitib chiz; qator oralig'i va chap-o'ng chegaralari mavjud bloklar bilan bir xil. Natija professional ko'rinsin.
- Ramka/fon/chiziqlar (nuqtali chegaralar, yumaloq ramkalar) vektor: ularni `get_drawings()` bilan topib, kerak bo'lsa content stream'dan olib tashlab, yangi o'lchamda qayta chiz (rang, qalinlik, nuqta oralig'i bir xil).
- Siljitish vektor/matn holida bo'lsin (rasmga aylantirma!). Sarlavha (header) va pastki satr (footer) o'zgarmaydi, bet raqamlari joyida.
- Ustma-ust tushish, kesilish, yangi bo'sh joylar bo'lmasin; bloklar orasidagi oraliq ≈26–28 pt.
- O'zgarmagan betlar bazaga piksel jihatdan bir xil bo'lishi shart (tekshir).
- Faqat o'z betlaringda ishla; Git'ga tegma.

## Natija
- `kitob/parts_e/eK.pdf` — faqat sening betlaringdan (ketma-ket tartibda; 10-agentda bet soni o'zgarishi mumkin — hisobotda yoz).
- `kitob/parts_e/eK_report.md`: har bir o'zgargan bet uchun (bet, nima edi, nima qilindi); o'zgarmagan betlar ro'yxati; **"qolgan bo'sh joylar"**: sahifa oxiridagi bo'sh balandligi >100 pt betlar va keyingi betning birinchi bloki sig'ish-sig'maslik ma'lumoti.
- Oldin/keyin PNG: `kitob/render/eK_before_N.png`, `eK_after_N.png` — Read bilan ko'rib tasdiqla.
- Oxirida 150 so'zdan oshmaydigan qisqa xulosa.
