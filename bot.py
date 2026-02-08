import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp

# Token Render / Platform থেকে আসবে
BOT_TOKEN = os.getenv("8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_video(url, audio_only=False):
    ydl_opts = {
        "format": "bestaudio/best" if audio_only else "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    if audio_only:
        ydl_opts.update({
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


async def fake_progress(msg):
    for p in range(0, 101, 20):
        await asyncio.sleep(1)
        try:
            await msg.edit_text(f"⏳ Downloading… {p}%")
        except:
            pass


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("🎥 Video", callback_data="video"),
            InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio"),
        ]
    ]

    await update.message.reply_text(
        "কী ডাউনলোড করতে চাও?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    audio_only = query.data == "audio"

    status = await query.edit_message_text("⏳ Downloading… 0%")
    progress_task = asyncio.create_task(fake_progress(status))

    try:
        file_path = await asyncio.to_thread(download_video, url, audio_only)
    except Exception:
        progress_task.cancel()
        await status.edit_text("❌ Download failed")
        return

    progress_task.cancel()
    await status.edit_text("📤 Uploading…")

    if audio_only:
        await query.message.reply_audio(audio=open(file_path, "rb"))
    else:
        await query.message.reply_video(
            video=open(file_path, "rb"),
            supports_streaming=True,
        )

    os.remove(file_path)
    await status.delete()


if __name__ == "__main__":
    main()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot running...")
    app.run_polling()
