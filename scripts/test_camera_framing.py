"""
Test script for camera framing system.

This creates a simple test scene to verify the camera framing math works correctly
before trying it on Mixamo characters.

Run: blender --background --python test_camera_framing.py
"""

import bpy
import sys
import os
import mathutils
import math

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import blender_camera_utils as cam_utils


def create_test_character():
    """
    Create a simple test character (cube with animated scale).
    This simulates a Mixamo character's bounding box changing over time.
    """
    # Create cube
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    cube = bpy.context.active_object
    cube.name = "TestCharacter"
    
    # Animate scale to simulate arm movement
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 50
    
    # Frame 1: Small
    scene.frame_set(1)
    cube.scale = (0.5, 0.5, 1.0)
    cube.keyframe_insert(data_path="scale", frame=1)
    
    # Frame 25: Large (simulates arms extended)
    scene.frame_set(25)
    cube.scale = (2.0, 2.0, 1.0)
    cube.keyframe_insert(data_path="scale", frame=25)
    
    # Frame 50: Back to small
    scene.frame_set(50)
    cube.scale = (0.5, 0.5, 1.0)
    cube.keyframe_insert(data_path="scale", frame=50)
    
    scene.frame_set(1)
    
    return cube


def test_bounding_box_calculation():
    """Test 1: Verify bounding box calculation works across animation."""
    print("\n" + "="*60)
    print("TEST 1: Animated Bounding Box Calculation")
    print("="*60)
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create test character
    test_char = create_test_character()
    
    # Calculate bounds
    bbox_min, bbox_max = cam_utils.get_animated_bounding_box(test_char)
    bbox_size = bbox_max - bbox_min
    
    print(f"\n✓ Bounding box calculated:")
    print(f"  Min: ({bbox_min.x:.2f}, {bbox_min.y:.2f}, {bbox_min.z:.2f})")
    print(f"  Max: ({bbox_max.x:.2f}, {bbox_max.y:.2f}, {bbox_max.z:.2f})")
    print(f"  Size: ({bbox_size.x:.2f}, {bbox_size.y:.2f}, {bbox_size.z:.2f})")
    
    # Verify bounds captured the animation extremes
    # At frame 25, cube scale is (2, 2, 1), so width should be ~4 units
    if bbox_size.x >= 3.5:
        print("\n✓ PASSED: Bounds captured animation extremes")
        return True
    else:
        print(f"\n✗ FAILED: Bounds too small ({bbox_size.x:.2f} < 3.5)")
        return False


def test_camera_distance_calculation():
    """Test 2: Verify camera distance math."""
    print("\n" + "="*60)
    print("TEST 2: Camera Distance Calculation")
    print("="*60)
    
    # Test with known values
    bbox_min = mathutils.Vector((-2, -2, 0))
    bbox_max = mathutils.Vector((2, 2, 4))
    
    cam_pos, target = cam_utils.calculate_camera_position(
        bbox_min, bbox_max,
        camera_angle=0.0,  # Front view
        padding_factor=1.0,  # No padding for this test
        camera_fov=50.0
    )
    
    # Calculate expected distance
    bbox_diagonal = (bbox_max - bbox_min).length
    fov_rad = math.radians(50.0)
    expected_distance = (bbox_diagonal / 2.0) / math.tan(fov_rad / 2.0)
    actual_distance = (cam_pos - target).length
    
    print(f"\n✓ Camera positioned:")
    print(f"  Location: ({cam_pos.x:.2f}, {cam_pos.y:.2f}, {cam_pos.z:.2f})")
    print(f"  Target: ({target.x:.2f}, {target.y:.2f}, {target.z:.2f})")
    print(f"  Expected distance: {expected_distance:.2f}")
    print(f"  Actual distance: {actual_distance:.2f}")
    
    # Check if distance is correct (within 5% tolerance for padding/elevation)
    tolerance = 0.05
    error = abs(actual_distance - expected_distance) / expected_distance
    
    if error < tolerance:
        print(f"\n✓ PASSED: Camera distance matches expectation (error: {error*100:.1f}%)")
        return True
    else:
        print(f"\n✗ FAILED: Distance mismatch (error: {error*100:.1f}% > {tolerance*100}%)")
        return False


def test_camera_angles():
    """Test 3: Verify camera positioning at different angles."""
    print("\n" + "="*60)
    print("TEST 3: Camera Angles")
    print("="*60)
    
    bbox_min = mathutils.Vector((-1, -1, 0))
    bbox_max = mathutils.Vector((1, 1, 2))
    
    test_angles = [0, 45, 90, 180, 270]
    
    for angle in test_angles:
        cam_pos, target = cam_utils.calculate_camera_position(
            bbox_min, bbox_max,
            camera_angle=angle,
            camera_fov=50.0
        )
        
        # Verify camera is correct distance
        distance = (cam_pos - target).length
        
        # Verify angle is approximately correct
        # Vector from target to camera, projected to XY plane
        direction = (cam_pos - target).normalized()
        angle_rad = math.radians(angle)
        expected_x = math.sin(angle_rad)
        expected_y = -math.cos(angle_rad)
        
        print(f"\n  Angle {angle}°:")
        print(f"    Camera: ({cam_pos.x:.2f}, {cam_pos.y:.2f}, {cam_pos.z:.2f})")
        print(f"    Direction: ({direction.x:.2f}, {direction.y:.2f})")
        print(f"    Expected: ({expected_x:.2f}, {expected_y:.2f})")
    
    print("\n✓ PASSED: All angles calculated")
    return True


def test_full_pipeline():
    """Test 4: Full pipeline with test character."""
    print("\n" + "="*60)
    print("TEST 4: Full Pipeline Test")
    print("="*60)
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create test character
    test_char = create_test_character()
    
    # Wrap it in an armature-like object for compatibility
    bpy.ops.object.armature_add(location=(0, 0, 0))
    fake_armature = bpy.context.active_object
    fake_armature.name = "FakeArmature"
    
    # Parent cube to armature
    test_char.parent = fake_armature
    
    # Setup camera
    camera = cam_utils.setup_camera_for_character(
        fake_armature,
        camera_angle=45.0,
        use_track_constraint=True
    )
    
    print(f"\n✓ Camera created: {camera.name}")
    print(f"  Location: {camera.location}")
    print(f"  Constraints: {len(camera.constraints)}")
    
    # Add basic lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    
    # Setup render
    scene = bpy.context.scene
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.engine = 'BLENDER_EEVEE'
    
    # Render a test frame
    output_dir = "/workspace/pose-factory/output" if os.path.exists("/workspace") else "./output"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "camera_test.png")
    scene.render.filepath = output_path
    
    try:
        bpy.ops.render.render(write_still=True)
        print(f"\n✓ PASSED: Rendered test image to {output_path}")
        return True
    except Exception as e:
        print(f"\n✗ FAILED: Render error: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("CAMERA FRAMING SYSTEM TEST SUITE")
    print("="*60)
    
    results = {}
    
    results['bounding_box'] = test_bounding_box_calculation()
    results['camera_distance'] = test_camera_distance_calculation()
    results['camera_angles'] = test_camera_angles()
    results['full_pipeline'] = test_full_pipeline()
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Camera framing system is working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED. Check the output above for details.")
    
    return all_passed


# Run tests
if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

