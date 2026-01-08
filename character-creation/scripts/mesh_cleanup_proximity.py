#!/usr/bin/env python3
"""
Mesh Cleanup using Vertex-Weight-Proximity + Mask approach.

Instead of boolean operations, this uses proximity-based vertex weighting
to mask/delete body vertices that are too close to the clothing mesh.
This often produces cleaner results than boolean intersections.

Usage:
    blender --background --python mesh_cleanup_proximity.py -- \
        --input character.blend \
        --output character_clean.blend \
        --object Mesh1.0
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
class ProximitySettings:
    remesh_voxel: float = 0.0075
    smooth_iterations: int = 12
    smooth_lambda: float = 0.2
    shrink_thickness: float = 0.004
    proximity_min: float = 0.0
    proximity_max: float = 0.006  # verts closer than this to clothes get masked
    body_cleanup_merge_dist: float = 0.0005
    mesh_cleanup_name: str = COLLECTION_NAME
    auto_hide_original: bool = True
    assign_materials: bool = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create layered body + dressed meshes using proximity masking."
    )
    parser.add_argument("--input", help="Path to .blend file to open")
    parser.add_argument("--output", help="Path to write processed .blend")
    parser.add_argument("--object", help="Name of mesh object to process")
    parser.add_argument("--use-active", action="store_true")
    parser.add_argument("--remesh-voxel", type=float, default=0.0075)
    parser.add_argument("--smooth-iters", type=int, default=12)
    parser.add_argument("--smooth-lambda", type=float, default=0.2)
    parser.add_argument("--shrink", type=float, default=0.004)
    parser.add_argument(
        "--proximity-distance",
        type=float,
        default=0.006,
        help="Body verts closer than this to clothing will be removed.",
    )
    parser.add_argument("--keep-original-visible", action="store_true")
    parser.add_argument("--no-materials", action="store_true")
    parser.add_argument("--collection", default=COLLECTION_NAME)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    return args


def log(msg: str) -> None:
    print(f"[proximity_cleanup] {msg}")


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


def create_body_mesh_with_proximity(
    body_obj: bpy.types.Object,
    dressed_obj: bpy.types.Object,
    settings: ProximitySettings,
) -> None:
    """
    Create body mesh using proximity-based masking instead of boolean.
    
    1. Remesh and smooth the body
    2. Shrink it inward
    3. Use Vertex Weight Proximity to weight verts by distance to clothing
    4. Use Mask modifier to hide/delete verts too close to clothing
    """
    log(f"Remeshing body at voxel {settings.remesh_voxel}")
    remesh = body_obj.modifiers.new("BodyRemesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = settings.remesh_voxel
    remesh.use_remove_disconnected = False
    apply_modifier(body_obj, remesh)

    if settings.smooth_iterations > 0:
        log(f"Smoothing body ({settings.smooth_iterations} iterations)")
        smooth = body_obj.modifiers.new("BodySmooth", "LAPLACIANSMOOTH")
        smooth.iterations = settings.smooth_iterations
        smooth.lambda_factor = settings.smooth_lambda
        smooth.lambda_border = settings.smooth_lambda
        apply_modifier(body_obj, smooth)

    log(f"Shrinking body inward by {settings.shrink_thickness}")
    solid = body_obj.modifiers.new("ShrinkBody", "SOLIDIFY")
    solid.thickness = -abs(settings.shrink_thickness)
    solid.offset = 1.0
    solid.use_even_offset = True
    solid.use_quality_normals = True
    apply_modifier(body_obj, solid)

    # Create vertex group for proximity weighting
    log("Creating proximity vertex group")
    vg = body_obj.vertex_groups.new(name="under_clothes")
    
    # Initially assign all verts with weight 1.0
    all_verts = [v.index for v in body_obj.data.vertices]
    vg.add(all_verts, 1.0, 'REPLACE')

    # Add Vertex Weight Proximity modifier
    log(f"Adding proximity weighting (distance threshold: {settings.proximity_max}m)")
    prox = body_obj.modifiers.new("ClothingProximity", "VERTEX_WEIGHT_PROXIMITY")
    prox.vertex_group = "under_clothes"
    prox.target = dressed_obj
    prox.proximity_mode = 'GEOMETRY'
    prox.proximity_geometry = {'FACE'}
    prox.min_dist = settings.proximity_min
    prox.max_dist = settings.proximity_max
    # Verts at min_dist get weight 1, at max_dist get weight 0
    # We want to DELETE verts close to clothing, so we'll invert
    prox.falloff_type = 'LINEAR'
    apply_modifier(body_obj, prox)

    # Add Mask modifier to hide verts with high weight (close to clothing)
    log("Applying mask to remove body under clothing")
    mask = body_obj.modifiers.new("MaskUnderClothes", "MASK")
    mask.vertex_group = "under_clothes"
    mask.invert_vertex_group = True  # Hide verts WITH weight (close to clothes)
    mask.threshold = 0.5
    apply_modifier(body_obj, mask)

    # Final smoothing
    log("Final smoothing pass")
    smooth2 = body_obj.modifiers.new("FinalSmooth", "LAPLACIANSMOOTH")
    smooth2.iterations = 6
    smooth2.lambda_factor = 0.15
    smooth2.lambda_border = 0.15
    apply_modifier(body_obj, smooth2)

    cleanup_mesh(body_obj, merge_distance=settings.body_cleanup_merge_dist)
    body_obj.name = "BodyMesh"
    body_obj.data.name = "BodyMeshData"


def create_or_get_material(name: str, color: tuple) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    return mat


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
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


def build_settings(args: argparse.Namespace) -> ProximitySettings:
    return ProximitySettings(
        remesh_voxel=args.remesh_voxel,
        smooth_iterations=args.smooth_iters,
        smooth_lambda=args.smooth_lambda,
        shrink_thickness=args.shrink,
        proximity_max=args.proximity_distance,
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

    # Step 1: Create dressed mesh (copy of original)
    dressed_obj = duplicate_object(target, "DressedMesh", result_collection)
    dressed_obj.data.name = "DressedMeshData"
    log(f"Created DressedMesh ({len(dressed_obj.data.vertices):,} verts)")

    # Step 2: Create body mesh with proximity-based masking
    body_obj = duplicate_object(target, f"{target.name}_Body", result_collection)
    create_body_mesh_with_proximity(body_obj, dressed_obj, settings)
    log(f"Created BodyMesh ({len(body_obj.data.vertices):,} verts)")

    # Step 3: Assign materials
    if settings.assign_materials:
        log("Assigning materials")
        body_mat = create_or_get_material("BodyMaterial", (0.8, 0.6, 0.5))
        dressed_mat = create_or_get_material("DressedMaterial", (0.6, 0.6, 0.8))
        assign_material(body_obj, body_mat)
        assign_material(dressed_obj, dressed_mat)

    # Step 4: Hide original
    if settings.auto_hide_original:
        log("Hiding original mesh")
        hide_object(target)

    log("=" * 50)
    log("PROXIMITY-BASED LAYERED OUTPUT:")
    log(f"  BodyMesh:    {len(body_obj.data.vertices):,} verts")
    log(f"  DressedMesh: {len(dressed_obj.data.vertices):,} verts")
    log("=" * 50)

    if args.output:
        save_file(args.output)


if __name__ == "__main__":
    main()

