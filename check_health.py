import google.generativeai as genai
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

# CONFIG
API_KEY = "AIzaSyDnK1HyjCbkpn7FJTgpKXAbr479hQAwNHE"
genai.configure(api_key=API_KEY)

MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash", 
    "gemini-2.0-flash-exp", 
    "gemini-1.5-pro", 
    "gemini-1.5-flash", 
    "gemini-pro"
]

BUTTON_QUERIES = [
    "List all wetsuits under $300 in a table.",
    "Compare the Suunto and Oceanic dive computers specs.",
    "What represents the best value primary light for tech diving?"
]

print("--- HEALTH CHECK & FIX LOOP ---")

# 1. Find a Working Model
print("\n[1] Finding Working Model...")
active_model = None

for m in MODELS_TO_TRY:
    print(f"Testing {m}...", end=" ")
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("ping")
        print("✅ SUCCESS")
        active_model = model
        break
    except Exception as e:
        print(f"❌ FAILED")

if not active_model:
    print("\n❌ CRITICAL: No models working. Cannot proceed.")
    exit(1)

# 2. Test Button Logic
print("\n[2] Verifying Button Queries...")
all_passed = True
for q in BUTTON_QUERIES:
    print(f"Query: '{q[:30]}...' -> ", end=" ")
    try:
        response = active_model.generate_content(q)
        if response.text:
            print("✅ Response Verified")
        else:
            print("⚠️ Empty Response")
            all_passed = False
    except Exception as e:
        print(f"❌ Error: {e}")
        all_passed = False

if all_passed:
    print("\n✅ ALL SYSTEMS GO. App is ready.")
else:
    print("\n⚠️ ISSUES DETECTED with some queries.")
