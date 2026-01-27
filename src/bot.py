import os
import sys
import asyncio
from telegram import Update, BotCommand, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import src.database as database

import glob
import threading

def send_telegram_message(message):
    """Sends a one-off message to the admin."""
    if not hasattr(config, "TELEGRAM_CHAT_ID") or not config.TELEGRAM_CHAT_ID or config.TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("Cannot send notification: Chat ID missing.")
        return

    async def _send():
        try:
            bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
            await bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=message)
        except Exception as e:
            print(f"Telegram Notification Failed: {e}")

    try:
        asyncio.run(_send())
    except Exception as e:
        print(f"Asyncio Error in notification: {e}")

# Global control flag
PAUSED = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global PAUSED
    PAUSED = False
    await update.message.reply_text('Bot Started & Resumed! Automation is ACTIVE.')

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global PAUSED
    PAUSED = True
    await update.message.reply_text('Bot STOPPED! Future uploads are paused.')

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global PAUSED
    PAUSED = False
    await update.message.reply_text('Bot RESUMED! Back to work.')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uploads_today = database.get_uploads_today_count()
    state = "PAUSED 🛑" if PAUSED else "RUNNING ✅"
    
    # Get next scheduled time (simple check of config)
    # Ideally scheduler gives this info, but for now static
    next_time = "Check Console" 
    
    msg = (
        f"State: {state}\n"
        f"Uploads Today: {uploads_today}/{config.UPLOADS_PER_DAY}\n"
        f"Next Batch: {config.UPLOAD_TIMES}"
    )
    await update.message.reply_text(msg)

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Find latest log file
    try:
        list_of_files = glob.glob(os.path.join(config.LOGS_DIR, '*.log')) # Assuming main.py writes .log files or we just cat console output?
        # Actually main.py uses print, so no file logs unless run.bat redirects.
        # run.bat echoes "Logs will be saved to logs/", implying output redirection?
        # Let's check run.bat. It just says "echo Logs will be saved...". 
        # It doesn't actually redirect: "python main.py".
        # We need to rely on a 'latest_error' global or just say "No log file configured".
        
        # But for now, let's just return a placeholder or check if any file exists.
        await update.message.reply_text("Log reading not fully configured (Console Output Only).")
    except Exception as e:
         await update.message.reply_text(f"Error fetching logs: {e}")

async def upload_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if PAUSED:
        await update.message.reply_text("Cannot upload: Bot is PAUSED. Use /resume first.")
        return

    if not context.bot_data.get('upload_callback'):
        await update.message.reply_text("Upload callback not configured.")
        return
        
    await update.message.reply_text("Triggering immediate upload... 🚀")
    
    callback = context.bot_data['upload_callback']
    threading.Thread(target=callback).start()

def is_paused():
    return PAUSED

async def post_init(application):
    """
    Sets the bot info and command list on startup.
    """
    commands = [
        BotCommand("start", "Start the bot & Show Chat ID"),
        BotCommand("status", "Show current status & stats"),
        BotCommand("stop", "Pause automation"),
        BotCommand("resume", "Resume automation"),
        BotCommand("upload_now", "Force immediate upload"),
        BotCommand("logs", "Show latest error logs")
    ]
    await application.bot.set_my_commands(commands)
    print("Bot commands menu updated!")

def run_bot(upload_callback=None):
    if not hasattr(config, "TELEGRAM_BOT_TOKEN") or config.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Telegram bot token not set. Skipping bot.")
        return

    # Use existing timeouts, add post_init
    app = (
        ApplicationBuilder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .read_timeout(60)
        .get_updates_read_timeout(60)
        .connect_timeout(60)
        .post_init(post_init)
        .build()
    )
    
    app.bot_data['upload_callback'] = upload_callback

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("resume", resume))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("logs", logs_command))
    app.add_handler(CommandHandler("upload_now", upload_now))

    print("Telegram Bot is polling...")
    app.run_polling()

if __name__ == "__main__":
    # Asyncio run
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
