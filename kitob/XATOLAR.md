# "Neokimyo — Umumiy kimyo, 1-qism" (91 bet) — tuzatiladigan xatolar ro'yxati

Manba: `kitob/original.pdf` (A4, 91 bet, `pypdf` yig'gan; `.tex` manba YO'Q).
Bet raqamlari = PDF bet raqami = kitobdagi bet raqami (1..91).
Shriftlar: `kitob/fonts/CMUSerif-{Roman,Bold,Italic,BoldItalic}.ttf` (to'liq CMU Serif, OFL).
CMU Serif'da YO'Q glyphlar: `≈ ₂ ₃ ₄ ⁻ ⁺ ⇄ ★ ✔ ✘ ✕ ▶ ↴ ⟶ ✎`. Bor: `‘ ’ ʻ ʼ ρ − – — → ↑ ² · × ° Σ`.

Daraja: **A** = albatta tuzatiladi; **B** = texnik imkon bo'lsa; **C** = faqat hisobotga yoziladi, o'zgartirilmaydi.

## Umumiy talablar (hamma betlar)
- **U1 (A) Qora bo'yalgan joylar** (8 ta vektor to'rtburchak, fill rangi to'q ko'k `(0.06,0.15,0.25)` yoki `(0.0,0.13,0.38)`; ostidagi kontent ko'rinishi/o'qilishi kerak):
  - 51-bet: rect (309,120,548,252) — "Molyar massa" katagi
  - 52-bet: rect (49,516,163,539) — "1 Ma'nosi" sarlavhasi
  - 82-bet: rect (30,654,571,754) — "3 Davr bo'ylab oksid va gidroksidlar..." bloki
  - 83-bet: rect (26,258,563,663) — 2-davr/3-davr jadvallari ustidagi katta maydon
  - 84-bet: rect (160,308,537,327), (160,352,539,371), (156,510,540,529), (157,576,539,593) — Fe²⁺, Cu²⁺, Fe³⁺, Al³⁺ qatorlari
  Faqat shu to'rtburchaklar (va ularga tegishli fill amallari) olib tashlanadi; boshqa chiziq/matn/rasm buzilmasin. Olib tashlangach asl (to'g'ri) ranglar/matn ko'rinishini sahifani render qilib tekshiring.
- **U2 (A) Shrift:** CMU Serif bo'lmagan MATN (harf/raqam) CMU Serif Roman'ga o'tkaziladi (Inter, DejaVu, LiberationSerif, Helvetica). Mavjud CMU Serif **Bold/Italic**'ni o'zgartirmang (sarlavha dizayni buzilmasin). Belgilar (`▶ ★ ✔ ✘ ✕ ⇄ ↴ ⟶ ✎ ≈`) CMU'da yo'q — o'zgarishsiz qoldiring va hisobotga yozing. Topilgan non-CMU matnlar: 27-bet "qog'ozida" (Type3), 60–61-bet "x" harflari (Type3), 91-bet yorliqlari (Type3: tashqi sfera, kompleks hosil, ligand, kationi, qiluvchi, qotishma, eritma). Avval ularning haqiqiy shriftini aniqlang (Type3 ba'zan CMU Italic bo'ladi) — agar allaqachon CMU Serif bo'lsa tegmang.

## 1–20-betlar
- p6 (A): "ρ = 1 g/cm³ (suv)" dagi zichlik belgisi arabcha "م" ko'rinishida chiqqan (glyph buzuq) → to'g'ri yunoncha **ρ** (CMU Serif'da bor).
- p7 (A): "Boshqa moddalar bilan reaksiyasi" katagi sarlavhasi → **"Qizdirilganda parchalanish"** (2KMnO₄ → K₂MnO₄ + MnO₂ + O₂ parchalanish reaksiyasi).
- p7 (B): "O₂" yozuvi (probirka tepasida) katak o'ng chegarasidan tashqariga chiqqan → katak ichiga siljiting.
- p11 (A): Fosfor rasmlari tartibi noto'g'ri. Tepada ustunlar: oq | qora | qizil (sxemalar shu tartibda), pastdagi suratlar esa: qizil fosfor | qora fosfor | oq fosfor. 1- va 3-surat (rasm + ostidagi yozuv) o'rin almashsin: 1-ustunda **oq fosfor**, 3-ustunda **qizil fosfor** bo'lsin.
- p22 (A): "Deistillyator" → **"Distillyator"**.
- p22 (B): "(aralashtirgich)" yozuvi katak chegarasidan oshgan → kichraytirib sig'diring.
- p2 (C): atom rasmida "tashkil topgan" matnini strelka kesib o'tgan.
- p3–4 (C): elementlar jadvali 3 ustunga bo'lingan, Z tartibi uzilgan.
- p15 (C): "Gidridlar" ta'rifi ("biri H bo'lgan 2 xil element...") HCl, H₂O'ni ham qamrab oladi — aniqroq bo'lishi kerak.
- p6→7 (C): "4 Kimyoviy xossalar" sarlavhasi keyingi betga ajralib qolgan; p15→16 jadvalning bitta qatori ajralgan.

## 21–45-betlar
- p35 (A): "Qattiqdan **suyuqqa**" → **"suyuqlikka"**.
- p41 (A): jadvalda Z=20 "**Kaltsiy**" → **"Kalsiy"** (3 va 40-betlar bilan bir xil).
- p42 (B): Na₂SO₄ molekula modelida o'ng chetdagi "Na" katak chegarasida kesilgan.
- p43 (B): "VIII A" sarlavha katagi o'ng chetda kesilgan.
- p44 (B): "+1 V" yozuvi bog' chizig'i bilan ustma-ust tushgan (H₃PO₂ sxemasi).
- p46 (A): "yadro uning markazidagi **no'xat donasi** kabi bo'ladi" → **"qum donasi"** (100 m stadion ↔ yadro ≈ 1 mm).
- p38–45 (C): bo'sh joylar (40, 42, 45-betlar yarmi bo'sh).

## 46–66-betlar
- p51 (U1): qora "Molyar massa" katagi (yuqoridagi U1).
- p52 (U1): qora "1 Ma'nosi" sarlavhasi.
- p51 (B): "1 mol H" shari oq, ichidagi "H" harfi ham oq → harf ko'rinadigan rangda (to'q) bo'lsin.
- p53–54 (B): daraja ko'rsatkichlari defis bilan yozilgan ("10-24", "10-27", "10-26", "2,99·10-26") → haqiqiy minus **"−"** (U+2212) bilan, yuqori indeksda.
- p59 (A): "1 mol H₂SO₄ **molekulasi** esa:" → **"1 mol H₂SO₄ da:"**.
- p66 (A) 4-bo'lim ("Tabiatda uchrashi yoki turmushda qo'llanilishiga ko'ra tanish nomlar"):
  - "SO₂ – gaz, kvars" → **"SO₂ – gaz; SiO₂ – kvars"**
  - "MnO – pirolyuzit" → **"MnO₂ – pirolyuzit"**
  - "PbO – surik" → **"Pb₃O₄ – surik"**
- p66 (A): "**Aluminiy** + oksid" va "**aluminiy** oksid (valentligi doimiy, III)" → **"Alyuminiy"**, **"alyuminiy"** (kitobning qolgan joylari bilan bir xil). Bu 65→66-betdagi nomlash sxemasi.
- p60→61 (C): "3. 80 g Fe₂(SO₄)₃..." sarlavhasi keyingi betga ajralgan.
- p52 (C): §1.22 sarlavha ostidagi "Mol, Avogadro soni va haqiqiy massa" mavzuga mos emas.
- p53 vs 47–49 (C): molekula massasi uchun "A" belgisi (atom massasi bilan chalkash).
- p46,48,49,50,60 (C/U2): "≈" LiberationSerif'da — CMU'da yo'q, shunday qoldiring.

## 67–81-betlar
- p68 (A): "2) suyuqliklar" qatorida "**N₂O₅** — ko'k rangli", "3) qattiq moddalar" qatorida "**N₂O₃** — oq rangli". Haqiqatda N₂O₃ — ko'k suyuqlik, N₂O₅ — oq qattiq modda. Faqat formula yorliqlarini almashtiring: suyuqliklarda **N₂O₃** (ko'k rangli), qattiqlarda **N₂O₅** (oq rangli).
- p74 (A): "Oksidlarning xossalari (taqqoslash jadvali)": "Kislota bilan" qatori hozir `+ | − | +` → **`− | + | +`**; "Ishqor bilan" qatori hozir `− | + | +` → **`+ | − | +`** (ustunlar: Kislotali | Asosli | Amfoter). "+" va "−" belgilarining ranglari (kulrang / pushti) har bir belgi bilan birga turishi kerak.
- p74 (A): "2.5-§ Peroksidlar va **subperoksidlar**" → **"Peroksidlar va superoksidlar"**; "**Subperoksidlar**: O₂⁻" → **"Superoksidlar: O₂⁻"**; "**Subperoksidlar** (superoksidlar)" → **"Superoksidlar"**; matn ichidagi boshqa "subperoksid" → "superoksid".
- p75 (A): "Metall oksidini oksidlash: 2CaO + O₂ → 2CaO₂" → **"2BaO + O₂ → 2BaO₂"** (to'g'ri sanoat reaksiyasi).
- p78 (B): jadvalda "Metallurgiyada flyus sifatida (ardoqsizlantirish" matni ustun chetida kesilgan; "Oltingugurt(" / "VI) oksid" qator bo'linishi xunuk → sig'diring.
- p80 (A): "NaOH — O'yuvchi natriy **(soda)**" → **"O'yuvchi natriy (kaustik soda)"** (soda = Na₂CO₃). Kerak bo'lsa 2 qatorga bo'ling; KOH yozuvi o'zgarmaydi.
- p71→72 (C): "Ishqor + kislotali oksid = tuz + suv" sarlavhasi keyingi betga ajralgan.

## 82–91-betlar
- p82, p83, p84 (U1): 6 ta qora maydon.
- p85 (A): "Eriymaydigan asoslar" bo'limida **Fe(OH)₂** "jigarrang" → **"oq"** va **Mn(OH)₂** "jigarrang" → **"oq"**; ularning doira ranglari ham Mg(OH)₂ doirasi kabi och (oqish) bo'lsin. (Cu(OH)₂ ko'k, qolganlari o'zgarmaydi; Amfoter bo'limidagi Fe(OH)₃ jigarrang — to'g'ri.)
- p87 (A): indikatorlar jadvalida **Metilzarg'aldoq**ning neytral muhitdagi "Sariq" → **"To'q sariq"** (ishqoriy muhitdagi "Sariq" o'zgarmaydi).
- p91 (C): sxemada "tetra gidrokso alyuminat + kaliy" tartibi (nomlashda kation oldin: kaliy tetragidroksoalyuminat); Zn, Al, Be uchun "eritma" strelkalari yo'q; pastdagi kvadrat qavslar o'ng chetda kesilgan (B: qavslar kesilishini tuzatsa bo'ladi).
- p89 (C): Cl₂, Br₂ qatoridagi "sovuqda"/"t" strelka yozuvlari buzuq joylashgan.
