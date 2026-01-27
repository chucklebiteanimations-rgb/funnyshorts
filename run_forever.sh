#!/bin/bash

# Navigate to script directory
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

echo "====================================================="
echo "Starting Shorts Automation Bot (Linux)..."
echo "====================================================="

while true; do
    # Add assets to PATH (in case local binaries are used)
    export PATH=$PATH:$(pwd)/assets

    # Run the bot
    python3 main.py

    exit_code=$?
    
    echo ""
    echo "====================================================="
    echo "WARNING: Bot has stopped or crashed! (Exit Code: $exit_code)"
    echo "====================================================="
    echo "Restarting in 10 seconds..."
    echo "Press CTRL+C to stop."
    echo ""

    # Log crash
    echo "[$(date)] CRASH DETECTED - Exit Code: $exit_code" >> logs/crash_history.log

    sleep 10
done
