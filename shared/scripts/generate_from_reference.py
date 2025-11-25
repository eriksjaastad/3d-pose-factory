#!/usr/bin/env blender --background --python
"""
Image-to-Image AI Character Generation
=======================================

Uses YOUR reference image as the starting point for AI generation!

USAGE:
    cd /workspace && blender --background --python scripts/generate_from_reference.py

OUTPUTS:
    - AI-generated: /workspace/output/ai-render-*-2-after.png

COST: ~$0.04 per generation (1024x1024, 20 steps, SDXL)
"""

import bpy
import sys
from pathlib import Path

# Configuration
CONFIG = {
    'reference_image': '/workspace/reference.png',  # Your reference image
    'prompt': 'A stylized 3D anime character with large expressive eyes, long flowing dark hair, wearing pastel purple outfit, soft lighting, cherry blossom atmosphere, cute kawaii aesthetic, 8k quality, digital art',
    'negative_prompt': 'photorealistic, realistic, ugly, deformed, bad anatomy, distorted, blurry, low quality, nsfw',
    'image_similarity': 0.5,  # 0.0 = ignore reference, 1.0 = copy exactly
    'steps': 20,
    'cfg_scale': 7.0,
    'seed': 42,
    'output_dir': '/workspace/output/',
}

def download_reference_image():
    """Download the reference image from R2."""
    print("\n" + "="*60)
    print("📥 Downloading reference image from R2...")
    print("="*60)
    
    import subprocess
    result = subprocess.run(
        ['rclone', 'copy', 'r2_pose_factory:pose-factory/reference/reference.png', '/workspace/'],
        capture_output=True,
        text=True
    )
    
    ref_path = Path(CONFIG['reference_image'])
    if ref_path.exists():
        size_mb = ref_path.stat().st_size / (1024 * 1024)
        print(f"✅ Downloaded: {ref_path}")
        print(f"   Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"❌ Failed to download reference image")
        print(f"   stderr: {result.stderr}")
        return False

def configure_ai_render():
    """Enable and configure AI Render addon for image-to-image."""
    print("\n" + "="*60)
    print("🤖 Configuring AI Render (Image-to-Image mode)...")
    print("="*60)
    
    # Enable addon
    addon_name = "AI-Render"
    if addon_name not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module=addon_name)
        print(f"✅ Enabled {addon_name} addon")
    
    # Configure addon preferences
    prefs = bpy.context.preferences.addons['AI-Render'].preferences
    prefs.sd_backend = 'dreamstudio'  # Uses Stability API
    
    # Load API key from config
    config_path = Path.home() / ".config/blender/4.0/scripts/addons/AI-Render/config.py"
    if config_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("ai_render_config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        if hasattr(config_module, 'STABILITY_API_KEY'):
            prefs.dream_studio_api_key = config_module.STABILITY_API_KEY
            print(f"✅ API key loaded")
        else:
            print(f"⚠️  No API key found in config")
            return False
    else:
        print(f"❌ Config not found: {config_path}")
        return False
    
    # Configure scene properties
    scene = bpy.context.scene
    
    # Set render resolution to 1024x1024 (SDXL requirement)
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    
    scene.air_props.is_enabled = True
    scene.air_props.auto_run = True
    scene.air_props.prompt_text = CONFIG['prompt']
    scene.air_props.negative_prompt_text = CONFIG['negative_prompt']
    scene.air_props.steps = CONFIG['steps']
    scene.air_props.cfg_scale = CONFIG['cfg_scale']
    scene.air_props.image_similarity = CONFIG['image_similarity']  # KEY: Use reference image!
    scene.air_props.use_random_seed = False
    scene.air_props.seed = CONFIG['seed']
    
    # CRITICAL: Enable autosave (required for headless mode)
    scene.air_props.do_autosave_after_images = True
    scene.air_props.autosave_image_path = CONFIG['output_dir']
    
    print(f"✅ Prompt: {CONFIG['prompt'][:60]}...")
    print(f"✅ Image Similarity: {CONFIG['image_similarity']} (0.0=ignore, 1.0=copy)")
    print(f"✅ Steps: {CONFIG['steps']}, CFG: {CONFIG['cfg_scale']}")
    print(f"✅ Autosave: {scene.air_props.autosave_image_path}")
    
    return True

def load_reference_as_render_result():
    """Load the reference image into Blender as 'Render Result' and resize to 1024x1024."""
    print("\n" + "="*60)
    print("🖼️  Loading and resizing reference image...")
    print("="*60)
    
    ref_path = CONFIG['reference_image']
    
    # Load the reference image
    ref_img = bpy.data.images.load(ref_path)
    ref_img.update()
    
    print(f"   Original size: {ref_img.size[0]}x{ref_img.size[1]}")
    
    # Resize to 1024x1024 (SDXL requirement)
    if ref_img.size[0] != 1024 or ref_img.size[1] != 1024:
        print(f"   Resizing to 1024x1024...")
        ref_img.scale(1024, 1024)
        ref_img.update()
    
    # Remove existing Render Result if present
    if 'Render Result' in bpy.data.images:
        bpy.data.images.remove(bpy.data.images['Render Result'])
    
    # Rename reference image to 'Render Result' (AI Render expects this)
    ref_img.name = 'Render Result'
    
    print(f"✅ Loaded and resized reference image")
    print(f"   Final size: {ref_img.size[0]}x{ref_img.size[1]}")
    print(f"   Has data: {ref_img.has_data}")
    
    return True

def generate_ai_character():
    """Call AI Render to generate the character from reference."""
    print("\n" + "="*60)
    print("🚀 Generating AI character from YOUR reference image...")
    print("="*60)
    print(f"   Image Similarity: {CONFIG['image_similarity']*100:.0f}%")
    print(f"   This will take 30-90 seconds...")
    print(f"   Expected cost: ~$0.04")
    
    scene = bpy.context.scene
    
    # Import and call AI Render
    from importlib import import_module
    operators_module = import_module('AI-Render.operators')
    
    # Pre-API setup
    operators_module.do_pre_api_setup(scene)
    
    # Generate!
    try:
        result = operators_module.sd_generate(scene)
        if result:
            print("\n   ✅ AI generation complete!")
            
            # Find the generated image
            output_dir = Path(CONFIG['output_dir'])
            ai_images = sorted(
                output_dir.glob("ai-render-*-2-after.png"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if ai_images:
                newest = ai_images[0]
                size_mb = newest.stat().st_size / (1024 * 1024)
                print(f"   📁 AI-generated image: {newest.name}")
                print(f"      Size: {size_mb:.2f} MB")
                return True
            else:
                print("   ⚠️  AI image not found in output directory")
                return False
        else:
            print("\n   ❌ AI generation failed")
            return False
    except Exception as e:
        print(f"\n   ❌ Error during AI generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the image-to-image pipeline."""
    print("\n" + "="*60)
    print("🎨 IMAGE-TO-IMAGE AI CHARACTER GENERATION")
    print("="*60)
    print(f"Blender: {bpy.app.version_string}")
    print(f"Mode: Image-to-Image (using your reference)")
    print("="*60)
    
    # Ensure output directory exists
    Path(CONFIG['output_dir']).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Download reference image
    if not download_reference_image():
        print("\n❌ Failed to download reference image!")
        sys.exit(1)
    
    # Step 2: Configure AI Render
    if not configure_ai_render():
        print("\n❌ AI Render configuration failed!")
        sys.exit(1)
    
    # Step 3: Load reference as Render Result
    if not load_reference_as_render_result():
        print("\n❌ Failed to load reference image!")
        sys.exit(1)
    
    # Step 4: AI generation
    if not generate_ai_character():
        print("\n❌ AI generation failed!")
        sys.exit(1)
    
    # Success!
    print("\n" + "="*60)
    print("🎉 IMAGE-TO-IMAGE PIPELINE COMPLETE!")
    print("="*60)
    print(f"📂 Check outputs in: {CONFIG['output_dir']}")
    print("="*60)

if __name__ == "__main__":
    main()

