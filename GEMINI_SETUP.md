# How to Get a Free Google Gemini API Key

Follow these simple steps to get your API key. It is 100% free.

1.  **Go to Google AI Studio**
    - Click this link: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

2.  **Sign In**
    - Log in with your Google Account (Gmail).
    - If asked, accept the Terms of Service.

3.  **Create API Key**
    - Look for a big blue button that says **"Create API key"** (or "Get API key").
    - Click **"Create API key in new project"**.
    - Wait a few seconds.

4.  **Copy the Key**
    - A popup will appear with a long string of random characters starting with `AIza...`.
    - Click the **Copy** button.

5.  **Paste into Config**
    - Open your `d:\funny shorts\config.py` file.
    - Find the line that says:
      ```python
      GEMINI_API_KEY = "YOUR_GEMINI_KEY_HERE"
      ```
    - Replace `YOUR_GEMINI_KEY_HERE` with the key you just copied.
      - **Example**: `GEMINI_API_KEY = "AIzaSyD-1234567890abcdef"`
    - Save the file.

**Done!** Your bot will now use Google's AI to generate smart titles and descriptions.
