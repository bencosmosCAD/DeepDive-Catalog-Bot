import google.generativeai as genai
import os
import sys

# Extract key from app_v2.py since env var might not be set in this shell
key = None
with open("app_v2.py", "r") as f:
    for line in f:
        if 'API_KEY = "AIza' in line:
            key = line.split('"')[1]
            break

if not key:
    print("Could not find API Key")
    sys.exit(1)

genai.configure(api_key=key)

try:
    print("Testing gemini-2.5-flash specifically...")
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content("Hello")
    print("SUCCESS: Gemini 2.5 Flash is available!")
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
