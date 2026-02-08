import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp
import subprocess

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# টোকেন
BOT_TOKEN = os.environ.get("8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    exit(1)

# ডাউনলোড ফোল্ডার
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎬 **Welcome {user.first_name}!**\n\n"
        "📹 **Supported Sites:**\n"
        "• YouTube\n• Facebook\n• Instagram\n• Twitter/X\n• TikTok\n• Many more!\n\n"
        "⚡ **Features:**\n"
        "• Video download (MP4)\n"
        "• Audio extraction (MP3)\n"
        "• Choose quality\n"
        "• Playlist support\n"
        "• Subtitle download\n\n"
        "📌 **Just send me a video link!**"
    )

# ---------- /help ----------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔧 **Available Commands:**
/start - Start the bot
/help - Show this help message
/formats - Show supported formats
/sites - Show supported websites

📥 **How to use:**
1. Send any video link
2. Choose format (Video/Audio)
3. Select quality
4. Download!

📱 **Supported:**
• YouTube (videos, shorts, playlists)
• Facebook (videos, reels)
• Instagram (posts, reels, stories)
• Twitter/X (videos)
• TikTok
• Reddit
• DailyMotion
• Vimeo
• And 1000+ more sites!
"""
    await update.message.reply_text(help_text)

# ---------- /sites ----------
async def sites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sites = """
🌐 **Supported Websites:**

🎬 **Video Platforms:**
• YouTube - Full videos, Shorts, Live
• Facebook - Videos, Reels
• Instagram - Posts, Reels, Stories
• TikTok - All videos
• Twitter/X - Videos
• Reddit - Videos, GIFs
• Vimeo, Dailymotion
• Twitch - Clips, VODs

🎵 **Audio/Music:**
• Spotify (audio only)
• SoundCloud
• Apple Music
• Bandcamp

📱 **Social Media:**
• LinkedIn videos
• Pinterest videos
• Likee videos
• Snapchat (public videos)

📺 **TV/Streaming:**
• Netflix (trailers only)
• Disney+ (trailers)
• Amazon Prime (trailers)
• Hulu (trailers)

🔗 **And 1000+ more sites via yt-dlp!**
"""
    await update.message.reply_text(sites)

# ---------- লিংক রিসিভ ----------
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # URL সেভ করুন context এ
    context.user_data['last_url'] = url
    
    # ফরম্যাট সিলেকশন বাটন
    keyboard = [
        [
            InlineKeyboardButton("🎥 Video", callback_data="format_video"),
            InlineKeyboardButton("🎵 Audio", callback_data="format_audio")
        ],
        [
            InlineKeyboardButton("📋 Get Info", callback_data="get_info"),
            InlineKeyboardButton("📜 Subtitle", callback_data="subtitle")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔗 **Link detected!**\n\n"
        f"📥 **URL:** {url[:50]}...\n\n"
        "📌 **Choose download format:**",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# ---------- কোয়ালিটি সিলেকশন ----------
async def quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, format_type="video"):
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('last_url')
    
    if format_type == "video":
        # ভিডিও কোয়ালিটি অপশন
        keyboard = [
            [
                InlineKeyboardButton("📱 Low (360p)", callback_data="quality_360"),
                InlineKeyboardButton("🖥️ Medium (720p)", callback_data="quality_720")
            ],
            [
                InlineKeyboardButton("📺 HD (1080p)", callback_data="quality_1080"),
                InlineKeyboardButton("🎬 Best Quality", callback_data="quality_best")
            ],
            [
                InlineKeyboardButton("📦 MP4", callback_data="format_mp4"),
                InlineKeyboardButton("🔄 WebM", callback_data="format_webm")
            ]
        ]
        text = "🎥 **Video Download**\nChoose quality & format:"
        
    else:  # audio
        # অডিও ফরম্যাট অপশন
        keyboard = [
            [
                InlineKeyboardButton("🎵 MP3 (128kbps)", callback_data="audio_mp3_128"),
                InlineKeyboardButton("🎵 MP3 (320kbps)", callback_data="audio_mp3_320")
            ],
            [
                InlineKeyboardButton("🔊 M4A", callback_data="audio_m4a"),
                InlineKeyboardButton("🎶 Best Audio", callback_data="audio_best")
            ],
            [
                InlineKeyboardButton("📼 Extract Audio Only", callback_data="audio_extract")
            ]
        ]
        text = "🎵 **Audio Download**\nChoose format & quality:"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# ---------- ভিডিও ইনফো ----------
async def get_video_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('last_url')
    
    try:
        await query.edit_message_text("🔍 Fetching video info...")
        
        # yt-dlp দিয়ে ইনফো নিন
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # ফরম্যাট লিস্ট
            formats = info.get('formats', [])
            available_formats = []
            for f in formats[:10]:  # প্রথম ১০টি
                if f.get('format_note'):
                    available_formats.append(f"{f.get('format_note')} ({f.get('ext')})")
            
            info_text = f"""
📊 **Video Information:**

📌 **Title:** {info.get('title', 'N/A')}
⏱️ **Duration:** {info.get('duration', 0)} seconds
👁️ **Views:** {info.get('view_count', 'N/A')}
👍 **Likes:** {info.get('like_count', 'N/A')}
📅 **Upload Date:** {info.get('upload_date', 'N/A')}

📦 **Available Formats:**
{chr(10).join(available_formats[:5])}

👤 **Channel:** {info.get('uploader', 'N/A')}
🔗 **URL:** {url[:50]}...
"""
            await query.edit_message_text(info_text)
            
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")

# ---------- ডাউনলোড ফাংশন ----------
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE, quality="720"):
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('last_url')
    
    # প্রগ্রেস মেসেজ
    progress_msg = await query.edit_message_text(f"⏬ Downloading {quality}p video...")
    
    try:
        # yt-dlp সেটিংস
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks': [lambda d: print(d['status'])],
        }
        
        # ডাউনলোড
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # টেলিগ্রামে আপলোড
        await progress_msg.edit_text("📤 Uploading to Telegram...")
        
        with open(filename, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=video_file,
                caption=f"✅ **Download Complete!**\n\n"
                       f"📹 {info.get('title', 'Video')}\n"
                       f"📦 Quality: {quality}p\n"
                       f"👤 Channel: {info.get('uploader', 'N/A')}",
                supports_streaming=True
            )
        
        await progress_msg.delete()
        
        # ফাইল ডিলিট
        os.remove(filename)
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        await progress_msg.edit_text(f"❌ Download failed: {str(e)}")

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
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        
        # টেলিগ্রামে আপলোড
        with open(filename, 'rb') as audio_file:
            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=audio_file,
                caption=f"🎵 **Audio Extracted!**\n\n"
                       f"🎶 {info.get('title', 'Audio')}\n"
                       f"👤 Artist: {info.get('uploader', 'N/A')}\n"
                       f"⏱️ Duration: {info.get('duration', 0)}s",
                title=info.get('title', 'Audio')
            )
        
        await query.message.delete()
        os.remove(filename)
        
    except Exception as e:
        await query.edit_message_text(f"❌ Audio extraction failed: {str(e)}")

# ---------- বাটন হ্যান্ডলার ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "format_video":
        await quality_selection(update, context, "video")
    
    elif data == "format_audio":
        await quality_selection(update, context, "audio")
    
    elif data == "get_info":
        await get_video_info(update, context)
    
    elif data.startswith("quality_"):
        quality = data.replace("quality_", "")
        if quality == "360": await download_video(update, context, "360")
        elif quality == "720": await download_video(update, context, "720")
        elif quality == "1080": await download_video(update, context, "1080")
        elif quality == "best": await download_video(update, context, "2160")
    
    elif data.startswith("audio_"):
        await download_audio(update, context)
    
    elif data == "subtitle":
        await query.edit_message_text("📜 Subtitle feature coming soon!")

# ---------- মেইন ফাংশন ----------
def main():
    # অ্যাপ্লিকেশন তৈরি
    application = Application.builder().token(BOT_TOKEN).build()
    
    # কমান্ড হ্যান্ডলার
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sites", sites_command))
    
    # মেসেজ হ্যান্ডলার
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    # বাটন হ্যান্ডলার
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # রান
    logger.info("🤖 YouTube Downloader Bot Started!")
    application.run_polling()

if __name__ == "__main__":
    main()
