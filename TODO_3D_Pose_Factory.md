## 3D Pose Factory – Project TODOs

- **Cloudflare R2 setup** (R2 is Cloudflare's S3-compatible storage service)
  - [ ] Go to https://dash.cloudflare.com and sign up/login
  - [ ] Navigate to R2 Object Storage in the left sidebar
  - [ ] Click "Create bucket" → name it `pose-factory`
  - [ ] Go to "Manage R2 API Tokens" → "Create API token"
  - [ ] Select "Edit" permissions, apply to `pose-factory` bucket
  - [ ] Save the Access Key ID and Secret Access Key (shown once!)
  - [ ] Note your Account ID (shown in R2 dashboard)
  - [ ] Store credentials in `~/.config/rclone/rclone.conf` (not in git!)

- **RunPod pod configuration**
  - [x] SSH access to pod using dedicated `id_ed25519_runpod` key
  - [x] Update + upgrade system packages
  - [x] Install core dependencies (`wget`, `git`, `curl`, `build-essential`, etc.)
  - [x] Install Blender via `apt`
  - [x] Install Python 3 + `pip` + `venv`
  - [x] Install Python pose tools (`numpy`, `pillow`, `opencv-python`, `mediapipe`)
  - [x] Install `rclone`

- **Cloudflare R2 integration** (rclone is the tool that connects to R2)
  - [ ] **On local Mac:** Install rclone: `brew install rclone`
  - [ ] **On local Mac:** Run `rclone config` and configure R2:
    - Choose "n" for new remote, name it `r2_pose_factory`
    - Choose "s3" (R2 is S3-compatible)
    - Choose "Cloudflare R2" provider
    - Enter Access Key ID and Secret Access Key from above
    - Endpoint: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`
    - Leave region blank, set ACL to "private"
  - [ ] **On local Mac:** Test upload: `rclone copy config/config.yaml r2_pose_factory:pose-factory/test/`
  - [ ] **On local Mac:** Test download: `rclone ls r2_pose_factory:pose-factory/test/`
  - [ ] **On RunPod:** Run same `rclone config` setup (rclone already installed)
  - [ ] **On RunPod:** Test download from R2 to verify connection works
  - [ ] Create directory structure in R2 bucket: `input/`, `output/`, `test/`

- **Local laptop integration**
  - [x] Create `scripts/` and `data/` folders locally as per `Local_Integration_Design.md`
  - [x] Create `config/` folder locally and add example config file
  - [x] Set up a Python virtualenv under `scripts/`
  - [x] Add a `pose_sync.py` stub script for R2 ↔ local sync
  - [x] Create `requirements.txt` for local Python dependencies

- **Pose generation + validation**
  - [x] Install and test MediaPipe pose extraction in pod
  - [x] Add a small reusable pose test script in the pod workspace (`pose_test.py` uploaded)
  - [x] Decide where 3D→2D outputs will be written on the pod (e.g., `/workspace/pose-factory/output/`)
  - [ ] Test pose detection on sample image to verify full pipeline works
  - [ ] Set up reliable file transfer method (direct SSH pipe doesn't work with RunPod)

- **Git / GitHub integration**
  - [x] Initialize git repo locally for 3D Pose Factory
  - [x] Add a `.gitignore` (exclude `data/`, virtualenvs, and any secrets)
  - [x] Create GitHub repo and push initial commit (https://github.com/eriksjaastad/3d-pose-factory.git)
  - [x] Verify RunPod pod can `git clone` the repo


