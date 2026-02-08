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

# ---------- Commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi!\nSend me a video link.\nI will give you download options."
    )

# ---------- Handle text / link ----------
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🎥 Video", callback_data="video"),
            InlineKeyboardButton("🎵 Audio", callback_data="audio"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose download type 👇",
        reply_markup=reply_markup
    )

# ---------- Button handler ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "video":
        await query.edit_message_text("🎥 Video download started...")
    elif query.data == "audio":
        await query.edit_message_text("🎵 Audio download started...")

# ---------- MAIN ----------
def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in environment variables")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot running...")
    app.run_polling()

# ⚠️ এই লাইনটাই আগে ভুল ছিল
if name == "main":
    main()
