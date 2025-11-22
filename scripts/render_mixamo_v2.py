"""
Production-grade Mixamo character rendering using automatic camera framing.

This replaces the old render_mixamo.py with proper bounding box calculations
and deterministic camera positioning that works in headless mode.
"""

import bpy
import sys
import os

# Import our camera utilities module
# (Blender needs the script directory in Python path)
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import blender_camera_utils as cam_utils


def render_mixamo_character(fbx_path: str, output_path: str, camera_angle: float = 45.0):
    """
    Render a single frame of a Mixamo character with automatic camera framing.
    
    Args:
        fbx_path: Path to Mixamo FBX file
        output_path: Where to save the rendered image
        camera_angle: Horizontal camera angle in degrees (0=front, 90=side)
    """
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import FBX
    print(f"Importing: {fbx_path}")
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    imported_objects = bpy.context.selected_objects
    
    # Find armature
    armature = cam_utils.find_armature_in_selection(imported_objects)
    if not armature:
        raise ValueError("No armature found in imported FBX")
    
    print(f"✓ Found armature: {armature.name}")
    print(f"  Original scale: {armature.scale}")
    
    # Fix Mixamo's scale issues
    cam_utils.normalize_mixamo_character(armature)
    
    # Center character
    armature.location = (0, 0, 0)
    
    # Setup camera with automatic framing
    camera = cam_utils.setup_camera_for_character(
        armature,
        camera_angle=camera_angle,
        use_track_constraint=True,
        camera_fov=50.0
    )
    
    print(f"✓ Camera positioned at: {camera.location}")
    
    # Add lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    
    # Render settings
    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.eevee.taa_render_samples = 64
    
    # Render
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    
    print(f"✓ Rendered to: {output_path}")


# ----- Main execution -----

if __name__ == "__main__":
    fbx_path = "/workspace/pose-factory/characters/X Bot.fbx"
    output_path = "/workspace/pose-factory/output/mixamo_test_v2.png"
    
    render_mixamo_character(fbx_path, output_path, camera_angle=45.0)

