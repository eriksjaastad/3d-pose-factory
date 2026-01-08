#!/usr/bin/env python3
"""
Render Static Character

Opens a .blend file and renders it with studio lighting.
Great for meshy.ai characters that don't have rigs.

Usage:
    blender --background --python render_static_character.py -- \
        --file /path/to/character.blend \
        --output /path/to/output.png
"""

import bpy
import sys
import argparse
import os
import math


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Render a static character")
    parser.add_argument("--file", type=str, required=True,
                        help="Path to .blend file")
    parser.add_argument("--output", type=str, default="/workspace/output/character-creation/render.png",
                        help="Output image path")
    parser.add_argument("--resolution", type=int, default=1024,
                        help="Render resolution (square)")
    parser.add_argument("--samples", type=int, default=64,
                        help="Render samples (higher = better quality, slower)")
    parser.add_argument("--angle", type=float, default=45,
                        help="Camera angle in degrees (0=front, 90=side)")
    
    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    else:
        args = parser.parse_args([])
    
    return args


def setup_studio_lighting():
    """Create professional 3-point studio lighting."""
    # Remove existing lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Key light (main light, front-left)
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 4))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 500
    key_light.data.size = 3
    key_light.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Fill light (softer, front-right)
    bpy.ops.object.light_add(type='AREA', location=(-2, -2, 2))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 200
    fill_light.data.size = 4
    fill_light.rotation_euler = (math.radians(60), 0, math.radians(-30))
    
    # Rim light (back light for edge definition)
    bpy.ops.object.light_add(type='AREA', location=(0, 4, 3))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Light"
    rim_light.data.energy = 300
    rim_light.data.size = 2
    rim_light.rotation_euler = (math.radians(-45), 0, math.radians(180))
    
    print("✅ Studio lighting set up (3-point)")
    return key_light, fill_light, rim_light


def setup_camera(target_obj, angle_degrees=45, distance_multiplier=2.5):
    """Position camera to frame the character."""
    # Remove existing cameras
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Calculate object bounds
    min_co = [float('inf')] * 3
    max_co = [float('-inf')] * 3
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for v in obj.bound_box:
                world_v = obj.matrix_world @ mathutils.Vector(v)
                for i in range(3):
                    min_co[i] = min(min_co[i], world_v[i])
                    max_co[i] = max(max_co[i], world_v[i])
    
    # Calculate center and size
    center = [(min_co[i] + max_co[i]) / 2 for i in range(3)]
    size = max(max_co[i] - min_co[i] for i in range(3))
    
    # Camera distance based on object size
    distance = size * distance_multiplier
    
    # Camera position (orbit around center)
    angle_rad = math.radians(angle_degrees)
    cam_x = center[0] + distance * math.sin(angle_rad)
    cam_y = center[1] - distance * math.cos(angle_rad)
    cam_z = center[2] + size * 0.3  # Slightly above center
    
    # Create camera
    bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
    camera = bpy.context.active_object
    camera.name = "Render_Camera"
    
    # Point at center
    direction = mathutils.Vector(center) - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    print(f"✅ Camera positioned at angle {angle_degrees}°")
    return camera


def setup_render_settings(resolution, samples):
    """Configure render settings for quality output."""
    scene = bpy.context.scene
    
    # Use Cycles for better quality
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = False  # Disabled - apt Blender lacks OpenImageDenoiser
    
    # Resolution
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    
    # Output format
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    
    # Transparent background
    scene.render.film_transparent = True
    
    # GPU if available
    prefs = bpy.context.preferences.addons.get('cycles')
    if prefs:
        prefs.preferences.compute_device_type = 'CUDA'
        bpy.context.scene.cycles.device = 'GPU'
    
    print(f"✅ Render settings: {resolution}x{resolution}, {samples} samples")


def add_simple_material():
    """Add a simple gray material to objects without materials."""
    # Create a simple material
    mat = bpy.data.materials.new(name="Simple_Gray")
    mat.use_nodes = True
    
    # Get the principled BSDF
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.5
    
    # Apply to meshes without materials
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
            print(f"   Added material to: {obj.name}")
    
    print("✅ Simple material added to unmaterialed objects")


def main():
    args = parse_args()
    
    # Need mathutils for camera positioning
    global mathutils
    import mathutils
    
    print("\n" + "=" * 60)
    print("  STATIC CHARACTER RENDERER")
    print("=" * 60)
    print(f"\nFile: {args.file}")
    print(f"Output: {args.output}")
    print(f"Resolution: {args.resolution}x{args.resolution}")
    print(f"Samples: {args.samples}")
    print(f"Camera angle: {args.angle}°")
    print("=" * 60 + "\n")
    
    # Check file exists
    if not os.path.exists(args.file):
        print(f"❌ ERROR: File not found: {args.file}")
        sys.exit(1)
    
    # Open the file
    print("📂 Opening file...")
    bpy.ops.wm.open_mainfile(filepath=args.file)
    print("   ✅ File opened")
    
    # Find mesh objects
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    print(f"\n📦 Found {len(mesh_objects)} mesh object(s)")
    
    if not mesh_objects:
        print("❌ No mesh objects found!")
        sys.exit(1)
    
    # Setup
    print("\n🔧 Setting up scene...")
    add_simple_material()
    setup_studio_lighting()
    camera = setup_camera(mesh_objects[0], args.angle)
    setup_render_settings(args.resolution, args.samples)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Render
    print(f"\n🎬 Rendering...")
    bpy.context.scene.render.filepath = args.output
    bpy.ops.render.render(write_still=True)
    
    # Check if output exists
    if os.path.exists(args.output):
        file_size = os.path.getsize(args.output) / 1024 / 1024
        print(f"\n✅ Render complete!")
        print(f"   📁 Output: {args.output}")
        print(f"   📏 Size: {file_size:.2f} MB")
    else:
        print(f"\n❌ Render failed - output not found")
    
    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

