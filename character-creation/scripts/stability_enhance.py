#!/usr/bin/env python3
"""
Stability AI Structure Control Enhancement

Uses the 3D render as a CONTROL IMAGE (structure reference).
The AI colorizes and styles the exact shape provided.

This is different from img2img - here the mesh shape is PRESERVED
and AI paints colors/textures directly onto that structure.

Usage:
    python stability_enhance.py \
        --input /path/to/gray_render.png \
        --output-dir /path/to/output/ \
        --variations 3 \
        --prompt "Anime girl with brown hair..."
"""

import argparse
import base64
import glob
import os
import requests
import sys
import time
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Enhance images with Stability AI Structure Control")
    parser.add_argument("--input", type=str, help="Single input image path")
    parser.add_argument("--input-dir", type=str, help="Directory of input images")
    parser.add_argument("--output-dir", type=str, default="./ai_enhanced",
                        help="Output directory")
    parser.add_argument("--variations", type=int, default=3,
                        help="Number of AI variations per input image")
    parser.add_argument("--prompt", type=str,
                        default="Beautiful anime girl, long flowing brown hair, bright blue eyes, fair skin tone, cute pink off-shoulder crop top, white pleated mini skirt, stylish white sneakers, detailed face, soft lighting, vibrant colors, high quality anime art style, full body",
                        help="AI generation prompt")
    parser.add_argument("--negative-prompt", type=str,
                        default="ugly, deformed, blurry, low quality, bad anatomy, extra limbs, missing limbs, watermark, text, gray, monochrome",
                        help="Negative prompt")
    parser.add_argument("--control-strength", type=float, default=0.7,
                        help="How strongly to follow the control image structure (0.0-1.0)")
    parser.add_argument("--api-key", type=str, help="Stability API key (or set STABILITY_API_KEY env var)")
    
    return parser.parse_args()


def get_api_key(args):
    """Get API key from args, env, or config file."""
    if args.api_key:
        return args.api_key
    
    if os.environ.get('STABILITY_API_KEY'):
        return os.environ['STABILITY_API_KEY']
    
    for env_path in [Path('/workspace/.env'), Path('.env')]:
        if env_path.exists():
            for line in env_path.read_text().split('\n'):
                if line.startswith('STABILITY_API_KEY='):
                    return line.split('=', 1)[1].strip()
    
    return None


def call_structure_control_api(api_key, image_path, prompt, negative_prompt, control_strength, seed=None):
    """
    Call Stability AI Structure Control API.
    
    This uses the input image as a STRUCTURE REFERENCE.
    The AI generates colors/details while preserving the exact shape.
    """
    
    # Structure Control endpoint - uses image as structural guide
    url = "https://api.stability.ai/v2beta/stable-image/control/structure"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"  # Get raw image back
    }
    
    # Read the control image
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Prepare multipart form data
    files = {
        "image": ("control.png", image_data, "image/png")
    }
    
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "control_strength": control_strength,
        "output_format": "png",
    }
    
    if seed is not None:
        data["seed"] = seed
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code != 200:
        error_msg = response.text
        try:
            error_json = response.json()
            error_msg = error_json.get('message', error_json.get('errors', response.text))
        except:
            pass
        raise Exception(f"API error {response.status_code}: {error_msg}")
    
    # Response is raw image bytes
    return response.content


def call_sketch_control_api(api_key, image_path, prompt, negative_prompt, control_strength, seed=None):
    """
    Fallback: Call Stability AI Sketch Control API.
    
    Treats the input as a sketch to be colorized/detailed.
    """
    
    url = "https://api.stability.ai/v2beta/stable-image/control/sketch"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    files = {
        "image": ("sketch.png", image_data, "image/png")
    }
    
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "control_strength": control_strength,
        "output_format": "png",
    }
    
    if seed is not None:
        data["seed"] = seed
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code != 200:
        error_msg = response.text
        try:
            error_json = response.json()
            error_msg = error_json.get('message', error_json.get('errors', response.text))
        except:
            pass
        raise Exception(f"API error {response.status_code}: {error_msg}")
    
    return response.content


def enhance_image(api_key, input_path, output_dir, prompt, negative_prompt, control_strength, variations):
    """Generate multiple AI variations using structure control."""
    
    input_name = Path(input_path).stem
    results = []
    
    print(f"\n🖼️  Processing: {input_path}")
    print(f"   Using as STRUCTURE CONTROL (shape will be preserved)")
    
    for i in range(1, variations + 1):
        print(f"   🎨 Generating variation {i}/{variations}...")
        
        try:
            seed = 42 + i * 1000
            
            # Try structure control first
            try:
                image_bytes = call_structure_control_api(
                    api_key, input_path, prompt, negative_prompt, control_strength, seed
                )
                method = "structure"
            except Exception as e:
                if "not found" in str(e).lower() or "404" in str(e):
                    print(f"      ⚠️ Structure control unavailable, trying sketch control...")
                    image_bytes = call_sketch_control_api(
                        api_key, input_path, prompt, negative_prompt, control_strength, seed
                    )
                    method = "sketch"
                else:
                    raise
            
            output_path = os.path.join(output_dir, f"{input_name}_ctrl_{i:02d}.png")
            
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            file_size = os.path.getsize(output_path) / 1024
            print(f"      ✅ Saved ({method}): {output_path} ({file_size:.1f} KB)")
            results.append(output_path)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"      ❌ Failed: {e}")
    
    return results


def main():
    args = parse_args()
    
    print("\n" + "🎨" * 30)
    print("  STABILITY AI STRUCTURE CONTROL")
    print("  (Your mesh shape WILL be preserved)")
    print("🎨" * 30)
    
    api_key = get_api_key(args)
    if not api_key:
        print("\n❌ ERROR: No API key found!")
        print("   Set STABILITY_API_KEY env var or use --api-key")
        sys.exit(1)
    print(f"\n✅ API key found")
    
    # Get input images
    input_images = []
    if args.input:
        input_images = [args.input]
    elif args.input_dir:
        input_images = sorted(glob.glob(os.path.join(args.input_dir, "*.png")))
    else:
        print("\n❌ ERROR: Specify --input or --input-dir")
        sys.exit(1)
    
    if not input_images:
        print("\n❌ ERROR: No input images found!")
        sys.exit(1)
    
    print(f"📂 Input images: {len(input_images)}")
    print(f"🔢 Variations per image: {args.variations}")
    print(f"📁 Output directory: {args.output_dir}")
    print(f"🎛️  Control strength: {args.control_strength} (higher = stricter shape adherence)")
    print(f"\n📝 Prompt: {args.prompt[:80]}...")
    
    # Cost estimate (structure control is ~$0.04/image for SDXL)
    total_images = len(input_images) * args.variations
    estimated_cost = total_images * 0.04
    print(f"\n💰 Estimated cost: ~${estimated_cost:.2f} ({total_images} images × $0.04)")
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process each input image
    all_results = []
    for input_path in input_images:
        results = enhance_image(
            api_key, input_path, args.output_dir,
            args.prompt, args.negative_prompt, args.control_strength, args.variations
        )
        all_results.extend(results)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"  ✅ COMPLETE: {len(all_results)} AI images generated")
    print(f"  📁 Output: {args.output_dir}")
    print(f"  💰 Estimated cost: ~${len(all_results) * 0.04:.2f}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
