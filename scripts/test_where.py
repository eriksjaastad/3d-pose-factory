import bpy
import mathutils

# Clear and import
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.fbx(filepath="/workspace/pose-factory/characters/X Bot.fbx")

# Get all objects
print("\n" + "="*60)
print("ALL OBJECTS IN SCENE:")
print("="*60)
for obj in bpy.data.objects:
    print(f"\n{obj.name} ({obj.type})")
    print(f"  Location: {obj.location}")
    print(f"  Scale: {obj.scale}")
    print(f"  Rotation (radians): {obj.rotation_euler}")
    print(f"  Rotation (degrees): ({obj.rotation_euler.x * 57.3:.1f}°, {obj.rotation_euler.y * 57.3:.1f}°, {obj.rotation_euler.z * 57.3:.1f}°)")
    
    if obj.type == 'MESH':
        bbox = obj.bound_box
        print(f"  Bounding box (local):")
        print(f"    X: {min([v[0] for v in bbox]):.2f} to {max([v[0] for v in bbox]):.2f}")
        print(f"    Y: {min([v[1] for v in bbox]):.2f} to {max([v[1] for v in bbox]):.2f}")
        print(f"    Z: {min([v[2] for v in bbox]):.2f} to {max([v[2] for v in bbox]):.2f}")
        
        # World space
        matrix = obj.matrix_world
        world_coords = [matrix @ mathutils.Vector(corner) for corner in bbox]
        print(f"  Bounding box (world):")
        print(f"    X: {min([v[0] for v in world_coords]):.4f} to {max([v[0] for v in world_coords]):.4f}")
        print(f"    Y: {min([v[1] for v in world_coords]):.4f} to {max([v[1] for v in world_coords]):.4f}")
        print(f"    Z: {min([v[2] for v in world_coords]):.4f} to {max([v[2] for v in world_coords]):.4f}")

print("\n" + "="*60)
print("CAMERA at (0, -10, 2) looking forward")
print("="*60)

# Camera
bpy.ops.object.camera_add(location=(0, -10, 2))
camera = bpy.context.active_object
camera.rotation_euler = (1.5708, 0, 0)
bpy.context.scene.camera = camera

# Light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))

# Render
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.filepath = "/workspace/pose-factory/output/test_where.png"
bpy.ops.render.render(write_still=True)
print("\n✓ Rendered to: output/test_where.png")

