# d3 hisoboti (betlar 28-36)

Usul kodlari: FADE = chetga yumshoq so'nish (smoothstep, oq fonga, 8-20 px); SF = spherefix (kesilgan shar/atom to'ldirildi). Rasmlar `replace_image` bilan almashtirildi.

| Bet | xref / joy | Qaror | Usul |
|---|---|---|---|
| 28 | 489 tuproq uyumi (chap, past) | tuzatildi | FADE chap+past |
| 28 | 490 suv stakani (o'ng, past, tepadagi uzilgan och chiziq) | tuzatildi | FADE o'ng+past+tepa |
| 28 | 491 aralashma stakani (past, tepa chiziq) | tuzatildi | FADE past+tepa |
| 28 | 492, 493, 494 stakanlar/doiralar | kesilish emas: chetlariga faqat oq fon tegadi, doiralar to'liq | tekshirildi |
| 29 | 500, 501, 504, 505 (loyqa suv, tiniq suv, cho'kma, dekantatsiya) | tuzatildi | FADE (past/tepa/o'ng) |
| 30 | 508 temir+qum uyumi (past) | tuzatildi | FADE past |
| 30 | 509 magnit surati (tepasi va chap chet tekis) | tuzatildi | FADE tepa 48 px, chap |
| 30 | 510 toza qum | kesilish emas: oq fon, obyekt to'liq | tekshirildi |
| 30 | 511 filtrlash chizmasi: quyilayotgan kolbaning tepasi tekis kesilgan | tuzatildi | rasm ichida kolba tepasiga yumshoq so'nish (qatorlar 64-104) |
| 30 | 511: yozuv ostidagi baked-in oq to'rtburchaklar kolba tubi va xira soyani qisman kesadi | qisman: tiklab bo'lmaydi, juda xira soya | o'zgarishsiz |
| 31 | 518/520/522/524/526/534-538 (yuqori qator suratlari) | tuzatildi | FADE past/o'ng/chap |
| 31 | 529 muz kubi (chap chet tekis) | tuzatildi | FADE chap |
| 31 | 531/539 suv stakani + doira | kesilish emas: 539 (1-to'lqin) to'liq, doira va stakan butun | tekshirildi |
| 31 | 533 gaz: doira o'ng tomonda ~8 px kesilgan; stend/bug tepa/chap/past tekis | tuzatildi | doira o'ngga to'ldirildi (ko'zgu-to'ldirish + to'q ko'k halqa qayta chizildi, +16 px), tepa/past/chap FADE |
| 31 | kattalashtirish doiralari (muz, suv) | kesilish emas, to'liq yumaloq | tekshirildi |
| 32 | 541, 543, 545, 547 | kesilish emas: doira/to'rtburchak kadrlar to'liq | bet baza bilan bir xil |
| 33 | 550, 552, 554 | kesilish emas: butun to'rtburchak fotosuratlar | bet baza bilan bir xil |
| 34 | 576 "bug'lanish": pastki molekulaning chap H atomi kesilgan | tuzatildi | SF bottom (630,374,r30.5, kulrang halqa, pad 14) |
| 34 | 577 "reaksiya" O2/H2/H2O sharlari | kesilish emas: barcha sharlar to'liq (Hough + ko'z) | tekshirildi |
| 34 | 563 (o'ng), 567, 569 yog'ochning yonishi (alanga/tutun tepada), 573, 575 | tuzatildi | FADE tepa (o'ng: 563) |
| 34 | 561, 565, 571 | kesilish emas, oq fon | tekshirildi |
| 35 | 580, 582 zanjir+gorelka | kesilish emas: butun to'rtburchak fotosurat kadri | bet baza bilan bir xil |
| 36 | 593 CO2 bulut: chap atom kesilgan | tuzatildi | SF (2,116.5,r7.7) |
| 36 | 597 NH3 bulut: o'ng 2 ta H atomi kesilgan | tuzatildi | SF (197.5,35.6,r5.3),(197.5,51.5,r5.3) |
| 36 | 599 H2S bulut: chap H atomi kesilgan | tuzatildi | SF (-1.5,92,r5.2) |
| 36 | 587 H2 bulut: o'ng chetda uzilgan chiziq | tuzatildi | FADE o'ng |
| 36 | 589, 591, 595 (O2, N2, CH4 bulutlari) | kesilish emas: atomlar to'liq | tekshirildi |
| 36 | 586, 588, 590, 592, 594, 596, 598 katta molekulalar | kesilish emas / 1-to'lqinda tuzatilgan (618/619); 594 tepasidagi mayda dog' ko'zga tashlanmaydi | tekshirildi |
| 36 | 600-604, 606-609, 611-613 (idishlar, qattiq moddalar, metallar, oksidlar) | tuzatildi | FADE (608 chap, 609 o'ng, qolganlari past/tepa) |

Eslatma: `tools/spherefix.py` da "left"/"right" yo'nalishlari almashgan (rot90); nusxada (scratchpad) teskari berdim va mayda atomlar uchun `inner.sum()` chegarasini pasaytirdim. Asl fayl o'zgarmadi.

Tekshiruv: d3.pdf 9 bet; 32, 33, 35-betlar baza bilan piksel jihatdan bir xil. Oldin/keyin PNG: `render/d3_before_N.png`, `d3_after_N.png` (N = 28, 29, 30, 31, 34, 36).

## Xulosa
Tuzatildi: taxminan 36 ta rasm: 4 ta shar/atom to'ldirish (34-bet 1, 36-bet 3 mayda bulut), 31-betdagi gaz doirasi to'ldirildi, qolganlari yumshoq so'nish bilan. Kesilish emas: 32, 33, 35-betlar, 577, 589/591/595 va katta molekulalar. Qisman: 30-betdagi filtrlash chizmasida baked-in oq yozuv oynalari kolba tubi/xira soyani kesadi (tiklab bo'lmaydi).
