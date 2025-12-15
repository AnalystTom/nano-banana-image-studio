import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
DATABASE_URL = 'sqlite+aiosqlite:///./database.db'
STATIC_DIR = '/home/user/backend/static'
IMAGES_DIR = f'{STATIC_DIR}/images'

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
