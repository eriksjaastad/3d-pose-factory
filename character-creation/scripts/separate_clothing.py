#!/usr/bin/env python3
"""
Automated clothing/body separation for single-mesh characters.

Workflow:
1. Load a source .blend file.
2. Duplicate the base mesh to create body + clothing candidates.
3. Remesh + smooth + shrink the body copy to form a watertight inner mesh.
4. Boolean-difference the shrunk body from the original to isolate clothing.
5. Save the result (body + clothing objects) into a new .blend file.

Usage:
    blender --background --python separate_clothing.py -- \\
        --file path/to/source.blend \\
        --output path/to/destination.blend \\
        [--base-object Mesh1.0] \\
        [--voxel-size 0.0075] \\
        [--smooth-iterations 12] \\
        [--shrink-thickness 0.004]

Tune voxel size + shrink thickness depending on your mesh scale.
"""

import argparse
import os
import sys

import bmesh
import bpy
from mathutils import kdtree


def parse_args():
    parser = argparse.ArgumentParser(description="Separate clothing from body mesh")
    parser.add_argument("--file", required=True, help="Path to source .blend file")
    parser.add_argument("--output", required=True, help="Path to save processed .blend")
    parser.add_argument(
        "--base-object",
        default=None,
        help="Name of mesh object to process (defaults to largest mesh)",
    )
    parser.add_argument(
        "--voxel-size",
        type=float,
        default=0.0075,
        help="Voxel size for remeshing (smaller = more detail, slower)",
    )
    parser.add_argument(
        "--smooth-iterations",
        type=int,
        default=12,
        help="Laplacian smooth iterations for body mesh",
    )
    parser.add_argument(
        "--shrink-thickness",
        type=float,
        default=0.004,
        help="Negative solidify thickness to shrink body inside clothing",
    )
    parser.add_argument(
        "--collection-name",
        default="SeparatedCharacter",
        help="Collection to store generated body/clothing meshes",
    )
    parser.add_argument(
        "--remove-skin-distance",
        type=float,
        default=0.0025,
        help="Delete clothing vertices closer than this distance (meters) to the body mesh. "
        "Set to 0 to keep skin surfaces.",
    )
    parser.add_argument(
        "--split-loose",
        action="store_true",
        help="Split the clothing mesh into loose parts (hair, shoes, top, etc.)",
    )
    parser.add_argument(
        "--min-part-verts",
        type=int,
        default=2000,
        help="Minimum vertex count required to keep a separated clothing part "
        "(only used when --split-loose is set). Smaller parts are discarded as noise.",
    )
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    return args


def log(msg):
    print(f"[separate_clothing] {msg}")


def ensure_object_mode():
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")


def deselect_all():
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)


def select_active(obj):
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_modifier(obj, modifier):
    ensure_object_mode()
    select_active(obj)
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def duplicate_object(obj, name, collection):
    dup = obj.copy()
    dup.data = obj.data.copy()
    dup.name = name
    collection.objects.link(dup)
    dup.matrix_world = obj.matrix_world.copy()
    return dup


def add_collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def find_base_object(name_hint=None):
    mesh_objs = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    if not mesh_objs:
        raise RuntimeError("No mesh objects found in scene.")

    if name_hint:
        obj = bpy.data.objects.get(name_hint)
        if not obj:
            raise RuntimeError(f"Mesh '{name_hint}' not found in file.")
        return obj

    mesh_objs.sort(key=lambda obj: len(obj.data.vertices), reverse=True)
    return mesh_objs[0]


def cleanup_mesh(obj):
    ensure_object_mode()
    select_active(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0005)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def configure_body_mesh(obj, voxel_size, smooth_iterations, shrink_thickness):
    log(f"Remeshing body with voxel size {voxel_size}")
    remesh = obj.modifiers.new("Remesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = voxel_size
    if hasattr(remesh, "use_fix_poles"):
        remesh.use_fix_poles = True
    remesh.use_remove_disconnected = False
    apply_modifier(obj, remesh)

    if smooth_iterations > 0:
        log(f"Smoothing body mesh ({smooth_iterations} iterations)")
        smooth = obj.modifiers.new("BodySmooth", "LAPLACIANSMOOTH")
        smooth.iterations = smooth_iterations
        smooth.lambda_factor = 0.2
        smooth.lambda_border = 0.2
        apply_modifier(obj, smooth)

    log(f"Shrinking body mesh inward by {shrink_thickness}")
    solid = obj.modifiers.new("ShrinkBody", "SOLIDIFY")
    solid.thickness = -abs(shrink_thickness)
    solid.offset = 1.0
    solid.use_even_offset = True
    solid.use_quality_normals = True
    apply_modifier(obj, solid)

    cleanup_mesh(obj)
    obj.name = "BodyMesh"
    obj.data.name = "BodyMeshData"


def configure_clothing_mesh(obj, body_obj):
    log("Running boolean difference to isolate clothing shell")
    boolean = obj.modifiers.new("ExtractClothing", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = body_obj
    apply_modifier(obj, boolean)

    cleanup_mesh(obj)
    obj.name = "ClothingMesh"
    obj.data.name = "ClothingMeshData"


def build_body_kdtree(body_obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = body_obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    kd = kdtree.KDTree(len(mesh.vertices))
    matrix = body_obj.matrix_world

    for i, v in enumerate(mesh.vertices):
        kd.insert(matrix @ v.co, i)

    kd.balance()
    eval_obj.to_mesh_clear()
    return kd


def remove_skin_surfaces(clothing_obj, body_obj, distance):
    log(f"Removing vertices within {distance}m of body mesh to strip skin surfaces")
    kd = build_body_kdtree(body_obj)
    matrix = clothing_obj.matrix_world

    bm = bmesh.new()
    bm.from_mesh(clothing_obj.data)
    remove_verts = []

    for vert in bm.verts:
        world_co = matrix @ vert.co
        nearest = kd.find(world_co)
        if nearest is None:
            continue
        _, _, dist = nearest
        if dist is not None and dist < distance:
            remove_verts.append(vert)

    if remove_verts:
        bmesh.ops.delete(bm, geom=remove_verts, context="VERTS")

    bm.to_mesh(clothing_obj.data)
    bm.free()
    clothing_obj.data.update()
    cleanup_mesh(clothing_obj)


def split_loose_parts(clothing_obj, collection, min_vertices):
    log("Splitting clothing into loose parts")
    ensure_object_mode()
    select_active(clothing_obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")

    parts = bpy.context.selected_objects
    kept = []
    for idx, part in enumerate(parts):
        vert_count = len(part.data.vertices)
        if vert_count < min_vertices:
            log(f"Discarding part '{part.name}' ({vert_count} verts) below threshold")
            bpy.data.objects.remove(part, do_unlink=True)
            continue
        new_name = f"ClothingPart_{idx:02d}"
        part.name = new_name
        part.data.name = f"{new_name}Data"
        if collection not in part.users_collection:
            collection.objects.link(part)
        kept.append(part)

    return kept


def save_file(output_path):
    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    log(f"Saved separated meshes to {output_path}")


def main():
    args = parse_args()

    if not os.path.exists(args.file):
        raise SystemExit(f"Source file not found: {args.file}")

    log(f"Opening {args.file}")
    bpy.ops.wm.open_mainfile(filepath=args.file)

    base_obj = find_base_object(args.base_object)
    log(f"Using base mesh '{base_obj.name}' ({len(base_obj.data.vertices):,} verts)")

    result_collection = add_collection(args.collection_name)

    body_obj = duplicate_object(base_obj, "BodyCandidate", result_collection)
    clothing_obj = duplicate_object(base_obj, "ClothingCandidate", result_collection)

    configure_body_mesh(
        body_obj,
        voxel_size=args.voxel_size,
        smooth_iterations=args.smooth_iterations,
        shrink_thickness=args.shrink_thickness,
    )

    configure_clothing_mesh(clothing_obj, body_obj)

    if args.remove_skin_distance > 0:
        remove_skin_surfaces(clothing_obj, body_obj, args.remove_skin_distance)

    if args.split_loose:
        split_loose_parts(clothing_obj, result_collection, args.min_part_verts)
        clothing_obj = None

    body_obj.select_set(False)
    if clothing_obj:
        try:
            clothing_obj.select_set(False)
        except ReferenceError:
            pass

    save_file(args.output)
    log("Separation complete!")


if __name__ == "__main__":
    main()


