# src/tools/image_tools.py
"""
Image Generation Tools - Stable Diffusion XL via Hugging Face (Updated for new HF Inference Router)
"""

import os
import requests
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool("Generate Image with Stable Diffusion XL")
def generate_image(prompt: str) -> str:
    """Generates an image using Stable Diffusion XL via the Hugging Face Inference Router."""
    
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not api_token:
        return "❌ Error: HUGGINGFACEHUB_API_TOKEN not found in .env file"
    
    # ✅ Use new HF Inference Router endpoint
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"

    headers = {"Authorization": f"Bearer {api_token}"}
    
    try:
        print(f"🎨 Generating image with prompt: '{prompt[:60]}...'")
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=120
        )
        
        if response.status_code == 200:
            output_dir = "generated_images"
            os.makedirs(output_dir, exist_ok=True)
            
            safe_filename = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
            image_path = f"{output_dir}/{safe_filename}.png"
            
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ Image saved to: {image_path}")
            return f"Image successfully generated and saved to: {image_path}"
        
        elif response.status_code == 503:
            return "⏳ Model is loading on Hugging Face servers. Please wait 20 seconds and try again."
        
        else:
            return f"❌ Error generating image: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    print("🧪 Testing Image Generation Tool...\n")
    test_prompt = "A futuristic eco-friendly sneaker made of sustainable materials, product photography, white background"
    result = generate_image.run(test_prompt)
    print(f"\n{result}")
