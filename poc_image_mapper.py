import fitz  # PyMuPDF
import os
import google.generativeai as genai
import json

def load_api_key():
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            for line in f:
                if "GEMINI_API_KEY" in line:
                    return line.split('"')[1]
    except Exception as e:
        print(f"Error loading API key: {e}")
    return None

def extract_and_analyze():
    api_key = load_api_key()
    if not api_key:
        print("API Key not found.")
        return

    genai.configure(api_key=api_key)
    # Gemini 2.5 Flash has native multimodal capabilities
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Let's test on the Atomic catalog
    pdf_path = "data/Atomic.pdf"
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    output_dir = "images_poc"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Opening {pdf_path} for extraction...")
    doc = fitz.open(pdf_path)
    
    # We will process just the first 3 pages as a Proof of Concept
    pages_to_process = min(3, len(doc))
    
    results = []

    for page_num in range(pages_to_process):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        print(f"Page {page_num + 1}: Found {len(image_list)} images.")
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Filter out very small images (like tiny logos or icons)
                if len(image_bytes) < 10000:
                    continue

                image_filename = f"atomic_p{page_num+1}_i{img_index}.{image_ext}"
                image_filepath = os.path.join(output_dir, image_filename)
                
                with open(image_filepath, "wb") as f:
                    f.write(image_bytes)
                
                print(f" -> Saved {image_filename} ({len(image_bytes)/1024:.1f} KB)... Analyzing with AI...")

                # Construct image payload for Gemini
                image_parts = [
                    {
                        "mime_type": f"image/{image_ext}",
                        "data": image_bytes
                    }
                ]

                # Prompt the AI to identify products and charts within the image
                prompt = """
                Analyze this image extracted from a scuba diving product catalog.
                1. Does this image contain a specific product, a variant chart, or is it just lifestyle/marketing?
                2. If it contains a product or chart, extract the Product Name, Model, and any choices/variants visible.
                Return ONLY valid JSON in this format:
                {
                    "is_product": true/false,
                    "product_name": "Name or null",
                    "variants_or_choices": ["List", "of", "variants"]
                }
                """
                
                response = model.generate_content([prompt, image_parts[0]])
                
                # Cleanup the markdown formatting from the response
                resp_text = response.text.strip().replace("```json", "").replace("```", "")
                
                try:
                    analysis = json.loads(resp_text)
                    analysis["stored_image"] = image_filename
                    results.append(analysis)
                    print(f"    AI Results: {analysis['product_name']} | Variants found: {len(analysis.get('variants_or_choices', []))}")
                except json.JSONDecodeError:
                    print(f"    AI returned non-JSON response: {resp_text[:50]}...")
            
            except Exception as e:
                print(f"    Error processing image {img_index}: {e}")

    print("\n=== POC Extraction Complete ===")
    print("Saving mapped data to image_map_poc.json")
    with open("image_map_poc.json", "w") as f:
        json.dump(results, f, indent=4)
        
if __name__ == "__main__":
    extract_and_analyze()
