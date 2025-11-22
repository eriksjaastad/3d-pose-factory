# Blender Camera Framing System - Getting Started

## ⚠️ Important: Where to Run These Scripts

These scripts **require Blender** to run. You have two options:

---

## 🚀 **Option 1: Run on RunPod (Recommended)**

**Why:** Blender is already installed, you have GPU acceleration, and this is where your production renders will happen anyway.

### Quick Start:

```bash
# 1. Upload scripts from Mac
cd ~/projects/3D\ Pose\ Factory/
rclone copy scripts/ r2_pose_factory:pose-factory/scripts/
rclone copy downloads/ r2_pose_factory:pose-factory/characters/

# 2. SSH to RunPod
ssh -i ~/.ssh/id_ed25519 root@<POD_ID>-ssh.runpod.io -p <PORT>

# 3. Download to pod
cd /workspace/pose-factory/
rclone copy r2_pose_factory:pose-factory/scripts/ scripts/
rclone copy r2_pose_factory:pose-factory/characters/ characters/

# 4. Test the system
blender --background --python scripts/test_camera_framing.py

# 5. Render!
blender --background --python scripts/render_multi_angle.py -- --batch
```

**That's it!** No local Blender installation needed.

---

## 🍎 **Option 2: Run Locally on Mac**

**Why:** Test before uploading, iterate faster during development.

**Requires:** Installing Blender on your Mac.

### Step 1: Install Blender

**Via Homebrew (easiest):**
```bash
brew install --cask blender
```

**Or download from:** https://www.blender.org/download/

### Step 2: Find Blender's Path

```bash
# Test if 'blender' command works
blender --version

# If not found, use full path:
/Applications/Blender.app/Contents/MacOS/Blender --version
```

### Step 3: Run Scripts

```bash
cd ~/projects/3D\ Pose\ Factory/

# If 'blender' command works:
blender --background --python scripts/test_camera_framing.py

# If you need full path:
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/test_camera_framing.py
```

### Step 4: Create an Alias (Optional)

Add to your `~/.zshrc`:
```bash
alias blender="/Applications/Blender.app/Contents/MacOS/Blender"
```

Then reload:
```bash
source ~/.zshrc
```

---

## 📋 **Which Option Should I Choose?**

| Scenario | Recommendation |
|----------|----------------|
| "I just want renders fast" | **Option 1** (RunPod only) |
| "I want to test code changes locally" | **Option 2** (Install on Mac) |
| "I don't want to install Blender" | **Option 1** (RunPod only) |
| "I'm developing new features" | **Option 2** (faster iteration) |
| "I have slow internet" | **Option 2** (avoid uploads) |

**Most users:** Start with **Option 1** (RunPod). Install locally only if you need faster iteration.

---

## 🧪 **Testing the Installation**

### On Mac (if you installed Blender):

```bash
cd ~/projects/3D\ Pose\ Factory/

# Test 1: Blender is installed
blender --version
# Should show: "Blender 4.0.2" or similar

# Test 2: Camera system works
blender --background --python scripts/test_camera_framing.py
# Should show: "✓ ALL TESTS PASSED!"

# Test 3: Single character render
blender --background --python scripts/render_mixamo_v2.py
# Should create: output/mixamo_test_v2.png
```

### On RunPod:

```bash
cd /workspace/pose-factory/

# Test 1: Blender is installed
blender --version
# Should show: "Blender 4.0.2" or similar

# Test 2: Camera system works
blender --background --python scripts/test_camera_framing.py
# Should show: "✓ ALL TESTS PASSED!"

# Test 3: Batch render
blender --background --python scripts/render_multi_angle.py -- --batch
# Should create: output/batch_multi_angle/*/
```

---

## 📚 **Next Steps**

- **For workflow commands:** See `WORKFLOW_CHEATSHEET.md`
- **For camera usage:** See `CAMERA_QUICK_START.md`
- **For technical details:** See `BLENDER_CAMERA_GUIDE.md`

---

## 🐛 **Troubleshooting**

### "Command not found: blender" (Mac)

**Solution:** Blender not installed or not in PATH.

```bash
# Option A: Install via Homebrew
brew install --cask blender

# Option B: Use full path
/Applications/Blender.app/Contents/MacOS/Blender --version

# Option C: Create alias in ~/.zshrc
alias blender="/Applications/Blender.app/Contents/MacOS/Blender"
```

### "Command not found: blender" (RunPod)

**Solution:** Run the setup script first.

```bash
cd /workspace/pose-factory/
bash scripts/setup_pod.sh
```

This installs Blender + all dependencies.

### "No module named 'blender_camera_utils'"

**Solution:** Script directory not in Python path.

Make sure you're running from the project root:
```bash
cd ~/projects/3D\ Pose\ Factory/  # Mac
# or
cd /workspace/pose-factory/        # RunPod

# Then run:
blender --background --python scripts/test_camera_framing.py
```

### "No armature found in imported FBX"

**Solution:** FBX file path is wrong or file is corrupted.

```bash
# Check the file exists:
ls -lh downloads/*.fbx  # Mac
ls -lh characters/*.fbx  # RunPod

# Re-download from Mixamo if needed
```

---

## ✅ **Recommended Workflow**

1. **Develop/test on Mac** (optional, requires Blender installation)
2. **Upload to R2** (rclone copy)
3. **Render on RunPod** (production, GPU-accelerated)
4. **Download results** (rclone copy back)

**Or skip step 1** and go straight to RunPod! 🚀

