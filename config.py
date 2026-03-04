import os

# Paths
# Paths
# Get the directory where config.py is located (project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHORTS_DIR = os.path.join(BASE_DIR, "shorts")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SRC_DIR = os.path.join(BASE_DIR, "src")

# Database
DB_PATH = os.path.join(SRC_DIR, "automation.db")

# YouTube API
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secrets.json")
# This is the writable path we will ALWAYS save to on Render
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

# Render Secret Files Support (Read-Only)
SECRET_TOKEN_FILE = "/etc/secrets/token.json" if os.path.exists("/etc/secrets/token.json") else None

if os.path.exists("/etc/secrets/client_secrets.json"):
    CLIENT_SECRETS_FILE = "/etc/secrets/client_secrets.json"
    
# If the local token doesn't exist but the secret one does, we load from secret initially
if not os.path.exists(TOKEN_FILE) and SECRET_TOKEN_FILE:
    TOKEN_FILE = SECRET_TOKEN_FILE

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/drive.readonly"
]

DRIVE_FOLDER_ID = "16lN0H-oSl6MUSFbkgR6hKZD4oA1Ylo4V"

# Instagram
INSTA_USERNAME = "chuckle.bites"
INSTA_PASSWORD = "amit.@#18"
INSTA_SESSION_FILE = os.path.join(BASE_DIR, "instagrapi_session.json")

# Schedule & Timezone
TIMEZONE = "Asia/Kolkata" # Indian Standard Time
UPLOADS_PER_DAY = 3
UPLOAD_TIMES = ["10:00", "14:00", "19:00"] # 24-hour format

# Telegram
TELEGRAM_BOT_TOKEN = "8262698363:AAEapp3_MsIFC6XkdIKmnomyg3IVTE4eYtk"
TELEGRAM_CHAT_ID = "5593260304"

# AI
GEMINI_API_KEY = "YOUR_GEMINI_KEY_HERE"
