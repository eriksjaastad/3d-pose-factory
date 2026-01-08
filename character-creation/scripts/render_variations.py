#!/usr/bin/env python3
"""
Render Variations - Stage 1 of Character Pipeline

Opens a mesh and renders multiple variations with different:
- Colors (skin tones, clothing colors)
- Lighting setups
- Camera angles

Usage:
    blender --background --python render_variations.py -- \
        --file /path/to/character.blend \
        --output-dir /path/to/output/ \
        --variations 5

Output:
    Creates numbered images: variation_001.png, variation_002.png, etc.
"""

import bpy
import sys
import argparse
import os
import math
import random
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Render mesh variations")
    parser.add_argument("--file", type=str, required=True,
                        help="Path to .blend file")
    parser.add_argument("--output-dir", type=str, default="/workspace/output/character-creation/variations",
                        help="Output directory for renders")
    parser.add_argument("--variations", type=int, default=5,
                        help="Number of variations to render")
    parser.add_argument("--resolution", type=int, default=1024,
                        help="Render resolution (square)")
    parser.add_argument("--samples", type=int, default=32,
                        help="Render samples")
    
    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    else:
        args = parser.parse_args([])
    
    return args


# Color palettes for variations
SKIN_TONES = [
    (0.95, 0.87, 0.78, 1.0),  # Light
    (0.87, 0.72, 0.60, 1.0),  # Medium light
    (0.76, 0.57, 0.42, 1.0),  # Medium
    (0.55, 0.38, 0.26, 1.0),  # Medium dark
    (0.36, 0.22, 0.14, 1.0),  # Dark
]

CLOTHING_COLORS = [
    (0.8, 0.2, 0.2, 1.0),    # Red
    (0.2, 0.5, 0.8, 1.0),    # Blue
    (0.2, 0.7, 0.3, 1.0),    # Green
    (0.9, 0.7, 0.2, 1.0),    # Yellow/Gold
    (0.6, 0.3, 0.7, 1.0),    # Purple
    (0.9, 0.5, 0.6, 1.0),    # Pink
    (0.3, 0.3, 0.3, 1.0),    # Dark gray
    (0.9, 0.9, 0.9, 1.0),    # White
    (0.1, 0.1, 0.1, 1.0),    # Black
    (0.6, 0.4, 0.2, 1.0),    # Brown
]

LIGHTING_SETUPS = [
    {"name": "Studio", "key": 500, "fill": 200, "rim": 300, "key_pos": (3, -3, 4)},
    {"name": "Dramatic", "key": 800, "fill": 50, "rim": 400, "key_pos": (4, -2, 3)},
    {"name": "Soft", "key": 300, "fill": 250, "rim": 150, "key_pos": (2, -4, 5)},
    {"name": "Backlit", "key": 200, "fill": 100, "rim": 600, "key_pos": (1, -2, 3)},
    {"name": "Side", "key": 600, "fill": 150, "rim": 200, "key_pos": (5, 0, 3)},
]


def clear_lights():
    """Remove all lights from scene."""
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)


def setup_lighting(config):
    """Create lighting based on config."""
    clear_lights()
    
    # Key light
    bpy.ops.object.light_add(type='AREA', location=config["key_pos"])
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = config["key"]
    key.data.size = 3
    key.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Fill light (opposite side)
    fill_pos = (-config["key_pos"][0], config["key_pos"][1], config["key_pos"][2] * 0.7)
    bpy.ops.object.light_add(type='AREA', location=fill_pos)
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = config["fill"]
    fill.data.size = 4
    fill.rotation_euler = (math.radians(60), 0, math.radians(-30))
    
    # Rim light (back)
    bpy.ops.object.light_add(type='AREA', location=(0, 4, 3))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = config["rim"]
    rim.data.size = 2
    rim.rotation_euler = (math.radians(-45), 0, math.radians(180))


def setup_camera(angle_degrees=45):
    """Position camera at given angle."""
    import mathutils
    
    # Remove existing cameras
    for obj in list(bpy.data.objects):
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
    
    center = [(min_co[i] + max_co[i]) / 2 for i in range(3)]
    size = max(max_co[i] - min_co[i] for i in range(3))
    distance = size * 2.5
    
    angle_rad = math.radians(angle_degrees)
    cam_x = center[0] + distance * math.sin(angle_rad)
    cam_y = center[1] - distance * math.cos(angle_rad)
    cam_z = center[2] + size * 0.3
    
    bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
    camera = bpy.context.active_object
    camera.name = "Render_Camera"
    
    direction = mathutils.Vector(center) - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    bpy.context.scene.camera = camera
    return camera


def create_material(name, base_color):
    """Create a simple colored material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = 0.5
    
    return mat


def apply_color_variation(variation_num):
    """Apply random colors to the mesh."""
    # Pick colors for this variation
    random.seed(variation_num * 42)  # Reproducible randomness
    
    main_color = random.choice(CLOTHING_COLORS)
    accent_color = random.choice(CLOTHING_COLORS)
    
    # Create materials
    main_mat = create_material(f"Main_{variation_num}", main_color)
    
    # Apply to all meshes
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Clear existing materials
            obj.data.materials.clear()
            obj.data.materials.append(main_mat)
    
    return {"main_color": main_color[:3], "accent_color": accent_color[:3]}


def setup_render_settings(resolution, samples):
    """Configure render settings."""
    scene = bpy.context.scene
    
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = False  # apt Blender lacks denoiser
    
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    
    # Try GPU
    try:
        prefs = bpy.context.preferences.addons.get('cycles')
        if prefs:
            prefs.preferences.compute_device_type = 'CUDA'
            scene.cycles.device = 'GPU'
    except Exception as e:
        # DNA Fix: Log GPU setup error
        logger.warning(f"Could not enable GPU rendering: {e}")


def main():
    args = parse_args()
    
    print("\n" + "=" * 60)
    print("  RENDER VARIATIONS - Stage 1")
    print("=" * 60)
    print(f"\nFile: {args.file}")
    print(f"Output: {args.output_dir}")
    print(f"Variations: {args.variations}")
    print("=" * 60 + "\n")
    
    # Check file exists
    if not os.path.exists(args.file):
        print(f"❌ ERROR: File not found: {args.file}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Open the file
    print("📂 Opening file...")
    bpy.ops.wm.open_mainfile(filepath=args.file)
    
    # Setup render settings (once)
    setup_render_settings(args.resolution, args.samples)
    
    # Track metadata for each variation
    metadata = []
    
    # Generate variations
    for i in range(1, args.variations + 1):
        print(f"\n🎨 Variation {i}/{args.variations}")
        
        # Pick random parameters
        random.seed(i * 123)
        lighting = random.choice(LIGHTING_SETUPS)
        angle = random.choice([0, 30, 45, 60, 90, -30, -45])
        
        # Apply variation
        colors = apply_color_variation(i)
        setup_lighting(lighting)
        setup_camera(angle)
        
        # Render
        output_path = os.path.join(args.output_dir, f"variation_{i:03d}.png")
        bpy.context.scene.render.filepath = output_path
        
        print(f"   Lighting: {lighting['name']}, Angle: {angle}°")
        print(f"   Rendering...")
        
        bpy.ops.render.render(write_still=True)
        
        if os.path.exists(output_path):
            print(f"   ✅ Saved: {output_path}")
            metadata.append({
                "variation": i,
                "file": f"variation_{i:03d}.png",
                "lighting": lighting["name"],
                "angle": angle,
                "colors": colors
            })
        else:
            print(f"   ❌ Failed to save")
    
    # Save metadata
    metadata_path = os.path.join(args.output_dir, "variations_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\n📋 Metadata saved: {metadata_path}")
    
    print("\n" + "=" * 60)
    print(f"  ✅ Stage 1 Complete: {len(metadata)} variations rendered")
    print("=" * 60 + "\n")
    
    # Return metadata path for next stage
    print(f"STAGE1_OUTPUT={args.output_dir}")


if __name__ == "__main__":
    main()
