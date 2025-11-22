# 3D Pose Factory

**AI-Powered 3D Character Pipeline for Pose Detection Training Data**

---

## Two Workflows

### 1. Pose Rendering Pipeline ✅
**Status:** Production-ready

Render Mixamo characters from 8 angles → Generate MediaPipe training data

📁 **[pose-rendering/](pose-rendering/)** - Complete workflow with documentation

### 2. AI Character Creation 🚧  
**Status:** Research & Development

Use Blender + AI to create custom 3D characters → Feed to rendering pipeline

📁 **[character-creation/](character-creation/)** - Experimental workflow, templates ready

---

## Quick Start

**Prerequisites:** RunPod instance running (see [shared/docs/RUNPOD_CONFIG.md](shared/docs/RUNPOD_CONFIG.md))

### For Pose Rendering (Ready Now):
```bash
pose-rendering/scripts/render_pipeline.sh --batch
```

**Script will prompt for your POD_ID.** Result: 48 renders in ~2-3 minutes!

### For Character Creation (Coming Soon):
```bash
character-creation/scripts/character_pipeline.sh --create "athletic woman, age 25"
```

**Script will prompt for your POD_ID.** Result: Custom character FBX!

---

**Tip:** Set `RUNPOD_POD_ID` environment variable to skip the prompt.

**See individual workflow READMEs for complete details.**

---

## 📁 Project Structure

```
3D Pose Factory/
│
├── pose-rendering/          ← ✅ Workflow 1: Mixamo render pipeline
│   ├── scripts/             ← Render automation (render_pipeline.sh, etc.)
│   ├── docs/                ← Full pose rendering documentation
│   ├── downloads/           ← Mixamo FBX files
│   ├── data/                ← Rendered output
│   └── README.md            ← START HERE for pose rendering
│
├── character-creation/      ← 🚧 Workflow 2: AI character generation
│   ├── scripts/             ← Character creation scripts (templates)
│   ├── docs/                ← Character creation research & docs
│   ├── downloads/           ← Character assets
│   ├── data/                ← Generated characters
│   └── README.md            ← START HERE for character creation
│
├── shared/                  ← Common infrastructure
│   ├── scripts/             ← RunPod setup, shared utilities
│   └── docs/                ← RunPod/R2 configuration
│
├── config/                  ← Project configuration
└── README.md                ← You are here
```

---

## 🔑 Key Features

### ✅ Workflow 1: Pose Rendering
- **Fully automated** - One command uploads, renders, and downloads
- **Smart camera** - Mathematical framing, no manual positioning
- **Fast** - 48 renders in 2-3 minutes on RunPod GPU
- **Production-ready** - Tested, documented, generating training data

### 🚧 Workflow 2: Character Creation
- **AI-driven** - Describe character, Blender generates it
- **Parametric** - Control body type, age, gender, appearance
- **Unlimited variety** - Beyond Mixamo's limited library
- **In development** - Templates ready, tool selection in progress

---

## 💻 System Requirements

**On Your Mac:**
- rclone (cloud storage sync)
- SSH (RunPod connection)
- **No Blender needed!**

**On RunPod:**
- GPU: A40 or better
- Software: Auto-installed (Blender, Python, MediaPipe)

---

## 📚 Documentation

### Start Here:
- **[pose-rendering/README.md](pose-rendering/)** ⭐ - For rendering Mixamo characters
- **[character-creation/README.md](character-creation/)** 🚧 - For creating custom characters
- **[shared/docs/RUNPOD_CONFIG.md](shared/docs/)** - RunPod & R2 setup

**Each workflow has complete, independent documentation.**

---

## 🎯 What This Project Does

### Workflow 1: Pose Rendering (Production)
**Input:** Mixamo animated characters (free download)  
**Process:** Auto-import → Smart camera framing → 8-angle render  
**Output:** 512×512 PNG images, perfect for MediaPipe training  
**Use Case:** Generate thousands of labeled poses at scale

### Workflow 2: Character Creation (Experimental)
**Input:** Text description ("athletic woman, age 25")  
**Process:** AI interprets → Blender generates → Export FBX  
**Output:** Custom 3D character ready for animation  
**Use Case:** Create diverse, unique characters beyond Mixamo

**These workflows integrate:** Create custom character → Animate with Mixamo → Render with Workflow 1

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Pose Rendering** | |
| Single character (8 angles) | ~2-3 seconds |
| Batch (6 chars × 8 angles = 48 images) | ~2-3 minutes |
| Full workflow (upload → render → download) | ~10-15 minutes |
| Cost per batch (RunPod A40) | ~$0.50-1.00 |
| **Character Creation** | |
| Status | 🚧 Coming soon |

---

## 🔗 Useful Links

- **Mixamo** (free rigged characters): https://www.mixamo.com/
- **RunPod** (GPU compute): https://www.runpod.io/
- **Cloudflare R2** (storage): https://dash.cloudflare.com/
- **Blender** (3D software): https://www.blender.org/
- **MediaPipe** (pose detection): https://google.github.io/mediapipe/

---

## 🎉 Ready to Start?

### Pose Rendering (5 Steps):
1. Read [pose-rendering/README.md](pose-rendering/)
2. Set up RunPod + R2 (see [shared/docs/RUNPOD_CONFIG.md](shared/docs/))
3. Download 2-3 Mixamo characters
4. Run `cd pose-rendering && ./scripts/render_pipeline.sh --batch`
5. Get 48 perfect renders in minutes!

### Character Creation:
🚧 **Coming soon** - Templates ready, researching best tool (Charmorph vs procedural)

---

**Status:**  
✅ Pose Rendering - Production-ready, generating training data  
🚧 Character Creation - Structure ready, tool selection in progress

**Built with:** Production-grade pipeline engineering + mathematical camera framing + cloud automation
