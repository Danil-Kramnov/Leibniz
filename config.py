import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

CATEGORIES = {
    "Fiction": "novel story fiction narrative plot character literary",
    "Technical": "programming code software engineering computer algorithm",
    "Philosophy": "philosophy ethics metaphysics logic existence thought",
    "Science": "science physics biology chemistry research theory",
    "History": "history historical war civilization ancient modern",
    "Business": "business management economics finance marketing strategy",
    "Self-Help": "self-help motivation productivity habits personal"
}
