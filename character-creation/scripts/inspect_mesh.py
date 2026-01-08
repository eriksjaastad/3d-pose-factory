#!/usr/bin/env python3
"""
Inspect Meshy.ai Character Mesh

Opens a .blend file and reports on its contents:
- Objects (meshes, armatures, empties, etc.)
- Materials and textures
- Animation data
- Mesh statistics

Usage:
    blender --background --python inspect_mesh.py -- --file /path/to/file.blend
"""

import bpy
import sys
import argparse
import os


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Inspect a Blender file")
    parser.add_argument("--file", type=str, required=True,
                        help="Path to .blend file to inspect")
    
    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    else:
        args = parser.parse_args([])
    
    return args


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def inspect_objects():
    """Inspect all objects in the scene."""
    print_header("OBJECTS IN SCENE")
    
    objects_by_type = {}
    for obj in bpy.data.objects:
        obj_type = obj.type
        if obj_type not in objects_by_type:
            objects_by_type[obj_type] = []
        objects_by_type[obj_type].append(obj)
    
    for obj_type, objects in sorted(objects_by_type.items()):
        print(f"\n📦 {obj_type} ({len(objects)})")
        for obj in objects:
            parent_info = f" → parent: {obj.parent.name}" if obj.parent else ""
            location = f"loc: ({obj.location.x:.2f}, {obj.location.y:.2f}, {obj.location.z:.2f})"
            print(f"   • {obj.name} [{location}]{parent_info}")


def inspect_meshes():
    """Inspect mesh data."""
    print_header("MESH DETAILS")
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            print(f"\n🔷 {obj.name}")
            print(f"   Vertices: {len(mesh.vertices):,}")
            print(f"   Edges: {len(mesh.edges):,}")
            print(f"   Faces: {len(mesh.polygons):,}")
            print(f"   UV Maps: {len(mesh.uv_layers)}")
            for uv in mesh.uv_layers:
                print(f"      • {uv.name}")
            print(f"   Vertex Colors: {len(mesh.color_attributes)}")
            for vc in mesh.color_attributes:
                print(f"      • {vc.name}")


def inspect_armatures():
    """Inspect armature/skeleton data."""
    print_header("ARMATURES (SKELETONS)")
    
    armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
    
    if not armatures:
        print("\n⚠️  No armatures found")
        print("   (This mesh is NOT rigged - cannot apply Mixamo animations directly)")
        return False
    
    for arm_obj in armatures:
        armature = arm_obj.data
        print(f"\n🦴 {arm_obj.name}")
        print(f"   Bones: {len(armature.bones)}")
        
        # Show bone hierarchy (just root bones and their children count)
        root_bones = [b for b in armature.bones if b.parent is None]
        print(f"   Root bones: {len(root_bones)}")
        for bone in root_bones[:5]:  # Show first 5
            child_count = len(bone.children_recursive)
            print(f"      • {bone.name} ({child_count} descendants)")
        if len(root_bones) > 5:
            print(f"      ... and {len(root_bones) - 5} more root bones")
    
    return True


def inspect_materials():
    """Inspect materials and textures."""
    print_header("MATERIALS & TEXTURES")
    
    if not bpy.data.materials:
        print("\n⚠️  No materials found")
        return
    
    for mat in bpy.data.materials:
        print(f"\n🎨 {mat.name}")
        if mat.use_nodes:
            print("   Uses node tree: Yes")
            # Count texture nodes
            tex_nodes = [n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE']
            print(f"   Image textures: {len(tex_nodes)}")
            for tex in tex_nodes:
                if tex.image:
                    print(f"      • {tex.image.name} ({tex.image.filepath})")
                else:
                    print(f"      • {tex.name} (no image loaded)")
        else:
            print("   Uses node tree: No (simple material)")


def inspect_animations():
    """Inspect animation data."""
    print_header("ANIMATIONS")
    
    # Check for actions
    if bpy.data.actions:
        print(f"\n🎬 Actions found: {len(bpy.data.actions)}")
        for action in bpy.data.actions:
            frame_range = action.frame_range
            print(f"   • {action.name}")
            print(f"     Frames: {int(frame_range[0])} - {int(frame_range[1])}")
            print(f"     Duration: {int(frame_range[1] - frame_range[0])} frames")
    else:
        print("\n⚠️  No animation actions found")
    
    # Check for shape keys
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.data.shape_keys:
            print(f"\n📐 Shape Keys on {obj.name}:")
            for key in obj.data.shape_keys.key_blocks:
                print(f"   • {key.name}")


def print_summary(has_armature):
    """Print a summary with next steps."""
    print_header("SUMMARY & NEXT STEPS")
    
    mesh_count = len([o for o in bpy.data.objects if o.type == 'MESH'])
    mat_count = len(bpy.data.materials)
    
    print(f"\n📊 Found: {mesh_count} mesh(es), {mat_count} material(s)")
    
    if has_armature:
        print("\n✅ This character IS RIGGED!")
        print("   → Can potentially apply Mixamo animations")
        print("   → Need to check bone naming compatibility")
    else:
        print("\n⚠️  This character is NOT RIGGED")
        print("   → Cannot directly apply Mixamo animations")
        print("   → Options:")
        print("      1. Upload to Mixamo for auto-rigging")
        print("      2. Manually rig in Blender")
        print("      3. Use as static prop/character")


def main():
    args = parse_args()
    
    print("\n" + "🔍" * 30)
    print("  MESHY.AI CHARACTER INSPECTOR")
    print("🔍" * 30)
    print(f"\nFile: {args.file}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"\n❌ ERROR: File not found: {args.file}")
        sys.exit(1)
    
    # Open the file
    print(f"\n📂 Opening file...")
    bpy.ops.wm.open_mainfile(filepath=args.file)
    print("   ✓ File opened successfully")
    
    # Run inspections
    inspect_objects()
    inspect_meshes()
    has_armature = inspect_armatures()
    inspect_materials()
    inspect_animations()
    
    # Print summary
    print_summary(has_armature)
    
    print("\n" + "=" * 60)
    print("  Inspection complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

