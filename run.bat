@echo off
cd /d "d:\funny shorts"
echo Starting Shorts Automation...
echo Logs will be saved to logs/
set PATH=%PATH%;%~dp0assets
python main.py
pause
