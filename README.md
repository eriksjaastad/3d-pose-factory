# Pose Factory Render Agent 🏭

**AI-Powered 3D Character Pipeline for Pose Detection Training Data**

> *Fully automated Blender + Stability AI SDXL pipeline with SSH agent orchestration*

📖 **[Read the Pipeline Overview](PIPELINE_OVERVIEW.md)** - Architecture, workflows, and lessons learned

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

### 🎨 Mission Control Dashboard (Web UI - NEW!)

**The best way to use Mission Control - with a beautiful web interface!**

```bash
# First time setup
cd dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the dashboard (subsequent runs)
cd dashboard
source venv/bin/activate
python3 app.py

# Browser auto-opens to: http://localhost:5001
```

**Features:**
- 📊 Visual job queue with real-time updates
- ➕ Submit jobs with a form (no terminal!)
- 📥 One-click download of results
- 🎨 Dark mode UI (because we're civilized)

### 🚀 Mission Control CLI (Command Line)

**Prefer the terminal? The CLI still works great:**

```bash
# From your Mac, render characters automatically:
./shared/scripts/mission_control.py render --wait

# That's it! ☕ Go make coffee while it:
#   1. Uploads scripts to R2
#   2. Pod picks up job automatically
#   3. Renders on GPU
#   4. Downloads results to your Mac
```

**First time?** See setup below ⬇️

### Traditional Workflow (Legacy)

If you prefer the old manual approach:

```bash
# Pose rendering
pose-rendering/scripts/render_pipeline.sh --batch

# Character creation (coming soon)
character-creation/scripts/character_pipeline.sh
```

---

## 🛠️ Setup

### Dashboard Setup (One Time)

```bash
cd "${PROJECTS_ROOT}/3D Pose Factory/dashboard"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Daily Usage

```bash
cd "${PROJECTS_ROOT}/3D Pose Factory/dashboard"
source venv/bin/activate
python3 app.py
```

Browser opens automatically to http://localhost:5001

**That's it!** Everything else (starting pods, submitting jobs, downloading results) happens in the dashboard.

**Full docs:** [dashboard/README.md](dashboard/README.md)

---

## 📁 Project Structure

```
3D Pose Factory/
│
├── dashboard/               ← 🎨 NEW! Web UI for everything
│   ├── app.py               ← Flask backend
│   ├── templates/           ← Dashboard UI
│   ├── requirements.txt     ← Python dependencies
│   ├── venv/                ← Virtual environment
│   ├── TODO.md              ← Dashboard feature roadmap
│   └── README.md            ← Dashboard documentation
│
├── pose-rendering/          ← ✅ Workflow 1: Mixamo render pipeline
│   ├── scripts/             ← Render automation
│   ├── docs/                ← Documentation
│   ├── downloads/           ← Mixamo FBX files
│   ├── data/                ← Rendered output
│   ├── TODO.md              ← Pose rendering roadmap
│   └── README.md            ← START HERE for pose rendering
│
├── character-creation/      ← 🚧 Workflow 2: AI character generation
│   ├── scripts/             ← Character creation scripts
│   ├── docs/                ← Research & documentation
│   ├── downloads/           ← Character assets
│   ├── data/                ← Generated characters
│   ├── TODO.md              ← Character creation roadmap
│   └── README.md            ← START HERE for character creation
│
├── shared/                  ← Common infrastructure
│   ├── scripts/             ← RunPod setup, Mission Control CLI
│   └── docs/                ← RunPod/R2 configuration
│
├── docs/                    ← Project-wide documentation
├── config/                  ← Project configuration
├── TODO.md                  ← Main project roadmap
└── README.md                ← You are here
```

---

## 🔑 Key Features

### 🚀 Mission Control
- **One command** - `./mission_control.py render --wait` does everything
- **No terminal switching** - Submit from Mac, auto-execute on pod, auto-download
- **Job queue system** - Uses R2 as message queue, pod polls every 30s
- **Real-time monitoring** - Check status, download anytime
- **Bulletproof workflow** - No more copy-paste errors between terminals

### ✅ Workflow 1: Pose Rendering
- **Fully automated** - Uploads, renders, and downloads automatically
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
- **[dashboard/README.md](dashboard/)** 🎨 NEW! - Web dashboard (the best way)
- **[shared/docs/MISSION_CONTROL.md](shared/docs/MISSION_CONTROL.md)** 🚀 - One-command workflow orchestrator (CLI)
- **[pose-rendering/README.md](pose-rendering/)** ⭐ - For rendering Mixamo characters
- **[character-creation/README.md](character-creation/)** 🚧 - For creating custom characters
- **[shared/docs/RUNPOD_CONFIG.md](shared/docs/)** - RunPod & R2 setup
- **[docs/RESOURCES.md](docs/RESOURCES.md)** - Blender API, tools, links

### Roadmaps & TODOs:
- **[TODO.md](TODO.md)** - Main project roadmap (infrastructure, cross-cutting features)
- **[dashboard/TODO.md](dashboard/TODO.md)** - Dashboard feature roadmap
- **[pose-rendering/TODO.md](pose-rendering/TODO.md)** - Pose rendering improvements
- **[character-creation/TODO.md](character-creation/TODO.md)** - Character creation progress

**Each workflow has complete, independent documentation and its own TODO list.**

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
