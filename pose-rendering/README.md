# Pose Rendering Pipeline

**Automated Mixamo character rendering for MediaPipe training data generation**

---

## Status: ✅ Production Ready

This workflow renders Mixamo animated characters from 8 angles with automatic camera framing.

---

## Quick Start

### One-Command Render (Recommended):
```bash
./scripts/render_pipeline.sh --batch
```

That's it! Upload → Render → Download all automated.

### Manual Steps:
```bash
# 1. Upload characters to R2
rclone copy downloads/ r2_pose_factory:pose-factory/characters/

# 2. SSH to RunPod and render
ssh -i ~/.ssh/id_ed25519_runpod root@YOUR_POD_ID-ssh.runpod.io
cd /workspace/pose-factory
blender --background --python render_simple_working.py -- --batch

# 3. Download results
rclone copy r2_pose_factory:pose-factory/output/ data/working/
```

See [docs/POSE_RENDERING_WORKFLOW.md](docs/POSE_RENDERING_WORKFLOW.md) for full details.

---

## What It Does

### Input:
- Mixamo FBX files (rigged, animated 3D characters)
- Download free from https://www.mixamo.com/

### Process (Fully Automatic):
1. ✅ Import character (fixes Mixamo's scale issues)
2. ✅ Calculate optimal camera position
3. ✅ Render from 8 angles
4. ✅ Export 512×512 PNG images

### Output:
```
data/working/
  Dancing_Twerk/
    front.png
    front_right.png
    right.png
    back_right.png
    back.png
    back_left.png
    left.png
    front_left.png
  X_Bot/
    front.png
    ... (8 images)
```

**Perfect training data for MediaPipe pose detection!**

---

## Key Features

### 🎥 Smart Camera System
- **Automatic framing** - Characters always in frame, no manual positioning
- **Mathematical positioning** - Uses FOV + bounding box calculations
- **Handles Mixamo quirks** - Fixes 0.01 armature scale issue
- **Headless compatible** - Runs on RunPod without GUI

### ⚡ Fast & Efficient
- **6 characters × 8 angles** = 48 renders in ~2-3 minutes
- **Cloud rendering** - No local Blender needed
- **Batch processing** - Process entire directory automatically

### 🧪 Production Grade
- **Tested** - Full test suite validates camera math
- **Documented** - 6 comprehensive guides
- **Automated** - One-command pipeline script

---

## Project Structure

```
pose-rendering/
├── scripts/
│   ├── render_simple_working.py     ← ⭐ Main renderer
│   ├── render_pipeline.sh           ← ⭐ Automation script
│   ├── blender_camera_utils.py      ← Camera framing library
│   ├── test_camera_framing.py       ← Test suite
│   ├── batch_process.py             ← MediaPipe processing
│   └── ...
├── docs/
│   ├── POSE_RENDERING_WORKFLOW.md   ← ⭐ START HERE
│   ├── WORKFLOW_CHEATSHEET.md       ← Quick reference
│   ├── BLENDER_CAMERA_GUIDE.md      ← Technical deep dive
│   └── ...
├── downloads/                        ← Put Mixamo FBX files here
├── data/
│   ├── working/                      ← Downloaded renders appear here
│   └── archive/                      ← Old renders
└── README.md                         ← You are here
```

---

## Performance

| Metric | Value |
|--------|-------|
| Render time (1 character, 8 angles) | ~2-3 seconds |
| Batch (6 characters × 8 angles) | ~2-3 minutes |
| Image resolution | 512×512 (configurable) |
| Full workflow (upload → render → download) | ~10-15 minutes |
| Cost per batch on RunPod (A40 GPU) | ~$0.50-1.00 |

---

## Documentation

| Document | Purpose |
|----------|---------|
| **[POSE_RENDERING_WORKFLOW.md](docs/POSE_RENDERING_WORKFLOW.md)** | ⭐ Complete visual workflow |
| **[WORKFLOW_CHEATSHEET.md](docs/WORKFLOW_CHEATSHEET.md)** | Quick command reference |
| **[GETTING_STARTED.md](docs/GETTING_STARTED.md)** | First-time setup |
| **[BLENDER_CAMERA_GUIDE.md](docs/BLENDER_CAMERA_GUIDE.md)** | Technical details |
| **[CAMERA_QUICK_START.md](docs/CAMERA_QUICK_START.md)** | Camera customization |
| **[CAMERA_SYSTEM_SUMMARY.md](docs/CAMERA_SYSTEM_SUMMARY.md)** | Implementation overview |

**New user?** Start with `POSE_RENDERING_WORKFLOW.md`

---

## Next Steps

1. **Download Mixamo Characters**
   - Go to https://www.mixamo.com/
   - Download 2-3 animated FBX files
   - Save to `downloads/`

2. **Set Up R2 + RunPod**
   - See `../shared/docs/RUNPOD_CONFIG.md`
   - Get your pod ID and SSH key

3. **Run First Batch**
   ```bash
   ./scripts/render_pipeline.sh --batch
   ```

4. **Expand Dataset**
   - Download more Mixamo animations
   - Render hundreds of poses
   - Feed to MediaPipe for training labels

---

## Integration with Character Creation

Want to use custom characters instead of Mixamo?

1. Create character using `../character-creation/` workflow
2. Export as FBX
3. Apply Mixamo animation to custom character (via Mixamo website)
4. Use this rendering pipeline as usual

---

**Last Updated:** 2025-11-22

**Status:** ✅ Production ready, actively generating training data

## Related Documentation

- [Automation Reliability](patterns/automation-reliability.md) - automation
- [Cost Management](Documents/reference/MODEL_COST_COMPARISON.md) - cost management
- [README](README) - 3D Pose Factory
