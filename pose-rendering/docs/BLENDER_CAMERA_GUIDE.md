# Production-Grade Camera Framing for Blender Headless Rendering

## 🎯 The Problem We're Solving

When rendering Mixamo characters in Blender's headless mode for pose dataset generation, you encounter several critical issues:

### Issue 1: Mixamo's Broken Scale Hierarchy
```
Imported FBX structure:
├── Armature (scale: 0.01, 0.01, 0.01)
│   └── Mesh (scale: 1.0, 1.0, 1.0)
│       └── Effective world scale: 0.01 × 1.0 = 0.01
```

**Problem:** Blender's bounding box calculations can fail with this compound transformation, especially in headless mode where the dependency graph isn't automatically updated.

### Issue 2: Viewport Operators Don't Work in Headless Mode
```python
# ❌ BROKEN in headless mode:
bpy.ops.view3d.camera_to_view_selected()

# ❌ UNRELIABLE in headless mode:
camera.location = (4, -4, 2)  # Magic numbers
```

### Issue 3: Animation Extends Beyond Frame 1
A character's bounding box at frame 1 might be completely different at frame 50 (arm raised, leg extended). **You must calculate the bounding box across ALL frames.**

---

## ✅ The Solution: Mathematical Camera Framing

### Core Principles

1. **Calculate World-Space Bounding Box Across All Frames**
   - Sample every frame in the animation
   - Force dependency graph updates (`evaluated_depsgraph_get()`)
   - Get actual vertex positions in world space
   - Track min/max corners across all frames

2. **Use Trigonometry to Position Camera**
   ```
   Given:
   - Object diagonal size: D
   - Camera FOV: θ
   
   Required distance: d = (D/2) / tan(θ/2)
   
   This guarantees the object fits in frame with no guesswork.
   ```

3. **Use Track To Constraints (Not Manual Rotation)**
   - More stable in headless mode
   - Automatically updates if character moves
   - Production standard for camera rigs

4. **Normalize the Scale Hierarchy First**
   - Apply armature scale to mesh data
   - Reset armature to scale 1.0
   - Makes all subsequent calculations reliable

---

## 📐 Step-by-Step Camera Math Breakdown

### Step 1: Get Animated Bounding Box

```python
def get_animated_bounding_box(obj, scene):
    min_corner = Vector((inf, inf, inf))
    max_corner = Vector((-inf, -inf, -inf))
    
    for frame in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame)
        
        # CRITICAL: Force evaluation in headless mode
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        
        # Get actual vertex positions (not just bounding box corners)
        mesh = obj_eval.to_mesh()
        for vertex in mesh.vertices:
            world_pos = obj_eval.matrix_world @ vertex.co
            min_corner.x = min(min_corner.x, world_pos.x)
            # ... (track min/max for all axes)
```

**Why this works:**
- `evaluated_get()` forces Blender to compute transformations (critical in headless)
- Samples every frame (catches animation extremes)
- Uses vertex positions (more accurate than `bound_box`)
- World space coordinates (accounts for all parent transforms)

### Step 2: Calculate Camera Distance

```python
bbox_center = (bbox_min + bbox_max) / 2.0
bbox_diagonal = (bbox_max - bbox_min).length * padding_factor

fov_radians = math.radians(camera_fov)
distance = (bbox_diagonal / 2.0) / math.tan(fov_radians / 2.0)
```

**Geometric proof:**
```
         Camera (top view)
            /|\
           / | \
          /  |  \   <- FOV angle (θ)
         /   |   \
        /    |    \
       /     d     \
      /      |      \
     --------+--------  <- Object width (w)
     
tan(θ/2) = (w/2) / d
Therefore: d = (w/2) / tan(θ/2)
```

### Step 3: Position Camera in 3D Space

```python
# Convert horizontal angle to radians
angle_radians = math.radians(camera_angle)

camera_location = Vector((
    center.x + distance * sin(angle_radians),   # X offset
    center.y - distance * cos(angle_radians),   # Y offset (negative = in front)
    center.z + bbox_size.z * 0.3                # Z elevated slightly
))
```

**Why elevate the camera?**
- Poses look better from slightly above eye level
- Avoids foreshortening of feet
- Standard for character renders

### Step 4: Point Camera at Target

```python
# Create empty at bounding box center
empty = bpy.data.objects.new("CameraTarget", None)
empty.location = bbox_center

# Add Track To constraint
constraint = camera.constraints.new(type='TRACK_TO')
constraint.target = empty
constraint.track_axis = 'TRACK_NEGATIVE_Z'  # Camera looks down -Z
constraint.up_axis = 'UP_Y'                 # Keep Y up
```

**Why use constraint instead of manual rotation?**
- Handles edge cases automatically
- Updates if character moves
- More stable across different Blender versions
- Production standard (how real studios do it)

---

## ⚠️ Critical Pitfalls & Solutions

### Pitfall 1: Not Updating Dependency Graph in Headless Mode

**Problem:**
```python
# In headless mode, this may return STALE data:
for vertex in obj.data.vertices:
    pos = obj.matrix_world @ vertex.co  # ❌ May be frame 1 data!
```

**Solution:**
```python
# Force evaluation:
depsgraph = bpy.context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(depsgraph)
mesh = obj_eval.to_mesh()  # ✓ Fresh, evaluated mesh
```

### Pitfall 2: Scaling Objects After Import

**Problem:**
```python
# This compounds the existing scale issue:
armature.scale = (0.01, 0.01, 0.01)  # ❌ Now scale is 0.01 × 0.01 = 0.0001!
```

**Solution:**
```python
# Apply parent scale to children, then normalize:
for child in armature.children:
    child.scale = (
        child.scale.x * armature.scale.x,
        child.scale.y * armature.scale.y,
        child.scale.z * armature.scale.z
    )
    bpy.ops.object.transform_apply(scale=True)  # Make permanent

armature.scale = (1.0, 1.0, 1.0)  # ✓ Now everything is normalized
```

### Pitfall 3: Using Viewport Operators

**Problem:**
```python
# ❌ FAILS in headless mode (no viewport):
bpy.ops.view3d.camera_to_view_selected()
bpy.ops.view3d.view_selected()
```

**Solution:**
```python
# ✓ Use data API directly:
camera.location = calculated_position
constraint = camera.constraints.new(type='TRACK_TO')
```

### Pitfall 4: Assuming Frame 1 Bounds = Animation Bounds

**Problem:**
```python
# ❌ Only checks first frame:
bbox = obj.bound_box
```

**Solution:**
```python
# ✓ Sample all frames:
for frame in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(frame)
    # Calculate bounds...
```

### Pitfall 5: Not Accounting for Padding

**Problem:**
```python
# ❌ Character might touch frame edges:
distance = bbox_diagonal / 2.0 / tan(fov / 2.0)
```

**Solution:**
```python
# ✓ Add 20% padding:
bbox_diagonal = bbox_size.length * 1.2
```

---

## 🔧 Usage Examples

### Basic Usage (Single Frame)

```python
import blender_camera_utils as cam_utils

# Import FBX
bpy.ops.import_scene.fbx(filepath="character.fbx")
armature = cam_utils.find_armature_in_selection(bpy.context.selected_objects)

# Normalize scale
cam_utils.normalize_mixamo_character(armature)

# Setup camera (automatic framing)
camera = cam_utils.setup_camera_for_character(
    armature,
    camera_angle=45.0,  # 45° from front
    camera_fov=50.0
)

# Render
bpy.ops.render.render(write_still=True)
```

### Advanced Usage (Multiple Camera Angles)

```python
# Render from 4 angles
angles = [0, 90, 180, 270]  # Front, right, back, left

for i, angle in enumerate(angles):
    camera = cam_utils.setup_camera_for_character(
        armature,
        camera_name=f"Camera_{i}",
        camera_angle=angle
    )
    
    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = f"output_angle_{angle}.png"
    bpy.ops.render.render(write_still=True)
```

### Production Pipeline (All Frames)

```python
# See blender_camera_utils.py -> example_production_pipeline()

cam_utils.example_production_pipeline(
    fbx_path="/path/to/character.fbx",
    output_dir="/path/to/output"
)

# Renders all frames with automatic camera framing
```

---

## 📊 Performance Considerations

### Bounding Box Calculation Time

**For a 250-frame animation:**
- Sampling all frames: ~2-5 seconds
- Vertex-level precision: Adds ~1 second

**Is this worth it?**
✓ YES - because the alternative is:
- Manual camera tweaking: 5-30 minutes per character
- Re-renders when camera is wrong: Hours of wasted GPU time

### Optimization Tips

1. **For very long animations (1000+ frames):**
   ```python
   # Sample every 10th frame:
   for frame in range(start, end, 10):
       scene.frame_set(frame)
   ```

2. **For batch processing:**
   - Calculate bounds once, reuse for all camera angles
   - Cache bounding box results between renders

3. **For real-time preview:**
   - Use `bound_box` instead of vertex-level (less accurate but faster)

---

## 🎬 Production Best Practices

### 1. Always Normalize Scale First
```python
cam_utils.normalize_mixamo_character(armature)
armature.location = (0, 0, 0)  # Center at origin
```

### 2. Use Consistent FOV
```python
# 50mm is standard for character work
camera_fov = 50.0  # Not too wide (distortion) or narrow (flat)
```

### 3. Add Padding for Animation Extremes
```python
# 20% padding accounts for motion blur, unexpected poses
padding_factor = 1.2
```

### 4. Sample All Frames
```python
# Don't trust frame 1 bounds!
for frame in range(scene.frame_start, scene.frame_end + 1):
    # Calculate bounds...
```

### 5. Use Track Constraints
```python
# More stable than manual rotation
use_track_constraint = True
```

---

## 🐛 Debugging Tips

### Camera Not Framing Correctly?

1. **Check scale normalization:**
   ```python
   print(f"Armature scale: {armature.scale}")  # Should be (1, 1, 1)
   print(f"Mesh scale: {mesh.scale}")          # Should be (1, 1, 1)
   ```

2. **Visualize bounding box:**
   ```python
   bbox_min, bbox_max = cam_utils.get_character_bounding_box(armature)
   print(f"Bounds: {bbox_min} to {bbox_max}")
   print(f"Size: {bbox_max - bbox_min}")
   ```

3. **Check camera distance:**
   ```python
   print(f"Camera location: {camera.location}")
   print(f"Target location: {target.location}")
   print(f"Distance: {(camera.location - target.location).length}")
   ```

4. **Test in GUI first:**
   - Run script in Blender GUI (not headless)
   - Verify camera framing visually
   - Then test in headless mode

### Character Too Small/Large in Frame?

- **Too small:** Decrease `padding_factor` (try 1.1)
- **Too large:** Increase `padding_factor` (try 1.3)
- **Clipped at edges:** Increase FOV or padding

---

## 🚀 Migration from Old render_mixamo.py

### Old Approach (Broken)
```python
# ❌ Manual scaling (compounds issue)
char.scale = (0.01, 0.01, 0.01)

# ❌ Magic number camera position
camera.location = (4, -4, 2)
camera.rotation_euler = (1.2, 0, 0.785)
```

### New Approach (Production-Grade)
```python
# ✓ Normalize scale hierarchy
cam_utils.normalize_mixamo_character(armature)

# ✓ Mathematical camera framing
camera = cam_utils.setup_camera_for_character(
    armature,
    camera_angle=45.0,
    use_track_constraint=True
)
```

### Testing the Migration

```bash
# Test old script (for comparison)
blender --background --python scripts/render_mixamo.py

# Test new script
blender --background --python scripts/render_mixamo_v2.py

# Compare outputs
```

---

## 📚 Further Reading

- [Blender Dependency Graph](https://docs.blender.org/api/current/bpy.types.Depsgraph.html)
- [Camera Framing Math](https://en.wikipedia.org/wiki/Angle_of_view)
- [Mixamo Import Issues](https://blenderartists.org/t/mixamo-scale-problems)

---

## ✅ Summary Checklist

Before rendering your pose dataset, verify:

- [ ] FBX imported without manual scaling
- [ ] Scale hierarchy normalized (`normalize_mixamo_character()`)
- [ ] Camera positioned using bounding box calculation
- [ ] All animation frames sampled for bounds
- [ ] Track To constraint enabled
- [ ] Dependency graph forced to update (`evaluated_get()`)
- [ ] Tested in headless mode (not just GUI)
- [ ] Output frames verified for correct framing

**If all checked:** You have a production-grade pipeline! 🎉

