import bpy
import os
import glob

# Configuration
animations_dir = "/workspace/pose-factory/animations"
output_dir = "/workspace/pose-factory/output/animation_frames"
frame_interval = 5  # Extract every 5th frame

os.makedirs(output_dir, exist_ok=True)

# Get all FBX animation files (skip X Bot.fbx as it's just the character)
fbx_files = glob.glob(os.path.join(animations_dir, "*.fbx"))
animation_files = [f for f in fbx_files if "X Bot.fbx" not in f]

print(f"Found {len(animation_files)} animation files to process")

# Set up camera once
def setup_scene():
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Add camera - closer and better framed
    bpy.ops.object.camera_add(location=(2.5, -2.5, 1.5))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.3, 0, 0.785)
    bpy.context.scene.camera = camera
    
    # Add lights
    bpy.ops.object.light_add(type='SUN', location=(2, 2, 3))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    
    # Set render settings
    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

# Process each animation
total_frames_rendered = 0

for anim_file in animation_files:
    anim_name = os.path.splitext(os.path.basename(anim_file))[0]
    print(f"\nProcessing: {anim_name}")
    
    # Setup clean scene
    setup_scene()
    
    # Import animation
    bpy.ops.import_scene.fbx(filepath=anim_file)
    
    # Find and setup the armature/character
    armature = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break
    
    if armature:
        # Scale the armature (character)
        armature.scale = (1, 1, 1)  # Try normal scale first
        armature.location = (0, 0, 0)
        
        # Update the scene
        bpy.context.view_layer.update()
        
        # Also scale any mesh children
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.scale = (1, 1, 1)
    
    # Get animation frame range
    start_frame = bpy.context.scene.frame_start
    end_frame = bpy.context.scene.frame_end
    
    print(f"  Animation has {end_frame - start_frame + 1} frames")
    
    # Extract frames at intervals
    frame_count = 0
    for frame_num in range(start_frame, end_frame + 1, frame_interval):
        bpy.context.scene.frame_set(frame_num)
        
        # Render
        output_path = f"{output_dir}/{anim_name}_frame_{frame_num:04d}.png"
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        
        frame_count += 1
        total_frames_rendered += 1
    
    print(f"  Rendered {frame_count} frames from {anim_name}")

print(f"\n{'='*50}")
print(f"Total frames rendered: {total_frames_rendered}")
print(f"Output directory: {output_dir}")
print(f"{'='*50}")

