#!/usr/bin/env blender --background --python
"""
Golden Script: AI Character Generation Pipeline
================================================

This is the ONE COMMAND demo of the full pipeline:
- Blender scene setup
- Headless rendering  
- AI Render (Stability AI SDXL)
- Automatic output to /workspace/output/

USAGE:
    cd /workspace && blender --background --python scripts/generate_character_from_cube.py

OUTPUTS:
    - Blender render: /workspace/output/character_base.png
    - AI-generated: /workspace/output/ai-render-*-2-after.png

COST: ~$0.04 per generation (1024x1024, 20 steps, SDXL)
"""

import bpy
import sys
from pathlib import Path

# Configuration
CONFIG = {
    'prompt': 'A stylized 3D anime character with large expressive eyes, long flowing dark hair, wearing pastel purple outfit with pleated skirt, soft lighting, cherry blossom atmosphere, cute kawaii aesthetic, full body, standing pose, 8k quality, digital art',
    'negative_prompt': 'photorealistic, realistic, ugly, deformed, bad anatomy, distorted, blurry, low quality, nsfw',
    'resolution': (1024, 1024),
    'steps': 20,
    'cfg_scale': 7.0,
    'seed': 42,
    'output_dir': '/workspace/output/',
    'output_filename': 'character_base.png',
}

def setup_scene():
    """Create a simple scene: cube, camera, light."""
    print("\n" + "="*60)
    print("🎬 Setting up Blender scene...")
    print("="*60)
    
    # Clear default scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Add cube (our character placeholder)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    cube = bpy.context.active_object
    cube.name = "Character"
    
    # Add camera
    bpy.ops.object.camera_add(location=(4, -4, 3))
    camera = bpy.context.active_object
    camera.name = "Camera"
    
    # Point camera at cube
    direction = cube.location - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    bpy.context.scene.camera = camera
    
    # Add light
    bpy.ops.object.light_add(type='SUN', location=(2, 2, 5))
    light = bpy.context.active_object
    light.data.energy = 2.0
    
    print(f"✅ Scene ready: {cube.name}, {camera.name}, {light.name}")

def configure_render_settings():
    """Set up render resolution and output."""
    print("\n" + "="*60)
    print("⚙️  Configuring render settings...")
    print("="*60)
    
    scene = bpy.context.scene
    scene.render.resolution_x = CONFIG['resolution'][0]
    scene.render.resolution_y = CONFIG['resolution'][1]
    scene.render.resolution_percentage = 100
    
    # Set output path
    output_path = Path(CONFIG['output_dir']) / CONFIG['output_filename']
    scene.render.filepath = str(output_path)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    
    print(f"✅ Resolution: {CONFIG['resolution'][0]}x{CONFIG['resolution'][1]}")
    print(f"✅ Output: {scene.render.filepath}")

def configure_ai_render():
    """Enable and configure AI Render addon."""
    print("\n" + "="*60)
    print("🤖 Configuring AI Render...")
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
    scene.air_props.is_enabled = True
    scene.air_props.auto_run = True
    scene.air_props.prompt_text = CONFIG['prompt']
    scene.air_props.negative_prompt_text = CONFIG['negative_prompt']
    scene.air_props.steps = CONFIG['steps']
    scene.air_props.cfg_scale = CONFIG['cfg_scale']
    scene.air_props.image_similarity = 0.0  # Pure text-to-image
    scene.air_props.use_random_seed = False
    scene.air_props.seed = CONFIG['seed']
    
    # CRITICAL: Enable autosave (required for headless mode)
    scene.air_props.do_autosave_after_images = True
    scene.air_props.autosave_image_path = CONFIG['output_dir']
    
    print(f"✅ Prompt: {CONFIG['prompt'][:60]}...")
    print(f"✅ Steps: {CONFIG['steps']}, CFG: {CONFIG['cfg_scale']}")
    print(f"✅ Autosave: {scene.air_props.autosave_image_path}")
    
    return True

def render_base_image():
    """Render the base Blender scene."""
    print("\n" + "="*60)
    print("🎨 Rendering base image...")
    print("="*60)
    
    bpy.ops.render.render(write_still=True)
    
    output_path = Path(bpy.context.scene.render.filepath)
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Saved: {output_path}")
        print(f"   Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"❌ Render failed: {output_path}")
        return False

def generate_ai_character():
    """Call AI Render to generate the character."""
    print("\n" + "="*60)
    print("🚀 Generating AI character with Stability AI SDXL...")
    print("="*60)
    print("   This will take 30-90 seconds...")
    print(f"   Expected cost: ~$0.04 (1024x1024, 20 steps)")
    
    scene = bpy.context.scene
    
    # Fix headless mode: Manually load rendered image into Render Result
    render_result = bpy.data.images.get('Render Result')
    if render_result and not render_result.has_data:
        print("   Fixing headless mode: Loading rendered image...")
        rendered_path = bpy.context.scene.render.filepath
        temp_img = bpy.data.images.load(rendered_path)
        temp_img.update()
        
        # Replace Render Result
        bpy.data.images.remove(render_result)
        temp_img.name = 'Render Result'
        print(f"   ✅ Loaded and updated Render Result")
    
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
    """Run the full pipeline."""
    print("\n" + "="*60)
    print("🏭 AI CHARACTER GENERATION PIPELINE")
    print("="*60)
    print(f"Blender: {bpy.app.version_string}")
    print(f"Scene: {bpy.context.scene.name}")
    print("="*60)
    
    # Ensure output directory exists
    Path(CONFIG['output_dir']).mkdir(parents=True, exist_ok=True)
    
    # Step 1: Setup
    setup_scene()
    configure_render_settings()
    
    # Step 2: AI Render config
    if not configure_ai_render():
        print("\n❌ AI Render configuration failed!")
        sys.exit(1)
    
    # Step 3: Render base
    if not render_base_image():
        print("\n❌ Base render failed!")
        sys.exit(1)
    
    # Step 4: AI generation
    if not generate_ai_character():
        print("\n❌ AI generation failed!")
        sys.exit(1)
    
    # Success!
    print("\n" + "="*60)
    print("🎉 PIPELINE COMPLETE!")
    print("="*60)
    print(f"📂 Check outputs in: {CONFIG['output_dir']}")
    print("="*60)

if __name__ == "__main__":
    main()

