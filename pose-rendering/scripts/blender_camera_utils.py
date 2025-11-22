"""
Production-grade camera framing utilities for Blender headless rendering.
Handles Mixamo FBX imports with scale inconsistencies and provides deterministic camera positioning.

Author: Pipeline TD System
Use Case: Automated pose dataset rendering for MediaPipe training
"""

import bpy
import mathutils
import math
from typing import Tuple, Optional, List


def get_animated_bounding_box(obj, scene=None) -> Tuple[mathutils.Vector, mathutils.Vector]:
    """
    Calculate the world-space bounding box across ALL animation frames.
    
    This is critical for Mixamo characters because:
    - Different poses extend to different spatial extents
    - We need the camera to frame the ENTIRE animation, not just frame 1
    
    Args:
        obj: Blender object (typically armature or mesh)
        scene: Blender scene (uses current scene if None)
    
    Returns:
        Tuple of (min_corner, max_corner) as Vector objects in world space
    """
    if scene is None:
        scene = bpy.context.scene
    
    # Store original frame
    original_frame = scene.frame_current
    
    # Initialize with impossibly extreme values
    min_corner = mathutils.Vector((float('inf'), float('inf'), float('inf')))
    max_corner = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))
    
    # Sample every frame in the animation range
    for frame in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame)
        
        # Force dependency graph update (critical in headless mode)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        
        # Get bounding box corners in world space
        if obj_eval.type == 'MESH':
            # For meshes, use actual vertex positions (most accurate)
            mesh = obj_eval.to_mesh()
            matrix_world = obj_eval.matrix_world
            
            for vertex in mesh.vertices:
                world_pos = matrix_world @ vertex.co
                min_corner.x = min(min_corner.x, world_pos.x)
                min_corner.y = min(min_corner.y, world_pos.y)
                min_corner.z = min(min_corner.z, world_pos.z)
                max_corner.x = max(max_corner.x, world_pos.x)
                max_corner.y = max(max_corner.y, world_pos.y)
                max_corner.z = max(max_corner.z, world_pos.z)
            
            obj_eval.to_mesh_clear()
        else:
            # For armatures or other objects, use bounding box
            for corner in obj_eval.bound_box:
                world_pos = obj_eval.matrix_world @ mathutils.Vector(corner)
                min_corner.x = min(min_corner.x, world_pos.x)
                min_corner.y = min(min_corner.y, world_pos.y)
                min_corner.z = min(min_corner.z, world_pos.z)
                max_corner.x = max(max_corner.x, world_pos.x)
                max_corner.y = max(max_corner.y, world_pos.y)
                max_corner.z = max(max_corner.z, world_pos.z)
    
    # Restore original frame
    scene.frame_set(original_frame)
    
    return min_corner, max_corner


def get_character_bounding_box(armature_obj) -> Tuple[mathutils.Vector, mathutils.Vector]:
    """
    Get the complete bounding box for a Mixamo character (armature + all child meshes).
    
    Handles the common Mixamo import structure:
    - Armature at scale 0.01
    - Mesh children at scale 1.0
    - Compound transformations
    
    Args:
        armature_obj: The imported armature object
    
    Returns:
        Tuple of (min_corner, max_corner) covering all animated frames
    """
    min_corner = mathutils.Vector((float('inf'), float('inf'), float('inf')))
    max_corner = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))
    
    # Get armature bounds
    arm_min, arm_max = get_animated_bounding_box(armature_obj)
    min_corner.x = min(min_corner.x, arm_min.x)
    min_corner.y = min(min_corner.y, arm_min.y)
    min_corner.z = min(min_corner.z, arm_min.z)
    max_corner.x = max(max_corner.x, arm_max.x)
    max_corner.y = max(max_corner.y, arm_max.y)
    max_corner.z = max(max_corner.z, arm_max.z)
    
    # Get all child mesh bounds
    for child in armature_obj.children:
        if child.type == 'MESH':
            child_min, child_max = get_animated_bounding_box(child)
            min_corner.x = min(min_corner.x, child_min.x)
            min_corner.y = min(min_corner.y, child_min.y)
            min_corner.z = min(min_corner.z, child_min.z)
            max_corner.x = max(max_corner.x, child_max.x)
            max_corner.y = max(max_corner.y, child_max.y)
            max_corner.z = max(max_corner.z, child_max.z)
    
    return min_corner, max_corner


def calculate_camera_position(
    bbox_min: mathutils.Vector,
    bbox_max: mathutils.Vector,
    camera_angle: float = 45.0,
    padding_factor: float = 1.2,
    camera_fov: float = 50.0
) -> Tuple[mathutils.Vector, mathutils.Vector]:
    """
    Calculate camera position to frame a bounding box perfectly.
    
    Uses trigonometry to determine exact distance needed based on FOV.
    This is production-grade: no magic numbers, fully deterministic.
    
    Args:
        bbox_min: Minimum corner of bounding box
        bbox_max: Maximum corner of bounding box
        camera_angle: Horizontal angle from front in degrees (0=front, 45=front-left, 90=left)
        padding_factor: Multiply bounding box size by this (1.2 = 20% padding)
        camera_fov: Camera field of view in degrees
    
    Returns:
        Tuple of (camera_location, target_location)
    """
    # Calculate bounding box center and dimensions
    bbox_center = (bbox_min + bbox_max) / 2.0
    bbox_size = bbox_max - bbox_min
    
    # Apply padding to account for animation extremes
    bbox_diagonal = bbox_size.length * padding_factor
    
    # Calculate required camera distance based on FOV
    # Formula: distance = (object_size / 2) / tan(fov / 2)
    fov_radians = math.radians(camera_fov)
    distance = (bbox_diagonal / 2.0) / math.tan(fov_radians / 2.0)
    
    # Convert camera angle to radians
    angle_radians = math.radians(camera_angle)
    
    # Position camera at calculated distance, at specified angle
    # Place camera slightly above center for better pose visibility
    camera_location = mathutils.Vector((
        bbox_center.x + distance * math.sin(angle_radians),
        bbox_center.y - distance * math.cos(angle_radians),
        bbox_center.z + bbox_size.z * 0.3  # Slightly elevated
    ))
    
    return camera_location, bbox_center


def setup_camera_for_character(
    armature_obj,
    camera_name: str = "RenderCamera",
    camera_angle: float = 45.0,
    use_track_constraint: bool = True,
    camera_fov: float = 50.0
) -> bpy.types.Object:
    """
    Create and position a camera to frame the character perfectly.
    
    This is the main function you'll call. It handles everything:
    - Bounding box calculation across all frames
    - Mathematically correct camera positioning
    - Optional Track To constraint for stability
    
    Args:
        armature_obj: The imported Mixamo armature
        camera_name: Name for the camera object
        camera_angle: Horizontal viewing angle in degrees
        use_track_constraint: Add Track To constraint (recommended)
        camera_fov: Camera field of view in degrees
    
    Returns:
        The created camera object
    """
    # Calculate character bounds across entire animation
    bbox_min, bbox_max = get_character_bounding_box(armature_obj)
    
    # Calculate camera position
    camera_location, target_location = calculate_camera_position(
        bbox_min, bbox_max,
        camera_angle=camera_angle,
        camera_fov=camera_fov
    )
    
    # Create camera
    camera_data = bpy.data.cameras.new(name=camera_name)
    camera_data.lens_unit = 'FOV'
    camera_data.angle = math.radians(camera_fov)
    
    camera_obj = bpy.data.objects.new(camera_name, camera_data)
    bpy.context.scene.collection.objects.link(camera_obj)
    camera_obj.location = camera_location
    
    # Point camera at target
    if use_track_constraint:
        # Create an empty at the target location for the constraint
        empty = bpy.data.objects.new("CameraTarget", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = target_location
        
        # Add Track To constraint (more stable than manual rotation)
        constraint = camera_obj.constraints.new(type='TRACK_TO')
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
    else:
        # Manual rotation (less recommended)
        direction = target_location - camera_location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        camera_obj.rotation_euler = rot_quat.to_euler()
    
    # Set as active scene camera
    bpy.context.scene.camera = camera_obj
    
    return camera_obj


def normalize_mixamo_character(armature_obj):
    """
    Fix Mixamo's broken scale hierarchy.
    
    Mixamo imports with:
    - Armature scale: 0.01
    - Mesh scale: 1.0 (parented to armature)
    
    This scales the armature UP by 100x so the character is normal size.
    
    Args:
        armature_obj: The imported Mixamo armature
    """
    # Store original armature scale
    original_scale = armature_obj.scale.copy()
    
    # If armature is at 0.01, scale it UP to 1.0 (100x bigger)
    # This makes the effective character size normal
    if original_scale.x < 0.02:  # Detect Mixamo's 0.01 scale
        scale_factor = 1.0 / original_scale.x  # 1.0 / 0.01 = 100
        armature_obj.scale = (1.0, 1.0, 1.0)
        
        print(f"✓ Normalized character: scaled armature from {original_scale.x:.4f} to 1.0 (factor: {scale_factor:.1f}x)")
    else:
        print(f"✓ Character already at normal scale: {original_scale.x:.4f}")


def find_armature_in_selection(selected_objects: List[bpy.types.Object]) -> Optional[bpy.types.Object]:
    """
    Find the armature object from imported selection.
    
    Args:
        selected_objects: List of objects (from bpy.context.selected_objects)
    
    Returns:
        Armature object or None
    """
    for obj in selected_objects:
        if obj.type == 'ARMATURE':
            return obj
    return None


# ----- Production Pipeline Example -----

def example_production_pipeline(fbx_path: str, output_dir: str):
    """
    Complete example showing the full pipeline.
    
    This demonstrates best practices for:
    - FBX import
    - Scale normalization
    - Camera setup
    - Rendering
    """
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import FBX (DON'T manually scale anything!)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    imported_objects = bpy.context.selected_objects
    
    # Find the armature
    armature = find_armature_in_selection(imported_objects)
    if not armature:
        raise ValueError("No armature found in imported FBX")
    
    print(f"✓ Imported: {armature.name}")
    print(f"  Original armature scale: {armature.scale}")
    
    # Fix Mixamo's broken scale hierarchy
    normalize_mixamo_character(armature)
    
    # Center character at world origin (optional but recommended)
    armature.location = (0, 0, 0)
    
    # Setup camera with automatic framing
    camera = setup_camera_for_character(
        armature,
        camera_angle=45.0,      # Front-left view
        use_track_constraint=True,
        camera_fov=50.0
    )
    
    print(f"✓ Camera positioned at: {camera.location}")
    
    # Add lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Configure render settings
    scene = bpy.context.scene
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 64  # Anti-aliasing
    
    # Render all frames
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for frame in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame)
        output_path = os.path.join(output_dir, f"frame_{frame:04d}.png")
        scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        print(f"✓ Rendered frame {frame}/{scene.frame_end}")
    
    print(f"\n✓ Pipeline complete! Frames in: {output_dir}")


# ----- Standalone Script Entry Point -----

if __name__ == "__main__":
    # Example: Run from command line
    # blender --background --python blender_camera_utils.py
    
    fbx_path = "/workspace/pose-factory/characters/X Bot.fbx"
    output_dir = "/workspace/pose-factory/output/animation_frames"
    
    example_production_pipeline(fbx_path, output_dir)

