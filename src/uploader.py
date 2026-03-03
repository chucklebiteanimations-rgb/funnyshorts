import os
import sys
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import src.auth as auth
import src.database as database

def upload_video(file_path, title, description, tags, category_id="23"):
    """
    Uploads a video to YouTube.
    category_id="23" is typically Comedy.
    """
    creds = auth.get_authenticated_service()
    if not creds:
        print("Authentication failed. Cannot upload.")
        return None

    try:
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        print(f"Uploading {file_path}...")
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags.split() if isinstance(tags, str) else tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public", # or 'private' for testing
                "selfDeclaredMadeForKids": False
            }
        }

        # Chunk size 4MB
        media = MediaFileUpload(file_path, chunksize=4*1024*1024, resumable=True)

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")

        print(f"Upload Complete! Video ID: {response['id']}")
        return response['id']

    except googleapiclient.errors.HttpError as e:
        print(f"An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Test upload (Optional)
    pass
