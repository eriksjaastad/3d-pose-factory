#!/usr/bin/env python3
"""
Debug script to check what dimensions AI Render sees
"""
import bpy
import sys
import os

# Set up scene
scene = bpy.context.scene
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100

print(f"\n🔍 DIMENSION DEBUG:")
print(f"   resolution_x: {scene.render.resolution_x}")
print(f"   resolution_y: {scene.render.resolution_y}")
print(f"   resolution_percentage: {scene.render.resolution_percentage}")

# Try to enable AI Render addon and access its utils
try:
    # Enable the addon
    addon_name = "AI-Render"
    if addon_name not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module=addon_name)
    
    # Import the addon module
    import importlib
    air_module = importlib.import_module("AI-Render")
    air_utils = air_module.utils
    
    width = air_utils.get_output_width(scene)
    height = air_utils.get_output_height(scene)
    valid = air_utils.are_dimensions_valid(scene)
    is_sdxl = air_utils.is_using_sdxl_1024_model(scene)
    
    print(f"\n📐 AI Render sees:")
    print(f"   get_output_width(): {width}")
    print(f"   get_output_height(): {height}")
    print(f"   is_using_sdxl_1024_model(): {is_sdxl}")
    print(f"   are_dimensions_valid(): {valid}")
    
    # Manual validation check
    min_dim = 128
    max_dim = 2048
    step = 64
    width_valid = width in range(min_dim, max_dim + step, step)
    height_valid = height in range(min_dim, max_dim + step, step)
    
    print(f"\n✅ Manual validation:")
    print(f"   width ({width}) in range: {width_valid}")
    print(f"   height ({height}) in range: {height_valid}")
    print(f"   Both valid: {width_valid and height_valid}")
    
    # Check current AI Render settings
    print(f"\n⚙️ AI Render settings:")
    if hasattr(scene, 'air_props'):
        props = scene.air_props
        print(f"   sd_model: {props.sd_model if hasattr(props, 'sd_model') else 'N/A'}")
        print(f"   use_animated_prompts: {props.use_animated_prompts if hasattr(props, 'use_animated_prompts') else 'N/A'}")
    
except Exception as e:
    print(f"❌ Error importing AI Render utils: {e}")
    import traceback
    traceback.print_exc()

