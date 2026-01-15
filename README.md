# Leibniz Book Bot

A Telegram bot for cataloging and managing your ebook library. Forward book files to the bot, and it automatically extracts metadata, categorizes using NLP, and stores references for easy retrieval.

## How It Works

1. Forward a book file (PDF/EPUB) to the bot
2. Bot extracts metadata (title, author, pages)
3. Auto-categorizes using ML (sentence-transformers)
4. Saves metadata + Telegram file_id to PostgreSQL
5. Files stay on Telegram servers - no local storage needed

## Features

- Auto-categorization (Fiction, Technical, Philosophy, Science, History, Business, Self-Help)
- Search by title or author
- Reading queue management
- Track reading status (want to read, reading, finished)
- Browse by category
- Random book selection
- Library statistics

## Setup

### 1. Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow prompts
3. Copy the bot token

### 2. Setup Database

```bash
# Install PostgreSQL if needed
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb leibniz
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your BOT_TOKEN
```

### 4. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Run

```bash
python -m bot.main
```

## Usage

| Command | Description |
|---------|-------------|
| `/start` | Show welcome message |
| `/browse` | Browse books by category |
| `/reading` | Show currently reading |
| `Search` | Search by title/author |
| `Queue` | View reading queue |
| `Random` | Get a random book |
| `Stats` | View library statistics |

## Project Structure

```
leibniz/
├── bot/
│   ├── handlers.py      # Message/command handlers
│   ├── keyboards.py     # Button layouts
│   └── main.py          # Entry point
├── services/
│   ├── nlp.py           # ML categorization
│   └── metadata.py      # PDF/EPUB metadata extraction
├── db/
│   ├── models.py        # SQLAlchemy models
│   └── operations.py    # Database operations
├── config.py
└── requirements.txt
```

## License

MIT
