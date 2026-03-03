import io
import os
import sys
import googleapiclient.discovery
from googleapiclient.http import MediaIoBaseDownload

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import src.auth as auth

def get_drive_service():
    creds = auth.get_authenticated_service()
    return googleapiclient.discovery.build("drive", "v3", credentials=creds)

def list_files_in_folder(folder_id):
    """Lists files in the specified Drive folder."""
    service = get_drive_service()
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType)",
        pageSize=100
    ).execute()
    return results.get("files", [])

def download_file(file_id, output_path):
    """Downloads a file from Drive to a local path."""
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download Progress: {int(status.progress() * 100)}%")
    
    print(f"File downloaded to: {output_path}")
    return True

if __name__ == "__main__":
    # Test listing
    print("Testing Drive Listing...")
    files = list_files_in_folder(config.DRIVE_FOLDER_ID)
    for f in files:
        print(f"{f['name']} ({f['id']})")
