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

BOT_TOKEN = "8335582124:AAF1Pd4SSaguT1WfFJbsOLLejJis3LTDXcs"
GROUP_LINK = "https://t.me/+Qm_5J1hj8NcwYjBl"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------- helpers ----------

def is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def download_tiktok(url, quality):
    fmt = "best"
    if quality == "480":
        fmt = "bv*[height<=480]+ba/b"
    elif quality == "720":
        fmt = "bv*[height<=720]+ba/b"

    ydl_opts = {
        "format": fmt,
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# ---------- handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📢 Support Group", url=GROUP_LINK)]]
    await update.message.reply_text(
        "👋 স্বাগতম! 🎬\nভিডিও ডাউনলোড করতে TikTok লিংক প্রেরণ করুন 🥹",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if is_youtube(url):
        await update.message.delete()
        await update.message.chat.send_message(
            "❌ YouTube ভিডিও ডাউনলোড করা যায় না\n"
            "✅ শুধুমাত্র TikTok ভিডিও ডাউনলোড করা যাবে"
        )
        return

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("480p", callback_data="q_480"),
            InlineKeyboardButton("720p", callback_data="q_720"),
        ]
    ]
    await update.message.reply_text(
        "কোন কোয়ালিটিতে ডাউনলোড করবে?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    quality = query.data.split("_")[1]

    msg = await query.message.edit_text("⏳ Downloading... 1%")

    for i in [10, 25, 40, 60, 80, 100]:
        await asyncio.sleep(0.6)
        await msg.edit_text(f"⏳ Downloading... {i}%")

    path = await asyncio.to_thread(download_tiktok, url, quality)

    await query.message.delete()
    await query.message.chat.send_video(
        video=open(path, "rb"),
        supports_streaming=True,
    )
    os.remove(path)

# ---------- main ----------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
