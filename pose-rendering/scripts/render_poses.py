import bpy
import math
import os

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create simple stick figure using cylinders
def create_stick_figure():
    # Body parts as cylinders
    parts = [
        ("head", (0, 0, 1.7), 0.15, 0.25),
        ("torso", (0, 0, 1.2), 0.12, 0.6),
        ("left_arm", (-0.3, 0, 1.4), 0.05, 0.5),
        ("right_arm", (0.3, 0, 1.4), 0.05, 0.5),
        ("left_leg", (-0.15, 0, 0.5), 0.08, 0.9),
        ("right_leg", (0.15, 0, 0.5), 0.08, 0.9),
    ]
    
    for name, location, radius, depth in parts:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
        bpy.context.active_object.name = name
    
    return bpy.data.objects

# Add camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

# Add light
bpy.ops.object.light_add(type='SUN', location=(2, 2, 5))

# Create figure
create_stick_figure()

# Set render settings
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Render 5 different poses
output_dir = "/workspace/pose-factory/output/frames"
os.makedirs(output_dir, exist_ok=True)

for i in range(5):
    # Simple pose variation - rotate arms
    if "left_arm" in bpy.data.objects:
        bpy.data.objects["left_arm"].rotation_euler = (0, 0, math.radians(30 * i))
    if "right_arm" in bpy.data.objects:
        bpy.data.objects["right_arm"].rotation_euler = (0, 0, math.radians(-30 * i))
    
    # Render
    filepath = f"{output_dir}/pose_{i:03d}.png"
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {filepath}")

print("All renders complete!")

