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
_stat = {"requests": 0, "input": 0, "output": 0}
_users = {}  # id -> {"name", "username", "count"}
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


async def myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(f"Sizning Telegram ID raqamingiz: {uid}")


async def stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ALLOWED and update.effective_user.id not in ALLOWED:
        return
    n = _stat["requests"]
    await update.message.reply_text(
        f"Bot qayta ishga tushganidan beri:\nSo'rovlar: {n}\n"
        f"Kirish tokenlari: {_stat['input']}\nChiqish tokenlari: {_stat['output']}\n"
        f"O'rtacha: {(_stat['input'] + _stat['output']) // max(n, 1)} token/masala\n\n"
        "Aniq narx: platform.claude.com → Расходы / Usage.")


async def users(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ALLOWED and update.effective_user.id not in ALLOWED:
        return
    if not _users:
        await update.message.reply_text("Hali hech kim yozmagan (bot qayta ishga tushganidan beri).")
        return
    rows = [f"{i}. {r['name']} (@{r['username']}) id={uid}, xabar: {r['count']}"
            for i, (uid, r) in enumerate(sorted(_users.items(), key=lambda x: -x[1]["count"]), 1)]
    await update.message.reply_text("Foydalanuvchilar (qayta ishga tushganidan beri):\n" + "\n".join(rows[:40]))


async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg, uid = update.message, update.effective_user.id
    u = update.effective_user
    rec = _users.setdefault(uid, {"name": u.full_name, "username": u.username or "-", "count": 0})
    rec["count"] += 1
    log.info("Foydalanuvchi: id=%s ism=%s username=@%s xabar#%s", uid, u.full_name, u.username, rec["count"])
    if ALLOWED and uid not in ALLOWED:
        await msg.reply_text(f"Kechirasiz, sizga ruxsat berilmagan. (ID: {uid})")
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
            u = data.pop("_usage", {})
            _stat["requests"] += 1
            _stat["input"] += u.get("input", 0)
            _stat["output"] += u.get("output", 0)
            log.info("Token: kirish=%s chiqish=%s (jami so'rov: %s)", u.get("input"), u.get("output"), _stat["requests"])
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
        except Exception as e:  # noqa: BLE001
            log.exception("xatolik")
            detail = f"{type(e).__name__}: {e}"[:300]
            await status.edit_text(
                "❌ Xatolik yuz berdi. Masalani aniqroq yozib, qayta yuboring.\n\n"
                f"Texnik sabab: {detail}")


def main():
    for name in ("TELEGRAM_BOT_TOKEN", "ANTHROPIC_API_KEY"):
        if not os.getenv(name):
            raise SystemExit(f"Muhit o'zgaruvchisi topilmadi: {name}")
    log.info("Bot ishga tushmoqda. Ruxsat berilgan ID lar: %s", sorted(ALLOWED) or "hamma")
    app = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"].strip()).build()
    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(CommandHandler("stat", stat))
    app.add_handler(CommandHandler("id", myid))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.PHOTO, handle))
    app.run_polling()


if __name__ == "__main__":
    main()
