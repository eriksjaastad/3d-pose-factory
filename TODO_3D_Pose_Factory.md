## 3D Pose Factory – Project TODOs

- **Cloudflare R2 setup**
  - [ ] Create Cloudflare account (if not already created)
  - [ ] Create R2 bucket for 3D Pose Factory outputs (e.g., `pose-factory`)
  - [ ] Generate R2 Access Key + Secret Key
  - [ ] Decide where to store these locally (env vars / `.env` file, not in git)

- **RunPod pod configuration**
  - [x] SSH access to pod using dedicated `id_ed25519_runpod` key
  - [x] Update + upgrade system packages
  - [x] Install core dependencies (`wget`, `git`, `curl`, `build-essential`, etc.)
  - [x] Install Blender via `apt`
  - [x] Install Python 3 + `pip` + `venv`
  - [x] Install Python pose tools (`numpy`, `pillow`, `opencv-python`, `mediapipe`)
  - [x] Install `rclone`

- **Cloudflare R2 integration**
  - [ ] Configure `rclone` on RunPod to talk to the R2 bucket
  - [ ] Configure `rclone` on local Mac to talk to the same R2 bucket
  - [ ] Decide on standard remote name (e.g., `r2_pose_factory`)
  - [ ] Run test: upload small sample from RunPod → R2
  - [ ] Run test: download sample from R2 → local `data/raw/pose-factory`

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


