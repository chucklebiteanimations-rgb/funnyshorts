from google import genai
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Initialize Gemini
GEMINI_AVAILABLE = False
client = None

if hasattr(config, "GEMINI_API_KEY") and config.GEMINI_API_KEY and config.GEMINI_API_KEY != "YOUR_GEMINI_KEY_HERE":
    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
else:
    print("Warning: Gemini API Key not properly set in config.py")

DEFAULT_TAGS = "#funny #shorts #comedy #memes #lol #viral #trending"
DEFAULT_DESCRIPTION = """
Enjoy the best funny moments!
Subscribe for daily laughs!

#funny #shorts #comedy #memes
"""

def generate_text(prompt):
    """Generic helper to call Gemini API."""
    if not GEMINI_AVAILABLE:
        return None
        
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def generate_title(image_filename):
    """
    Generates a funny title for the short based on the filename.
    """
    # Clean up filename for context
    base_name = os.path.splitext(image_filename)[0]
    clean_name = base_name.replace("_", " ").replace("-", " ")
    
    if not GEMINI_AVAILABLE:
        return f"{clean_name} 😂 #shorts"

    prompt = f"Generate a single short, viral execution title for a video about '{clean_name}'. It must be funny and under 50 characters. Include one emoji. Do not use quotes."
    
    title = generate_text(prompt)
    
    if not title:
        # Fallback if AI fails
        return f"Funny Shorts 😂 #shorts"
        
    # Ensure it has #shorts
    if "#shorts" not in title.lower():
        title += " #shorts"
        
    return title

def get_description_and_tags(title_context="funny video"):
    """
    Generates a description and tags based on the title context.
    """
    if not GEMINI_AVAILABLE:
        return DEFAULT_DESCRIPTION, DEFAULT_TAGS

    # 1. Generate Description
    desc_prompt = f"Write a catchy 2-sentence YouTube Shorts description for a video titled '{title_context}'. Invite people to subscribe."
    description = generate_text(desc_prompt)
    
    if not description:
        description = DEFAULT_DESCRIPTION

    # 2. Generate Tags
    tags_prompt = f"Generate 10 viral hashtags for a funny video titled '{title_context}'. Separate them with spaces. Start each with #."
    tags = generate_text(tags_prompt)
    
    if not tags:
        tags = DEFAULT_TAGS
        
    # Combine for full description
    full_description = f"{description}\n\n{tags}"
    
    return full_description, tags

if __name__ == "__main__":
    # Fix for Windows Unicode printing
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    test_file = "cat_jump_fail.mp4"
    print(f"Testing with: {test_file}")
    
    t = generate_title(test_file)
    print(f"Title: {t}")
    
    d, tags = get_description_and_tags(t)
    print(f"Description:\n{d}")
    print(f"Tags: {tags}")
