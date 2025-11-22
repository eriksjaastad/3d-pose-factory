"""
Multi-angle rendering for pose training data generation.

Renders a Mixamo character from multiple camera angles to create
a comprehensive training dataset for MediaPipe pose detection.

Features:
- 4 or 8 camera angles per animation frame
- Automatic camera framing for all angles
- Batch processing of multiple FBX files
- Organized output directory structure

Run: blender --background --python render_multi_angle.py
"""

import bpy
import sys
import os
import math

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import blender_camera_utils as cam_utils


def render_character_multi_angle(
    fbx_path: str,
    output_dir: str,
    num_angles: int = 8,
    render_all_frames: bool = False
):
    """
    Render a Mixamo character from multiple camera angles.
    
    Args:
        fbx_path: Path to Mixamo FBX file
        output_dir: Base directory for outputs
        num_angles: Number of camera angles (4 or 8 recommended)
        render_all_frames: If True, renders all animation frames; if False, just frame 1
    """
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import FBX
    print(f"\n{'='*60}")
    print(f"Importing: {os.path.basename(fbx_path)}")
    print(f"{'='*60}")
    
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
    armature.location = (0, 0, 0)
    
    # Setup lighting (same for all angles)
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Add fill light from opposite side
    bpy.ops.object.light_add(type='SUN', location=(-5, 5, 10))
    fill = bpy.context.active_object
    fill.data.energy = 1.0
    fill.rotation_euler = (math.radians(45), 0, math.radians(-135))
    
    # Configure render settings
    scene = bpy.context.scene
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 64
    
    # Determine frame range
    if render_all_frames:
        frame_range = range(scene.frame_start, scene.frame_end + 1)
    else:
        frame_range = [scene.frame_current]  # Just current frame
    
    # Calculate camera angles (evenly distributed around character)
    angles = [i * (360.0 / num_angles) for i in range(num_angles)]
    
    # Angle descriptions for filenames
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
    
    # Create output directory structure
    character_name = os.path.splitext(os.path.basename(fbx_path))[0]
    character_output_dir = os.path.join(output_dir, character_name)
    os.makedirs(character_output_dir, exist_ok=True)
    
    # Setup cameras for all angles (calculate bounding box once)
    print(f"\n{'='*60}")
    print(f"Setting up {num_angles} cameras...")
    print(f"{'='*60}")
    
    cameras = []
    for i, angle in enumerate(angles):
        # Create camera for this angle
        camera = cam_utils.setup_camera_for_character(
            armature,
            camera_name=f"Camera_{i:02d}_{int(angle)}deg",
            camera_angle=angle,
            use_track_constraint=True,
            camera_fov=50.0
        )
        cameras.append((camera, angle))
        
        # Get friendly name
        friendly_name = angle_names.get(int(angle), f"{int(angle)}deg")
        print(f"  ✓ Camera {i+1}/{num_angles}: {friendly_name} ({angle}°)")
    
    # Render from each camera angle
    print(f"\n{'='*60}")
    print(f"Rendering {len(cameras)} angles × {len(frame_range)} frames = {len(cameras) * len(frame_range)} images")
    print(f"{'='*60}")
    
    total_renders = 0
    
    for frame in frame_range:
        scene.frame_set(frame)
        
        for i, (camera, angle) in enumerate(cameras):
            # Set active camera
            scene.camera = camera
            
            # Create output filename
            friendly_name = angle_names.get(int(angle), f"{int(angle)}deg")
            
            if render_all_frames:
                output_filename = f"frame_{frame:04d}_{friendly_name}.png"
            else:
                output_filename = f"{friendly_name}.png"
            
            output_path = os.path.join(character_output_dir, output_filename)
            
            # Render
            scene.render.filepath = output_path
            bpy.ops.render.render(write_still=True)
            
            total_renders += 1
            print(f"  ✓ [{total_renders}/{len(cameras) * len(frame_range)}] Frame {frame}, {friendly_name}")
    
    print(f"\n{'='*60}")
    print(f"✓ COMPLETE!")
    print(f"  Total renders: {total_renders}")
    print(f"  Output directory: {character_output_dir}")
    print(f"{'='*60}\n")


def batch_render_characters(fbx_directory: str, output_dir: str, num_angles: int = 8):
    """
    Batch render all FBX files in a directory.
    
    Args:
        fbx_directory: Directory containing Mixamo FBX files
        output_dir: Base output directory
        num_angles: Number of camera angles per character
    """
    import glob
    
    # Find all FBX files
    fbx_pattern = os.path.join(fbx_directory, "*.fbx")
    fbx_files = glob.glob(fbx_pattern)
    
    if not fbx_files:
        print(f"⚠️  No FBX files found in: {fbx_directory}")
        return
    
    print(f"\n{'='*60}")
    print(f"BATCH RENDERING {len(fbx_files)} CHARACTERS")
    print(f"{'='*60}")
    
    for i, fbx_path in enumerate(fbx_files):
        print(f"\n[{i+1}/{len(fbx_files)}] Processing: {os.path.basename(fbx_path)}")
        
        try:
            render_character_multi_angle(
                fbx_path,
                output_dir,
                num_angles=num_angles,
                render_all_frames=False  # Just one frame per character for now
            )
        except Exception as e:
            print(f"⚠️  ERROR rendering {fbx_path}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"✓ BATCH COMPLETE!")
    print(f"  Processed: {len(fbx_files)} characters")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}\n")


# ----- Configuration -----

# For single character rendering:
SINGLE_FBX_PATH = "/workspace/pose-factory/characters/X Bot.fbx"
SINGLE_OUTPUT_DIR = "/workspace/pose-factory/output/multi_angle"

# For batch rendering:
BATCH_FBX_DIR = "/workspace/pose-factory/characters"
BATCH_OUTPUT_DIR = "/workspace/pose-factory/output/batch_multi_angle"

# Number of camera angles (4, 8, or 16 recommended)
NUM_ANGLES = 8

# Mode selection
BATCH_MODE = False  # Set to True to render all FBX files in directory


# ----- Main Execution -----

if __name__ == "__main__":
    # Parse command line arguments if provided
    if len(sys.argv) > 1 and "--batch" in sys.argv:
        BATCH_MODE = True
    
    if BATCH_MODE:
        print("Running in BATCH mode...")
        
        # Use local paths if workspace doesn't exist
        if not os.path.exists("/workspace"):
            BATCH_FBX_DIR = "../downloads"  # Relative to scripts directory
            BATCH_OUTPUT_DIR = "../data/working/multi_angle_batch"
        
        batch_render_characters(BATCH_FBX_DIR, BATCH_OUTPUT_DIR, NUM_ANGLES)
    
    else:
        print("Running in SINGLE character mode...")
        
        # Use local paths if workspace doesn't exist
        if not os.path.exists("/workspace"):
            SINGLE_FBX_PATH = "../downloads/X Bot.fbx"
            SINGLE_OUTPUT_DIR = "../data/working/multi_angle"
        
        render_character_multi_angle(
            SINGLE_FBX_PATH,
            SINGLE_OUTPUT_DIR,
            num_angles=NUM_ANGLES,
            render_all_frames=False
        )
    
    print("\n✅ Done! Check output directory for rendered images.")

