import os
import asyncio
import re
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp

# ================= CONFIG =================

BOT_TOKEN = "8335582124:AAF1Pd4SSaguT1WfFJbsOLLejJis3LTDXcs"
SUPPORT_GROUP = "https://t.me/+Qm_5J1hj8NcwYjBl"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================= HELPERS =================

def is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def is_tiktok(url: str) -> bool:
    return "tiktok.com" in url

def download_tiktok(url: str, audio=False):
    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }

    if audio:
        ydl_opts["format"] = "bestaudio"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ]
    else:
        ydl_opts["format"] = "mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if audio:
            filename = re.sub(r"\.\w+$", ".mp3", filename)
        return filename

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম!\n\n"
        "🎬 টিকটক ভিডিও ওয়াটারমার্ক ছাড়া ডাউনলোড করতে\n"
        "👉 দয়া করে TikTok ভিডিওর লিংক পাঠান\n\n"
        "❌ YouTube সাপোর্ট করে না\n\n"
        f"📢 সাপোর্ট গ্রুপ:\n{SUPPORT_GROUP}"
    )

# ================= LINK HANDLER =================

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if is_youtube(url):
        await update.message.delete()
        await update.message.reply_text(
            "❌ YouTube ভিডিও সাপোর্ট করে না\n"
            "👉 দয়া করে শুধুমাত্র TikTok ভিডিওর লিংক দিন"
        )
        return

    if not is_tiktok(url):
        await update.message.reply_text("❌ এটি TikTok লিংক নয়")
        return

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("🎬 MP4 Video", callback_data="mp4"),
            InlineKeyboardButton("🎵 MP3 Audio", callback_data="mp3"),
        ]
    ]

    await update.message.reply_text(
        "👇 কোন ফরম্যাটে ডাউনলোড করবেন?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ================= PROGRESS BAR =================

async def fake_progress(msg):
    for i in range(1, 101, 5):
        await msg.edit_text(f"⏳ ডাউনলোড হচ্ছে... {i}%")
        await asyncio.sleep(0.25)

# ================= BUTTON HANDLER =================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ লিংক পাওয়া যায়নি")
        return

    progress_msg = await query.edit_message_text("⏳ ডাউনলোড শুরু হচ্ছে...")

    await fake_progress(progress_msg)

    try:
        if query.data == "mp4":
            path = await asyncio.to_thread(download_tiktok, url, False)
            await query.message.reply_video(open(path, "rb"))
        else:
            path = await asyncio.to_thread(download_tiktok, url, True)
            await query.message.reply_audio(open(path, "rb"))

        os.remove(path)

        await progress_msg.delete()
        await query.message.delete()

    except Exception:
        await progress_msg.edit_text("❌ ডাউনলোড ব্যর্থ হয়েছে")

# ================= MAIN =================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 TikTok Downloader Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
