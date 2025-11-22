## 3D Pose Factory – Project TODOs

- **🚀 PRIORITY: Streamline Upload/Render/Download Workflow** ⏰ **URGENT**
  - **Problem:** Manual copy-paste of commands between Mac/Pod/R2 is exhausting and error-prone
  - **Goal:** One-command workflow for the entire render pipeline
  - **Solutions to explore:**
    - [ ] Create shell script on Mac that does: upload scripts → SSH to pod → trigger render → download results
    - [ ] Use `ssh` command with inline script execution: `ssh pod "cd /workspace && blender ..."`
    - [ ] Create a "render pipeline" Python script that orchestrates everything via SSH + rclone
    - [ ] Set up rsync or direct SSH file transfer instead of R2 for scripts (faster)
    - [ ] Create aliases in ~/.zshrc for common commands:
      ```bash
      alias pod_upload="rclone copy scripts/ r2_pose_factory:pose-factory/scripts/"
      alias pod_render="ssh pod 'cd /workspace/pose-factory && blender --background --python render_simple_working.py -- --batch'"
      alias pod_download="rclone copy r2_pose_factory:pose-factory/output/simple_multi_angle/ data/working/latest/"
      alias pod_pipeline="pod_upload && pod_render && pod_download"
      ```
    - [ ] Investigate RunPod's API for programmatic job submission
  - **Impact:** Reduce 10+ manual commands down to 1-2 commands
  - **Context:** After 5 hours of debugging camera issues, manual workflow became a major pain point

- **Cloudflare R2 setup** (R2 is Cloudflare's S3-compatible storage service)
  - [x] Go to https://dash.cloudflare.com and sign up/login
  - [x] Navigate to R2 Object Storage in the left sidebar
  - [x] Click "Create bucket" → name it `pose-factory`
  - [x] Go to "Manage R2 API Tokens" → "Create API token"
  - [x] Select "Object Read & Write" permissions
  - [x] Save the Access Key ID and Secret Access Key (shown once!)
  - [x] Note your Account ID (shown in R2 dashboard)
  - [x] Store credentials securely in `.r2_credentials` (in .gitignore)

- **RunPod pod configuration**
  - [x] SSH access to pod using dedicated `id_ed25519_runpod` key
  - [x] New pod deployed with working A40 GPU (Pod ID: 6gpur3lb2h5pzi-6441128f)
  - [x] Install Blender via `apt` + graphics libraries (libegl1, libgl1, libgomp1)
  - [x] Install Python 3 + pip
  - [x] Install Python pose tools (`numpy`, `pillow`, `opencv-python`, `mediapipe`)
  - [x] Install `rclone` and configure with R2 credentials
  - [x] Clone GitHub repo to `/workspace/pose-factory/`
  - [x] Test Blender rendering (cube render successful)
  - [x] Test pose detection (yoga_warrior.jpg - successful)
  - [x] Full workflow tested: Mac → R2 → Pod → Process → R2 → Mac
  - [x] **Create pod setup script** - setup_pod.sh for fast fresh pod initialization (2-3 mins)
  - [x] **Document pod configuration** - Created RUNPOD_CONFIG.md with template, GPU, settings
  - [x] **Decision: Skip network volumes** - Not worth the cost, fresh pods + setup script is easier

- **Cloudflare R2 integration** (rclone is the tool that connects to R2)
  - [x] **On local Mac:** rclone already installed via Homebrew
  - [x] **On local Mac:** Configured rclone as `r2_pose_factory` remote with R2 credentials
  - [x] **On local Mac:** Test upload successful: `config.yaml` → R2
  - [x] **On local Mac:** Test download successful: verified file in R2
  - [x] **On RunPod:** Configured rclone with same credentials (rclone already installed)
  - [x] **On RunPod:** Test upload successful: `pose_test.py` → R2
  - [x] **On RunPod:** Test download successful: read files from R2
  - [x] Full bidirectional sync working: Mac ↔ R2 ↔ RunPod
  - [x] Directory structure in R2 bucket: `input/`, `output/`, `test/`, `scripts/` (auto-created)

- **Local laptop integration**
  - [x] Create `scripts/` and `data/` folders locally as per `Local_Integration_Design.md`
  - [x] Create `config/` folder locally and add example config file
  - [x] Set up a Python virtualenv under `scripts/`
  - [x] Add a `pose_sync.py` stub script for R2 ↔ local sync
  - [x] Create `requirements.txt` for local Python dependencies

- **Pose generation + validation**
  - [x] Install and test MediaPipe pose extraction in pod
  - [x] Add a small reusable pose test script in the pod workspace (`pose_test.py`)
  - [x] Decide where 3D→2D outputs will be written on the pod (`/workspace/pose-factory/output/`)
  - [x] Test pose detection on sample image (yoga_warrior.jpg - pose detected successfully)
  - [x] Test full file transfer pipeline (Mac → R2 → Pod working)
  - [x] Test Blender 3D rendering (test_render.png - cube rendered successfully)

- **Production Workflow Setup** 🎯 ✅ **COMPLETE!**
  - [x] Create Blender script for batch rendering poses
    - [x] Created render_poses.py - renders 5 stick figure poses with varying arm positions
    - [x] Renders in ~1 second using Blender 4.0.2
  - [x] Create batch processing script on pod
    - [x] batch_process.py - processes all images in input directory
    - [x] Draws MediaPipe skeleton overlays on detected poses
    - [x] Progress logging and error handling included
  - [x] Create automated workflow script
    - [x] auto_process.sh - complete hands-off automation
    - [x] Downloads from R2 → Processes → Uploads results → Cleanup
    - [x] Timestamps output folders for organization
  - [x] Test full production run
    - [x] Successfully tested with yoga_warrior.jpg
    - [x] Pose detected and skeleton overlay drawn
    - [x] Results uploaded to R2 and downloaded to Mac
    - [x] ENTIRE PIPELINE WORKING END-TO-END!
  
- **Next Steps (Future)**
  - [x] **Find/integrate pose reference library**
    - [x] Research: Mixamo (free rigged characters), MakeHuman, or pose datasets
    - [x] Option 1: Download Mixamo characters and import to Blender ✅ CHOSEN
    - [x] Successfully downloaded 6 Mixamo animations (X Bot, Dancing, Walking, etc.)
  - [x] **Solve Mixamo import + camera framing issues** 🎯 ✅ **COMPLETE!**
    - [x] Identified Mixamo scale problem (armature 0.01, mesh 1.0)
    - [x] Built production-grade camera framing system (`blender_camera_utils.py`)
    - [x] Implemented mathematical bounding box calculations (works in headless mode)
    - [x] Created scale normalization system for Mixamo characters
    - [x] Added Track To constraints for camera stability
    - [x] Built test suite (`test_camera_framing.py`)
    - [x] Created multi-angle rendering system (`render_multi_angle.py`)
    - [x] Documented complete pipeline in `BLENDER_CAMERA_GUIDE.md`
  - [x] **Production rendering workflow** 🎯 ✅ **WORKING!** (Nov 22, 2024)
    - [x] Test camera system on RunPod with downloaded Mixamo characters
    - [x] Discovered camera positioning issue (complex math was calculating wrong distance)
    - [x] Created simple working renderer with fixed camera settings (distance 3.5m, height 1.3-1.6m)
    - [x] Successfully rendered all 6 characters with 8 camera angles each (48 images)
    - [x] Created automated pipeline script (`render_pipeline.sh`) - ONE command for entire workflow!
    - [ ] Fine-tune camera height (currently testing 1.6m vs 1.3m)
    - [ ] Run MediaPipe pose detection on rendered images
    - [ ] Verify pose keypoints are correctly detected
    - [ ] Integrate MediaPipe into automated workflow
  
  - [ ] **⚡ PERFORMANCE: Cache Bounding Box Calculations (5-6x speedup)**
    - **Current Issue:** Bounding box calculated 8 times per character (once per camera angle)
      - Each calculation samples ALL animation frames (50-250 frames)
      - For 8 angles × 250 frames = 2,000 frame samples per character
      - Takes ~2-3 minutes per character
    - **Optimization Goal:** Calculate bounding box ONCE, reuse for all 8 cameras
      - 1× calculation + 8× camera positioning = ~30 seconds per character
      - **5-6x faster!**
    - **Implementation Approach:**
      - Modify `render_multi_angle.py` to call `get_character_bounding_box()` BEFORE the camera loop
      - Store result in variables: `bbox_min, bbox_max = cam_utils.get_character_bounding_box(armature)`
      - Pass these to `calculate_camera_position()` for each angle instead of recalculating
      - **Code change location:** `render_character_multi_angle()` function around line 60-90
    - **Pseudocode:**
      ```python
      # BEFORE (current - slow):
      for angle in angles:
          camera = setup_camera_for_character(armature, angle)  # recalcs bbox
          render()
      
      # AFTER (optimized - fast):
      bbox_min, bbox_max = get_character_bounding_box(armature)  # calc once!
      for angle in angles:
          cam_pos, target = calculate_camera_position(bbox_min, bbox_max, angle)
          camera = create_camera_at_position(cam_pos, target)  # reuse bbox
          render()
      ```
    - **Files to modify:**
      - `scripts/render_multi_angle.py` - main optimization
      - Possibly refactor `blender_camera_utils.py` to expose bbox-reuse workflow
    - **Testing:**
      - Time before optimization (current render)
      - Time after optimization (should be 5-6x faster)
      - Verify images look identical
    - **Priority:** MEDIUM - wait until first renders are verified, then optimize
  
  - [ ] **Custom Character Creation** 🎨
    - [ ] Install DAZ Studio (free) - https://www.daz3d.com/get_studio
    - [ ] Learn DAZ basics (similar to Poser workflow)
    - [ ] Create first custom character (body type, features, clothing)
    - [ ] Export character to FBX format
    - [ ] Test importing custom character into Blender with camera system
    - [ ] Create diverse character library (different ages, body types, etc.)
    - [ ] Future: Consider Character Creator 4 (~$200-500) for professional work
    - [ ] Alternative: Try MakeHuman (free) for quick human character generation
  
  - [ ] **Expand dataset**
    - [ ] Download more Mixamo animations (target: 50+ diverse poses)
    - [ ] Create custom characters with DAZ Studio (diverse body types)
    - [ ] Render full animation sequences (not just single frames)
    - [ ] Add depth maps and normal maps to output
  - [ ] Optional: Enable auto-shutdown in auto_process.sh

- **Git / GitHub integration**
  - [x] Initialize git repo locally for 3D Pose Factory
  - [x] Add a `.gitignore` (exclude `data/`, virtualenvs, and any secrets)
  - [x] Create GitHub repo and push initial commit (https://github.com/eriksjaastad/3d-pose-factory.git)
  - [x] Verify RunPod pod can `git clone` the repo


