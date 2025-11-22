# Camera Framing Quick Start

## 🚀 TL;DR

**Problem:** Mixamo characters import with broken scales, camera framing fails in headless mode.

**Solution:** Use `blender_camera_utils.py` for automatic, mathematical camera positioning.

---

## ⚡ Quick Usage

### Single Character, Single Angle

```bash
# Edit render_mixamo_v2.py to set your paths, then:
blender --background --python scripts/render_mixamo_v2.py
```

### Single Character, 8 Angles

```bash
# Edit render_multi_angle.py to set your paths, then:
blender --background --python scripts/render_multi_angle.py
```

### Batch: All Characters, 8 Angles Each

```bash
blender --background --python scripts/render_multi_angle.py -- --batch
```

### Test the System First

**⚠️ These commands require Blender to be installed!**

**On Mac:**
```bash
# Install Blender first:
brew install --cask blender

# Then test:
blender --background --python scripts/test_camera_framing.py
# or: /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/test_camera_framing.py
```

**On RunPod (Blender already installed):**
```bash
blender --background --python scripts/test_camera_framing.py
```

---

## 📝 Code Template

```python
import blender_camera_utils as cam_utils

# 1. Import FBX
bpy.ops.import_scene.fbx(filepath="character.fbx")
armature = cam_utils.find_armature_in_selection(bpy.context.selected_objects)

# 2. Fix Mixamo scale issues
cam_utils.normalize_mixamo_character(armature)

# 3. Auto-frame camera (no math required!)
camera = cam_utils.setup_camera_for_character(
    armature,
    camera_angle=45.0,  # 0=front, 90=side, 180=back
    camera_fov=50.0
)

# 4. Render
bpy.ops.render.render(write_still=True)
```

---

## 🎯 Common Camera Angles

| Angle | View | Use Case |
|-------|------|----------|
| 0° | Front | Face detection |
| 45° | Front-right | Natural 3/4 view |
| 90° | Right side | Profile poses |
| 135° | Back-right | Over-shoulder |
| 180° | Back | Back poses |
| 225° | Back-left | Over-shoulder (left) |
| 270° | Left side | Profile (left) |
| 315° | Front-left | Natural 3/4 view (left) |

**Recommendation:** Use 8 angles for comprehensive training data.

---

## 🔧 Customization Options

### Change Field of View

```python
camera = cam_utils.setup_camera_for_character(
    armature,
    camera_fov=35.0  # Wider = more distortion, narrower = flatter
)
# 50mm is standard for characters
```

### Adjust Padding

```python
cam_pos, target = cam_utils.calculate_camera_position(
    bbox_min, bbox_max,
    padding_factor=1.3  # 1.2 = 20% padding (default)
)
```

### Multiple Cameras in Scene

```python
# Create cameras for all 8 angles
angles = [0, 45, 90, 135, 180, 225, 270, 315]
cameras = []

for angle in angles:
    cam = cam_utils.setup_camera_for_character(
        armature,
        camera_name=f"Camera_{angle}deg",
        camera_angle=angle
    )
    cameras.append(cam)

# Switch between them
bpy.context.scene.camera = cameras[0]  # Use front camera
```

---

## ⚠️ Troubleshooting

### Character too small in frame?
```python
padding_factor=1.1  # Decrease padding
```

### Character too large/clipped?
```python
padding_factor=1.4  # Increase padding
```

### Camera pointing wrong direction?
```python
# Make sure you used Track To constraint
use_track_constraint=True  # This is the default
```

### Animation getting clipped?
```python
# Bounding box samples all frames automatically
# If still clipping, increase padding:
padding_factor=1.5
```

### Still having issues?
1. Check armature scale: `print(armature.scale)` should be `(1, 1, 1)`
2. Run the test script: `blender --background --python test_camera_framing.py`
3. Read `BLENDER_CAMERA_GUIDE.md` for detailed explanations

---

## 📊 Performance

| Operation | Time |
|-----------|------|
| Import FBX | ~1-2 seconds |
| Calculate bounds (250 frames) | ~3-5 seconds |
| Setup camera | <1 second |
| Render single frame (512×512) | ~1-2 seconds |

**Total for 8 angles:** ~15-20 seconds per character (one frame)

---

## 📁 File Overview

| File | Purpose |
|------|---------|
| `blender_camera_utils.py` | Core library (all the math) |
| `render_mixamo_v2.py` | Simple single-character render |
| `render_multi_angle.py` | Multi-angle + batch rendering |
| `test_camera_framing.py` | Test suite |
| `BLENDER_CAMERA_GUIDE.md` | Detailed documentation |
| `CAMERA_QUICK_START.md` | This file! |

---

## ✅ Best Practices Checklist

Before running production renders:

- [ ] Tested with `test_camera_framing.py` (all tests pass)
- [ ] Verified one character renders correctly
- [ ] Checked output directory has enough space
- [ ] Set correct `num_angles` (8 recommended)
- [ ] Configured correct paths for your environment
- [ ] Decided: single frame or full animation?

---

## 🎓 Learn More

- **Why does this work?** Read `BLENDER_CAMERA_GUIDE.md`
- **Production pipeline details?** See `blender_camera_utils.py` docstrings
- **Customization examples?** Check `render_multi_angle.py`

---

## 💡 Pro Tips

1. **Start with 4 angles** (front, right, back, left) to verify pipeline, then scale to 8
2. **Render just frame 1 first** to test camera framing before committing to full animation
3. **Use batch mode** to process all downloaded Mixamo characters at once
4. **Name your FBX files descriptively** - output folders use the FBX filename
5. **Monitor the first few renders** to catch any import issues early

---

**Ready to render?** Run the test script, then choose your rendering script! 🎬

