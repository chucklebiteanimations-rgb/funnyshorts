import schedule
import time
import os
import sys
import threading
import asyncio
from datetime import datetime

import config
import src.database as database
import src.scheduler as scheduler
import src.processor as processor
import src.uploader as uploader
import src.ai_content as ai_content
import src.bot as bot

def job():
    print(f"[{datetime.now()}] Job started...")
    
    # 0. Check if Paused (Telegram Stop)
    if bot.is_paused():
        print(f"[{datetime.now()}] Job skipped (PAUSED).")
        return

    # 1. Check schedule/quota
    if not scheduler.check_schedule():
        return

    # 2. Get content
    day_folder, files = scheduler.get_current_day_number()
    if not day_folder:
        print("No content found.")
        return

    print(f"Processing {day_folder}...")
    
    # Upload one video per job execution
    # Find first non-uploaded video in this folder
    target_file = None
    for f in files:
        if not database.is_video_uploaded(f):
            target_file = f
            break
            
    if not target_file:
        print(f"All files in {day_folder} uploaded?")
        return

    full_path = os.path.join(config.SHORTS_DIR, day_folder, target_file)
    print(f"Selected: {full_path}")
    
    # 3. Process (Convert if needed, Watermark)
    # If it is image, convert. If video, just watermark?
    # Logic: Always produce a 'ready' path
    ready_path = os.path.join(config.BASE_DIR, "shorts", "temp_ready_" + target_file + ".mp4")
    
    processing_success = False
    if target_file.lower().endswith(('.jpg', '.jpeg', '.png')):
        # Convert Image -> Video + Watermark steps
        # Optimization: processor.create_video_from_image handles create. Watermark logic separate.
        # Let's assume create_video handles everything or we chain.
        
        # Temp 1
        temp_video = os.path.join(config.BASE_DIR, "shorts", "temp_raw_" + target_file + ".mp4")
        if processor.create_video_from_image(full_path, temp_video):
            # Watermark (Text based "ChuckleBites")
            # We pass dummy path as watermark_path since processor ignores it
            processing_success = processor.add_watermark(temp_video, "dummy", ready_path)
            
            # Cleanup temp 1
            if os.path.exists(temp_video):
                os.remove(temp_video)
                
    elif target_file.lower().endswith('.mp4'):
        # Just watermark (Text based "ChuckleBites")
        processing_success = processor.add_watermark(full_path, "dummy", ready_path)

    if not processing_success:
        print("Processing failed.")
        return

    # 4. Generate Metadata
    title = ai_content.generate_title(target_file)
    desc, tags = ai_content.get_description_and_tags(title)
    
    # 5. Upload
    print(f"Uploading as: {title}")
    video_id = uploader.upload_video(ready_path, title, desc, tags)
    
    if video_id:
        print(f"SUCCESS: {video_id}")
        database.log_upload(target_file, day_folder, "UPLOADED", video_id)
        
        # Notify via Telegram
        short_url = f"https://youtube.com/shorts/{video_id}"
        msg = f"✅ <b>Upload Success!</b>\n\nTitle: {title}\nFile: {target_file}\nLink: {short_url}"
        bot.send_telegram_message(msg)
        
        # Cleanup ready file if it was temp
        if "temp_ready_" in ready_path and os.path.exists(ready_path):
            os.remove(ready_path)
    else:
        print("Upload Failed.")

def run_scheduler_loop():
    print("Scheduler running with Catch-up Logic...")
    
    # Sort times just in case
    times = sorted(config.UPLOAD_TIMES)
    
    while True:
        try:
            # 1. Get current status
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            
            # 2. Calculate "Expected Uploads" for today
            # Example: times=["10:00", "14:00", "19:00"]
            # If now is 12:00, expected = 1 (10:00 passed)
            # If now is 15:00, expected = 2 (10:00, 14:00 passed)
            
            expected_uploads = 0
            for t in times:
                if current_time_str >= t:
                    expected_uploads += 1
            
            # 3. Get "Actual Uploads"
            actual_uploads = database.get_uploads_today_count()
            
            # 4. Compare
            if actual_uploads < expected_uploads:
                print(f"[{current_time_str}] Catch-up needed! Expected: {expected_uploads}, Actual: {actual_uploads}. Running job...")
                job()
                # Wait a bit after job to avoid rapid-fire if job fails quickly
                time.sleep(60) 
                continue
            
            # 5. Normal Schedule Check (for exact time hit)
            # Actually, the logic above covers "exact time" too because 
            # as soon as clock hits 10:00, expected becomes 1, actual is 0 -> Trigger.
            
            # So we just sleep and check again.
            # print(f"[{current_time_str}] On track. Expected: {expected_uploads}, Actual: {actual_uploads}. Sleeping...")
            schedule.run_pending() # Keep this if other libraries use 'schedule'
            time.sleep(30) # Check every 30 seconds
            
        except Exception as e:
            print(f"Scheduler Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    database.init_db()
    
    # Start Scheduler in separate thread
    sched_thread = threading.Thread(target=run_scheduler_loop)
    sched_thread.daemon = True
    sched_thread.start()
    
    # Run Bot
    # Pass 'job' as callback for /upload_now
    print("Starting System...")
    try:
        bot.run_bot(job)
    except KeyboardInterrupt:
        print("Stopping...")
