#!/usr/bin/env python3
"""
Stability AI Structure Control

Uses the Control/Structure endpoint which treats the input image
as a STRUCTURAL GUIDE (pose, shape) and generates a completely 
new colorized image following that structure.

This is different from img2img which tries to preserve colors!

Usage:
    python stability_control.py \
        --input /path/to/gray_render.png \
        --output-dir /path/to/output/ \
        --variations 3 \
        --prompt "Anime girl..."
"""

import argparse
import base64
import glob
import os
import requests
import sys
import time
from pathlib import Path

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
from utils import get_env_var


def parse_args():
    parser = argparse.ArgumentParser(description="Use Stability AI Structure Control")
    parser.add_argument("--input", type=str, help="Single input image path")
    parser.add_argument("--input-dir", type=str, help="Directory of input images")
    parser.add_argument("--output-dir", type=str, default="./ai_controlled",
                        help="Output directory")
    parser.add_argument("--variations", type=int, default=3,
                        help="Number of AI variations per input image")
    parser.add_argument("--prompt", type=str,
                        default="Beautiful anime girl, long flowing brown hair with pink highlights, bright blue eyes, fair peachy skin, cute pink off-shoulder top, white pleated skirt, white sneakers, joyful expression, full body, vibrant colors, high quality anime art style, studio lighting",
                        help="AI generation prompt")
    parser.add_argument("--negative-prompt", type=str,
                        default="ugly, deformed, blurry, low quality, bad anatomy, extra limbs, gray, monochrome, statue, sculpture",
                        help="Negative prompt")
    parser.add_argument("--control-strength", type=float, default=0.7,
                        help="How closely to follow the structure (0.0-1.0)")
    parser.add_argument("--api-key", type=str, help="Stability API key")
    
    return parser.parse_args()


def get_api_key(args):
    """Get API key from args or standardized environment variable lookup."""
    if args.api_key:
        return args.api_key
    
    # DNA Fix: Use standardized environment variable lookup (Doppler ready)
    api_key = get_env_var('STABILITY_API_KEY')
    if api_key:
        return api_key
    
    # Legacy fallback for local .env files
    for env_path in [Path('/workspace/.env'), Path('.env')]:
        if env_path.exists():
            for line in env_path.read_text().split('\n'):
                if line.startswith('STABILITY_API_KEY='):
                    return line.split('=', 1)[1].strip()
    
    return None


def call_structure_control(api_key, image_path, prompt, negative_prompt, control_strength, seed=None):
    """
    Call Stability AI Structure Control endpoint.
    This treats input as structural guide, not color source!
    """
    
    # Structure control endpoint (v2beta)
    url = "https://api.stability.ai/v2beta/stable-image/control/structure"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"  # Get raw image bytes back
    }
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    files = {
        "image": ("render.png", image_data, "image/png")
    }
    
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "control_strength": control_strength,
        "output_format": "png"
    }
    
    if seed is not None:
        data["seed"] = seed
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code != 200:
        # Check for error message
        try:
            error = response.json()
            raise Exception(f"API error {response.status_code}: {error}")
        except Exception as e:
            # DNA Fix: Log JSON parsing error
            print(f"      ⚠️  Could not parse error JSON: {e}")
            raise Exception(f"API error {response.status_code}: {response.text[:500]}")
    
    return response.content  # Raw image bytes


def call_sketch_control(api_key, image_path, prompt, negative_prompt, control_strength, seed=None):
    """
    Alternative: Sketch control - treats input as a sketch to colorize.
    """
    
    url = "https://api.stability.ai/v2beta/stable-image/control/sketch"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    files = {
        "image": ("render.png", image_data, "image/png")
    }
    
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "control_strength": control_strength,
        "output_format": "png"
    }
    
    if seed is not None:
        data["seed"] = seed
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code != 200:
        try:
            error = response.json()
            raise Exception(f"API error {response.status_code}: {error}")
        except Exception as e:
            # DNA Fix: Log JSON parsing error
            print(f"      ⚠️  Could not parse error JSON: {e}")
            raise Exception(f"API error {response.status_code}: {response.text[:500]}")
    
    return response.content


def enhance_image(api_key, input_path, output_dir, prompt, negative_prompt, control_strength, variations, use_sketch=False):
    """Generate AI variations using structure/sketch control."""
    
    input_name = Path(input_path).stem
    results = []
    
    control_func = call_sketch_control if use_sketch else call_structure_control
    control_type = "sketch" if use_sketch else "structure"
    
    print(f"\n🖼️  Processing: {input_path}")
    print(f"   Using {control_type} control (input = pose guide, NOT color source)")
    
    for i in range(1, variations + 1):
        print(f"   🎨 Generating variation {i}/{variations}...")
        
        try:
            seed = 42 + i * 1000
            
            image_bytes = control_func(
                api_key, input_path, prompt, negative_prompt, control_strength, seed
            )
            
            output_path = os.path.join(output_dir, f"{input_name}_ctrl_{i:02d}.png")
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            file_size = os.path.getsize(output_path) / 1024
            print(f"      ✅ Saved: {output_path} ({file_size:.1f} KB)")
            results.append(output_path)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            # If structure fails, try sketch
            if not use_sketch and "not found" in str(e).lower():
                print(f"      ⚡ Trying sketch control instead...")
                try:
                    image_bytes = call_sketch_control(
                        api_key, input_path, prompt, negative_prompt, control_strength, seed
                    )
                    output_path = os.path.join(output_dir, f"{input_name}_sketch_{i:02d}.png")
                    with open(output_path, 'wb') as f:
                        f.write(image_bytes)
                    file_size = os.path.getsize(output_path) / 1024
                    print(f"      ✅ Saved (sketch): {output_path} ({file_size:.1f} KB)")
                    results.append(output_path)
                except Exception as e2:
                    print(f"      ❌ Sketch also failed: {e2}")
    
    return results


def main():
    args = parse_args()
    
    print("\n" + "🎯" * 30)
    print("  STABILITY AI STRUCTURE CONTROL")
    print("  (Input = Pose Guide, NOT Color Source!)")
    print("🎯" * 30)
    
    api_key = get_api_key(args)
    if not api_key:
        print("\n❌ ERROR: No API key found!")
        sys.exit(1)
    print(f"\n✅ API key found")
    
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
    print(f"💪 Control strength: {args.control_strength}")
    print(f"\n📝 Prompt: {args.prompt[:80]}...")
    
    total_images = len(input_images) * args.variations
    print(f"\n💰 Estimated cost: ~${total_images * 0.04:.2f} ({total_images} images)")
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    all_results = []
    for input_path in input_images:
        results = enhance_image(
            api_key, input_path, args.output_dir,
            args.prompt, args.negative_prompt, args.control_strength, args.variations
        )
        all_results.extend(results)
    
    print("\n" + "=" * 60)
    print(f"  ✅ COMPLETE: {len(all_results)} AI images generated")
    print(f"  📁 Output: {args.output_dir}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

