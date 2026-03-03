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
    ready_path = os.path.join(config.BASE_DIR, "shorts", "temp_ready_" + target_file + ".mp4")
    
    processing_success = False
    if target_file.lower().endswith(('.jpg', '.jpeg', '.png')):
        temp_video = os.path.join(config.BASE_DIR, "shorts", "temp_raw_" + target_file + ".mp4")
        if processor.create_video_from_image(full_path, temp_video):
            processing_success = processor.add_watermark(temp_video, "dummy", ready_path)
            if os.path.exists(temp_video): os.remove(temp_video)
                
    elif target_file.lower().endswith('.mp4'):
        processing_success = processor.add_watermark(full_path, "dummy", ready_path)

    if not processing_success:
        print("Processing failed.")
        return

    # 4. Generate Metadata
    title = ai_content.generate_title(target_file)
    desc, tags = ai_content.get_description_and_tags(title)
    
    # 5. Upload to YouTube
    print(f"YouTube: Uploading as: {title}")
    yt_video_id = uploader.upload_video(ready_path, title, desc, tags)
    
    # 6. Upload to Instagram
    print(f"Instagram: Uploading as Reel...")
    insta_media_id = None
    try:
        import src.insta_uploader as insta_uploader
        # Use title + hashtags for IG caption
        ig_caption = f"{title}\n\n{tags}"
        insta_media_id = insta_uploader.upload_reel(ready_path, ig_caption)
    except Exception as e:
        print(f"Instagram Upload Error: {e}")

    # 7. Logging & Notifications
    if yt_video_id or insta_media_id:
        database.log_upload(target_file, day_folder, 
                           "UPLOADED" if yt_video_id else "FAILED", yt_video_id,
                           "UPLOADED" if insta_media_id else "FAILED", insta_media_id)
        
        # Notify via Telegram
        short_url = f"https://youtube.com/shorts/{yt_video_id}" if yt_video_id else "N/A"
        ig_status = "✅ Success" if insta_media_id else "❌ Failed"
        
        msg = (
            f"🚀 <b>New Upload!</b>\n\n"
            f"Title: {title}\n"
            f"File: {target_file}\n\n"
            f"📺 YouTube: {short_url}\n"
            f"📸 Instagram: {ig_status}"
        )
        bot.send_telegram_message(msg)
        
        # Cleanup
        if "temp_ready_" in ready_path and os.path.exists(ready_path):
            os.remove(ready_path)
    else:
        print("All Uploads Failed.")

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
