import os
import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp

BOT_TOKEN = "8335582124:AAF1Pd4SSaguT1WfFJbsOLLejJis3LTDXcs"
GROUP_LINK = "https://t.me/+Qm_5J1hj8NcwYjBl"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# -------- helpers --------

def is_youtube(url):
    return "youtube.com" in url or "youtu.be" in url

def is_tiktok(url):
    return "tiktok.com" in url

def download_tiktok(url, quality):
    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "format": "mp4",
        "quiet": True,
    }
    if quality == "480":
        ydl_opts["format"] = "mp4[height<=480]/mp4"
    elif quality == "720":
        ydl_opts["format"] = "mp4[height<=720]/mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# -------- handlers --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Support Group", url=GROUP_LINK)]
    ]
    await update.message.reply_text(
        "👋 স্বাগতম!\n🎬 ভিডিও ডাউনলোড করতে লিংক প্রেরণ করুন 🥹",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if is_youtube(url):
        await update.message.delete()
        await update.message.reply_text(
            "❌ YouTube ভিডিও ডাউনলোড করা যায় না।\n✅ শুধুমাত্র TikTok ভিডিও পাঠান।"
        )
        return

    if not is_tiktok(url):
        return

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("480p", callback_data="q_480"),
            InlineKeyboardButton("720p", callback_data="q_720"),
        ]
    ]
    await update.message.reply_text(
        "🎞 কোন কোয়ালিটিতে ডাউনলোড করবেন?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def quality_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    quality = query.data.split("_")[1]

    msg = await query.edit_message_text("⏳ Processing... 1%")

    for i in range(2, 101, 7):
        await asyncio.sleep(0.2)
        try:
            await msg.edit_text(f"⏳ Processing... {i}%")
        except:
            pass

    path = await asyncio.to_thread(download_tiktok, url, quality)
    await query.message.reply_video(video=open(path, "rb"))
    os.remove(path)

# -------- main --------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(quality_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
