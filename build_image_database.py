import fitz  # PyMuPDF
import os
import json
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

def load_api_key():
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            for line in f:
                if "GEMINI_API_KEY" in line:
                    return line.split('"')[1].strip()
    except Exception as e:
        return None

def extract_all_catalogs():
    api_key = load_api_key()
    if not api_key:
        print("API Key not found in .streamlit/secrets.toml")
        return

    genai.configure(api_key=api_key)
    # Using Gemini 2.5 Pro for advanced native vision capabilities and best quality
    model = genai.GenerativeModel("gemini-2.5-pro")

    data_dir = "data"
    output_dir = "images"
    os.makedirs(output_dir, exist_ok=True)
    
    map_file = "image_map.json"
    results = []
    
    # Load existing progress so we can stop and resume anytime
    if os.path.exists(map_file):
        try:
            with open(map_file, "r") as f:
                results = json.load(f)
        except Exception:
            pass
    
    processed_images = {r["stored_image"] for r in results if "stored_image" in r}
    pdfs = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    
    print(f"Found {len(pdfs)} catalogs to process...")
    
    print(f"Total PDFs found: {len(pdfs)} (Skipping previously processed images)\n" + "="*50)
    
    total_catalogs = len(pdfs)
    
    for cat_num, pdf in enumerate(pdfs, 1):
        brand = pdf.replace(".pdf", "")
        pdf_path = os.path.join(data_dir, pdf)
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            print(f"\n[{cat_num}/{total_catalogs}] 🌊 Processing {brand.upper()} Catalog ({total_pages} Pages)...")
        except Exception as e:
            print(f"Error opening {pdf}: {e}")
            continue
            
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    if len(image_bytes) < 15000: 
                        continue
                        
                    image_filename = f"{brand}_p{page_num+1}_i{img_index}.{image_ext}"
                    
                    if image_filename in processed_images:
                        continue 
                        
                    image_filepath = os.path.join(output_dir, image_filename)
                    with open(image_filepath, "wb") as f:
                        f.write(image_bytes)
                        
                    print(f"  [P.{page_num+1} | Img {img_index}] 🔍 Sending {len(image_bytes)/1024:.1f}KB image to Gemini...", end=" ", flush=True)
                    
                    image_parts = [{"mime_type": f"image/{image_ext}", "data": image_bytes}]
                    prompt = """
                    Analyze this image from a scuba diving catalog.
                    Extract the exact Product Name, Model, and any choices/variants visible.
                    Return ONLY a JSON response in this strict format:
                    {
                        "is_product": true,
                        "brand": "Brand Name if visible",
                        "product_name": "Product Name/Model",
                        "variants": ["variant 1", "variant 2"]
                    }
                    If there is no product (e.g., lifestyle, scenery), set is_product to false and leave the rest null.
                    """
                    
                    success = False
                    retries = 3
                    
                    while not success and retries > 0:
                        try:
                            response = model.generate_content([prompt, image_parts[0]])
                            resp_text = response.text.strip().replace("```json", "").replace("```", "")
                            try:
                                analysis = json.loads(resp_text)
                                analysis["stored_image"] = image_filename
                                analysis["brand_file"] = brand
                                results.append(analysis)
                                
                                if analysis.get('is_product'):
                                    print(f"✅ Found: {analysis.get('product_name')} ({len(analysis.get('variants', []))} variants)")
                                else:
                                    print("❌ Skipped: No product detected (e.g., Lifestyle Image)")
                                
                                with open(map_file, "w") as f:
                                    json.dump(results, f, indent=4)
                                    
                                success = True
                                processed_images.add(image_filename)
                                
                            except json.JSONDecodeError:
                                print("⚠️ AI returned unreadable format. Retrying...")
                                retries -= 1
                                
                        except ResourceExhausted:
                            print("\n    ⏳ Auto-Pause: Rate limit reached. Cooling down 60 seconds...", end=" ", flush=True)
                            time.sleep(60)
                            print("Resuming...")
                        except Exception as e:
                            print(f"\n    ⚠️ API Error: {e}")
                            break
                            
                    time.sleep(2) 
                    
                except Exception as e:
                    print(f"\n    ⚠️ Error extracting image bytes: {e}")

    print("\n" + "="*50)
    print("✅ Catalog Image Extraction and Mapping Complete!")
    print(f"Database contains {len(results)} mapped image assets.")

if __name__ == "__main__":
    extract_all_catalogs()
