import os

# Paths
BASE_DIR = r"d:\funny shorts"
SHORTS_DIR = os.path.join(BASE_DIR, "shorts")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SRC_DIR = os.path.join(BASE_DIR, "src")

# Database
DB_PATH = os.path.join(SRC_DIR, "automation.db")

# YouTube API
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secrets.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Bot Settings
UPLOADS_PER_DAY = 3
UPLOAD_TIMES = ["10:00", "14:00", "19:00"] # 24-hour format

# Telegram
TELEGRAM_BOT_TOKEN = "8262698363:AAEapp3_MsIFC6XkdIKmnomyg3IVTE4eYtk"
TELEGRAM_CHAT_ID = "5593260304"

# AI
GEMINI_API_KEY = "AIzaSyCwxl_fxz7txPirUWgG-2JGQYFqVP-4nTs"
