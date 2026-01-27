# How to Deploy to Render.com (Free)

This guide explains how to host your bot on Render for free.

## Step 1: Push Code to GitHub
Render pulls code from GitHub. You need to upload your code there first.
1.  Create a repository on GitHub (e.g., `shorts-bot`).
2.  Upload all your files (`main.py`, `src/`, `Dockerfile`, `requirements.txt`, `config.py`, `token.json`, `assets/`).
    - **Note**: Uploading `token.json` and `config.py` to a PUBLIC repo is risky. Make the repo **PRIVATE**.

## Step 2: Create Web Service on Render
1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  **Settings**:
    - **Name**: `shorts-bot`
    - **Runtime**: `Docker` (Important! Check this)
    - **Region**: Any (e.g., Frankfurt)
    - **Instance Type**: `Free`
5.  **Environment Variables** (Optional, if you didn't upload config.py):
    - You can set `GEMINI_API_KEY`, etc. here if you modified the code to read env vars.
    - Since you likely uploaded `config.py`, you can skip this.
6.  **Secret Files (Critical!)**:
    - Since GitHub blocked `token.json` and `client_secrets.json` for safety, we must upload them directly here.
    - Click **"Add Secret File"**.
    - **Filename**: `token.json`. **Content**: Copy-paste everything from your local `token.json` file.
    - Click **"Add Secret File"** again.
    - **Filename**: `client_secrets.json`. **Content**: Copy-paste everything from your local `client_secrets.json` file.
    - Click **Create Web Service**.

## Step 3: Wait for Build
Render will read your `Dockerfile`, install FFmpeg, install Python, and start the bot.
- Once deployed, you will see a URL like: `https://shorts-bot.onrender.com`.
- Click it. It should say: **"I am alive! Bot is running."**

## Step 4: The "Wake Up" Trick (Critical!) ⏰
Render puts free apps to sleep after 15 minutes of silence. To stop this:

1.  Go to [uptimerobot.com](https://uptimerobot.com/) (It is free).
2.  Sign up.
3.  Click **Add New Monitor**.
4.  **Monitor Type**: `HTTP(s)`.
5.  **Friendly Name**: `My Bot`.
6.  **URL (or IP)**: Paste your Render URL (e.g., `https://shorts-bot.onrender.com`).
7.  **Monitoring Interval**: **5 minutes**.
8.  Click **Create Monitor**.

**Now, UptimeRobot will ping your bot every 5 minutes.**
This keeps the bot "awake" so it can check the time and upload your videos!
