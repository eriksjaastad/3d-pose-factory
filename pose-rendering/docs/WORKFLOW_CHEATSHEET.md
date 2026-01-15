# 3d-pose-factory - Workflow Cheatsheet

Quick reference for your complete pipeline: Mac → R2 → RunPod → R2 → Mac

---

## 🚀 **AUTOMATED PIPELINE (Recommended!)** 

**Stop copy-pasting commands!** Use the automation script instead:

### **Full batch render (all characters):**
```bash
cd ~/projects/3D\ Pose\ Factory/
./scripts/render_pipeline.sh
```
**What it does:** Uploads scripts to R2 → SSHs to pod → downloads scripts → renders all 6 characters × 8 angles → uploads results → downloads to Mac with timestamp → done!

**Time:** ~2-3 minutes total (mostly automatic)

### **Quick test (single character):**
```bash
./scripts/render_pipeline.sh --single
```
Renders just X Bot (8 images) for testing camera settings

### **Just download existing results:**
```bash
./scripts/render_pipeline.sh --download-only
```
Skip upload/render, only download what's already in R2

### **Provide pod ID upfront:**
```bash
./scripts/render_pipeline.sh --pod 6gpur3lb2h5pzi-6441128f
```
Skips the interactive prompt for pod ID

---

## 💡 **Manual Workflow (If Script Doesn't Work)**

**Only use this if the automated script fails.** The script above is much easier!

---

## 📥 Step 1: Download Mixamo Characters

1. Go to https://www.mixamo.com/
2. Select character (e.g., "X Bot")
3. Choose animation
4. Download with FBX format
5. Save to: `~/projects/3d-pose-factory/downloads/`

---

## ☁️ Step 2: Upload to R2

```bash
cd ~/projects/3D\ Pose\ Factory/

# Upload Mixamo characters to R2
rclone copy downloads/ r2_pose_factory:pose-factory/characters/ --progress

# Upload Blender camera scripts to R2
rclone copy scripts/blender_camera_utils.py r2_pose_factory:pose-factory/scripts/
rclone copy scripts/render_multi_angle.py r2_pose_factory:pose-factory/scripts/
rclone copy scripts/render_mixamo_v2.py r2_pose_factory:pose-factory/scripts/
rclone copy scripts/test_camera_framing.py r2_pose_factory:pose-factory/scripts/

# Verify upload
rclone ls r2_pose_factory:pose-factory/characters/
rclone ls r2_pose_factory:pose-factory/scripts/ | grep blender
```

---

## 🚀 Step 3: Deploy RunPod

### Start Pod

1. Go to https://www.runpod.io/console/pods
2. Click "Deploy" or resume existing pod
3. Select template with A40 GPU
4. Wait for pod to start (~30 seconds)
5. Copy the Pod ID (e.g., `6gpur3lb2h5pzi-6441128f`)

### Connect to Pod

```bash
# Use _runpod shortcut if you have it set up, or:
ssh <POD_ID>@ssh.runpod.io -i ~/.ssh/id_ed25519

# Get your POD_ID from RunPod web UI
# Example: ssh 6gpur3lb2h5pzi-6441128f@ssh.runpod.io -i ~/.ssh/id_ed25519
```

### Setup Pod (Fresh Pod Only)

```bash
# If fresh pod, run setup script
cd /workspace/pose-factory/
bash setup_pod.sh

# This installs:
# - Blender
# - Python + MediaPipe
# - rclone
# - Clones GitHub repo
```

### Download from R2 to Pod

```bash
cd /workspace/pose-factory/

# Download Mixamo characters
rclone copy r2_pose_factory:pose-factory/characters/ characters/ --progress

# Download scripts
rclone copy r2_pose_factory:pose-factory/scripts/ scripts/ --progress

# Verify
ls -lh characters/*.fbx
ls -lh scripts/*.py
```

---

## 🎬 Step 4: Render on RunPod

### Test Camera System First (Recommended)

```bash
cd /workspace/pose-factory/

# Run test suite (verifies camera math works correctly)
blender --background --python scripts/test_camera_framing.py

# Should see: "✓ ALL TESTS PASSED!"
```

**If tests fail:** Check the error message and refer to `GETTING_STARTED.md` for troubleshooting.

### Render Single Character (8 Angles)

```bash
# Edit script to set correct paths
nano scripts/render_multi_angle.py

# Update these lines:
# SINGLE_FBX_PATH = "/workspace/pose-factory/characters/X Bot.fbx"
# SINGLE_OUTPUT_DIR = "/workspace/pose-factory/output/multi_angle"

# Run render
blender --background --python scripts/render_multi_angle.py

# Check output
ls -lh output/multi_angle/X_Bot/
# Should see: front.png, front_right.png, right.png, etc.
```

### Render All Characters (Batch Mode)

```bash
# Run batch render (all FBX files, 8 angles each)
blender --background --python scripts/render_multi_angle.py -- --batch

# For 6 characters × 8 angles = 48 renders
# Takes ~2-3 minutes

# Check output
ls -lh output/batch_multi_angle/
```

---

## 🔍 Run Pose Detection

```bash
cd /workspace/pose-factory/

# Process rendered images with MediaPipe
doppler run -- python3 scripts/batch_process.py

# Or use the automated workflow:
bash scripts/auto_process.sh
```

---

## 📤 Upload Results to R2

```bash
cd /workspace/pose-factory/

# Upload rendered images
rclone copy output/ r2_pose_factory:pose-factory/output/ --progress

# Upload pose detection results
rclone copy output/ r2_pose_factory:pose-factory/results/$(date +%Y%m%d_%H%M%S)/ --progress

# Verify
rclone ls r2_pose_factory:pose-factory/output/
```

---

## 💻 Download Results to Mac

```bash
cd ~/projects/3D\ Pose\ Factory/

# Download everything
rclone copy r2_pose_factory:pose-factory/output/ data/working/ --progress

# Or download specific results
rclone copy r2_pose_factory:pose-factory/results/20241121_120000/ data/working/results/ --progress

# Check
ls -lh data/working/
```

---

## 🧹 Cleanup

### On RunPod (Save GPU costs)

```bash
# Clear output directory (keep scripts and characters)
rm -rf /workspace/pose-factory/output/*

# Exit and terminate pod via web UI
exit
```

### On Mac (Optional)

```bash
# Archive processed data
cd ~/projects/3D\ Pose\ Factory/
mv data/working data/archive/$(date +%Y%m%d_%H%M%S)

# Clean downloads if needed
# rm downloads/*.fbx  # Only if you want to free space
```

---

## 🔄 Typical Full Workflow (No Local Blender)

```bash
# === ON MAC ===

# 1. Download Mixamo characters (web browser)
# → Save to ~/projects/3d-pose-factory/downloads/

# 2. Upload to R2
cd ~/projects/3D\ Pose\ Factory/
rclone copy downloads/ r2_pose_factory:pose-factory/characters/ --progress
rclone copy scripts/blender_camera_utils.py r2_pose_factory:pose-factory/scripts/
rclone copy scripts/render_multi_angle.py r2_pose_factory:pose-factory/scripts/

# === ON RUNPOD ===

# 3. Connect to RunPod (use _runpod shortcut or SSH)
# ssh <POD_ID>@ssh.runpod.io -i ~/.ssh/id_ed25519

# 4. Download from R2 to pod
cd /workspace/pose-factory/
rclone copy r2_pose_factory:pose-factory/characters/ characters/ --progress
rclone copy r2_pose_factory:pose-factory/scripts/ scripts/ --progress

# 5. Test camera system
blender --background --python scripts/test_camera_framing.py

# 6. Render (batch mode - all characters, 8 angles each)
blender --background --python scripts/render_multi_angle.py -- --batch

# 7. Process with MediaPipe (optional)
bash scripts/auto_process.sh

# 8. Upload results to R2
rclone copy output/ r2_pose_factory:pose-factory/output/ --progress

# 9. Exit pod
exit

# === BACK ON MAC ===

# 10. Download results from R2
cd ~/projects/3D\ Pose\ Factory/
rclone copy r2_pose_factory:pose-factory/output/ data/working/ --progress

# 11. Terminate pod via web UI (https://www.runpod.io/console/pods)
```

**Time:** ~10-15 minutes per batch (6 characters × 8 angles = 48 renders)

---

## 🧪 Advanced: Local Development (Optional)

**Only if you want to test/modify scripts locally before uploading to RunPod.**

### Install Blender on Mac

```bash
# Install via Homebrew
brew install --cask blender

# Verify installation
blender --version
# or: /Applications/Blender.app/Contents/MacOS/Blender --version
```

### Test Locally

```bash
cd ~/projects/3D\ Pose\ Factory/

# Run test suite
blender --background --python scripts/test_camera_framing.py

# Test single character
blender --background --python scripts/render_mixamo_v2.py

# Test multi-angle
blender --background --python scripts/render_multi_angle.py
```

**If `blender` command not found:** Use full path `/Applications/Blender.app/Contents/MacOS/Blender`

**Most users can skip this section** - test directly on RunPod instead!

---

## 🎯 Camera Angles Reference

| Angle | Name | Description |
|-------|------|-------------|
| 0° | Front | Face visible, best for facial landmarks |
| 45° | Front-right | Natural 3/4 view, good for most poses |
| 90° | Right | Full profile, side poses |
| 135° | Back-right | Over-shoulder right |
| 180° | Back | Back view, spine detection |
| 225° | Back-left | Over-shoulder left |
| 270° | Left | Full profile left |
| 315° | Front-left | Natural 3/4 view left |

**Default:** 8 angles (comprehensive coverage)  
**Quick test:** 4 angles (0°, 90°, 180°, 270°)

---

## ⚙️ Configuration Options

### Change Number of Angles

Edit `render_multi_angle.py`:
```bash
NUM_ANGLES = 4  # or 8, 16, etc.
```

### Change Resolution

Edit script:
```bash
scene.render.resolution_x = 1024  # Default: 512
scene.render.resolution_y = 1024  # Default: 512
```

### Render Full Animation (Not Just Frame 1)

Edit script:
```bash
render_character_multi_angle(
    fbx_path,
    output_dir,
    num_angles=8,
    render_all_frames=True  # Default: False
)
```

### Adjust Camera Distance (Padding)

Edit `blender_camera_utils.py`:
```bash
calculate_camera_position(
    bbox_min, bbox_max,
    padding_factor=1.3  # Default: 1.2 (20% padding)
)
```

---

## 🐛 Troubleshooting

### "No armature found"
- FBX file might be corrupted
- Try re-downloading from Mixamo
- Check file size: should be >100 KB

### "Character too small/large in frame"
- Edit `blender_camera_utils.py`
- Adjust `padding_factor` (1.2 = default)
- Increase for more space, decrease for tighter framing

### "Tests failing"
- Ensure Blender is installed correctly
- Check Python path in script
- Run with verbose: `blender --background --python-expr "import sys; print(sys.path)"`

### "Render is black"
- Check lighting setup
- Verify camera constraint is working
- Test in Blender GUI first

### "Out of GPU memory"
- Reduce resolution: 512×512 or 256×256
- Use fewer samples: `taa_render_samples = 32`
- Process fewer characters at once

---

## 📊 Performance Tips

### Fastest Workflow
1. Batch upload characters (all at once)
2. Run batch render (automatic)
3. Batch download results

### Most Efficient
- Keep RunPod running during active work
- Terminate immediately when done (GPU costs $$)
- Use spot instances if available (cheaper)

### Quality vs Speed
- **Fast:** 4 angles, 512×512, 32 samples
- **Balanced:** 8 angles, 512×512, 64 samples
- **High quality:** 8 angles, 1024×1024, 128 samples

---

## 📚 Documentation Index

| File | Purpose |
|------|---------|
| `WORKFLOW_CHEATSHEET.md` | This file - quick commands |
| `CAMERA_QUICK_START.md` | Camera system quick reference |
| `BLENDER_CAMERA_GUIDE.md` | Deep technical explanation |
| `CAMERA_SYSTEM_SUMMARY.md` | Implementation overview |
| `TODO_3D_Pose_Factory.md` | Project progress tracker |

---

## ✅ Pre-Flight Checklist

Before starting a render job on RunPod:

- [ ] Mixamo FBX files downloaded to Mac (`downloads/` folder)
- [ ] Files uploaded to R2 (`rclone copy downloads/ ...`)
- [ ] Blender camera scripts uploaded to R2 (`rclone copy scripts/ ...`)
- [ ] RunPod started and SSH connection working
- [ ] Characters downloaded to pod (`rclone copy` to `/workspace/pose-factory/characters/`)
- [ ] Camera scripts downloaded to pod (`rclone copy` to `/workspace/pose-factory/scripts/`)
- [ ] Test suite passed on pod (`blender --background --python scripts/test_camera_framing.py`)
- [ ] Output directory has space (~1 GB per 100 renders)
- [ ] Render settings configured (angles, resolution in script)

**All checked?** You're ready to render! 🎬

**Note:** You do NOT need Blender installed on your Mac. Everything runs on RunPod.

---

## ⚡ Quick Command Reference

### On Mac (Upload)
```bash
cd ~/projects/3D\ Pose\ Factory/
rclone copy downloads/ r2_pose_factory:pose-factory/characters/ --progress
rclone copy scripts/blender_camera_utils.py r2_pose_factory:pose-factory/scripts/
rclone copy scripts/render_multi_angle.py r2_pose_factory:pose-factory/scripts/
```

### On RunPod (Render)
```bash
cd /workspace/pose-factory/
rclone copy r2_pose_factory:pose-factory/characters/ characters/ --progress
rclone copy r2_pose_factory:pose-factory/scripts/ scripts/ --progress
blender --background --python scripts/test_camera_framing.py
blender --background --python scripts/render_multi_angle.py -- --batch
rclone copy output/ r2_pose_factory:pose-factory/output/ --progress
```

### On Mac (Download)
```bash
cd ~/projects/3D\ Pose\ Factory/
rclone copy r2_pose_factory:pose-factory/output/ data/working/ --progress
```

---

**Quick Start:** Test → Upload → Render → Download → Terminate  
**Time:** ~15 minutes per batch of 6 characters (8 angles each)  
**No local Blender needed!** Everything runs on RunPod.

