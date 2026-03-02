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

print("Sending request to Imagen 3 API...")
res = requests.post(url, json=payload)
print(f"Status Code: {res.status_code}")
if res.status_code == 200:
    print("Success! Image generated.")
else:
    print(f"Failed: {res.text}")
