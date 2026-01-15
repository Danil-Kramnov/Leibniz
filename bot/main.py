from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers import (
    start, handle_document, handle_text, handle_callback,
    browse_command, reading_command
)
from config import BOT_TOKEN


def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not set in .env file")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("browse", browse_command))
    app.add_handler(CommandHandler("reading", reading_command))

    # Document handler (for book files)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Text message handler (for menu buttons and search)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Callback handler (for inline buttons)
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Leibniz bot started!", flush=True)
    print("Press Ctrl+C to stop", flush=True)
    app.run_polling()


if __name__ == '__main__':
    main()
