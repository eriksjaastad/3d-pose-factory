# 3d-pose-factory - Simple Workflow (No Local Blender)

## 🚀 **AUTOMATED PIPELINE (Use This!)** 

**One command does everything!** No more copy-pasting 10+ commands.

### **Full batch render (all 6 characters × 8 angles = 48 images):**
```bash
cd ~/projects/3D\ Pose\ Factory/
./scripts/render_pipeline.sh
```
Automatically: uploads scripts → SSHs to pod → renders → downloads results with timestamp

### **Quick test (just X Bot - 8 images):**
```bash
./scripts/render_pipeline.sh --single
```
Perfect for testing camera adjustments before full batch

### **Just download existing results (no rendering):**
```bash
./scripts/render_pipeline.sh --download-only
```
Use this if render already completed on pod

### **Skip the pod ID prompt:**
```bash
./scripts/render_pipeline.sh --pod 6gpur3lb2h5pzi-6441128f
```
Saves one step if you know your current pod ID

**That's it!** One command replaces the entire manual workflow below.

---

## 💡 Pro Tips (Read This First!)

1. **Start small**: Test with 1-2 characters first, not all 6!
2. **Check the test**: Always run `test_camera_framing.py` on first use
3. **Monitor first render**: Watch the first character render to catch issues early
4. **Terminate pod immediately**: Don't leave it running after upload (costs $$)
5. **Batch downloads**: Get all characters at once from Mixamo, then batch render

## ⚠️ Common Issues

| Issue | Quick Fix |
|-------|-----------|
| "blender: command not found" on RunPod | Run `bash scripts/setup_pod.sh` first |
| "No armature found in FBX" | Verify FBX uploaded: `ls -lh characters/*.fbx` |
| Character too small/large in frame | Edit `blender_camera_utils.py`, adjust `padding_factor` |
| Tests failing | Check error message, see `GETTING_STARTED.md` |
| Render is black | Check lighting setup, verify camera constraint working |

---

## 📋 The Complete Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR MAC                                 │
│                                                                  │
│  1. Download Mixamo FBX files                                   │
│     → Save to: ~/projects/3d-pose-factory/downloads/            │
│                                                                  │
│  2. Upload to R2 cloud storage                                  │
│     $ rclone copy downloads/ r2_pose_factory:.../characters/    │
│     $ rclone copy scripts/ r2_pose_factory:.../scripts/         │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   R2 Cloud    │
                    │   Storage     │
                    └───────┬───────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RUNPOD                                    │
│                  (Blender installed here!)                       │
│                                                                  │
│  3. SSH to RunPod                                               │
│     $ ssh -i ~/.ssh/id_ed25519 root@...                 │
│                                                                  │
│  4. Download from R2                                            │
│     $ rclone copy r2_pose_factory:.../characters/ characters/   │
│     $ rclone copy r2_pose_factory:.../scripts/ scripts/         │
│                                                                  │
│  5. Test camera system                                          │
│     $ blender --background --python scripts/test_camera_...py   │
│                                                                  │
│  6. Render! (batch mode = all characters, 8 angles)             │
│     $ blender --background --python scripts/render_multi_...py  │
│                                                                  │
│  7. Upload results to R2                                        │
│     $ rclone copy output/ r2_pose_factory:.../output/           │
│                                                                  │
│  8. Exit & terminate pod (save money!)                          │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   R2 Cloud    │
                    │   Storage     │
                    └───────┬───────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR MAC                                 │
│                                                                  │
│  9. Download results                                            │
│     $ rclone copy r2_pose_factory:.../output/ data/working/     │
│                                                                  │
│  10. View your 48 perfectly-framed renders! 🎉                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Points

✅ **No Blender installation on Mac** - Everything runs on RunPod  
✅ **Automatic camera framing** - No manual positioning needed  
✅ **Handles Mixamo scale issues** - Just works  
✅ **Multi-angle rendering** - 8 angles per character automatically  
✅ **Fast** - 6 characters × 8 angles = 48 renders in ~2-3 minutes  

---

## 📝 The Exact Commands

### On Your Mac (Before RunPod)

```bash
# Navigate to project
cd ~/projects/3D\ Pose\ Factory/

# Upload characters
rclone copy downloads/ r2_pose_factory:pose-factory/characters/ --progress

# Upload scripts
rclone copy scripts/blender_camera_utils.py r2_pose_factory:pose-factory/scripts/
rclone copy scripts/render_multi_angle.py r2_pose_factory:pose-factory/scripts/
rclone copy scripts/test_camera_framing.py r2_pose_factory:pose-factory/scripts/
```

### On RunPod (The Main Work)

```bash
# Connect to your pod (use _runpod shortcut or SSH)
# ssh <POD_ID>@ssh.runpod.io -i ~/.ssh/id_ed25519

# Navigate to workspace
cd /workspace/pose-factory/

# Download everything
rclone copy r2_pose_factory:pose-factory/characters/ characters/ --progress
rclone copy r2_pose_factory:pose-factory/scripts/ scripts/ --progress

# Test (optional but recommended)
blender --background --python scripts/test_camera_framing.py

# RENDER! (This is the magic part)
blender --background --python scripts/render_multi_angle.py -- --batch

# Upload results
rclone copy output/ r2_pose_factory:pose-factory/output/ --progress

# Exit
exit

# Terminate pod via web UI: https://www.runpod.io/console/pods
```

### Back on Your Mac (Get Results)

```bash
# Download rendered images
cd ~/projects/3D\ Pose\ Factory/
rclone copy r2_pose_factory:pose-factory/output/ data/working/ --progress

# Check results
ls -R data/working/
```

---

## ⏱️ Time Breakdown

| Step | Time |
|------|------|
| Download Mixamo characters | 2-5 min (manual) |
| Upload to R2 | 1-2 min |
| SSH + download to RunPod | 1-2 min |
| Test camera system | 30 sec |
| Render (6 chars × 8 angles) | 2-3 min |
| Upload results to R2 | 1 min |
| Download to Mac | 1-2 min |
| **Total** | **~10-15 minutes** |

---

## 🎓 What Gets Rendered?

For each Mixamo character, you get **8 images** from different angles:

```
output/
  X_Bot/
    front.png         ← 0° (facing camera)
    front_right.png   ← 45°
    right.png         ← 90° (profile right)
    back_right.png    ← 135°
    back.png          ← 180° (back view)
    back_left.png     ← 225°
    left.png          ← 270° (profile left)
    front_left.png    ← 315°
    
  Dancing_Twerk/
    front.png
    front_right.png
    ... (8 images)
    
  (etc. for each character)
```

**Perfect for MediaPipe training data!**

---

## 💡 Pro Tips

1. **Start small**: Test with 1-2 characters first
2. **Check the test**: Always run `test_camera_framing.py` on first use
3. **Monitor first render**: Watch the first character render to catch issues early
4. **Terminate pod immediately**: Don't leave it running after upload (costs $$)
5. **Batch downloads**: Get all characters at once, then batch render

---

## 🐛 Common Issues

### "blender: command not found" on RunPod
**Fix:** Run the setup script first:
```bash
cd /workspace/pose-factory/
bash scripts/setup_pod.sh
```

### "No armature found in imported FBX"
**Fix:** Verify FBX files uploaded correctly:
```bash
ls -lh characters/*.fbx
```

### Tests failing
**Fix:** Check the error message - likely missing dependencies or paths wrong

### Character too small/large in frame
**Fix:** Edit `blender_camera_utils.py`, adjust `padding_factor` (default: 1.2)

---

## 📚 More Info

- **Full workflow:** `WORKFLOW_CHEATSHEET.md`
- **Camera system details:** `BLENDER_CAMERA_GUIDE.md`
- **Troubleshooting:** `GETTING_STARTED.md`
- **Quick reference:** `CAMERA_QUICK_START.md`

---

## ✅ Checklist (Print This!)

- [ ] Download Mixamo FBX files to `downloads/`
- [ ] Upload to R2: `rclone copy downloads/ ...`
- [ ] Upload scripts to R2: `rclone copy scripts/ ...`
- [ ] Start RunPod, get SSH credentials
- [ ] SSH to RunPod
- [ ] Download characters to pod
- [ ] Download scripts to pod
- [ ] Test: `blender --background --python scripts/test_camera_framing.py`
- [ ] Render: `blender --background --python scripts/render_multi_angle.py -- --batch`
- [ ] Upload results to R2
- [ ] Download to Mac
- [ ] Terminate pod
- [ ] Celebrate! 🎉

**You now have perfectly-framed, multi-angle pose renders!**

## Related Documentation

- [Cost Management](Documents/reference/MODEL_COST_COMPARISON.md) - cost management
- [Tiered AI Sprint Planning](patterns/tiered-ai-sprint-planning.md) - prompt engineering
- [README](README) - 3D Pose Factory
