import os
import asyncio
import random
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

BOT_TOKEN = "8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------- helpers ----------

async def fake_progress(msg):
    percent = 0
    while percent < 100:
        percent += random.randint(1, 9)
        if percent > 100:
            percent = 100
        try:
            await msg.edit_text(f"⬇️ ডাউনলোড হচ্ছে… {percent}%")
        except:
            pass
        await asyncio.sleep(random.uniform(0.4, 0.8))

def download_video(url, height):
    ydl_opts = {
        "format": f"bestvideo[height<={height}]+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# ---------- commands ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম!\n🎬 ভিডিও ডাউনলোড করতে লিংক প্রেরণ করুন 🥹"
    )

# ---------- handlers ----------

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["url"] = update.message.text.strip()

    keyboard = [
        [
            InlineKeyboardButton("1080p", callback_data="1080"),
            InlineKeyboardButton("720p", callback_data="720"),
        ],
        [
            InlineKeyboardButton("480p", callback_data="480"),
            InlineKeyboardButton("360p", callback_data="360"),
        ],
    ]

    await update.message.reply_text(
        "কোন কোয়ালিটিতে ডাউনলোড করবেন?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.message.delete()
        return

    # সব আগের মেসেজ ডিলিট
    try:
        await query.message.delete()
    except:
        pass

    progress_msg = await query.message.reply_text("⬇️ ডাউনলোড হচ্ছে… 0%")

    progress_task = asyncio.create_task(fake_progress(progress_msg))

    try:
        path = await asyncio.to_thread(download_video, url, query.data)
        progress_task.cancel()

        await progress_msg.delete()
        await query.message.reply_video(
            video=open(path, "rb"),
            supports_streaming=True
        )
        os.remove(path)
    except Exception:
        progress_task.cancel()
        await progress_msg.edit_text("❌ ডাউনলোড ব্যর্থ হয়েছে")

# ---------- main ----------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 Video downloader bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
