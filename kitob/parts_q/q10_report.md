# q10 hisobot (bet 71-90, baza v4)
Natija: parts_q/q10.pdf = v4 ning 71-90 betlari, aynan 20 bet, piksel jihatdan o'zgarmagan.

## Rasmlar (faqat 2 bet)
- Bet 84: 8 ta rasm-ikon (xref 2479, 2480, 2483 — 320x320; 2484-2488 — 320x308), joylashuvi 40x40 pt (~38 pt) => samarali ~576-600 dpi. Metrika: sharpness 337-557, noise 0.0, blockiness 0.9-1.2 (JPEG dog'i yo'q). 300-600 dpi render ko'zdan tekshirildi: doira chetlari silliq, rang tekis, halo yo'q.
- Bet 90: xref 2595, 4220x3370 px, 481x384 pt => ~632 dpi, blockiness 0.98, noise 0 (sharpness 20 — sahifa asosan oq bo'lgani uchun). 400 dpi render: formula, strelka, qavslar aniq. xref 2596 — 1x1 piksel (tegilmaydi).

## Tegilmadi (sabab)
Barcha rasmlar: allaqachon >=576 dpi va artefaktsiz; qayta ishlash faqat hajm oshirib/yumshatib yomonlashtirardi (BRIEF4: "allaqachon aniq — tegma"). 2479/2480 xreflari faqat bet 84 da ishlatiladi.

## Qo'shimcha kuzatuvlar
- Bet 71-83, 85-89 da raster rasm yo'q (faqat vektor + matn; bet 83 da 16021 vektor chizma) — sifat muammosi yo'q, ko'zdan ko'rib chiqildi.
- Bet 90 da 2-3-strelkaning uchi manba chizmasida biroz qo'sh chiziqli ko'rinadi (dizayn xususiyati, JPEG dog'i emas); raster 632 dpi, qayta chizish tavsiya etilmaydi.
- Oldin/keyin PNG: render/q10_before_84/90.png va q10_after_84/90.png (bir xil, o'zgarish yo'q).
