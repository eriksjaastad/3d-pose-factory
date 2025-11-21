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
  - [ ] **Save pod configuration** - Document exact GPU type, template, settings for easy redeployment
  - [ ] **Set up network volumes** - Use persistent network storage instead of local pod storage
    - [ ] Create network volume in RunPod dashboard
    - [ ] Attach network volume to pod at `/workspace`
    - [ ] This prevents "zero GPU" issues when stopping/restarting pods

- **Cloudflare R2 integration** (rclone is the tool that connects to R2)
  - [x] **On local Mac:** rclone already installed via Homebrew
  - [x] **On local Mac:** Configured rclone as `r2_pose_factory` remote with R2 credentials
  - [x] **On local Mac:** Test upload successful: `config.yaml` → R2
  - [x] **On local Mac:** Test download successful: verified file in R2
  - [x] **On RunPod:** Configured rclone with same credentials (rclone already installed)
  - [x] **On RunPod:** Test upload successful: `pose_test.py` → R2
  - [x] **On RunPod:** Test download successful: read files from R2
  - [x] Full bidirectional sync working: Mac ↔ R2 ↔ RunPod
  - [ ] Create directory structure in R2 bucket: `input/`, `output/` (test/ already exists)

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

- **Production Workflow Setup** 🎯 *NEXT PRIORITY*
  - [ ] Create Blender script for batch rendering human poses
    - [ ] Find/create human character rig (mixamo, makehuman, or manual)
    - [ ] Script to render multiple poses from different angles
    - [ ] Generate 10-20 test renders as a batch
  - [ ] Create batch processing script on pod
    - [ ] Script to: sync from R2 → run pose detection on all images → sync results back to R2
    - [ ] Add progress logging and error handling
  - [ ] Test 1-hour production run
    - [ ] Generate batch of renders (5-10 mins)
    - [ ] Upload to R2 (< 1 min)
    - [ ] Process on pod (pose detection - 40 mins)
    - [ ] Download results (< 1 min)
    - [ ] Review output quality
  - [ ] Document the production workflow for repeatable runs

- **Git / GitHub integration**
  - [x] Initialize git repo locally for 3D Pose Factory
  - [x] Add a `.gitignore` (exclude `data/`, virtualenvs, and any secrets)
  - [x] Create GitHub repo and push initial commit (https://github.com/eriksjaastad/3d-pose-factory.git)
  - [x] Verify RunPod pod can `git clone` the repo


