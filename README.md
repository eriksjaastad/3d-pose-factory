
<!-- SCAFFOLD:START - Do not edit between markers -->
# 3d-pose-factory

Brief description of the project's purpose

## Quick Start

```bash
# Setup
pip install -r requirements.txt

# Run
python main.py
```

## Documentation

See the `Documents/` directory for detailed documentation.

## Status

- **Current Phase:** Foundation
- **Status:** #status/active

<!-- SCAFFOLD:END - Custom content below is preserved -->
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
doppler run -- python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the dashboard (subsequent runs)
cd dashboard
source venv/bin/activate
doppler run -- python3 app.py

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
cd "${PROJECTS_ROOT}/3d-pose-factory/dashboard"
doppler run -- python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Daily Usage

```bash
cd "${PROJECTS_ROOT}/3d-pose-factory/dashboard"
source venv/bin/activate
doppler run -- python3 app.py
```

Browser opens automatically to http://localhost:5001

**That's it!** Everything else (starting pods, submitting jobs, downloading results) happens in the dashboard.

**Full docs:** [dashboard/README.md](dashboard/README.md)

---

## 📁 Project Structure

```bash
3d-pose-factory/
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
- **Parame... [truncated]

---
tags:
  - map/project
  - p/3d-pose-factory
  - type/ai-pipeline
  - domain/computer-vision
  - status/active
  - tech/python
  - tech/python/blender
  - infra/runpod
  - infra/r2
created: 2025-12-31

# 3d-pose-factory

AI-powered 3D character pipeline for pose detection training data generation using Blender automation on RunPod GPUs. This production system renders Mixamo characters from 8 angles in 2-3 minutes (48 images per batch), featuring Mission Control orchestration, smart camera framing, and MediaPipe training data output. The system includes both a web dashboard (Flask) and CLI for job submission, with SSH agent automation and Cloudflare R2 storage integration.

## Key Components

### Pose Rendering (Production)
- `pose-rendering/` - Main pipeline (33 files, 17 Python)
  - Render automation scripts
  - Smart camera framing (mathematical)
  - 8-angle capture system
  - MediaPipe data generation
  - Documentation (8 MD files)

### Character Creation (R&D)
- `character-creation/` - Experimental (16 files, 11 Python)
  - AI character generation
  - Blender templates
  - Character pipeline scripts

### Mission Control
- `dashboard/` - Web UI (8 files)
  - Flask backend (`app.py`)
  - Job submission interface
  - Real-time progress tracking
  - One-click result downloads
  - Dark mode UI

### Shared Infrastructure
- `shared/` - Common utilities (25 files)
  - `scripts/mission_control.py` - CLI orchestrator
  - RunPod setup scripts
  - R2 integration
  - SSH automation

### Configuration
- `config/` - System configuration (1 YAML)
  - RunPod credentials
  - R2 bucket settings
  - GPU preferences

## Status

**Tags:** #map/project #p/3d-pose-factory  
**Status:** #status/active #status/production (Pose Rendering)  
**Last Major Update:** November 2025 (Mission Control complete)  
**Infrastructure:** #infra/runpod #infra/r2


scaffolding_version: 1.0.0
scaffolding_date: 2026-01-14

## Related Documentation

- [Automation Reliability](patterns/automation-reliability.md) - automation
- [AI Team Orchestration](patterns/ai-team-orchestration.md) - orchestration
- [README](README) - 3D Pose Factory
- [AGENTS.md](AGENTS.md)
- [BLENDER_AI_FULL_DREAM_PIPELINE.md](BLENDER_AI_FULL_DREAM_PIPELINE.md)
- [CLAUDE.md](CLAUDE.md)
- [Documents/README.md](../ai-model-scratch-build/README.md)
- [Documents/REVIEWS_AND_GOVERNANCE_PROTOCOL.md](../project-scaffolding/REVIEWS_AND_GOVERNANCE_PROTOCOL.md)
- [Documents/patterns/code-review-standard.md](../writing/Documents/patterns/code-review-standard.md)
- [Documents/patterns/learning-loop-pattern.md](../writing/Documents/patterns/learning-loop-pattern.md)
- [Documents/reference/LOCAL_MODEL_LEARNINGS.md](../writing/Documents/reference/LOCAL_MODEL_LEARNINGS.md)
- [PIPELINE_OVERVIEW.md](PIPELINE_OVERVIEW.md)
- [QUICKSTART.md](QUICKSTART.md)
- [README.md](README.md)
- [REDEMPTION_CERTIFICATE.md](REDEMPTION_CERTIFICATE.md)
- [TODO.md](TODO.md)
- [character-creation/README.md](../ai-model-scratch-build/README.md)
- [character-creation/TODO.md](../TODO.md)
- [character-creation/docs/CHARACTER_CREATION_WORKFLOW.md](character-creation/docs/CHARACTER_CREATION_WORKFLOW.md)