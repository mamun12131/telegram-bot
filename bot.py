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

# ========= CONFIG =========
BOT_TOKEN = "8335582124:AAF1Pd4SSaguT1WfFJbsOLLejJis3LTDXcs"
GROUP_ID = -1002872325078   # ✅ তোর chat id এখানে বসানো
SUPPORT_GROUP = "https://t.me/+Qm_5J1hj8NcwYjBl"
DOWNLOAD_DIR = "downloads"
# ==========================

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# -------- /start --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text="🤖 Bot Started Successfully"
    )

    keyboard = [
        [InlineKeyboardButton("💬 Support Group", url=SUPPORT_GROUP)]
    ]

    await update.message.reply_text(
        "👋 স্বাগতম!\n\n"
        "🎬 TikTok ভিডিও ডাউনলোড করতে লিংক প্রেরণ করুন\n"
        "❌ YouTube সাপোর্ট করে না",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -------- link handler --------
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "youtube.com" in text or "youtu.be" in text:
        await update.message.reply_text(
            "❌ YouTube লিংক সাপোর্ট করে না\n"
            "✅ শুধুমাত্র TikTok ভিডিও লিংক পাঠান"
        )
        return

    context.user_data["url"] = text

    keyboard = [
        [
            InlineKeyboardButton("📹 MP4", callback_data="mp4"),
            InlineKeyboardButton("🎵 MP3", callback_data="mp3"),
        ]
    ]

    await update.message.reply_text(
        "👇 কোন ফরম্যাটে নামাবে?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -------- fake progress --------
async def fake_progress(msg):
    for i in range(1, 101, 5):
        await asyncio.sleep(0.4)
        try:
            await msg.edit_text(f"⏳ Downloading... {i}%")
        except:
            pass

# -------- button handler --------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ Link missing")
        return

    progress_msg = await query.edit_message_text("⏳ Downloading... 1%")
    progress = asyncio.create_task(fake_progress(progress_msg))

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        progress.cancel()
        await progress_msg.delete()

        if query.data == "mp4":
            await query.message.reply_video(video=open(file_path, "rb"))
        else:
            await query.message.reply_audio(audio=open(file_path, "rb"))

        os.remove(file_path)

    except Exception:
        progress.cancel()
        await query.message.reply_text("❌ Download failed")

# -------- main --------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
