# Qora qoplama qidiruvi (91 bet, original.pdf va Kimyo_1-qism_Roman.pdf)

Usul: (1) 60 dpi render (annotatsiyalar bilan), >=20x8 pt, max kanal<90 bir tekis (to'ldirish >=50%) komponentlar; (2) get_annots / get_drawings (to'q fill, >=20x8 pt) / get_image_info; (3) barcha nomzodlar Read bilan ko'rildi.

## original.pdf
| Bet | Joy (pt) | Rang | Tur | Natija |
|---|---|---|---|---|
| 51 | 308,119-548,253; 299,185-311,187 | (16,37,63) | 2 ta Square annot | qoplama (ma'lum) |
| 52 | 49,516-163,540 | (16,37,63) | Square annot | qoplama (ma'lum) |
| 82 | 30,654-571,754 | (16,37,63) | Square annot | qoplama (ma'lum) |
| 83 | 25,258-564,664 | (16,37,63) | Square annot | qoplama (ma'lum) |
| 84 | 160,307 / 160,351 / 155,510 / 156,576 (~380x20) | (16,37,63); 4-chisi (0,32,96) | 4 ta Square annot | qoplama (ma'lum; 4-chisi yorqinroq ko'k, piksel filtrida max>90 bo'lgani uchun o'tkazilgan, annot ro'yxatida bor) |
Boshqa betlar: yangi qoplama yo'q (toza).

## Kimyo_1-qism_Roman.pdf
Annotatsiya: 0 ta. To'q qoplama: 0 ta. Barcha 91 bet toza.
Piksel/vektor tahlilida chiqqan, lekin qoplama EMAS (dizayn/fotosuratlar):
- 7, 8, 10, 11, 18, 20, 22, 26, 28, 29, 31, 32, 33, 34, 35, 36, 56: to'q rangli fotosuratlar (ko'mir, grafit, qora sharlar, shtativ asosi, plita, CO2 o'chirgich, quruq muz, Yer sharidagi tasvir) - rasm ichida mazmun bor.
- 27 (409,566-529,633), 56 (4 ta ~48x37), 57 (2 ta), 20 (120,159-145,175): qora vektor shakllar, ko'rinmas/yupqa ramka-chiziqlar yoki rasm soyalari; matnni yopmaydi.
- 61-63: qora, 40% shaffoflikdagi kichik (~21x20) soyalar.
- 84, 83, 82, 52, 51: avval qoplangan joylar endi ochiq, matn/jadval ko'rinadi (84-betda ko'rib tasdiqlandi).

## Xulosa
Qo'shimcha qora qoplama topilmadi; faqat ma'lum 9 ta annot (jami 9 ta). Roman'da hammasi o'chirilgan. Shu sababli `Kimyo_1-qism_Roman_B.pdf` (qoplamani ochish varianti) yaratilmadi; vazifa o'zgargani uchun quyidagi o'chirish ishi bajarildi.

## 2-qism: bloklarni tagidagi yozuvlari bilan o'chirish

Skript: `kitob/tools/remove_black.py SRC.pdf DST.pdf` (SRC o'zgarmaydi, bet raqamlari o'zgarmaydi, idempotent: anchor matni topilmasa blok o'tkazib yuboriladi; original.pdf ustida ham ishlaydi, u holda 9 ta qora Square izohi ham olib tashlanadi).
Natija: `kitob/black_check/Kimyo_1-qism_Roman_removed.pdf` (Roman asosida).

| Bet | O'chirilgan | Usul |
|---|---|---|
| 51 | o'ng "Molyar massa" kartochkasi (matn, nuqtali ramka, sariq/ko'k panel, ▶ belgilari) | apply_redactions (TEXT_REMOVE, IMAGE_REMOVE, LINE_ART_REMOVE_IF_COVERED), "Mol nima?" kartasi tegilmadi |
| 52 | "1 Ma'nosi" sarlavhasi (doira + sariq yorliq); pastdagi hamma narsa 25.4 pt yuqoriga surildi (bo'sh joy qolmasin) | redaction + `show_pdf_page(clip)` bilan bo'laklab qayta qurish |
| 82 | pastdagi "3 Davr bo'ylab ..." bloki (ramka, sarlavha, "2-davr" paneli) | redaction |
| 83 | butun konteyner (2-davr jadvali, 3-davr paneli/jadvali, "Qoida" qutisi, rasmlar, strelkalar); "4 Umumiy formula" bloki sahifa tepasiga (y=74.6) surildi | redaction + siljitish |
| 84 | Fe2+, Cu2+, Fe3+, Al3+ qatorlari; jadvallar yopildi (chiziqlar qayta chizildi, chap birlashgan kataklar bir qatorga keltirildi, matni markazga surildi), pastdagi hamma narsa 88.4 pt gacha yuqoriga surildi | qator redaction + bo'laklab surish |

Eslatma: 83-betdagi "4 Umumiy formula" bloki "qoladi" talabiga ko'ra saqlandi, faqat bo'sh joy qolmasligi uchun tepaga surildi (xohlansa `do83`da `compact(...)` chaqiruvini o'chirib, joyida qoldirish mumkin).

Tekshiruv (Roman_removed):
- (a) get_text()da "Molyar massa", "Ma'nosi", "2-davr", "3-davr", "Qoida", "Fe2+", "Cu2+", "Fe3+", "Al3+", "mis(II) qoldig'i" va boshqa o'chirilganlar yo'q; qolgan "qoldig'i" faqat boshqa (qoladigan) qatorlarda.
- (b) izohlar 0 ta, qora/to'q ko'k to'rtburchak yo'q (to'q piksellar faqat matn).
- (c) qolgan 86 bet 72 dpi'da piksel jihatdan bir xil (farq 0).
- (d) 84-betda jadval silliq yopilgan (2 va 3-jadval, chiziqlar va chap kataklar to'g'ri) - 200 dpi'da ko'rib tasdiqlandi.
- (e) 51/52/82/83/84 PNG'lari Read bilan ko'rildi.
- Skriptni natijaning o'ziga qayta ishlatish hech narsani o'zgartirmaydi (idempotent, piksel farqi 0).
- Cheklov: 84-betda faqat 4 qator o'chiriladi; koordinatalar Roman versiyasiga moslangan, anchor matn tekshiruvi bo'lgani uchun boshqa maket bo'lsa blok o'tkazib yuboriladi.
