@echo off
cd /d "d:\funny shorts"

:: Create logs directory if it doesn't exist
if not exist logs mkdir logs

:loop
cls
echo =====================================================
echo [%DATE% %TIME%] Starting Shorts Automation Bot...
echo =====================================================

:: Run the bot. 
:: We are NOT redirecting output to file here so you can see it in this window.
:: If you want logs, the bot should handle logging internally or use a separate logging config.
set PATH=%PATH%;%~dp0assets
python main.py

echo.
echo =====================================================
echo [%DATE% %TIME%] WARNING: Bot has stopped or crashed!
echo Message: The bot process ended.
echo =====================================================
echo.
echo Restarting in 10 seconds...
echo Press CTRL+C to stop the loop.
echo.

:: Record the crash time to a file so you know it happened
echo [%DATE% %TIME%] CRASH DETECTED - Restarting >> logs\crash_history.log

timeout /t 10
goto loop
