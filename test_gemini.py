import google.generativeai as genai
import config
import sys

# Fix Windows Unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print(f"Checking models with key: {config.GEMINI_API_KEY[:5]}...")

try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
except Exception as e:
    print(f"Error: {e}")
