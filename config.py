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
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

# Render Secret Files Support
# Render mounts secret files at /etc/secrets/filename
if not os.path.exists(CLIENT_SECRETS_FILE) and os.path.exists("/etc/secrets/client_secrets.json"):
    CLIENT_SECRETS_FILE = "/etc/secrets/client_secrets.json"
    
if not os.path.exists(TOKEN_FILE) and os.path.exists("/etc/secrets/token.json"):
    TOKEN_FILE = "/etc/secrets/token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Bot Settings
UPLOADS_PER_DAY = 3
UPLOAD_TIMES = ["10:00", "14:00", "19:00"] # 24-hour format

# Telegram
TELEGRAM_BOT_TOKEN = "8262698363:AAEapp3_MsIFC6XkdIKmnomyg3IVTE4eYtk"
TELEGRAM_CHAT_ID = "5593260304"

# AI
GEMINI_API_KEY = "AIzaSyCwxl_fxz7txPirUWgG-2JGQYFqVP-4nTs"
