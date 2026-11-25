"""Telegram bot: kimyo masalasi -> video yechim."""
import asyncio
import logging
import os
import re
import tempfile
import time
from collections import defaultdict, deque

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import render
import solver

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("chembot")
# httpx so'rov manzilini (ichida bot tokeni bor) logga yozmasin
for _n in ("httpx", "httpcore"):
    logging.getLogger(_n).setLevel(logging.WARNING)

# Kredit himoyasi
ALLOWED = {int(x) for x in re.findall(r"\d+", os.getenv("ALLOWED_USERS", ""))}
MAX_PER_HOUR = int(os.getenv("MAX_PER_HOUR", "10"))
_hist = defaultdict(deque)
_sem = asyncio.Semaphore(int(os.getenv("MAX_PARALLEL", "2")))

HELP = ("Salom! Men kimyo masalalarini video yechimga aylantiraman.\n\n"
        "Masala matnini (yoki rasmini) yuboring: boshqa hech narsa kerak emas. "
        "Men o'zim yechib, vertikal video tayyorlab beraman (~1-2 daqiqa).")


def rate_ok(uid):
    now, q = time.time(), _hist[uid]
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= MAX_PER_HOUR:
        return False
    q.append(now)
    return True


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)


async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg, uid = update.message, update.effective_user.id
    if ALLOWED and uid not in ALLOWED:
        await msg.reply_text("Kechirasiz, sizga ruxsat berilmagan.")
        return
    text = (msg.text or msg.caption or "").strip()
    img = None
    if msg.photo:
        f = await msg.photo[-1].get_file()
        img = bytes(await f.download_as_bytearray())
    if not text and not img:
        return
    if not rate_ok(uid):
        await msg.reply_text("Soatlik limitga yetdingiz, birozdan so'ng urinib ko'ring.")
        return

    status = await msg.reply_text("⏳ Masala yechilmoqda...")
    async with _sem:
        try:
            await ctx.bot.send_chat_action(msg.chat_id, ChatAction.TYPING)
            data = await asyncio.to_thread(solver.solve, text, img)
            await status.edit_text("🎬 Video tayyorlanmoqda...")
            await ctx.bot.send_chat_action(msg.chat_id, ChatAction.UPLOAD_VIDEO)
            with tempfile.TemporaryDirectory() as tmp:
                out = os.path.join(tmp, "yechim.mp4")
                await asyncio.to_thread(render.render_video, data, out)
                with open(out, "rb") as fh:
                    await msg.reply_video(fh, width=render.W, height=render.H,
                                          supports_streaming=True,
                                          caption=data.get("title", "Video yechim"))
            await status.delete()
        except Exception:  # noqa: BLE001
            log.exception("xatolik")
            await status.edit_text("❌ Xatolik yuz berdi. Masalani aniqroq yozib, qayta yuboring.")


def main():
    for name in ("TELEGRAM_BOT_TOKEN", "ANTHROPIC_API_KEY"):
        if not os.getenv(name):
            raise SystemExit(f"Muhit o'zgaruvchisi topilmadi: {name}")
    log.info("Bot ishga tushmoqda. Ruxsat berilgan ID lar: %s", sorted(ALLOWED) or "hamma")
    app = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.PHOTO, handle))
    app.run_polling()


if __name__ == "__main__":
    main()
