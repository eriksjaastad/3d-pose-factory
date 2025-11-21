## 3D Pose Factory – Project TODOs

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
  - [ ] **Document pod configuration** - GPU type (A40), template, container image for reference
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
  - [ ] **Find/integrate pose reference library**
    - [ ] Research: Mixamo (free rigged characters), MakeHuman, or pose datasets
    - [ ] Option 1: Download Mixamo characters and import to Blender
    - [ ] Option 2: Use pose estimation datasets (COCO, MPII) for reference
    - [ ] Option 3: Manual Blender rigging with pose library
    - [ ] Decide on source and document in project
  - [ ] Create realistic human character rig in Blender
  - [ ] Generate diverse pose library (standing, sitting, action poses)
  - [ ] Render multiple camera angles per pose
  - [ ] Add depth maps and normal maps to output
  - [ ] Optional: Enable auto-shutdown in auto_process.sh

- **Git / GitHub integration**
  - [x] Initialize git repo locally for 3D Pose Factory
  - [x] Add a `.gitignore` (exclude `data/`, virtualenvs, and any secrets)
  - [x] Create GitHub repo and push initial commit (https://github.com/eriksjaastad/3d-pose-factory.git)
  - [x] Verify RunPod pod can `git clone` the repo


