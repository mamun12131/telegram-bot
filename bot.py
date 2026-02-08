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

# ===== CONFIG =====
BOT_TOKEN = "8335582124:AAF1Pd4SSaguT1WfFJbsOLLejJis3LTDXcs"
GROUP_LINK = "https://t.me/+Qm_5J1hj8NcwYjBl"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ===== HELPERS =====
def is_youtube(url: str):
    return "youtube.com" in url or "youtu.be" in url

def is_tiktok(url: str):
    return "tiktok.com" in url

def ydl_video(url):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.mp4",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        return ydl.prepare_filename(ydl.extract_info(url, download=False))

def ydl_audio(url):
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"{DOWNLOAD_DIR}/{info['id']}.mp3"

async def fake_progress(msg):
    for i in range(1, 101, 5):
        await asyncio.sleep(0.3)
        try:
            await msg.edit_text(f"⏳ ডাউনলোড হচ্ছে... {i}%")
        except:
            pass

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Support Group", url=GROUP_LINK)]
    ]
    await update.message.reply_text(
        "👋 স্বাগতম!\n🎬 শুধু TikTok ভিডিও ডাউনলোড করা যায়\n\n🔗 দয়া করে TikTok ভিডিওর লিংক পাঠান",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if is_youtube(url):
        await update.message.reply_text(
            "❌ YouTube লিংক সাপোর্ট করে না\n✅ শুধু TikTok ভিডিওর লিংক দিন"
        )
        return

    if not is_tiktok(url):
        await update.message.reply_text(
            "❌ ভুল লিংক\n✅ শুধু TikTok ভিডিওর লিংক দিন"
        )
        return

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("🎬 MP4 (Video)", callback_data="mp4"),
            InlineKeyboardButton("🎵 MP3 (Audio)", callback_data="mp3"),
        ]
    ]
    await update.message.reply_text(
        "📥 কোন ফরম্যাটে ডাউনলোড করবেন?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ লিংক পাওয়া যায়নি")
        return

    progress_msg = await query.edit_message_text("⏳ ডাউনলোড হচ্ছে... 1%")
    progress_task = asyncio.create_task(fake_progress(progress_msg))

    try:
        if query.data == "mp4":
            path = await asyncio.to_thread(ydl_video, url)
            await query.message.reply_video(open(path, "rb"))
        else:
            path = await asyncio.to_thread(ydl_audio, url)
            await query.message.reply_audio(open(path, "rb"))

        progress_task.cancel()
        await progress_msg.delete()
        os.remove(path)

    except Exception:
        progress_task.cancel()
        await progress_msg.edit_text("❌ ডাউনলোড ব্যর্থ হয়েছে")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 TikTok Downloader Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
