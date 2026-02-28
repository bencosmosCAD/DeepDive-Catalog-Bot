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
    # Using Gemini 1.5/2.5 Flash for speed and native vision cost-efficiency
    model = genai.GenerativeModel("gemini-2.5-flash")

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
    
    for pdf in pdfs:
        brand = pdf.replace(".pdf", "")
        pdf_path = os.path.join(data_dir, pdf)
        print(f"\n🌊 Processing {brand} Catalog...")
        
        try:
            doc = fitz.open(pdf_path)
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
                    
                    # Skip extremely small images (logos, bullets, icons)
                    if len(image_bytes) < 15000: 
                        continue
                        
                    image_filename = f"{brand}_p{page_num+1}_i{img_index}.{image_ext}"
                    
                    if image_filename in processed_images:
                        continue # Already processed in a previous run
                        
                    image_filepath = os.path.join(output_dir, image_filename)
                    with open(image_filepath, "wb") as f:
                        f.write(image_bytes)
                        
                    print(f" -> Analyzing new image: {image_filename}...", end=" ")
                    
                    image_parts = [{"mime_type": f"image/{image_ext}", "data": image_bytes}]
                    prompt = """
                    Analyze this image from a scuba diving catalog.
                    Extract the exact Product Name, Model, and any choices/variants (like sizes, colors) visible in charts next to it.
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
                                print(f"Identified: {analysis.get('product_name')} ({len(analysis.get('variants', []))} variants)")
                                
                                # Incremental save so we don't lose data if script stops
                                with open(map_file, "w") as f:
                                    json.dump(results, f, indent=4)
                                    
                                success = True
                                processed_images.add(image_filename)
                                
                            except json.JSONDecodeError:
                                print(f"Non-JSON response. Skipping.")
                                break 
                                
                        except ResourceExhausted:
                            print("\n ⏳ Rate limit reached. Cooling down for 30 seconds...")
                            time.sleep(30)
                            retries -= 1
                        except Exception as e:
                            print(f"API Error: {e}")
                            break
                            
                    # Small delay to respect standard API limits
                    time.sleep(1.5) 
                    
                except Exception as e:
                    print(f"\nError extracting image: {e}")

    print("\n✅ Catalog Image Extraction and Mapping Complete!")
    print(f"Database contains {len(results)} mapped image assets.")

if __name__ == "__main__":
    extract_all_catalogs()
