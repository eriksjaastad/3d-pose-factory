#!/usr/bin/env python3
"""
AI Enhance Batch - Stage 2 of Character Pipeline

Takes Blender renders and creates AI variations using Stability AI.
Runs inside Blender to use the AI Render addon.

Usage:
    blender --background --python ai_enhance_batch.py -- \
        --input-dir /path/to/variations/ \
        --output-dir /path/to/ai_output/ \
        --variations-per-image 5

Output:
    Creates AI variations: variation_001_ai_001.png, variation_001_ai_002.png, etc.
"""

import bpy
import sys
import argparse
import os
import glob
import json
import time


def parse_args():
    parser = argparse.ArgumentParser(description="Create AI variations of renders")
    parser.add_argument("--input-dir", type=str, required=True,
                        help="Directory containing Blender renders")
    parser.add_argument("--output-dir", type=str, default="/workspace/output/character-creation/ai_enhanced",
                        help="Output directory for AI images")
    parser.add_argument("--variations-per-image", type=int, default=5,
                        help="Number of AI variations per input image")
    parser.add_argument("--prompt", type=str, 
                        default="Beautiful anime character, detailed, vibrant colors, professional lighting, 8k quality",
                        help="AI generation prompt")
    parser.add_argument("--image-similarity", type=float, default=0.5,
                        help="How similar to keep to original (0.0-1.0)")
    
    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    else:
        args = parser.parse_args([])
    
    return args


def setup_ai_render():
    """Configure AI Render addon for image-to-image generation."""
    scene = bpy.context.scene
    
    # Enable AI Render addon
    try:
        bpy.ops.preferences.addon_enable(module='AI-Render')
    except:
        pass  # May already be enabled
    
    # Check if AI Render properties exist
    if not hasattr(scene, 'air_props'):
        print("❌ ERROR: AI Render addon not installed or enabled")
        return False
    
    return True


def configure_ai_settings(prompt, image_similarity, output_dir):
    """Set up AI Render settings."""
    scene = bpy.context.scene
    props = scene.air_props
    
    # Set prompt
    props.prompt_text = prompt
    
    # Image-to-image settings
    props.image_similarity = image_similarity
    
    # Use SDXL 1024
    props.sd_model = 'stable-diffusion-xl-1024-v1-0'
    
    # Resolution (must be 1024 for SDXL)
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    
    # Autosave settings (critical for headless mode!)
    props.do_autosave_after_images = True
    props.autosave_image_path = output_dir
    
    # Generation settings
    props.steps = 20
    props.cfg_scale = 7.0
    
    return True


def load_image_as_render_result(image_path):
    """Load an image and set it as the Render Result."""
    # Load the image
    img = bpy.data.images.load(image_path)
    img.update()
    
    # Create a simple scene to hold the image
    scene = bpy.context.scene
    scene.render.resolution_x = img.size[0]
    scene.render.resolution_y = img.size[1]
    
    # For AI Render to work, we need to set up a compositor node
    scene.use_nodes = True
    tree = scene.node_tree
    
    # Clear existing nodes
    for node in tree.nodes:
        tree.nodes.remove(node)
    
    # Create image node
    image_node = tree.nodes.new('CompositorNodeImage')
    image_node.image = img
    
    # Create composite output
    comp_node = tree.nodes.new('CompositorNodeComposite')
    
    # Link them
    tree.links.new(image_node.outputs['Image'], comp_node.inputs['Image'])
    
    # Set the loaded image as Render Result
    render_result = bpy.data.images.get('Render Result')
    if render_result:
        bpy.data.images.remove(render_result)
    
    # Rename our image to Render Result
    img.name = 'Render Result'
    
    return img


def generate_ai_variation(input_image_path, output_prefix, variation_num, prompt, image_similarity, output_dir):
    """Generate one AI variation of an image."""
    scene = bpy.context.scene
    props = scene.air_props
    
    # Load image
    load_image_as_render_result(input_image_path)
    
    # Configure settings
    props.prompt_text = prompt
    props.image_similarity = image_similarity
    
    # Set unique output name
    # AI Render uses its own naming, but we can control the directory
    props.autosave_image_path = output_dir
    
    # Generate
    try:
        bpy.ops.ai_render.generate_image()
        return True
    except Exception as e:
        print(f"   ❌ AI generation failed: {e}")
        return False


def main():
    args = parse_args()
    
    print("\n" + "=" * 60)
    print("  AI ENHANCE BATCH - Stage 2")
    print("=" * 60)
    print(f"\nInput: {args.input_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Variations per image: {args.variations_per_image}")
    print(f"Image similarity: {args.image_similarity}")
    print("=" * 60 + "\n")
    
    # Check input directory
    if not os.path.exists(args.input_dir):
        print(f"❌ ERROR: Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    # Find input images
    input_images = sorted(glob.glob(os.path.join(args.input_dir, "variation_*.png")))
    
    if not input_images:
        print(f"❌ ERROR: No variation images found in {args.input_dir}")
        sys.exit(1)
    
    print(f"📂 Found {len(input_images)} input images")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Setup AI Render
    print("\n🤖 Setting up AI Render...")
    if not setup_ai_render():
        print("❌ Failed to setup AI Render")
        sys.exit(1)
    
    configure_ai_settings(args.prompt, args.image_similarity, args.output_dir)
    print("   ✅ AI Render configured")
    
    # Track results
    results = []
    total_generated = 0
    total_expected = len(input_images) * args.variations_per_image
    
    # Process each input image
    for img_idx, input_path in enumerate(input_images, 1):
        input_name = os.path.basename(input_path)
        print(f"\n🖼️  Processing {img_idx}/{len(input_images)}: {input_name}")
        
        for var_num in range(1, args.variations_per_image + 1):
            print(f"   🎨 AI Variation {var_num}/{args.variations_per_image}...")
            
            # Generate AI variation
            success = generate_ai_variation(
                input_path,
                input_name.replace('.png', ''),
                var_num,
                args.prompt,
                args.image_similarity,
                args.output_dir
            )
            
            if success:
                total_generated += 1
                print(f"      ✅ Generated ({total_generated}/{total_expected})")
            else:
                print(f"      ❌ Failed")
            
            # Small delay to avoid rate limiting
            time.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"  ✅ Stage 2 Complete: {total_generated}/{total_expected} AI images generated")
    print(f"  📁 Output: {args.output_dir}")
    print("=" * 60 + "\n")
    
    print(f"STAGE2_OUTPUT={args.output_dir}")


if __name__ == "__main__":
    main()
