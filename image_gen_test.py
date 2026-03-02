import requests
import json
import base64

try:
    with open('.streamlit/secrets.toml', 'r') as f:
        for line in f:
            if 'GEMINI_API_KEY' in line:
                api_key = line.split('"')[1]
                break
except Exception as e:
    print(f"Error: {e}")
    exit(1)

url = f'https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}'
payload = {
  'instances': [{'prompt': 'A photorealistic scuba diving fins'}],
  'parameters': {'sampleCount': 1}
}

print("Testing :predict...")
res = requests.post(url, json=payload)
print(f"Status Code: {res.status_code}")
print(res.text[:200])

url2 = f'https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages?key={api_key}'
payload2 = {
  "instances": [
    {"prompt": "A photorealistic scuba diving fins"}
  ],
  "parameters": {
    "sampleCount": 1
  }
}
print("\nTesting :generateImages...")
res2 = requests.post(url2, json=payload2)
print(f"Status Code: {res2.status_code}")
print(res2.text[:200])
