import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE")

# ---------- Handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a video link and I will download it for you."
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("🎥 Video", callback_data="video"),
            InlineKeyboardButton("🎵 Audio", callback_data="audio"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data["link"] = text
    await update.message.reply_text(
        "Choose format:", reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    link = context.user_data.get("link")

    if query.data == "video":
        await query.edit_message_text(f"⬇️ Downloading video from:\n{link}")
    elif query.data == "audio":
        await query.edit_message_text(f"⬇️ Downloading audio from:\n{link}")

# ---------- Main ----------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot running...")
    app.run_polling()

if name == "main":
    main()
