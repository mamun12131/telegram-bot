import os
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp

# 🔐 BOT TOKEN (তুমি যে token দিয়েছিলে সেটাই বসানো)
BOT_TOKEN = "8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# -------- download helpers --------

def download_video(url):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def download_audio(url):
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).replace(".webm", ".mp3")

# -------- handlers --------

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("📹 Video", callback_data="video"),
            InlineKeyboardButton("🎵 Audio", callback_data="audio"),
        ]
    ]
    await update.message.reply_text(
        "কি নামাবে?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ Link missing")
        return

    await query.edit_message_text("⏳ Processing...")

    try:
        if query.data == "video":
            path = await asyncio.to_thread(download_video, url)
            await query.message.reply_video(
                video=open(path, "rb"),
                supports_streaming=True,
            )
        else:
            path = await asyncio.to_thread(download_audio, url)
            await query.message.reply_audio(
                audio=open(path, "rb"),
            )
        os.remove(path)
    except Exception:
        await query.message.reply_text("❌ Download failed")

# -------- main --------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 Button video bot running...")
    app.run_polling()

# ⚠️ এইটাই আসল ঠিক লাইন
if __name__ == "__main__":
    main()
