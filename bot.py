import os
import asyncio
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

# ===== CONFIG =====
BOT_TOKEN = "8335582124:AAF1Pd4SSaguT1WfFJbsOLLejJis3LTDXcs"
GROUP_LINK = "https://t.me/+Qm_5J1hj8NcwYjBl"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Support Group", url=GROUP_LINK)]
    ]
    await update.message.reply_text(
        "👋 স্বাগতম! 🎬\nভিডিও ডাউনলোড করতে লিংক প্রেরণ করুন 🥹",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== LINK HANDLE =====
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" in url or "youtu.be" in url:
        await update.message.delete()
        await update.message.chat.send_message(
            "❌ YouTube ভিডিও ডাউনলোড করা যায় না\n✅ শুধুমাত্র TikTok ভিডিও দিন"
        )
        return

    if "tiktok.com" not in url:
        return

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("720p", callback_data="720"),
            InlineKeyboardButton("480p", callback_data="480"),
        ]
    ]
    await update.message.reply_text(
        "🔽 কোয়ালিটি বেছে নিন",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== DOWNLOAD =====
def download_video(url, quality):
    ydl_opts = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def progress(msg):
    for i in range(1, 101, 7):
        await msg.edit_text(f"⏳ Downloading... {i}%")
        await asyncio.sleep(0.3)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    quality = query.data

    await query.message.delete()
    prog = await query.message.chat.send_message("⏳ Downloading... 1%")

    await progress(prog)

    path = await asyncio.to_thread(download_video, url, quality)
    await prog.delete()

    await query.message.chat.send_video(video=open(path, "rb"))
    os.remove(path)

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
