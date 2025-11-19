## 3D Pose Factory – Local Integration Plan

This document describes how your **local macOS laptop** will integrate with the cloud-based 3D Pose Factory (RunPod + Blender + pose extraction + Cloudflare R2).

It assumes:
- RunPod GPU instances generate outputs into a directory like `output/` on the pod.
- Those outputs are synced to Cloudflare R2 in a bucket such as `pose-factory`.
- Your local machine is where ComfyUI/SDXL lives and where you review and use pose data.

---

## 1. High-Level Local Role

Locally, you need to be able to:
- **Pull pose datasets** from Cloudflare R2 down to your laptop.
- **Organize them** into predictable folders ComfyUI can use.
- **Optionally push configs/metadata** (e.g., request definitions or job manifests) up to the cloud later.

All cloud-heavy work (Blender, pose extraction, rendering) stays on the RunPod GPU.  
All review, curation, and generation with SDXL/ComfyUI stays local.

---

## 2. Local Directory Layout

Under the project root (`/Users/eriksjaastad/projects/3D Pose Factory`), we will use:

- `scripts/`  
  - All Python/CLI utilities live here.  
  - Local virtual environment will also live inside this folder (e.g., `scripts/.venv/`), in line with your usual preference.

- `data/`  
  - Local copies of pose outputs pulled from R2.  
  - Proposed structure:
    - `data/raw/` – Direct mirror of what comes from R2 (read-only, no edits here).  
    - `data/working/` – Any derived/cleaned subsets for specific projects.  
    - `data/archive/` – Old batches you don’t want to delete but don’t actively use.

- `config/`  
  - Configuration files for:
    - Cloudflare R2 bucket names and paths.  
    - RunPod hostnames/IPs or pod IDs (once you have them).  
    - Any mapping from pose datasets → ComfyUI workflows.

---

## 3. Credentials & Configuration

Once you have accounts created, we will store secrets in **environment variables** rather than in code:

- `CLOUDFLARE_R2_ACCESS_KEY_ID`
- `CLOUDFLARE_R2_SECRET_ACCESS_KEY`
- `CLOUDFLARE_R2_ACCOUNT_ID`
- `POSE_FACTORY_R2_BUCKET` (e.g., `pose-factory`)

On macOS you can manage these via:
- `~/.zshrc` exports, or  
- a small `.env` file (ignored by git) loaded by the Python scripts.

The `config/` folder will hold **non-secret** settings like:
- Default R2 remote name if you use `rclone` (e.g., `r2_pose_factory`).  
- Default local data root (e.g., `data/raw/`).  
- Naming conventions for batches (e.g., date + project slug).

---

## 4. Local Sync Flows

### 4.1 Using `rclone` (Recommended for bulk sync)

On your laptop, we’ll:
- Install `rclone`.  
- Configure an S3-compatible remote pointing at Cloudflare R2 (same as on RunPod).

Typical operations:
- **Pull new outputs from R2 to local:**
  - `rclone sync r2_pose_factory:pose-factory data/raw/pose-factory`
- **Optionally sync specific subfolders:**
  - `rclone sync r2_pose_factory:pose-factory/<batch-id> data/raw/pose-factory/<batch-id>`

Later we can wrap these commands in a Python CLI so you can run simple commands like:
- `python scripts/pose_sync.py pull-latest`

### 4.2 Python-Based Access (Optional)

For more fine-grained control or listing/filtering:
- Use `boto3` (S3 API) in a local Python script inside `scripts/`.  
- Example capabilities:
  - List all batches in the R2 bucket.  
  - Pull only specific jobs (e.g., matching a project name or date range).  
  - Generate manifests for ComfyUI to consume.

---

## 5. Integration with ComfyUI / SDXL

Locally, we will:
- Define a **standard output folder** that ComfyUI nodes look at for:
  - Skeleton maps.  
  - Depth/normal maps.  
  - Segmentation masks.

Example:
- `data/working/current_batch/` is the folder you point ComfyUI at.  
- A local script can:
  - Pull a batch from `data/raw/pose-factory/<batch-id>`  
  - Copy/link it into `data/working/current_batch/`  
  - Optionally generate any manifest/index files that ComfyUI nodes need.

This keeps your **raw sync mirror** separate from the **active batch** you’re working on.

---

## 6. Future: RunPod Control from Local

Once you’re comfortable and have API keys, we can optionally:
- Add a small local tool that:
  - Starts a RunPod GPU instance.  
  - Submits a job definition (which Blender scene & camera angles to use, which rig, etc.).  
  - Monitors job completion and confirms that outputs have landed in R2.  
  - Shuts down the pod when done.

This can be done either:
- By calling the **RunPod HTTP API** from local Python, or  
- By using a lightweight scheduler/runner that lives inside the pod and is triggered via SSH.

For now, we’ll keep this as a **phase 2** feature once basic sync is working.

---

## 7. What We Can Do Before Accounts Exist

Even without accounts, we can safely:
- Set up the **local folder structure** (`scripts/`, `data/`, `config/`).  
- Create a **Python virtual environment** under `scripts/` with a minimal `requirements.txt`.  
- Stub out:
  - A `pose_sync.py` script with placeholder commands for `pull` / `list` / `prepare-batch`.  
  - A sample `config/local.example.yaml` showing how R2 + RunPod details will be stored.

When you’re ready, we’ll:
- Plug in real R2 credentials.  
- Configure `rclone` locally.  
- Connect the sync scripts to your live bucket and test the full “cloud → R2 → local → ComfyUI” loop.


