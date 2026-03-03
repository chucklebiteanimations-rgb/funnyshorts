# The Absolute Beginner's Guide to AWS Free Tier Deployment

This guide assumes **you have never used a VPS before**. Follow these steps exactly to use the Free Tier (12 months free).

## Phase 1: Create AWS Account
1.  Go to [aws.amazon.com/free](https://aws.amazon.com/free/).
2.  Click **"Create a Free Account"**.
3.  Fill in the details. You will need a Credit/Debit card for identity verification (they charge ~$1 and refund it).

## Phase 2: Launch Your Server
1.  **Search**: In the AWS Console search bar, type `EC2` and click it.
2.  **Launch**: Click the orange **"Launch instance"** button.
3.  **Name**: Call it `ShortsBot`.
4.  **OS Images**: Click **"Ubuntu"**.
5.  **Instance Type**: Choose **`t2.micro`** or **`t3.micro`** (Look for the "Free tier eligible" tag).
6.  **Key pair (Login)**:
    - Click **"Create new key pair"**.
    - **Name**: `bot-key`.
    - **Type**: `RSA`.
    - **Format**: Select **`.ppk`** (Important: Select `.ppk` so it works with PuTTY).
    - Click **"Create key pair"**. It will download `bot-key.ppk`. **Keep this file safe!**
7.  **Launch**: Click **"Launch instance"** (bottom right).

## Phase 3: Connect to Server
1.  **Get Public IP**: Go back to EC2 Dashboard -> Instances. Click your instance. Copy the **"Public IPv4 address"** (e.g., `54.123.45.67`).
2.  **Open PuTTY**:
    - **Host Name**: `ubuntu@YOUR_PUBLIC_IP` (Example: `ubuntu@54.123.45.67`).
    - **Connection -> SSH -> Auth -> Credentials**:
        - **Private key file for authentication**: Browse and select your `bot-key.ppk`.
    - Click **Open**.
    - Click **Accept** if a warning pops up.
    - You should see `ubuntu@ip-...:~$`. You are in!

## Phase 4: Upload Your Bot
1.  **Open WinSCP**.
2.  **Host name**: Your Public IP.
3.  **User name**: `ubuntu`.
4.  **Advanced...** button -> SSH -> Authentication -> **Private key file**: Select `bot-key.ppk`.
5.  Click **Login**.
6.  You will see two windows (Left: PC, Right: Server).
7.  **Right Side**: Right-click -> New -> Directory -> Name it `funny_shorts`. Open it.
8.  **Left Side**: Navigate to your bot folder (`d:\funny shorts`).
9.  **Select Files**: `main.py`, `config.py`, `token.json`, `run_forever.sh`, `requirements.txt`, `src/`, `assets/`.
    - **IMPORTANT**: Do NOT upload `env` or `__pycache__` folders.
10. **Drag and Drop** to the Right Side.

## Phase 5: Install Software (In PuTTY)
Copy and paste these commands into PuTTY (Right-click to paste).

**1. Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

**2. Install Python & FFmpeg**
```bash
sudo apt install python3 python3-pip ffmpeg dos2unix -y
```

**3. Go to Folder**
```bash
cd funny_shorts
```

**4. Install Libraries**
```bash
pip3 install -r requirements.txt --break-system-packages
```

**5. Make Script Runnable**
```bash
dos2unix run_forever.sh
chmod +x run_forever.sh
```

## Phase 6: Run the Bot!
```bash
./run_forever.sh
```

**To keep it running in background:**
1.  Stop bot (`Ctrl+C`).
2.  `sudo apt install screen -y`
3.  `screen -S bot`
4.  `./run_forever.sh`
5.  Detach: Press `Ctrl+A`, then `D`.

To check it later: `screen -r bot`.

