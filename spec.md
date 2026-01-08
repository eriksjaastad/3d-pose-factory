# 3D Pose Factory - System Specification

**Version**: 1.0.0
**Audit Date**: 2026-01-08
**Auditor**: Claude (Anthropic Opus 4.5)
**Status**: Contract Definition (Pre-Security Review)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Core Modules](#3-core-modules)
4. [Data Models & Schemas](#4-data-models--schemas)
5. [Entry Points](#5-entry-points)
6. [Workflow Contracts](#6-workflow-contracts)
7. [External Dependencies](#7-external-dependencies)
8. [Configuration Contracts](#8-configuration-contracts)
9. [Technical Debt Registry](#9-technical-debt-registry)
10. [Ghost Logic Inventory](#10-ghost-logic-inventory)
11. [Module Dependency Map](#11-module-dependency-map)

---

## 1. Executive Summary

### What This System Is

**3D Pose Factory** is a production pipeline for generating 3D character pose training data. It automates:

1. **Pose Rendering**: Multi-angle renders of Mixamo FBX characters using Blender (production-ready)
2. **Character Creation**: AI-assisted 3D character generation (R&D phase, placeholder implementation)
3. **Cloud Orchestration**: Job dispatch to RunPod GPUs via Cloudflare R2 storage

### Primary Use Case

Generate training datasets for MediaPipe pose detection by rendering animated 3D characters from multiple camera angles, creating labeled pose data at scale.

### System Boundaries

| Component | Location | Status |
|-----------|----------|--------|
| Local Mac | Development machine | Orchestrator |
| RunPod Pod | Cloud GPU | Execution environment |
| Cloudflare R2 | Cloud storage | Job queue + results |
| Stability AI | External API | AI image enhancement |

---

## 2. System Architecture

### 2.1 High-Level Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Local Mac     │────▶│  Cloudflare R2  │────▶│   RunPod Pod    │
│  (Orchestrator) │     │   (Job Queue)   │     │  (GPU Worker)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       ▼
        │                       │               ┌─────────────────┐
        │                       │               │    Blender      │
        │                       │               │  (Headless)     │
        │                       │               └─────────────────┘
        │                       │                       │
        │                       ◀───────────────────────┘
        │                       │
        ◀───────────────────────┘
        │
        ▼
┌─────────────────┐
│  Local Storage  │
│  data/working/  │
└─────────────────┘
```

### 2.2 Communication Patterns

| Pattern | Mechanism | Use Case |
|---------|-----------|----------|
| Job Dispatch | R2 file queue | `jobs/pending/*.json` |
| Status Check | R2 file existence | Poll `results/{job_id}/` |
| Result Transfer | rclone sync | Download from R2 to local |
| Pod Commands | SSH Agent (pexpect) | Bootstrap, setup |

### 2.3 Directory Structure Contract

```
3d-pose-factory/
├── dashboard/                 # Flask web UI
│   ├── app.py                 # Main Flask backend (465 lines)
│   ├── templates/             # Jinja2 HTML templates
│   └── tests/                 # pytest test suite
│
├── pose-rendering/            # PRODUCTION workflow
│   ├── scripts/               # 19 Python files
│   │   ├── render_simple_working.py  # PRIMARY RENDERER
│   │   ├── blender_camera_utils.py   # Camera math utilities
│   │   └── [debug/test files]        # GHOST LOGIC candidates
│   └── data/                  # Local working directory
│
├── character-creation/        # R&D workflow (INCOMPLETE)
│   ├── scripts/               # 11 Python files (mostly placeholders)
│   └── data/                  # Output directory
│
├── shared/                    # Common infrastructure
│   ├── scripts/               # Core orchestration
│   │   ├── mission_control.py         # CLI orchestrator
│   │   ├── setup_pod.sh               # Pod initialization
│   │   ├── pod_agent.sh               # Pod-side job executor
│   │   └── bootstrap_pod.py           # Automated pod setup
│   ├── cost_calculator.py     # Multi-provider pricing
│   └── cost_config.yaml       # Pricing data
│
└── config/
    └── config.yaml            # Base configuration
```

---

## 3. Core Modules

### 3.1 Mission Control (`shared/scripts/mission_control.py`)

**Purpose**: CLI orchestrator for job submission and monitoring.

**Class**: `MissionControl`

**Methods**:
```python
class MissionControl:
    def run_rclone(args, check=True) -> subprocess.Result
    def upload_to_r2(local_path, r2_path, show_progress=True) -> bool
    def download_from_r2(r2_path, local_path, show_progress=True) -> bool
    def create_job(job_type, params) -> Tuple[job_id, manifest_file]
    def check_job_status(job_id) -> Literal["completed", "pending", "processing", "unknown"]
    def wait_for_job(job_id, timeout=3600) -> bool
```

**Contract**:
- R2 remote: `r2_pose_factory:pose-factory`
- Job paths: `jobs/pending/`, `jobs/processing/`
- Results path: `results/{job_id}/`
- Poll interval: 30 seconds
- Default timeout: 3600 seconds (1 hour)

### 3.2 Flask Dashboard (`dashboard/app.py`)

**Purpose**: Web UI for job management and pod control.

**Routes**:
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Serve dashboard HTML |
| `/api/jobs` | GET | List all jobs |
| `/api/jobs` | POST | Submit new job |
| `/api/jobs/<id>` | GET | Get job details |
| `/api/jobs/<id>/download` | POST | Download results |
| `/api/pod/status` | GET | Get pod agent status |
| `/api/pod/id` | GET/POST | Get/save pod ID |
| `/api/pod/start` | POST | Start RunPod instance |
| `/api/pod/stop` | POST | Stop RunPod instance |
| `/api/pod/current` | GET | Get current pod from API |
| `/api/gpu/pricing` | GET | Query GPU pricing |
| `/api/cost/providers` | GET | List cost providers |
| `/api/cost/estimate` | POST | Estimate job cost |

**Contract**:
- Port: 5001
- Host: 0.0.0.0
- Debug mode: True (TECHNICAL DEBT)
- Browser auto-open: Yes (flag in `/tmp/mission_control_browser_opened`)

### 3.3 Render Engine (`pose-rendering/scripts/render_simple_working.py`)

**Purpose**: Multi-angle Blender rendering of Mixamo FBX characters.

**Functions**:
```python
def render_character_simple(fbx_path, output_dir, num_angles=8) -> None
def batch_render_simple(fbx_directory, output_dir, num_angles=8) -> None
```

**Contract - Render Parameters**:
| Parameter | Value | Notes |
|-----------|-------|-------|
| Camera distance | 3.5 meters | Hardcoded, empirically determined |
| Camera height | 1.6 meters | Near head height |
| Angles | 8 (45° increments) | 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315° |
| Resolution | 512x512 | Hardcoded |
| Render engine | EEVEE | GPU-accelerated |
| TAA samples | 64 | Anti-aliasing |
| Light type | SUN | Energy 3.0 |

**Output Structure**:
```
output_dir/
└── {character_name}/
    ├── front.png
    ├── front_right.png
    ├── right.png
    ├── back_right.png
    ├── back.png
    ├── back_left.png
    ├── left.png
    └── front_left.png
```

### 3.4 Camera Utilities (`pose-rendering/scripts/blender_camera_utils.py`)

**Purpose**: Mathematical camera positioning for Mixamo characters.

**Functions**:
```python
def get_animated_bounding_box(obj, scene=None) -> Tuple[Vector, Vector]
def get_character_bounding_box(armature_obj) -> Tuple[Vector, Vector]
def calculate_camera_position(bbox_min, bbox_max, camera_angle=45.0,
                               padding_factor=1.2, camera_fov=50.0) -> Tuple[Vector, Vector]
def setup_camera_for_character(armature_obj, camera_name="RenderCamera",
                                camera_angle=45.0, use_track_constraint=True,
                                camera_fov=50.0) -> Object
def normalize_mixamo_character(armature_obj) -> None
def find_armature_in_selection(selected_objects) -> Optional[Object]
```

**Contract**:
- Handles Mixamo scale issues (0.01 armature scale)
- Computes bounding box across ALL animation frames
- Uses FOV-based distance calculation: `distance = (bbox_diagonal / 2) / tan(fov / 2)`
- Default padding factor: 1.2 (20% margin)

**TECHNICAL DEBT**: This module is NOT used by `render_simple_working.py` - it uses simpler hardcoded camera values instead.

### 3.5 Cost Calculator (`shared/cost_calculator.py`)

**Purpose**: Multi-provider cost estimation with safety limits.

**Class**: `CostCalculator`

**Methods**:
```python
class CostCalculator:
    def estimate_cost(provider, resolution='512x512', steps=30, model='sd_1_5', count=1) -> Dict
    def validate_cost(total_cost, max_cost=None) -> Tuple[bool, str]
    def get_provider_info(provider) -> Dict
    def list_providers() -> List[Dict]
    def get_resolutions(provider) -> List[str]
    def get_models(provider) -> List[Dict]
```

**Contract - Providers**:
| Provider | Type | Base Cost | Notes |
|----------|------|-----------|-------|
| `local` | GPU time | $0.42/hr | ~5 sec/render |
| `stability` | API | $0.002 base | + resolution + steps |
| `dreamstudio` | API | $0.002 base | + resolution + steps |

**Contract - Safety Limits**:
| Limit | Value |
|-------|-------|
| `max_cost_per_job` | $100.00 |
| `warning_threshold` | $50.00 |
| `max_batch_size` | 1000 images |

### 3.6 Pod Agent (`shared/scripts/pod_agent.sh`)

**Purpose**: RunPod-side continuous job executor.

**Contract**:
- Poll interval: 30 seconds
- R2 remote: `r2_pose_factory:pose-factory`
- Workspace: `/workspace`
- Job types supported: `render`, `character`
- Cleanup: Removes local job files older than 24 hours

**Execution Flow**:
1. Poll `jobs/pending/` for `.json` files
2. Download job manifest
3. Move manifest to `jobs/processing/`
4. Download required scripts from R2
5. Download FBX files if not present
6. Execute `blender --background --python` with job script
7. Upload results to `results/{job_id}/`

### 3.7 Pod Setup (`shared/scripts/setup_pod.sh`)

**Purpose**: One-time pod environment initialization.

**Contract - Installed Packages**:
| Category | Packages |
|----------|----------|
| System | blender, libegl1, libgl1, libgomp1, jq, curl, wget, unzip, ffmpeg, tmux |
| Python | opencv-python==4.8.1.78, mediapipe==0.10.8, pillow==10.1.0, numpy==1.26.2, requests==2.31.0 |

**Contract - Directory Layout**:
```
/workspace/
├── assets/
│   ├── animations/
│   ├── characters/
│   └── meshes/
├── output/
│   ├── pose-rendering/
│   ├── character-creation/
│   └── scratch/
├── scripts/
├── logs/
├── config/
├── scratch/
└── jobs/
    ├── pending/
    └── processing/
```

**Contract - Legacy Symlinks**:
| Symlink | Target |
|---------|--------|
| `/workspace/meshes` | `/workspace/assets/meshes` |
| `/workspace/downloads` | `/workspace/assets` |

---

## 4. Data Models & Schemas

### 4.1 Job Manifest Schema

```json
{
  "job_id": "string (format: {type}_{YYYYMMDD}_{HHMMSS}_{uuid8})",
  "job_type": "render | character",
  "created_at": "string (ISO 8601)",
  "status": "pending | processing | completed | failed",
  "params": {
    "script": "string (relative path)",
    "characters": ["string"] | null,
    "output_dir": "string",
    "character_params": {
      "gender": "string",
      "age": "number",
      "body_type": "string",
      "ethnicity": "string"
    }
  }
}
```

### 4.2 Cost Estimate Response

```json
{
  "total": "number (USD)",
  "per_image": "number (USD)",
  "count": "number",
  "provider": "string",
  "provider_name": "string",
  "breakdown": {
    "type": "local | api",
    "base_cost": "number",
    "resolution": "string",
    "resolution_multiplier": "number",
    "model": "string",
    "model_multiplier": "number",
    "steps": "number",
    "steps_cost": "number"
  }
}
```

### 4.3 Pod State File

**Location**: `{PROJECT_ROOT}/.pod_id`

**Content**: Single line containing RunPod pod ID string.

### 4.4 Configuration Schema (`config/config.yaml`)

```yaml
paths:
  local_raw: "string"
  local_processed: "string"
  local_poses: "string"
  local_sync: "string"
  pod_workspace: "string"
  pod_output: "string"

r2:
  bucket: "string"
  remote_name: "string"
  use_r2: "boolean"

pose_settings:
  image_size: [width, height]
  skeleton_format: "string (mediapipe_33)"
  save_debug_images: "boolean"
  save_json: "boolean"
  save_numpy: "boolean"

blender:
  version: "string"
  headless: "boolean"
  output_frames: "string"
```

---

## 5. Entry Points

### 5.1 Production Entry Points

| Entry Point | Command | Purpose |
|-------------|---------|---------|
| **Dashboard** | `cd dashboard && python app.py` | Web UI at :5001 |
| **CLI** | `./shared/scripts/mission_control.py render --wait` | Full job workflow |
| **Pod Agent** | `./pod_agent.sh` | Pod-side executor |
| **Pod Setup** | `./setup_pod.sh` | Pod initialization |

### 5.2 CLI Commands

```bash
# Mission Control
mission_control.py render [--characters "A,B"] [--output DIR] [--wait]
mission_control.py setup-pod
mission_control.py status [--job JOB_ID]
mission_control.py download --job JOB_ID [--force]
```

### 5.3 Blender Scripts (Run on Pod)

```bash
# Multi-angle render
blender --background --python render_simple_working.py -- --batch

# Single character
blender --background --python render_simple_working.py
```

---

## 6. Workflow Contracts

### 6.1 Workflow 1: Pose Rendering (Production)

**Preconditions**:
- RunPod pod running with `setup_pod.sh` executed
- rclone configured with R2 credentials
- Mixamo FBX files in `/workspace/downloads/` or R2 `downloads/`

**Steps**:
1. Local: Create job manifest
2. Local: Upload scripts + manifest to R2
3. Pod: Agent polls R2, finds job
4. Pod: Download scripts and FBX files
5. Pod: Execute `blender --background --python render_simple_working.py -- --batch`
6. Pod: Upload results to R2 `results/{job_id}/`
7. Local: Poll R2 for results
8. Local: Download results to `data/working/`

**Postconditions**:
- 8 PNG images per character in output directory
- Job manifest updated with "completed" status

**Performance Contract**:
- 6 characters × 8 angles = 48 renders
- Time: 2-3 minutes on A40 GPU
- Cost: ~$0.02-0.05 (GPU time only)

### 6.2 Workflow 2: Character Creation (R&D - INCOMPLETE)

**Current State**: Placeholder implementation. `create_character.py` creates a cube, not an actual character.

**Intended Flow** (NOT IMPLEMENTED):
1. Parse text description
2. Generate character mesh (Charmorph or procedural)
3. Export as FBX
4. Apply Mixamo animations
5. Feed into Workflow 1

---

## 7. External Dependencies

### 7.1 Runtime Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| Blender | 4.0+ | Rendering |
| rclone | latest | R2 sync |
| jq | latest | JSON parsing (bash) |

### 7.2 Python Packages

**Dashboard** (`dashboard/requirements.txt`):
- Flask, flask-cors
- runpod
- PyYAML
- pytest
- python-dotenv

**Shared** (`shared/scripts/requirements.txt`):
- boto3
- Pillow
- PyYAML

**Pod** (installed by `setup_pod.sh`):
- opencv-python==4.8.1.78
- mediapipe==0.10.8
- pillow==10.1.0
- numpy==1.26.2
- requests==2.31.0

### 7.3 External Services

| Service | Purpose | Auth |
|---------|---------|------|
| Cloudflare R2 | Storage | rclone config (access_key_id, secret_access_key) |
| RunPod | GPU compute | API key (env: RUNPOD_API_KEY) |
| Stability AI | Image generation | API key (env: STABILITY_API_KEY) |

---

## 8. Configuration Contracts

### 8.1 Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `RUNPOD_API_KEY` | Yes (dashboard) | RunPod API access |
| `STABILITY_API_KEY` | Optional | AI image enhancement |
| `DREAMSTUDIO_API_KEY` | Optional | DreamStudio API |

### 8.2 rclone Configuration

**Required Section** (`~/.config/rclone/rclone.conf`):
```ini
[r2_pose_factory]
type = s3
provider = Cloudflare
access_key_id = {access_key}
secret_access_key = {secret_key}
endpoint = {endpoint_url}
acl = private
no_check_bucket = true
```

### 8.3 Hardcoded Values (TECHNICAL DEBT)

| Location | Value | Notes |
|----------|-------|-------|
| `mission_control.py:29` | `r2_pose_factory:pose-factory` | R2 remote |
| `render_simple_working.py:70` | `3.5` | Camera distance |
| `render_simple_working.py:71` | `1.6` | Camera height |
| `render_simple_working.py:40-42` | `512x512` | Resolution |
| `pod_agent.sh:26` | `30` | Poll interval |
| `bootstrap_pod.py:26-27` | `/Users/eriksjaastad/projects/_tools/ssh_agent/queue` | **HARDCODED USER PATH** |

---

## 9. Technical Debt Registry

### TD-001: Hardcoded User Path in bootstrap_pod.py
- **File**: `shared/scripts/bootstrap_pod.py:26-27`
- **Issue**: Contains hardcoded path `/Users/eriksjaastad/projects/_tools/ssh_agent/queue`
- **Impact**: Script unusable by other developers
- **Severity**: HIGH

### TD-002: Flask Debug Mode in Production
- **File**: `dashboard/app.py:461`
- **Issue**: `app.run(debug=True, ...)` should not be used in production
- **Impact**: Performance, security exposure
- **Severity**: MEDIUM

### TD-003: Unused Camera Utils Module
- **File**: `pose-rendering/scripts/blender_camera_utils.py`
- **Issue**: 363-line sophisticated camera system not used by main renderer
- **Impact**: Dead code, maintenance burden
- **Severity**: LOW

### TD-004: Duplicate rclone/R2 Functions
- **Files**: `mission_control.py`, `dashboard/app.py`
- **Issue**: Both files implement `run_rclone()` and `get_job_status()` identically
- **Impact**: Code duplication, maintenance burden
- **Severity**: MEDIUM

### TD-005: Placeholder Character Creation
- **File**: `character-creation/scripts/create_character.py:41-67`
- **Issue**: `create_character_placeholder()` creates a cube, not a character
- **Impact**: Workflow 2 non-functional
- **Severity**: LOW (documented as R&D)

### TD-006: Missing Error Handling in Pod Agent
- **File**: `shared/scripts/pod_agent.sh`
- **Issue**: Job failures not reported back to R2
- **Impact**: No visibility into failed jobs
- **Severity**: MEDIUM

### TD-007: Hardcoded Pod Workspace Paths
- **Files**: `render_simple_working.py:141-142`
- **Issue**: `/workspace/pose-factory/` hardcoded
- **Impact**: Inflexible deployment
- **Severity**: LOW

### TD-008: No Input Validation in Dashboard API
- **File**: `dashboard/app.py`
- **Issue**: POST endpoints don't validate input schemas
- **Impact**: Potential runtime errors
- **Severity**: MEDIUM

### TD-009: Browser Flag in /tmp
- **File**: `dashboard/app.py:447`
- **Issue**: Uses `/tmp/mission_control_browser_opened` flag file
- **Impact**: Race conditions, stale flags
- **Severity**: LOW

### TD-010: Pinned Dependency Versions on Pod
- **File**: `shared/scripts/setup_pod.sh:42`
- **Issue**: Specific versions may become unavailable
- **Impact**: Setup failures over time
- **Severity**: LOW

---

## 10. Ghost Logic Inventory

Files with unclear purpose, undocumented behavior, or abandoned functionality.

### GL-001: Debug/Test Render Scripts
**Files**:
- `pose-rendering/scripts/debug_import.py`
- `pose-rendering/scripts/debug_render.py`
- `pose-rendering/scripts/test_camera_framing.py`
- `pose-rendering/scripts/test_simple_camera.py`
- `pose-rendering/scripts/test_perfect.py`
- `pose-rendering/scripts/test_close.py`
- `pose-rendering/scripts/test_where.py`
- `pose-rendering/scripts/test_single_animation.py`

**Status**: Likely experimental/development artifacts. Not part of production workflow.

### GL-002: Alternative Render Scripts
**Files**:
- `pose-rendering/scripts/render_mixamo.py`
- `pose-rendering/scripts/render_mixamo_v2.py`
- `pose-rendering/scripts/render_multi_angle.py`
- `pose-rendering/scripts/render_poses.py`

**Status**: Earlier iterations of `render_simple_working.py`. Relationship unclear.

### GL-003: Stability AI Enhancement Scripts
**Files**:
- `character-creation/scripts/stability_control.py`
- `character-creation/scripts/stability_enhance.py`
- `shared/scripts/generate_character_from_cube.py`
- `shared/scripts/generate_from_reference.py`

**Status**: AI image enhancement experiments. Not integrated into main workflows.

### GL-004: Mesh Processing Scripts
**Files**:
- `character-creation/scripts/mesh_cleanup_proximity.py`
- `character-creation/scripts/mesh_cleanup_smooth_and_separate.py`
- `character-creation/scripts/separate_clothing.py`
- `character-creation/scripts/inspect_mesh.py`

**Status**: R&D for mesh preparation. Not documented, not integrated.

### GL-005: Unused Sync/Process Scripts
**Files**:
- `pose-rendering/scripts/pose_sync.py`
- `pose-rendering/scripts/batch_process.py`
- `pose-rendering/scripts/extract_animation_frames.py`

**Status**: Purpose unclear. May be for MediaPipe post-processing.

### GL-006: Root Test Files
**Files**:
- `pose_test.py`
- `shared/test_ai_render.py`
- `shared/test_dimension_debug.py`

**Status**: Test files outside standard test directories.

### GL-007: Character Pipeline Script
**File**: `character-creation/scripts/character_pipeline.py`

**Status**: Exists alongside `create_character.py`. Relationship/difference undocumented.

---

## 11. Module Dependency Map

```
dashboard/app.py
├── shared/cost_calculator.py
├── flask, flask_cors
├── runpod (SDK)
├── subprocess (→ rclone)
└── [Duplicates mission_control.py logic]

shared/scripts/mission_control.py
├── subprocess (→ rclone)
├── argparse, json, uuid
└── pathlib

shared/cost_calculator.py
├── yaml
└── shared/cost_config.yaml

pose-rendering/scripts/render_simple_working.py
├── bpy (Blender Python API)
├── math
└── glob

pose-rendering/scripts/blender_camera_utils.py [UNUSED]
├── bpy
├── mathutils
└── math

shared/scripts/pod_agent.sh
├── rclone
├── jq
└── blender

shared/scripts/setup_pod.sh
├── apt-get
├── pip3
├── rclone
└── blender

shared/scripts/bootstrap_pod.py
├── [HARDCODED PATH: /Users/eriksjaastad/...]
├── json
└── pathlib
```

---

## Appendix A: File Counts by Category

| Category | Files | Lines (est.) |
|----------|-------|--------------|
| Python (.py) | 38 | ~6,500 |
| Bash (.sh) | 7 | ~800 |
| YAML (.yaml) | 2 | ~100 |
| JSON (examples) | 2 | ~30 |
| Markdown (.md) | 20+ | ~3,000 |

---

## Appendix B: API Rate Limits & Costs

| API | Rate Limit | Cost |
|-----|------------|------|
| RunPod | Varies by plan | $0.42/hr (A40) |
| Stability AI | 150 req/10 sec | ~$0.002-0.008/image |
| R2 | 10M requests/month free | $0.015/GB stored |

---

## Appendix C: Audit Methodology

1. **Directory Exploration**: Mapped all files via glob patterns
2. **Core Module Analysis**: Read all Python files > 100 lines
3. **Configuration Audit**: Reviewed all YAML/JSON configs
4. **Entry Point Mapping**: Traced execution paths from CLI/web
5. **Contract Extraction**: Documented function signatures, return types, parameters
6. **Technical Debt Identification**: Flagged hardcoded values, dead code, duplication
7. **Ghost Logic Detection**: Identified files with unclear purpose or missing documentation

---

**END OF SPECIFICATION**

*This document defines the "as-is" contract of the 3D Pose Factory system. Security review will be conducted as a separate phase.*
