import os
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp

# 🔐 তোমার আগের BOT TOKEN (hard-coded)
BOT_TOKEN = "8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------- helpers ----------------

async def processing_animation(msg):
    frames = ["⏳ Processing.", "⏳ Processing..", "⏳ Processing..."]
    for _ in range(6):
        for f in frames:
            try:
                await msg.edit_text(f)
            except:
                pass
            await asyncio.sleep(0.5)

def download_video(url, quality):
    fmt = (
        "bestvideo[height<=720]+bestaudio/best"
        if quality == "720"
        else "bestvideo[height<=480]+bestaudio/best"
    )
    ydl_opts = {
        "format": fmt,
        "merge_output_format": "mp4",
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
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = ydl.prepare_filename(info)
        if path.endswith(".webm"):
            path = path.replace(".webm", ".mp3")
        return path

# ---------------- commands ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম!\n\n"
        "🎬 ভিডিও ডাউনলোড করতে লিংক প্রেরণ করুন\n"
        "🎵 MP3 / MP4 বেছে নেওয়ার অপশন পাবেন"
    )

# ---------------- handlers ----------------

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["url"] = update.message.text.strip()
    keyboard = [
        [
            InlineKeyboardButton("🎬 MP4 Video", callback_data="mp4"),
            InlineKeyboardButton("🎵 MP3 Audio", callback_data="mp3"),
        ]
    ]
    await update.message.reply_text(
        "কি ডাউনলোড করতে চান?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ লিংক পাওয়া যায়নি")
        return

    if query.data == "mp4":
        keyboard = [
            [
                InlineKeyboardButton("720p", callback_data="720"),
                InlineKeyboardButton("480p", callback_data="480"),
            ]
        ]
        await query.edit_message_text(
            "🎚️ ভিডিও কোয়ালিটি নির্বাচন করুন",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    msg = await query.edit_message_text("⏳ Processing...")
    try:
        anim = asyncio.create_task(processing_animation(msg))
        if query.data == "mp3":
            path = await asyncio.to_thread(download_audio, url)
            anim.cancel()
            await query.message.reply_audio(audio=open(path, "rb"))
        else:
            path = await asyncio.to_thread(download_video, url, query.data)
            anim.cancel()
            await query.message.reply_video(
                video=open(path, "rb"),
                supports_streaming=True
            )
        os.remove(path)
        await msg.delete()
    except Exception:
        await msg.edit_text("❌ Download failed")

# ---------------- main ----------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 Advanced downloader bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
