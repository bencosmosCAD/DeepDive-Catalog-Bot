import google.generativeai as genai
import json

API_KEY = "AIzaSyDnK1HyjCbkpn7FJTgpKXAbr479hQAwNHE"
genai.configure(api_key=API_KEY)
m = genai.GenerativeModel("gemini-2.5-flash")
res = m.generate_content("Give me a list of two fruits with their color", generation_config={"response_mime_type": "application/json"})
print("RAW:")
print(res.text)
print("PARSED:")
print(json.loads(res.text))
