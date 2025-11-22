import bpy
import os

# Test with just one animation
animation_file = "/workspace/pose-factory/animations/Dancing Twerk.fbx"
output_path = "/workspace/pose-factory/output/test_single_frame.png"

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add camera - use settings from extract_animation_frames.py
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

# Import animation
print(f"Importing: {animation_file}")
bpy.ops.import_scene.fbx(filepath=animation_file)

# Find armature and setup
armature = None
for obj in bpy.context.selected_objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

if armature:
    print(f"Found armature: {armature.name}")
    # Animation FBX uses different scale than character-only FBX
    armature.scale = (1, 1, 1)  # Use normal scale for animation FBX
    armature.location = (0, 0, 0)
    
    # Scale any mesh children
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.scale = (1, 1, 1)
            print(f"Scaled mesh: {obj.name}")

# Go to frame 10
bpy.context.scene.frame_set(10)

# Render
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)

print(f"Test render saved to: {output_path}")

