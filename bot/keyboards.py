from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import CATEGORIES


def main_menu():
    return ReplyKeyboardMarkup([
        ['Search', 'Queue'],
        ['Random', 'Stats']
    ], resize_keyboard=True)


def book_actions(book_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Change Category", callback_data=f"cat_{book_id}")],
        [
            InlineKeyboardButton("Add to Queue", callback_data=f"queue_{book_id}"),
            InlineKeyboardButton("Start Reading", callback_data=f"read_{book_id}")
        ],
        [InlineKeyboardButton("Mark Finished", callback_data=f"done_{book_id}")]
    ])


def category_keyboard(book_id):
    buttons = [
        [InlineKeyboardButton(cat, callback_data=f"setcat_{book_id}_{cat}")]
        for cat in CATEGORIES.keys()
    ]
    buttons.append([InlineKeyboardButton("Cancel", callback_data=f"cancel_{book_id}")])
    return InlineKeyboardMarkup(buttons)


def browse_categories():
    buttons = [
        [InlineKeyboardButton(cat, callback_data=f"browse_{cat}")]
        for cat in CATEGORIES.keys()
    ]
    buttons.append([InlineKeyboardButton("Uncategorized", callback_data="browse_Uncategorized")])
    return InlineKeyboardMarkup(buttons)
