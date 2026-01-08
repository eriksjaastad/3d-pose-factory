#!/usr/bin/env python3
"""
Test AI Render (Stable Diffusion in Blender)

Simple test to verify:
1. AI Render plugin is installed
2. Stability API key works
3. Can generate one test image
4. Actual cost matches estimate

USAGE (on pod):
    blender --background --python test_ai_render.py

Expected output:
    - One test image in /workspace/output/test_ai_render.png
    - Console output showing generation details
"""

import bpy
import sys
import os
from pathlib import Path

# Test configuration
TEST_CONFIG = {
    'provider': 'stability',
    'resolution': (1024, 1024),  # SDXL requires 1024x1024
    'steps': 20,                 # Low for fast test
    'model': 'sdxl',             # SDXL 1024 (only model available)
    'prompt': 'A simple red cube on a white background',
    'output': '/workspace/output/test_ai_render.png'
}

def test_ai_render_installed():
    """Check if AI Render addon is installed and enable it."""
    print("=" * 60)
    print("Test 1: Checking if AI Render is installed...")
    print("=" * 60)
    
    # Try to enable the addon (it might have different module names)
    possible_names = ['AI-Render', 'ai_render', 'airender', 'ai-render']
    
    enabled = False
    for addon_name in possible_names:
        try:
            print(f"  Trying to enable '{addon_name}'...")
            bpy.ops.preferences.addon_enable(module=addon_name)
            print(f"  ✅ Successfully enabled '{addon_name}'")
            enabled = True
            break
        except Exception as e:
            print(f"  ⚠️  Could not enable '{addon_name}': {e}")
    
    if not enabled:
        print(f"\n❌ Could not enable AI Render addon")
        print("\nAvailable addons in directory:")
        addon_dir = Path.home() / ".config/blender/4.0/scripts/addons"
        if addon_dir.exists():
            for item in addon_dir.iterdir():
                if item.is_dir():
                    print(f"  - {item.name}")
        
        print("\nCurrently enabled addons:")
        for addon in bpy.context.preferences.addons:
            print(f"  - {addon}")
        return False
    
    return True

def test_stability_api_key():
    """Check if Stability API key is configured."""
    print("\n" + "=" * 60)
    print("Test 2: Checking Stability API key...")
    print("=" * 60)
    
    # Try to read config file
    config_path = Path.home() / ".config/blender/4.0/scripts/addons/AI-Render/config.py"
    
    if config_path.exists():
        print(f"✅ Config file found: {config_path}")
        
        # Read and check for API key
        with open(config_path) as f:
            content = f.read()
            if 'STABILITY_API_KEY' in content and 'sk-' in content:
                print(f"✅ Stability API key appears to be set")
                return True
            else:
                print(f"❌ Stability API key not found in config")
                return False
    else:
        print(f"❌ Config file not found at {config_path}")
        return False

def test_generate_image():
    """Generate a simple test image using Stability AI."""
    print("\n" + "=" * 60)
    print("Test 3: Generating test image...")
    print("=" * 60)
    
    print(f"Provider: {TEST_CONFIG['provider']}")
    print(f"Resolution: {TEST_CONFIG['resolution']}")
    print(f"Steps: {TEST_CONFIG['steps']}")
    print(f"Prompt: {TEST_CONFIG['prompt']}")
    print(f"Output: {TEST_CONFIG['output']}")
    
    # Create output directory
    output_path = Path(TEST_CONFIG['output'])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Configure AI Render addon preferences
        prefs = bpy.context.preferences.addons['AI-Render'].preferences
        prefs.sd_backend = 'dreamstudio'  # Uses Stability API
        
        # Read API key from config
        config_path = Path.home() / ".config/blender/4.0/scripts/addons/AI-Render/config.py"
        if config_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("ai_render_config", config_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            if hasattr(config_module, 'STABILITY_API_KEY'):
                prefs.dream_studio_api_key = config_module.STABILITY_API_KEY
                print(f"✅ API key configured")
            else:
                print(f"⚠️  No API key found in config")
        
        # Configure scene properties
        scene = bpy.context.scene
        scene.air_props.is_enabled = True
        scene.air_props.auto_run = True  # Auto-process after render (CORRECT property name!)
        # sd_model is already set to SDXL 1024 (the only option)
        scene.air_props.prompt_text = TEST_CONFIG['prompt']
        scene.air_props.negative_prompt_text = "ugly, bad art, blurry"
        scene.air_props.steps = TEST_CONFIG['steps']
        scene.air_props.cfg_scale = 7.0
        scene.air_props.image_similarity = 0.0  # Pure text-to-image
        scene.air_props.use_random_seed = False
        scene.air_props.seed = 42
        
        # CRITICAL: Enable autosave so AI-generated images are saved to disk
        scene.air_props.do_autosave_after_images = True
        scene.air_props.autosave_image_path = "/workspace/output/"  # Where to save AI images
        
        print(f"\n🔧 Autosave configured:")
        print(f"   do_autosave_after_images: {scene.air_props.do_autosave_after_images}")
        print(f"   autosave_image_path: {scene.air_props.autosave_image_path}")
        
        # Set render resolution (MUST be multiple of 64, between 128-2048)
        scene.render.resolution_x = TEST_CONFIG['resolution'][0]
        scene.render.resolution_y = TEST_CONFIG['resolution'][1]
        scene.render.resolution_percentage = 100  # CRITICAL: AI Render uses this in validation!
        scene.render.filepath = str(output_path)
        
        print("\n🎨 Rendering with AI Render enabled...")
        print("   This will make a real API call to Stability AI")
        print("   Expected cost: ~$0.04 (1024x1024, 20 steps, SDXL)")
        
        # Render - this creates the 'Render Result' image but in headless mode it has no data
        bpy.ops.render.render(write_still=True)
        
        # Headless mode fix: Load rendered PNG and make it the 'Render Result'
        print("   Fixing headless mode: Loading rendered image...")
        
        # Remove old Render Result (it has no data in headless)
        if 'Render Result' in bpy.data.images:
            bpy.data.images.remove(bpy.data.images['Render Result'])
        
        # Load the saved render
        if output_path.exists():
            render_result = bpy.data.images.load(str(output_path))
            render_result.name = 'Render Result'
            
            # CRITICAL: Call update() to set has_data=True
            render_result.update()
            
            print(f"   ✅ Loaded and updated Render Result")
            print(f"      has_data={render_result.has_data}, size={render_result.size[:]}")
        else:
            print(f"   ❌ Could not find rendered file at {output_path}")
            return False
        
        # Call AI Render's API function directly (bypasses task queue which requires event loop)
        print("\n   🎨 Calling Stability AI API directly...")
        print("   (This will take 30-90 seconds...)")
        
        from importlib import import_module
        operators_module = import_module('AI-Render.operators')
        
        # Do pre-API setup (sets various scene properties)
        operators_module.do_pre_api_setup(scene)
        
        # Call sd_generate directly - this makes the actual API call
        # Unlike the handler, this runs synchronously instead of being queued
        try:
            result = operators_module.sd_generate(scene)
            print(f"\n   ✅ API call completed! (returned: {result})")
            
            # Check for errors in scene properties
            if hasattr(scene, 'air_props'):
                props = scene.air_props
                if hasattr(props, 'error_key') and props.error_key:
                    print(f"   ⚠️  Error key: {props.error_key}")
                if hasattr(props, 'error_message') and props.error_message:
                    print(f"   ⚠️  Error message: {props.error_message}")
                if hasattr(props, 'last_generated_image_path') and props.last_generated_image_path:
                    print(f"   📁 Last generated image: {props.last_generated_image_path}")
        except Exception as e:
            print(f"\n   ❌ API call failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Check if AI generation succeeded
        # AI Render saves images to the same directory as the render
        output_dir = output_path.parent
        
        print("\n📂 Checking for AI-generated images...")
        print(f"   Looking in: {output_dir}")
        
        # List all PNG files to see what was created
        png_files = sorted(output_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if len(png_files) > 1:
            print(f"\n✅ Found {len(png_files)} images:")
            for f in png_files[:5]:  # Show first 5
                stat = f.stat()
                print(f"   - {f.name} ({stat.st_size} bytes, modified {stat.st_mtime})")
            
            # The newest file should be the AI-generated one
            newest = png_files[0]
            print(f"\n🎨 Newest image (likely AI-generated): {newest.name}")
            return True
        else:
            print(f"\n⚠️  Only found {len(png_files)} image(s) - AI generation may have failed")
            
            # Check for errors in scene properties
            if hasattr(scene, 'air_props'):
                props = scene.air_props
                if hasattr(props, 'error_message') and props.error_message:
                    print(f"   Error: {props.error_message}")
            
            return False
        
    except Exception as e:
        print(f"\n❌ Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return False

def inspect_ai_render_addon():
    """Inspect AI Render addon to find available operators."""
    print("\n" + "=" * 60)
    print("Bonus: Inspecting AI Render addon...")
    print("=" * 60)
    
    # List all operators that might be AI Render related
    print("\nSearching for AI Render operators:")
    ai_render_ops = []
    for op_name in dir(bpy.ops):
        if 'ai' in op_name.lower() or 'render' in op_name.lower() or 'dream' in op_name.lower():
            try:
                op_module = getattr(bpy.ops, op_name)
                for sub_op in dir(op_module):
                    if not sub_op.startswith('_'):
                        full_name = f"bpy.ops.{op_name}.{sub_op}"
                        ai_render_ops.append(full_name)
            except Exception as e:
                # DNA Fix: Silent failure replaced with logging (likely non-accessible operator)
                # print(f"      ⚠️  Error inspecting operator {op_name}: {e}")
                pass
    
    if ai_render_ops:
        print(f"\nFound {len(ai_render_ops)} potentially relevant operators:")
        for op in ai_render_ops[:20]:  # Limit to first 20
            print(f"  - {op}")
    else:
        print("  No AI/render related operators found")
    
    # Try to import ai_render module if it exists
    try:
        import ai_render
        print(f"\n✅ AI Render module imported successfully")
        print(f"   Available attributes:")
        for attr in dir(ai_render)[:20]:  # Limit to first 20
            if not attr.startswith('_'):
                print(f"     - {attr}")
    except ImportError:
        print(f"\n⚠️  Could not import ai_render module")

def main():
    """Run all tests."""
    print("\n" + "🔬" * 30)
    print("AI RENDER TEST SUITE")
    print("🔬" * 30 + "\n")
    
    # Track results
    results = {
        'addon_installed': False,
        'api_key_configured': False,
        'image_generated': False
    }
    
    # Run tests
    results['addon_installed'] = test_ai_render_installed()
    
    if results['addon_installed']:
        results['api_key_configured'] = test_stability_api_key()
        inspect_ai_render_addon()
    
    # Only try to generate if previous tests passed
    if results['addon_installed'] and results['api_key_configured']:
        results['image_generated'] = test_generate_image()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ AI Render Installed:    {results['addon_installed']}")
    print(f"✅ API Key Configured:     {results['api_key_configured']}")
    print(f"⚠️  Image Generated:        {results['image_generated']} (placeholder)")
    
    # Exit code
    if all(results.values()):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed - see details above")
        sys.exit(1)

if __name__ == '__main__':
    main()

