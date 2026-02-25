import google.generativeai as genai
import os
import sys

# Extract key from app_v2.py
key = None
try:
    with open("app_v2.py", "r") as f:
        for line in f:
            if 'API_KEY = "AIza' in line:
                key = line.split('"')[1]
                break
except:
    pass

if not key:
    print("No API Key found")
    sys.exit(1)

genai.configure(api_key=key)

print("Checking for Gemini 3 / 2.5 models...")
found = []
try:
    for m in genai.list_models():
        if "gemini" in m.name:
            # Check for versions 3 or 2.5
            if "gemini-3" in m.name or "gemini-2.5" in m.name:
                found.append(m.name)
            # Also capture current max version just in case
            print(f"Seeing: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("-" * 30)
if found:
    print(f"SUCCESS: Found advanced models: {found}")
else:
    print("RESULT: No Gemini 3.x or 2.5.x models found on this account.")
