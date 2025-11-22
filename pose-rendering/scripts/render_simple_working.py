"""
WORKING multi-angle renderer for Mixamo characters.
Uses simple, proven camera positions - no complex math needed!

After hours of debugging, we found:
- Camera distance: 3.5 meters works perfectly
- Camera height: 1.0 meters (middle of character)  
- Don't "normalize" - just import and render!
"""

import bpy
import sys
import os
import math

def render_character_simple(fbx_path, output_dir, num_angles=8):
    """
    Simple multi-angle render that ACTUALLY WORKS!
    
    Args:
        fbx_path: Path to Mixamo FBX
        output_dir: Where to save images
        num_angles: Number of camera angles (default 8)
    """
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import FBX - NO MODIFICATIONS!
    print(f"\nImporting: {fbx_path}")
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    # Setup lighting (same for all angles)
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    
    # Render settings
    scene = bpy.context.scene
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 64
    
    # Calculate angles
    angles = [i * (360.0 / num_angles) for i in range(num_angles)]
    angle_names = {
        0: "front",
        45: "front_right",
        90: "right",
        135: "back_right",
        180: "back",
        225: "back_left",
        270: "left",
        315: "front_left"
    }
    
    # Create output directory
    character_name = os.path.splitext(os.path.basename(fbx_path))[0]
    char_output_dir = os.path.join(output_dir, character_name)
    os.makedirs(char_output_dir, exist_ok=True)
    
    print(f"\nRendering {num_angles} angles...")
    
    # Render from each angle
    for i, angle_deg in enumerate(angles):
        angle_rad = math.radians(angle_deg)
        
        # Camera position - circular orbit at distance 3.5
        camera_distance = 3.5
        camera_height = 1.6  # Raised to near head height for more natural viewing angle
        
        cam_x = camera_distance * math.sin(angle_rad)
        cam_y = -camera_distance * math.cos(angle_rad)  # Negative Y = in front
        cam_z = camera_height
        
        # Create camera for this angle
        bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
        camera = bpy.context.active_object
        camera.name = f"Camera_{i}"
        
        # Point camera at origin
        direction = -camera.location.normalized()
        rot_quat = direction.to_track_quat('-Z', 'Y')
        camera.rotation_euler = rot_quat.to_euler()
        
        scene.camera = camera
        
        # Render
        friendly_name = angle_names.get(int(angle_deg), f"{int(angle_deg)}deg")
        output_path = os.path.join(char_output_dir, f"{friendly_name}.png")
        scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        
        print(f"  ✓ [{i+1}/{num_angles}] {friendly_name}")
        
        # Delete camera for next angle
        bpy.ops.object.select_all(action='DESELECT')
        camera.select_set(True)
        bpy.ops.object.delete()
    
    print(f"\n✓ Complete! Saved to: {char_output_dir}")


def batch_render_simple(fbx_directory, output_dir, num_angles=8):
    """
    Batch render all FBX files in a directory.
    """
    import glob
    
    fbx_files = glob.glob(os.path.join(fbx_directory, "*.fbx"))
    
    if not fbx_files:
        print(f"No FBX files found in: {fbx_directory}")
        return
    
    print(f"\n{'='*60}")
    print(f"BATCH RENDERING {len(fbx_files)} CHARACTERS")
    print(f"{'='*60}")
    
    for i, fbx_path in enumerate(fbx_files):
        print(f"\n[{i+1}/{len(fbx_files)}] {os.path.basename(fbx_path)}")
        
        try:
            render_character_simple(fbx_path, output_dir, num_angles)
        except Exception as e:
            print(f"⚠️  ERROR: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"✓ BATCH COMPLETE!")
    print(f"{'='*60}")


# Main execution
if __name__ == "__main__":
    # Check for batch mode flag
    batch_mode = "--batch" in sys.argv
    
    if batch_mode:
        fbx_dir = "/workspace/pose-factory/characters"
        output_dir = "/workspace/pose-factory/output/simple_multi_angle"
        batch_render_simple(fbx_dir, output_dir, num_angles=8)
    else:
        # Single character test
        fbx_path = "/workspace/pose-factory/characters/X Bot.fbx"
        output_dir = "/workspace/pose-factory/output/simple_multi_angle"
        render_character_simple(fbx_path, output_dir, num_angles=8)

