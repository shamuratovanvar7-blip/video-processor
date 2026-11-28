# report_A: qora joylar tekshiruvi

Ko'rsatkich: to'rtburchak ichida `qorong'i piksel % (luma<90) / to'q-ko'k (16,37,63) piksel %`, 100 dpi. Rect'lar original.pdf dagi Square /Rect (PDF koordinatalari; 51: 308,589,548,723 va 299,655,311,657; 52: 49,302,163,326; 82: 30,88,571,188; 83: 25,178,564,584; 84: 4 ta).

| Fayl | Dastur | Bet | qorong'i%/ko'k% (har rect) |
|---|---|---|---|
| Kimyo_1-qism_Roman | mupdf | 51 | 1.99/0.24 ; 0.0/0.0 |
| Kimyo_1-qism_Roman | mupdf | 52 | 13.96/0.0 |
| Kimyo_1-qism_Roman | mupdf | 82 | 1.75/0.12 |
| Kimyo_1-qism_Roman | mupdf | 83 | 1.15/0.33 |
| Kimyo_1-qism_Roman | mupdf | 84 | 1.24/0.35 ; 1.24/0.23 ; 1.34/0.37 ; 1.4/0.46 |
| Kimyo_1-qism_Roman | poppler | 51 | 1.95/0.26 ; 0.0/0.0 |
| Kimyo_1-qism_Roman | poppler | 52 | 14.15/0.0 |
| Kimyo_1-qism_Roman | poppler | 82 | 1.76/0.13 |
| Kimyo_1-qism_Roman | poppler | 83 | 1.18/0.35 |
| Kimyo_1-qism_Roman | poppler | 84 | 1.34/0.27 ; 1.12/0.22 ; 1.37/0.38 ; 1.49/0.27 |
| Kimyo_1-qism_Roman | pdfium | 51 | 2.04/0.27 ; 0.0/0.0 |
| Kimyo_1-qism_Roman | pdfium | 52 | 13.75/0.0 |
| Kimyo_1-qism_Roman | pdfium | 82 | 1.79/0.21 |
| Kimyo_1-qism_Roman | pdfium | 83 | 1.23/0.29 |
| Kimyo_1-qism_Roman | pdfium | 84 | 1.29/0.39 ; 1.2/0.26 ; 1.45/0.55 ; 1.55/0.31 |
| original | mupdf | 51 | 99.46/96.08 ; 75.0/61.76 |
| original | mupdf | 52 | 96.36/77.29 |
| original | mupdf | 82 | 100.0/95.35 |
| original | mupdf | 83 | 99.82/96.58 |
| original | mupdf | 84 | 96.24/94.88 ; 96.25/94.93 ; 96.0/94.53 ; 95.82/94.76 |
| original | poppler | 51 | 99.46/95.17 ; 75.0/41.18 |
| original | poppler | 52 | 96.36/73.71 |
| original | poppler | 82 | 100.0/94.41 |
| original | poppler | 83 | 99.69/96.0 |
| original | poppler | 84 | 96.24/94.44 ; 96.25/91.11 ; 99.81/94.45 ; 95.82/94.85 |
| original | pdfium | 51 | 99.17/95.14 ; 75.0/64.71 |
| original | pdfium | 52 | 96.36/76.21 |
| original | pdfium | 82 | 99.28/94.99 |
| original | pdfium | 83 | 99.69/96.35 |
| original | pdfium | 84 | 96.24/92.85 ; 96.25/94.94 ; 95.97/94.31 ; 91.84/90.98 |

Ghostscript (gs), mutool, qpdf muhitda yo'q; pdf.js ishlatilmadi. 3 mustaqil dastur: MuPDF 1.28.6, Poppler pdftoppm, PDFium (pypdfium2 5.14).

## Natija
- Roman.pdf: barcha 3 dasturda rect ichida to'q-ko'k <= 0.55%, qorong'i 1-2% (faqat matn). Faqat 52-betdagi 14% qorong'i - bu sarlavha/qalin matn (ko'z bilan tekshirildi, matn o'qiladi). 51/83/84-betlar PNG'lari ko'rildi: matn to'liq o'qiladi. Ikkinchi rect (51-bet, 299,655,311,657) 0% - bo'sh joy.
- original.pdf: 75-100% qora, ko'k 41-96% (3 dasturda ham).
- tuzatilgan.pdf ham toza (Roman bilan bir xil darajada).

## Fayl darajasi (Roman.pdf)
- /Annots: hech bir betda yo'q; xom baytlarda /Square, /Popup, /Annots, /Widget, /Highlight, /Ink, /FreeText = 0.
- Root kalitlari: Info, Type, Pages. /AcroForm, /OCProperties, /Outlines, /OpenAction, /Names, /StructTreeRoot yo'q. /OC havolalari va 3 Tr (ko'rinmas matn) yo'q.
- Kontent oqimlari va Form XObject'larda (0.0627,0.1451,0.2471) yoki (0,0.1255,0.3765) to'ldirish: 0.
- Tuzilma: %%EOF 1 ta, startxref 1 ta, /Prev yo'q (incremental update qoldig'i yo'q), PDF 1.7, trailer Size 1750, 1749 obyekt - hammasi Root'dan yetib boriladi (ishlatilmayotgan/osilib turgan obyekt 0). pikepdf check: xato yo'q.
- Barcha 91 bet PDFium'da 40 dpi'da skan qilindi: katta to'q blok bor betlar (7,10,11,16,17,20,30,31,33,35,36,56) - ko'z bilan 11,16,20,33 ko'rildi: rasm/piktogramma (legitim). To'q-ko'k plash qoldig'i yo'q.

## Xulosa
Roman.pdf da qora joylar YO'Q, fayl darajasida ham qoldiq yo'q. iOS'dagi qora katak - eski/asl nusxa (keshlangan yoki original.pdf) bo'lishi ehtimoli yuqori; fayl o'zgarmagani uchun _clean nusxa yaratilmadi (4-qadam shart bajarilmadi).

## Yangilanish (vazifa o'zgardi: qoplama + ostidagi yozuv birga o'chirilishi kerak)
1-qism natijasi: hozirgi Roman.pdf'da qoplamalar yo'qolgan, lekin ostidagi matn/mazmun hali joyida (get_text/search_for topadi: "Molyar massa", "Davr bo'ylab oksid", "2-davr (bosh", "3-davr", "qoldig'i", "Qoida: element"). Yangi talab uchun bu YETARLI EMAS; Roman.pdf o'chirish bo'yicha tayyor emas.
