import bpy
import os

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the Mixamo FBX character
fbx_path = "/workspace/pose-factory/characters/X Bot.fbx"
bpy.ops.import_scene.fbx(filepath=fbx_path)

# Get all imported objects
imported_objects = bpy.context.selected_objects

# Find the armature/character and center it
if imported_objects:
    char = imported_objects[0]
    # Scale down if needed (Mixamo characters can be large)
    char.scale = (0.01, 0.01, 0.01)
    char.location = (0, 0, 0)

# Add camera - positioned to see full character from front
bpy.ops.object.camera_add(location=(4, -4, 2))
camera = bpy.context.active_object
camera.rotation_euler = (1.2, 0, 0.785)  # Looking at center from front-side angle
bpy.context.scene.camera = camera

# Add lights
bpy.ops.object.light_add(type='SUN', location=(2, 2, 3))
sun = bpy.context.active_object
sun.data.energy = 2.0

# Set render settings
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.engine = 'BLENDER_EEVEE'

# Render
output_path = "/workspace/pose-factory/output/mixamo_test.png"
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)

print(f"Rendered Mixamo character to: {output_path}")

