from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import main_menu, book_actions, category_keyboard, browse_categories
from services.nlp import categorize_book
from services.metadata import extract_metadata
from db.operations import (
    save_book, search_books, get_book, get_reading_queue,
    update_status, get_stats, update_book_category, get_random_book,
    get_books_by_category, book_exists, get_currently_reading
)
from db.models import StatusEnum


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Leibniz Book Library\n\n"
        "Forward me book files (PDF, EPUB) to catalog them!\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/browse - Browse by category\n"
        "/reading - Show currently reading",
        reply_markup=main_menu()
    )


async def browse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Select a category:",
        reply_markup=browse_categories()
    )


async def reading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    books = get_currently_reading(user_id)

    if not books:
        await update.message.reply_text("You're not currently reading any books.")
        return

    await update.message.reply_text(f"Currently reading ({len(books)} books):")
    for book in books[:10]:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=book.file_id,
            caption=f"{book.title}\nby {book.author or 'Unknown'}\n[{book.category}]",
            reply_markup=book_actions(book.id)
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    filename = document.file_name or "unknown"

    # Check supported formats
    supported = ['.pdf', '.epub', '.mobi', '.azw3']
    if not any(filename.lower().endswith(ext) for ext in supported):
        await update.message.reply_text(
            f"Unsupported format. Please send: {', '.join(supported)}"
        )
        return

    # Check if already exists
    if book_exists(document.file_unique_id):
        await update.message.reply_text("This book is already in your library!")
        return

    status_msg = await update.message.reply_text("Processing book...")

    # Get Telegram file references
    file_id = document.file_id
    file_unique_id = document.file_unique_id
    file_size = document.file_size

    # Download to memory for metadata extraction
    try:
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
    except Exception as e:
        await status_msg.edit_text(f"Failed to download file: {e}")
        return

    # Extract metadata
    title, author, pages, format = extract_metadata(bytes(file_bytes), filename)

    if not title:
        title = filename

    # Auto-categorize
    await status_msg.edit_text("Categorizing...")
    category, confidence = categorize_book(title, author)

    # Save to DB
    book_id = save_book(
        title=title,
        author=author,
        file_id=file_id,
        file_unique_id=file_unique_id,
        format=format,
        page_count=pages,
        file_size=file_size,
        category=category,
        confidence=confidence
    )

    # Confirm
    await status_msg.edit_text(
        f"Added: {title}\n"
        f"Author: {author or 'Unknown'}\n"
        f"Category: {category} ({confidence:.0%})\n"
        f"Pages: {pages or 'N/A'}",
        reply_markup=book_actions(book_id)
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'Search':
        await update.message.reply_text("Enter search term:")
        context.user_data['awaiting_search'] = True

    elif text == 'Queue':
        user_id = update.effective_user.id
        books = get_reading_queue(user_id)

        if not books:
            await update.message.reply_text("Your reading queue is empty!")
            return

        await update.message.reply_text(f"Reading queue ({len(books)} books):")
        for book in books[:10]:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=book.file_id,
                caption=f"{book.title}\nby {book.author or 'Unknown'}\n[{book.category}]",
                reply_markup=book_actions(book.id)
            )

    elif text == 'Random':
        book = get_random_book()
        if not book:
            await update.message.reply_text("No books in library yet!")
            return

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=book.file_id,
            caption=f"{book.title}\nby {book.author or 'Unknown'}\n[{book.category}]",
            reply_markup=book_actions(book.id)
        )

    elif text == 'Stats':
        user_id = update.effective_user.id
        total, reading, finished, queue = get_stats(user_id)
        await update.message.reply_text(
            f"Library Stats\n\n"
            f"Total books: {total}\n"
            f"Currently reading: {reading}\n"
            f"Finished: {finished}\n"
            f"In queue: {queue}"
        )

    elif context.user_data.get('awaiting_search'):
        context.user_data['awaiting_search'] = False
        books = search_books(text)

        if not books:
            await update.message.reply_text(f"No books found for '{text}'")
            return

        await update.message.reply_text(f"Found {len(books)} book(s):")
        for book in books[:5]:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=book.file_id,
                caption=f"{book.title}\nby {book.author or 'Unknown'}\n[{book.category}]",
                reply_markup=book_actions(book.id)
            )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = update.effective_user.id

    if data.startswith('cat_'):
        book_id = int(data.split('_')[1])
        await query.edit_message_reply_markup(reply_markup=category_keyboard(book_id))

    elif data.startswith('setcat_'):
        parts = data.split('_')
        book_id = int(parts[1])
        category = '_'.join(parts[2:])  # Handle categories with underscores
        update_book_category(book_id, category)
        book = get_book(book_id)
        await query.edit_message_caption(
            caption=f"{book.title}\nby {book.author or 'Unknown'}\n[{category}]",
            reply_markup=book_actions(book_id)
        )

    elif data.startswith('cancel_'):
        book_id = int(data.split('_')[1])
        book = get_book(book_id)
        await query.edit_message_reply_markup(reply_markup=book_actions(book_id))

    elif data.startswith('queue_'):
        book_id = int(data.split('_')[1])
        update_status(book_id, user_id, StatusEnum.want_to_read)
        book = get_book(book_id)
        await query.edit_message_caption(
            caption=f"{book.title}\nby {book.author or 'Unknown'}\n[{book.category}]\n\n[Added to queue]",
            reply_markup=book_actions(book_id)
        )

    elif data.startswith('read_'):
        book_id = int(data.split('_')[1])
        update_status(book_id, user_id, StatusEnum.reading)
        book = get_book(book_id)
        await query.edit_message_caption(
            caption=f"{book.title}\nby {book.author or 'Unknown'}\n[{book.category}]\n\n[Currently reading]",
            reply_markup=book_actions(book_id)
        )

    elif data.startswith('done_'):
        book_id = int(data.split('_')[1])
        update_status(book_id, user_id, StatusEnum.finished)
        book = get_book(book_id)
        await query.edit_message_caption(
            caption=f"{book.title}\nby {book.author or 'Unknown'}\n[{book.category}]\n\n[Finished]",
            reply_markup=book_actions(book_id)
        )

    elif data.startswith('browse_'):
        category = data.replace('browse_', '')
        books = get_books_by_category(category)

        if not books:
            await query.edit_message_text(f"No books in '{category}' category.")
            return

        await query.edit_message_text(f"Books in '{category}' ({len(books)}):")
        for book in books[:10]:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=book.file_id,
                caption=f"{book.title}\nby {book.author or 'Unknown'}",
                reply_markup=book_actions(book.id)
            )
