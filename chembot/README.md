# Kimyo video-yechim Telegram boti

Masala matni (yoki rasmi) -> Claude API yechadi -> vertikal 720x1280 MP4 video -> Telegramga yuboriladi.

## Ishga tushirish
1. @BotFather da bot yarating va tokenni oling.
2. platform.claude.com da API kalit oling (Billing ga kredit qo'shing, oylik limit qo'ying).
3. `cp .env.example .env`, qiymatlarni to'ldiring.
4. Lokal: `pip install -r requirements.txt` (ffmpeg o'rnatilgan bo'lsin), so'ng
   `set -a; source .env; set +a; python bot.py`
   Docker: `docker build -t chembot . && docker run --env-file .env chembot`
5. Botga masala yuboring.

## Kalitsiz sinash
`python render.py sample.json out.mp4` — tayyor JSON dan video chiqaradi.

Fayllar: `solver.py` (Claude), `render.py` (slayd/animatsiya/video), `bot.py` (Telegram).
