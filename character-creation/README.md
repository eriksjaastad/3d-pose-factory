# Character Creation Workflow

**AI-driven 3D character generation using Blender**

---

## Status: 🚧 Research & Development

This workflow uses Blender's Python API + AI to create custom 3D characters for pose rendering and training data generation.

---

## Quick Start

**Status:** 🚧 Templates ready, tool selection in progress

**Prerequisites:** RunPod instance running (have your POD_ID ready)

### Workflow:
**Note:** RunPod's SSH only supports interactive sessions (not remote command execution)

**Step 1 - Local:** Upload scripts to R2
```bash
character-creation/scripts/upload_to_r2.sh
```

**Step 2 - SSH to RunPod:**
```bash
ssh POD_ID@ssh.runpod.io -i ~/.ssh/id_ed25519
```

**Step 3 - On RunPod:** Run character creation
```bash
cd /workspace/character-creation
blender --background --python create_character.py -- --description "athletic woman, age 25"
```

**Step 4 - Upload results:**
```bash
rclone copy /workspace/character-creation/output/ r2_pose_factory:pose-factory/character-creation/output/
```

**Step 5 - Local:** Download results
```bash
rclone copy r2_pose_factory:pose-factory/character-creation/output/ character-creation/data/working/
```

**Status:** Testing Charmorph headless compatibility

---

## Why Custom Characters?

### Limitations of Mixamo:
- ❌ Generic "robot" aesthetic
- ❌ Limited body type variety
- ❌ No control over appearance

### Benefits of Custom Characters:
- ✅ Diverse body types (age, gender, build)
- ✅ Realistic human appearance
- ✅ AI-driven parametric generation
- ✅ Unlimited variety for training data

---

## Current Research

### Tool Options:
1. **Charmorph** (Blender add-on) - Leading candidate
   - Actively maintained (Blender 4.x compatible)
   - Parametric human generation
   - Python API for scripting
   
2. **Procedural Modeling** - Pure Python approach
   - Full control via `bpy` API
   - Time-intensive but flexible

See [docs/CHARACTER_CREATION_WORKFLOW.md](docs/CHARACTER_CREATION_WORKFLOW.md) for detailed research notes.

---

## Project Structure

```
character-creation/
├── scripts/
│   ├── character_pipeline.sh      ← Main automation (coming soon)
│   ├── create_character.py        ← Character generation script
│   └── test_character_creation.py ← Test suite
├── docs/
│   └── CHARACTER_CREATION_WORKFLOW.md
├── downloads/                      ← Textures, assets, etc.
├── data/
│   ├── working/                    ← Generated characters
│   └── archive/                    ← Old characters
└── README.md                       ← You are here
```

---

## Integration with Pose Rendering

Once characters are created, they can be used with the pose-rendering workflow:

1. Generate character → Export as FBX
2. Apply Mixamo animations to custom character
3. Use `../pose-rendering/scripts/render_simple_working.py` to render
4. Create training data as usual

---

## Next Steps

### 1. Upload Scripts to R2 (From Your Mac)
```bash
character-creation/scripts/upload_to_r2.sh
```

### 2. SSH to RunPod
```bash
ssh to6i4tul7p9hk2-644113d9@ssh.runpod.io -i ~/.ssh/id_ed25519
```

### 3. Setup & Test Charmorph (On RunPod)
```bash
cd /workspace && rclone copy r2_pose_factory:pose-factory/character-creation/scripts/setup_and_test_charmorph.sh ./ && chmod +x setup_and_test_charmorph.sh && ./setup_and_test_charmorph.sh
```

### 4. Remaining Tasks
- ⏳ Verify Charmorph works headless (test will show this)
- ⏳ Create proof-of-concept character generation
- ⏳ Build workflow for character creation → export → rendering
- ⏳ Test integration with pose rendering workflow

---

**Last Updated:** 2025-11-22

**Status:** Project structure ready, awaiting tool selection

