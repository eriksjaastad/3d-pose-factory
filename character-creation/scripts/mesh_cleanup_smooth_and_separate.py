#!/usr/bin/env python3
"""
Mesh Cleanup + Body/Clothing Layer Tool
=======================================

Create a clean body mesh underneath the original dressed character.
Instead of trying to separate clothing geometry (which is difficult for
skin-tight outfits), we create two layers:

1. BodyMesh - smoothed, remeshed body that can be used for rigging
2. DressedMesh - the original mesh preserved intact

This layered approach works better for characters where clothing hugs
the body closely and can't be reliably separated geometrically.

Typical usage:

    blender --background --python mesh_cleanup_smooth_and_separate.py -- \
        --input character.blend \
        --output character_layered.blend \
        --object Mesh1.0

The script duplicates the target mesh before processing so the original
remains untouched. Results are written to a `SeparatedCharacter` collection.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Optional

import bpy


COLLECTION_NAME = "SeparatedCharacter"


@dataclass
class LayerSettings:
    remesh_voxel: float = 0.0075
    smooth_iterations: int = 12
    smooth_lambda: float = 0.2
    shrink_thickness: float = 0.008  # 8mm shrink gives cleanest boolean results
    body_cleanup_merge_dist: float = 0.0005
    mesh_cleanup_name: str = COLLECTION_NAME
    auto_hide_original: bool = True
    assign_materials: bool = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create layered body + dressed character meshes."
    )
    parser.add_argument("--input", help="Path to .blend file to open before processing")
    parser.add_argument("--output", help="Path to write processed .blend (optional)")
    parser.add_argument(
        "--object",
        help="Name of mesh object to process (defaults to largest mesh in scene)",
    )
    parser.add_argument(
        "--use-active",
        action="store_true",
        help="Operate on the currently active mesh instead of selecting by name.",
    )
    parser.add_argument("--remesh-voxel", type=float, default=0.0075)
    parser.add_argument("--smooth-iters", type=int, default=12)
    parser.add_argument("--smooth-lambda", type=float, default=0.2)
    parser.add_argument("--shrink", type=float, default=0.008)
    parser.add_argument(
        "--keep-original-visible",
        action="store_true",
        help="Do not hide the original source mesh after processing.",
    )
    parser.add_argument(
        "--no-materials",
        action="store_true",
        help="Skip assigning material slots to the meshes.",
    )
    parser.add_argument(
        "--collection",
        default=COLLECTION_NAME,
        help="Collection name for generated meshes.",
    )
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    return args


def log(msg: str) -> None:
    print(f"[mesh_cleanup] {msg}")


def ensure_object_mode() -> None:
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")


def deselect_all() -> None:
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)


def select_active(obj: bpy.types.Object) -> None:
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_modifier(obj: bpy.types.Object, modifier: bpy.types.Modifier) -> None:
    ensure_object_mode()
    select_active(obj)
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def duplicate_object(obj: bpy.types.Object, new_name: str, collection: bpy.types.Collection) -> bpy.types.Object:
    dup = obj.copy()
    dup.data = obj.data.copy()
    dup.name = new_name
    dup.matrix_world = obj.matrix_world.copy()
    collection.objects.link(dup)
    return dup


def add_collection(name: str) -> bpy.types.Collection:
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def find_target_object(name: Optional[str], use_active: bool) -> bpy.types.Object:
    if use_active:
        obj = bpy.context.view_layer.objects.active
        if not obj:
            raise SystemExit("No active object selected.")
        return obj

    if name:
        obj = bpy.data.objects.get(name)
        if not obj:
            raise SystemExit(f"Object '{name}' not found.")
        return obj

    mesh_objs = [o for o in bpy.data.objects if o.type == "MESH"]
    if not mesh_objs:
        raise SystemExit("Scene contains no mesh objects.")
    mesh_objs.sort(key=lambda o: len(o.data.vertices), reverse=True)
    return mesh_objs[0]


def cleanup_mesh(obj: bpy.types.Object, merge_distance: float = 0.0005) -> None:
    ensure_object_mode()
    select_active(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    try:
        bpy.ops.mesh.merge_by_distance(distance=merge_distance)
    except AttributeError:
        bpy.ops.mesh.remove_doubles(threshold=merge_distance)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def create_body_mesh(obj: bpy.types.Object, dressed_obj: bpy.types.Object, settings: LayerSettings) -> None:
    """
    Create a clean, smoothed body mesh that sits underneath the clothing.
    
    Process:
    1. Remesh to get clean topology
    2. Smooth to remove noise
    3. Shrink inward so it sits inside the dressed mesh
    4. Boolean difference with dressed mesh to carve away clothing overlap
    5. Additional smoothing to clean up boolean artifacts
    """
    log(f"Remeshing body at voxel {settings.remesh_voxel}")
    remesh = obj.modifiers.new("BodyRemesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = settings.remesh_voxel
    remesh.use_remove_disconnected = False
    apply_modifier(obj, remesh)

    if settings.smooth_iterations > 0:
        log(f"Smoothing body ({settings.smooth_iterations} iterations)")
        smooth = obj.modifiers.new("BodySmooth", "LAPLACIANSMOOTH")
        smooth.iterations = settings.smooth_iterations
        smooth.lambda_factor = settings.smooth_lambda
        smooth.lambda_border = settings.smooth_lambda
        apply_modifier(obj, smooth)

    log(f"Shrinking body inward by {settings.shrink_thickness}")
    solid = obj.modifiers.new("ShrinkBody", "SOLIDIFY")
    solid.thickness = -abs(settings.shrink_thickness)
    solid.offset = 1.0
    solid.use_even_offset = True
    solid.use_quality_normals = True
    apply_modifier(obj, solid)

    # Use dressed mesh as boolean cutter to remove clothing volume from body
    log("Carving body under clothing using boolean difference")
    boolean = obj.modifiers.new("CarveClothing", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.object = dressed_obj
    boolean.solver = "EXACT"
    apply_modifier(obj, boolean)

    # Moderate smoothing to clean up boolean edges
    log("Final smoothing pass")
    smooth2 = obj.modifiers.new("FinalSmooth", "LAPLACIANSMOOTH")
    smooth2.iterations = 8
    smooth2.lambda_factor = 0.15
    smooth2.lambda_border = 0.15
    apply_modifier(obj, smooth2)

    cleanup_mesh(obj, merge_distance=settings.body_cleanup_merge_dist)
    obj.name = "BodyMesh"
    obj.data.name = "BodyMeshData"


def create_or_get_material(name: str, color: tuple) -> bpy.types.Material:
    """Create a simple material with the given color, or return existing one."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # Get the principled BSDF node
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    
    return mat


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    """Assign a material to all faces of an object."""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def hide_object(obj: bpy.types.Object) -> None:
    obj.hide_set(True)
    obj.hide_render = True


def save_file(path: str) -> None:
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    log(f"Saved output to {path}")


def build_settings(args: argparse.Namespace) -> LayerSettings:
    return LayerSettings(
        remesh_voxel=args.remesh_voxel,
        smooth_iterations=args.smooth_iters,
        smooth_lambda=args.smooth_lambda,
        shrink_thickness=args.shrink,
        mesh_cleanup_name=args.collection,
        auto_hide_original=not args.keep_original_visible,
        assign_materials=not args.no_materials,
    )


def main() -> None:
    args = parse_args()
    settings = build_settings(args)

    if args.input:
        if not os.path.exists(args.input):
            raise SystemExit(f"Input file not found: {args.input}")
        log(f"Opening {args.input}")
        bpy.ops.wm.open_mainfile(filepath=args.input)

    target = find_target_object(args.object, args.use_active)
    if target.type != "MESH":
        raise SystemExit(f"Target object '{target.name}' is not a mesh.")

    log(f"Processing mesh '{target.name}' ({len(target.data.vertices):,} verts)")

    result_collection = add_collection(settings.mesh_cleanup_name)
    ensure_object_mode()

    # Step 1: Create dressed mesh first (copy of original, preserved intact)
    dressed_obj = duplicate_object(target, "DressedMesh", result_collection)
    dressed_obj.data.name = "DressedMeshData"
    log(f"Created DressedMesh ({len(dressed_obj.data.vertices):,} verts)")
    
    # Step 2: Create body mesh (remesh + smooth + shrink + boolean carve under clothes)
    body_obj = duplicate_object(target, f"{target.name}_Body", result_collection)
    create_body_mesh(body_obj, dressed_obj, settings)
    log(f"Created BodyMesh ({len(body_obj.data.vertices):,} verts)")
    
    # Step 3: Assign materials for easy identification
    if settings.assign_materials:
        log("Assigning materials to layers")
        body_mat = create_or_get_material("BodyMaterial", (0.8, 0.6, 0.5))  # Skin tone
        dressed_mat = create_or_get_material("DressedMaterial", (0.6, 0.6, 0.8))  # Lavender (like reference)
        
        assign_material(body_obj, body_mat)
        assign_material(dressed_obj, dressed_mat)

    # Step 4: Hide original
    if settings.auto_hide_original:
        log("Hiding original mesh")
        hide_object(target)

    # Summary
    log("=" * 50)
    log("LAYERED OUTPUT CREATED:")
    log(f"  BodyMesh:    {len(body_obj.data.vertices):,} verts (smooth inner body for rigging)")
    log(f"  DressedMesh: {len(dressed_obj.data.vertices):,} verts (original with clothing intact)")
    log("")
    log("Usage tips:")
    log("  - Use BodyMesh for rigging/animation (clean topology)")
    log("  - Use DressedMesh for rendering (preserves clothing detail)")
    log("  - BodyMesh sits slightly inside DressedMesh (no clipping)")
    log("=" * 50)

    if args.output:
        save_file(args.output)
    else:
        log("Processing complete (no output path supplied, scene modified in-place).")


if __name__ == "__main__":
    main()
