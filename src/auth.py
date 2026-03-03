import os
import sys

# Add parent directory to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import config
# Import bot to send notifications.
# Note: config must be fully loaded before this import if it uses config values at module level.
import src.bot as bot 

def get_authenticated_service():
    """
    Authenticates with YouTube API and returns the credentials object.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(config.TOKEN_FILE):
        print(f"Loading credentials from {config.TOKEN_FILE}...")
        try:
            creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
        except Exception as e:
            print(f"Error loading token.json from {config.TOKEN_FILE}: {e}")
            creds = None
    else:
        print(f"Token file NOT FOUND at: {config.TOKEN_FILE}")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Credentials expired, attempting to refresh...", flush=True)
            try:
                creds.refresh(Request())
                print("Token refresh successful!")
            except Exception as e:
                print(f"Error refreshing token: {e}", flush=True)
                msg = f"🚨 **CRITICAL ALERT** 🚨\n\nGoogle Token Refresh Failed!\nError: {e}\n\nPlease update your `token.json` on Render with a newly generated one."
                bot.send_telegram_message(msg)
                creds = None

        if not creds:
           print(f"No valid credentials. Action Required alert sent.", flush=True)
           
           # Alert user that manual interaction is needed
           msg = "⚠️ **Action Required** ⚠️\n\nBot needs to log in to Google. If this is a VPS, you must do this on your local PC and upload the `token.json` file."
           bot.send_telegram_message(msg)
           
           if not os.path.exists(config.CLIENT_SECRETS_FILE):
               raise FileNotFoundError(f"Client secrets file not found at {config.CLIENT_SECRETS_FILE}. Please place your 'client_secrets.json' in 'd:\\funny shorts\\'.")

           try:
               flow = InstalledAppFlow.from_client_secrets_file(
                   config.CLIENT_SECRETS_FILE, config.SCOPES
               )
               try:
                   # Use port 8080 by default since port 80 often requires admin rights on Windows
                   print("Starting local server on port 8080...", flush=True)
                   creds = flow.run_local_server(port=8080, open_browser=True)
               except Exception as e:
                   print(f"Port 8080 failed: {e}. Trying port 8888...", flush=True)
                   creds = flow.run_local_server(port=8888, open_browser=True)
           except Exception as e:
               print(f"Manual Login Failed: {e}")
               bot.send_telegram_message(f"❌ Manual Login Failed: {e}")
               raise e

        # Save the credentials for the next run
        print(f"Saving new credentials to {config.TOKEN_FILE}...", flush=True)
        with open(config.TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds

if __name__ == "__main__":
    try:
        creds = get_authenticated_service()
        print("Authentication successful!", flush=True)
    except Exception as e:
        print(f"Authentication failed: {e}", flush=True)
