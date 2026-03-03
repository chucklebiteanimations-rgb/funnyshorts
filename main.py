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
import src.keep_alive as keep_alive

import pytz

import src.drive_manager as drive_manager

def job():
    print(f"[{datetime.now()}] Job started (Drive-Based Workflow)...")
    
    # 0. Check if Paused (Telegram Stop)
    if bot.is_paused():
        print(f"[{datetime.now()}] Job skipped (PAUSED).")
        return

    # 1. Check schedule/quota
    if not scheduler.check_schedule():
        return

    # 2. Get content from Drive
    print("Drive: Checking for new content...")
    drive_files = drive_manager.list_files_in_folder(config.DRIVE_FOLDER_ID)
    
    target_drive_file = None
    for df in drive_files:
        if not database.is_drive_video_uploaded(df['id']):
            target_drive_file = df
            break
            
    if not target_drive_file:
        print("No new content found on Google Drive.")
        return

    print(f"Drive: Selected {target_drive_file['name']} ({target_drive_file['id']})")
    
    # Define local paths
    local_raw_path = os.path.join(config.BASE_DIR, "temp_download_" + target_drive_file['name'])
    local_ready_path = os.path.join(config.BASE_DIR, "temp_ready_" + target_drive_file['name'].split('.')[0] + ".mp4")

    # 3. Download from Drive
    if not drive_manager.download_file(target_drive_file['id'], local_raw_path):
        print("Drive: Download failed.")
        return

    # 4. Process (Convert if needed, Watermark)
    processing_success = False
    try:
        if target_drive_file['name'].lower().endswith(('.jpg', '.jpeg', '.png')):
            temp_video = os.path.join(config.BASE_DIR, "temp_conv_" + target_drive_file['name'].split('.')[0] + ".mp4")
            if processor.create_video_from_image(local_raw_path, temp_video):
                processing_success = processor.add_watermark(temp_video, "dummy", local_ready_path)
                if os.path.exists(temp_video): os.remove(temp_video)
        else:
            # Assume it's a video file
            processing_success = processor.add_watermark(local_raw_path, "dummy", local_ready_path)
    except Exception as e:
        print(f"Processing Error: {e}")

    if not processing_success:
        print("Processing failed.")
        # Cleanup raw download even if failed
        if os.path.exists(local_raw_path): os.remove(local_raw_path)
        return

    # 5. Generate Metadata
    title = ai_content.generate_title(target_drive_file['name'])
    desc, tags = ai_content.get_description_and_tags(title)
    
    # 6. Upload to YouTube
    print(f"YouTube: Uploading as: {title}")
    yt_video_id = uploader.upload_video(local_ready_path, title, desc, tags)
    
    # 7. Upload to Instagram
    print(f"Instagram: Uploading as Reel...")
    insta_media_id = None
    try:
        import src.insta_uploader as insta_uploader
        ig_caption = f"{title}\n\n{tags}"
        insta_media_id = insta_uploader.upload_reel(local_ready_path, ig_caption)
    except Exception as e:
        print(f"Instagram Upload Error: {e}")

    # 8. Logging & Notifications
    if yt_video_id or insta_media_id:
        database.log_upload(target_drive_file['name'], 
                           "UPLOADED" if yt_video_id else "FAILED", 
                           drive_id=target_drive_file['id'],
                           yt_id=yt_video_id,
                           insta_status="UPLOADED" if insta_media_id else "FAILED", 
                           insta_id=insta_media_id)
        
        # Notify via Telegram
        short_url = f"https://youtube.com/shorts/{yt_video_id}" if yt_video_id else "N/A"
        ig_status = "✅ Success" if insta_media_id else "❌ Failed"
        
        msg = (
            f"🚀 <b>New Upload From Drive!</b>\n\n"
            f"Title: {title}\n"
            f"File: {target_drive_file['name']}\n\n"
            f"📺 YouTube: {short_url}\n"
            f"📸 Instagram: {ig_status}"
        )
        bot.send_telegram_message(msg)
    else:
        print("All Uploads Failed.")

    # 9. FINAL CLEANUP (Crucial for Render)
    print("Cleanup: Removing temporary files...")
    if os.path.exists(local_raw_path):
        os.remove(local_raw_path)
    if os.path.exists(local_ready_path):
        os.remove(local_ready_path)

def run_scheduler_loop():
    print(f"Scheduler running with IST ({config.TIMEZONE}) Catch-up Logic...")
    
    times = sorted(config.UPLOAD_TIMES)
    tz = pytz.timezone(config.TIMEZONE)
    
    while True:
        try:
            # 1. Get current time in IST
            now_ist = datetime.now(tz)
            current_time_str = now_ist.strftime("%H:%M")
            
            # 2. Daily Quota Check
            expected_uploads = 0
            for t in times:
                if current_time_str >= t:
                    expected_uploads += 1
            
            actual_uploads = database.get_uploads_today_count()
            
            if actual_uploads < expected_uploads:
                print(f"[{current_time_str} IST] Catch-up needed! Expected: {expected_uploads}, Actual: {actual_uploads}.")
                job()
                time.sleep(60) 
                continue
            
            schedule.run_pending() 
            time.sleep(30) 
            
        except Exception as e:
            print(f"Scheduler Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    database.init_db()

    # Start Scheduler in separate thread (Background Worker)
    sched_thread = threading.Thread(target=run_scheduler_loop)
    sched_thread.daemon = True
    sched_thread.start()
    
    # Start Telegram Poll in separate thread
    # Pass 'job' as callback for /upload_now
    # We use a lambda or partial to pass arguments to the target function
    bot_thread = threading.Thread(target=lambda: bot.run_bot(job))
    bot_thread.daemon = True
    bot_thread.start()

    print("Background threads started. Launching Web Server...")

    # Run Web Server in MAIN THREAD (Blocking)
    # This must be the last thing, as it blocks forever.
    # It ensures Render sees the app as "listening on port X".
    # This blocks forever.
    keep_alive.run()
