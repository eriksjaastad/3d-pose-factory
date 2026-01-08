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
---

# 3D Pose Factory

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

