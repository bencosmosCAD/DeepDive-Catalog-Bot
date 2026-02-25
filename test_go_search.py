import google.generativeai as genai
import fitz
import os
import json
import re

API_KEY = "AIzaSyDnK1HyjCbkpn7FJTgpKXAbr479hQAwNHE"
genai.configure(api_key=API_KEY)

MODEL_Flash = "gemini-2.5-flash"
MAX_CONTEXT_CHARS = 2_000_000

BRAND_MAPPING = {
    "Suunto": "Suunto", "Oceanic": "Oceanic", "Atomic": "Atomic Aquatics",
    "Hollis": "Hollis", "Ocean Hunter": "Ocean Hunter", "Rob Allen": "Rob Allen",
    "Salvimar": "Salvimar", "Zeagle": "Zeagle", "Bare": "Bare",
    "Stahlsac": "Stahlsac", "Princeton": "Princeton Tec",
    "Enth Degree": "Enth Degree", "Gear Aid": "Gear Aid", "Oceanpro": "Oceanpro",
}

def clean_filename(fname):
    name = fname.replace(".pdf", "")
    for k, v in BRAND_MAPPING.items():
        if k in name: return v
    return name

def index_data():
    folder = "data"
    if not os.path.exists(folder):
        return "", []
    
    files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
    all_text = []
    indexed_brands = set()
    total_chars = 0

    for f in files:
        path = os.path.join(folder, f)
        brand = clean_filename(f)
        indexed_brands.add(brand)
        
        try:
            doc = fitz.open(path)
            file_text = ""
            for page in doc:
                file_text += page.get_text()
            doc.close()
            
            if total_chars + len(file_text) > MAX_CONTEXT_CHARS:
                remaining = MAX_CONTEXT_CHARS - total_chars
                all_text.append(f"\n=== {brand} Catalog (Truncated) ===\n{file_text[:remaining]}")
                break
            
            all_text.append(f"\n=== {brand} Catalog ===\n{file_text}")
            total_chars += len(file_text)
            
        except Exception as e:
            pass

    return "\n".join(all_text), sorted(list(indexed_brands))

print("Indexing...")
CONTEXT, BRANDS = index_data()
print(f"Index complete. Chars: {len(CONTEXT)}")

query = "List all wetsuits under $300 with brand, model and price in a table."
print(f"Searching for: {query}")

model_flash = genai.GenerativeModel(MODEL_Flash)
prompt_catalog = f"""
You are DeepDive Intelligence. 

TASK:
Analyze the request and the catalog data.
Return a JSON LIST of products found. Dictionary format below.

REQUIRED JSON FORMAT:
[
  {{
    "brand": "Brand Name",
    "model": "Model Name",
    "sku": "SKU if found else null",
    "prices": {{
        "rrp": 100.00,
        "trade": 60.00,
        "partner": 70.00,
        "distributor": 50.00,
        "promo": 40.00
    }},
    "features": "Key features summary",
    "url": "https://www.google.com/search?q=Brand+Model"
  }}
]

PRICING LOGIC:
- If text lists multiple prices (e.g. "Trade $X", "RRP $Y"), map them.
- If ONLY RRP is found: set Trade=RRP*0.6, Partner=RRP*0.7 (ESTIMATES).
- If NO price found, set all to 0.00.

=== CATALOG DATA START ===
{CONTEXT}
=== CATALOG DATA END ===

USER QUESTION: {query}
"""

try:
    response_flash = model_flash.generate_content(prompt_catalog)
    text = response_flash.text
    print("RAW RESPONSE:")
    print(text)
    
    if "```" in text:
        pattern = r"```(?:json)?\s*(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            text = match.group(1)
    
    if text.strip() and not text.strip().startswith("["):
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            text = match.group(0)

    structured_data = json.loads(text)
    if not isinstance(structured_data, list):
        if isinstance(structured_data, dict): structured_data = [structured_data]
        else: structured_data = []
        
    print(f"Successfully parsed {len(structured_data)} items.")
except Exception as e:
    print(f"Exception during request/parsing: {e}")
