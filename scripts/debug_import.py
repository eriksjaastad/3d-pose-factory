import bpy
import os

# Test with just one animation
animation_file = "/workspace/pose-factory/animations/Dancing Twerk.fbx"

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import animation
print(f"Importing: {animation_file}")
bpy.ops.import_scene.fbx(filepath=animation_file)

# Debug: Print info about ALL imported objects
print("\n=== IMPORTED OBJECTS DEBUG ===")
for obj in bpy.data.objects:
    print(f"\nObject: {obj.name}")
    print(f"  Type: {obj.type}")
    print(f"  Location: {obj.location}")
    print(f"  Scale: {obj.scale}")
    print(f"  Rotation: {obj.rotation_euler}")
    
    if obj.type == 'MESH':
        # Get bounding box
        bbox = [obj.matrix_world @ v.co for v in obj.data.vertices]
        if bbox:
            min_z = min(v.z for v in bbox)
            max_z = max(v.z for v in bbox)
            print(f"  Height (Z): {min_z:.2f} to {max_z:.2f}")

# Set up camera VERY far away to see everything
bpy.ops.object.camera_add(location=(15, -15, 10))
camera = bpy.context.active_object
# Point camera at origin
camera.rotation_euler = (0.9, 0, 0.785)
bpy.context.scene.camera = camera

# Add light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Render settings
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.engine = 'BLENDER_EEVEE'

# Set to frame 10
bpy.context.scene.frame_set(10)

# Render from far away
output_path = "/workspace/pose-factory/output/debug_far.png"
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
print(f"\nDebug render (far away): {output_path}")

