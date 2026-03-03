import os
import sys
from instagrapi import Client
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def get_client():
    """
    Initializes and returns an authenticated instagrapi Client.
    Uses session file to avoid repetitive logins.
    """
    cl = Client()
    cl.delay_range = [1, 3] # Add some delay between actions
    
    if os.path.exists(config.INSTA_SESSION_FILE):
        try:
            cl.load_settings(config.INSTA_SESSION_FILE)
            print("Instagram: Loaded session from file.")
        except Exception as e:
            print(f"Instagram: Could not load session: {e}")
            
    try:
        cl.login(config.INSTA_USERNAME, config.INSTA_PASSWORD)
        cl.dump_settings(config.INSTA_SESSION_FILE)
        print("Instagram: Login successful.")
        return cl
    except Exception as e:
        print(f"Instagram: Login failed: {e}")
        return None

def upload_reel(video_path, caption):
    """
    Uploads a video as an Instagram Reel.
    """
    cl = get_client()
    if not cl:
        print("Instagram: Authentication failed. Cannot upload Reel.")
        return None

    try:
        print(f"Instagram: Uploading Reel {video_path}...")
        # caption can include hashtags
        media = cl.clip_upload(video_path, caption)
        print(f"Instagram: Upload Complete! Media ID: {media.pk}")
        return media.pk
    except Exception as e:
        print(f"Instagram: Upload failed: {e}")
        return None

if __name__ == "__main__":
    # Test block
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if os.path.exists(test_file):
            upload_reel(test_file, "Test Reel Upload #automation")
        else:
            print(f"Test file not found: {test_file}")
