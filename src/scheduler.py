import os
import sys
import datetime
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import src.database as database

def get_current_day_number():
    """
    Calculates the current 'Day_X' based on a start date or just continuous count.
    For this implementation, let's assume we map today's date to a day number.
    Or simpler: We look for the first Day folder that has PENDING items or hasn't been fully uploaded.
    
    Plan: Check DB for last uploaded 'Day_X'.
    If today's quota (3) is full, we stop.
    If not, we pick the current working day.
    """
    
    # Simple logic: Find the first Day_X folder that isn't fully marked as uploaded or has files.
    # But user put folders Day_1 ... Day_178.
    
    # Let's start with Day_1 and check if it's done. 
    # How do we know if Day_1 is done?
    # We can check if all files in Day_1 are in the 'uploads' table with status 'UPLOADED'.
    
    # Optimized approach: Maintain a 'current_day' in a state file or just scan.
    # Scanning 178 folders is fast enough.
    
    # Sort folders numerically
    try:
        folders = [f for f in os.listdir(config.SHORTS_DIR) if f.startswith("Day_") and os.path.isdir(os.path.join(config.SHORTS_DIR, f))]
        
        def extract_day_num(folder_name):
            try:
                return int(folder_name.split("_")[1])
            except:
                return 999999
                
        folders.sort(key=extract_day_num)
        
        for folder in folders:
            folder_path = os.path.join(config.SHORTS_DIR, folder)
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4'))]
            
            if not files:
                continue
                
            # Check if all files in this folder are uploaded
            all_uploaded = True
            for f in files:
                if not database.is_video_uploaded(f):
                    all_uploaded = False
                    break
            
            if not all_uploaded:
                print(f"Current working folder: {folder}")
                return folder, files

        print("All Day folders appear to be completed!")
        return None, None
        
    except Exception as e:
        print(f"Error finding current day: {e}")
        return None, None

def check_schedule():
    """
    Checks if we should upload now.
    Returns: True if we should upload, False otherwise.
    """
    # Check max uploads per day
    uploads_today = database.get_uploads_today_count()
    if uploads_today >= config.UPLOADS_PER_DAY:
        print(f"Daily quota reached ({uploads_today}/{config.UPLOADS_PER_DAY}). Waiting for tomorrow.")
        return False
        
    # Check time window? 
    # User wanted "Robust scheduling".
    # Simple approach: If we haven't hit quota, upload immediately (catch-up) 
    # OR strictly wait for times.
    # Implementation Plan said "Logic for 3 uploads/day at fixed times".
    
    now = datetime.datetime.now()
    current_time_str = now.strftime("%H:%M")
    
    # For now, let's just return True if quota not met, to process backlog.
    # Or strict:
    # allowed_times = config.UPLOAD_TIMES
    # But handling "exact minute" in a loop is flaky.
    
    # Better: If quota not met, we are "eligible".
    return True

if __name__ == "__main__":
    day, files = get_current_day_number()
    print(f"Day: {day}, Files: {files}")
    print(f"Should upload? {check_schedule()}")
