# Leibniz Book Bot

Telegram bot for cataloging ebooks. Forward PDF/EPUB files, get automatic metadata extraction and NLP categorization. Files stay on Telegram servers - bot only stores references.

## Setup

```bash
# Clone and enter directory
git clone https://github.com/YOUR_USERNAME/leibniz.git
cd leibniz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database
createdb leibniz

# Configure environment
cp .env.example .env
```

Edit `.env`:
- `BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather) on Telegram
- `DATABASE_URL` - Your PostgreSQL connection string

## Customization

Edit `config.py` to change categories:

```python
CATEGORIES = {
    "Fiction": "novel story fiction narrative",
    "Technical": "programming code software",
    # Add your own...
}
```

## Run

```bash
python -m bot.main
```

## Usage

- Forward PDF/EPUB files to catalog them
- `/start` - Welcome message
- `/browse` - Browse by category
- `/reading` - Currently reading
- Use keyboard buttons: Search, Queue, Random, Stats
