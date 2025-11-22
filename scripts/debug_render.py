"""
Debug script to figure out why characters aren't showing up in renders.
Outputs detailed info about bounding boxes, camera positions, etc.
"""

import bpy
import sys
import os
import math
import mathutils

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import blender_camera_utils as cam_utils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import ONE character for debugging
fbx_path = "/workspace/pose-factory/characters/X Bot.fbx"
print(f"\n{'='*60}")
print(f"IMPORTING: {fbx_path}")
print(f"{'='*60}")

bpy.ops.import_scene.fbx(filepath=fbx_path)
imported_objects = bpy.context.selected_objects

print(f"\n✓ Imported {len(imported_objects)} objects:")
for obj in imported_objects:
    print(f"  - {obj.name} (type: {obj.type})")
    print(f"    Location: {obj.location}")
    print(f"    Scale: {obj.scale}")
    print(f"    Rotation: {obj.rotation_euler}")

# Find armature
armature = cam_utils.find_armature_in_selection(imported_objects)
if not armature:
    print("\n❌ ERROR: No armature found!")
    sys.exit(1)

print(f"\n✓ Found armature: {armature.name}")
print(f"  Original scale: {armature.scale}")

# BEFORE normalization - check bounding box
print(f"\n{'='*60}")
print("BEFORE NORMALIZATION:")
print(f"{'='*60}")

scene = bpy.context.scene
scene.frame_set(1)
depsgraph = bpy.context.evaluated_depsgraph_get()

for obj in armature.children:
    if obj.type == 'MESH':
        obj_eval = obj.evaluated_get(depsgraph)
        print(f"\nMesh: {obj.name}")
        print(f"  Scale: {obj.scale}")
        print(f"  World matrix scale: {obj.matrix_world.to_scale()}")
        print(f"  Bound box corners:")
        for i, corner in enumerate(obj_eval.bound_box[:4]):  # Just first 4 corners
            world_pos = obj_eval.matrix_world @ mathutils.Vector(corner)
            print(f"    Corner {i}: {world_pos}")

# Normalize scale
print(f"\n{'='*60}")
print("NORMALIZING SCALE:")
print(f"{'='*60}")

cam_utils.normalize_mixamo_character(armature)

print(f"\n✓ After normalization:")
print(f"  Armature scale: {armature.scale}")
for obj in armature.children:
    if obj.type == 'MESH':
        print(f"  {obj.name} scale: {obj.scale}")

# Center at origin
armature.location = (0, 0, 0)
print(f"  Armature location: {armature.location}")

# Calculate bounding box
print(f"\n{'='*60}")
print("CALCULATING BOUNDING BOX:")
print(f"{'='*60}")

bbox_min, bbox_max = cam_utils.get_character_bounding_box(armature)
bbox_center = (bbox_min + bbox_max) / 2
bbox_size = bbox_max - bbox_min

print(f"\n✓ Bounding box calculated:")
print(f"  Min: {bbox_min}")
print(f"  Max: {bbox_max}")
print(f"  Center: {bbox_center}")
print(f"  Size: {bbox_size}")
print(f"  Diagonal: {bbox_size.length:.2f}")

# Calculate camera position
print(f"\n{'='*60}")
print("CALCULATING CAMERA POSITION:")
print(f"{'='*60}")

camera_fov = 50.0
padding_factor = 1.2

cam_pos, target = cam_utils.calculate_camera_position(
    bbox_min, bbox_max,
    camera_angle=0.0,  # Front view
    padding_factor=padding_factor,
    camera_fov=camera_fov
)

distance = (cam_pos - target).length

print(f"\n✓ Camera calculation:")
print(f"  FOV: {camera_fov}°")
print(f"  Padding: {padding_factor}")
print(f"  Camera position: {cam_pos}")
print(f"  Target position: {target}")
print(f"  Distance: {distance:.2f} units")

# Create camera
camera = cam_utils.setup_camera_for_character(
    armature,
    camera_angle=0.0,
    use_track_constraint=True,
    camera_fov=camera_fov
)

print(f"\n✓ Camera created:")
print(f"  Location: {camera.location}")
print(f"  Rotation: {camera.rotation_euler}")

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0

# Render settings
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 64

# Set camera clipping
camera.data.clip_start = 0.01  # Very close
camera.data.clip_end = 10000   # Very far

print(f"\n✓ Render settings:")
print(f"  Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"  Engine: {scene.render.engine}")
print(f"  Camera clip: {camera.data.clip_start} to {camera.data.clip_end}")

# Render
output_path = "/workspace/pose-factory/output/debug_render.png"
scene.render.filepath = output_path

print(f"\n{'='*60}")
print("RENDERING:")
print(f"{'='*60}")

bpy.ops.render.render(write_still=True)

print(f"\n✓ Rendered to: {output_path}")

# Check if any objects are in camera view
print(f"\n{'='*60}")
print("CHECKING VISIBILITY:")
print(f"{'='*60}")

# List all objects and their distance from camera
for obj in bpy.context.scene.objects:
    if obj.type in ['MESH', 'ARMATURE']:
        dist_from_camera = (camera.location - obj.location).length
        print(f"  {obj.name}: {dist_from_camera:.2f} units from camera")

print(f"\n{'='*60}")
print("DEBUG COMPLETE!")
print(f"{'='*60}")
print(f"\nUpload this debug render to check:")
print(f"  rclone copy {output_path} r2_pose_factory:pose-factory/output/")

