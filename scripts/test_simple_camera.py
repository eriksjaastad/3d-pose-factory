import bpy
import math

# Test with just one animation
animation_file = "/workspace/pose-factory/animations/Dancing Twerk.fbx"
output_path = "/workspace/pose-factory/output/test_simple_camera.png"

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import animation
print(f"Importing: {animation_file}")
bpy.ops.import_scene.fbx(filepath=animation_file)

# Simple camera setup - just back away and point at the character
# Character is at origin, about 1.8m tall
# Put camera 4 meters back, at chest height (1m), pointing forward
bpy.ops.object.camera_add(location=(0, -4, 1))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(90), 0, 0)  # 90 degrees = looking forward along Y axis
bpy.context.scene.camera = camera

# Simple bright light
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Render settings
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.engine = 'BLENDER_EEVEE'

# Go to frame 10 of the animation
bpy.context.scene.frame_set(10)

# Render
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
print(f"Rendered to: {output_path}")


