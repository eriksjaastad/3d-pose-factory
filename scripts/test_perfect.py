import bpy

# Clear and import
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.fbx(filepath="/workspace/pose-factory/characters/X Bot.fbx")

# Camera position that works - distance 3.5, height 1.0
bpy.ops.object.camera_add(location=(0, -3.5, 1.0))
camera = bpy.context.active_object
camera.rotation_euler = (1.5708, 0, 0)  # 90 degrees, looking forward
bpy.context.scene.camera = camera

# Light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
bpy.context.active_object.data.energy = 3.0

# Render
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.filepath = "/workspace/pose-factory/output/test_perfect.png"
bpy.ops.render.render(write_still=True)
print("✓ Rendered with camera at distance 3.5, height 1.0!")

