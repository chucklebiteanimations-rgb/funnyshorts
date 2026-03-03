
try:
    import flask
    print("Flask is installed")
except ImportError:
    print("Flask is NOT installed")

try:
    from google import genai
    print("google-genai is installed")
except ImportError as e:
    print(f"google-genai is NOT installed: {e}")
