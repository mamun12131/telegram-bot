import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
import yt_dlp


# ====== CONFIG ======
BOT_TOKEN = os.getenv("8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE")  # Render Environment Variable থেকে নেবে
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
# ====================


# ====== VIDEO DOWNLOAD FUNCTION ======
def download_video(url: str) -> str:
    ydl_opts = {
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
# ====================================


# ====== HANDLE MESSAGE ======
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("❌ Valid link দাও")
        return

    keyboard = [
        [InlineKeyboardButton("🎬 Download Video", callback_data=f"video|{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "কি ডাউনলোড করবে?",
        reply_markup=reply_markup
    )
# ====================================


# ====== BUTTON HANDLER ======
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, url = query.data.split("|", 1)

    msg = await query.edit_message_text("⏳ Downloading…")

    try:
        file_path = await asyncio.to_thread(download_video, url)
    except Exception as e:
        await msg.edit_text("❌ Download failed")
        return

    await msg.edit_text("📤 Uploading…")

    await query.message.reply_video(
        video=open(file_path, "rb"),
        supports_streaming=True
    )

    os.remove(file_path)
    await msg.delete()
# ====================================


# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")
    app.run_polling()
# ====================================


if name == "main":
    main()
