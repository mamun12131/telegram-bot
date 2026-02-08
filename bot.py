import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# টোকেন (Render Environment Variable থেকে নেবে)
BOT_TOKEN = os.environ.get("8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set in environment variables!")
    exit(1)

# ডাউনলোড ফোল্ডার
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎬 Welcome {user.first_name}!\n\n"
        "📹 I can download videos from YouTube!\n\n"
        "📌 Just send me a YouTube link!"
    )

# ---------- লিংক রিসিভ ----------
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # শুধুমাত্র YouTube লিংক চেক
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("❌ Please send a valid YouTube link")
        return
    
    # URL সেভ করুন context এ
    context.user_data['last_url'] = url
    
    # সিম্পল বাটন
    keyboard = [
        [
            InlineKeyboardButton("🎥 Video (360p)", callback_data="360"),
            InlineKeyboardButton("🎥 Video (720p)", callback_data="720")
        ],
        [
            InlineKeyboardButton("🎵 Audio (MP3)", callback_data="mp3"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔗 YouTube link detected!\n\nChoose option:",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# ---------- ডাউনলোড ফাংশন ----------
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE, quality="720"):
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('last_url')
    
    try:
        await query.edit_message_text(f"⏬ Downloading {quality}p video...")
        
        # yt-dlp সেটিংস
        ydl_opts = {
            'format': f'best[height<={quality}]',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        # ডাউনলোড
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # টেলিগ্রামে আপলোড
        await query.edit_message_text("📤 Uploading to Telegram...")
        
        with open(filename, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=video_file,
                caption=f"✅ Download Complete!\n\n"
                       f"📹 {info.get('title', 'Video')}",
                supports_streaming=True
            )
        
        await query.message.delete()
        
        # ফাইল ডিলিট
        os.remove(filename)
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        await query.edit_message_text(f"❌ Download failed: {str(e)[:100]}")

# ---------- অডিও ডাউনলোড ----------
async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('last_url')
    
    await query.edit_message_text("🎵 Extracting audio...")
    
    try:
        # অডিও এক্সট্রাক্ট
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # টেলিগ্রামে আপলোড
        with open(filename, 'rb') as audio_file:
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=audio_file,
                caption=f"🎵 Audio Extracted!\n\n"
                       f"🎶 {info.get('title', 'Audio')}",
                title=info.get('title', 'Audio')
            )
        
        await query.message.delete()
        os.remove(filename)
        
    except Exception as e:
        await query.edit_message_text(f"❌ Audio extraction failed: {str(e)[:100]}")

# ---------- বাটন হ্যান্ডলার ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data in ["360", "720"]:
        await download_video(update, context, data)
    
    elif data == "mp3":
        await download_audio(update, context)

# ---------- মেইন ফাংশন ----------
def main():
    # অ্যাপ্লিকেশন তৈরি
    application = Application.builder().token(BOT_TOKEN).build()
    
    # কমান্ড হ্যান্ডলার
    application.add_handler(CommandHandler("start", start))
    
    # মেসেজ হ্যান্ডলার
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    # বাটন হ্যান্ডলার
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # রান
    logger.info("🤖 YouTube Downloader Bot Started!")
    application.run_polling()

if __name__ == "__main__":
    main()
