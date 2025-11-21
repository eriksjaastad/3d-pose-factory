# 3D Pose Factory - Quick Start Guide

## How to Start and Run a Processing Session

Follow these steps each time you want to process images with the 3D Pose Factory.

---

## Step 1: Start a Fresh RunPod Pod

1. Go to https://runpod.io and log in
2. Click **"Deploy"** or **"+ Deploy"**
3. Select a GPU (A40, RTX 3080, or similar)
4. Choose **"RunPod Pytorch"** or **"RunPod Ubuntu"** template
5. Click **"Deploy On-Demand"**
6. Wait for the pod to start (~30 seconds)
7. Copy the SSH connection command (looks like: `ssh root@[pod-id]@ssh.runpod.io`)

---

## Step 2: Connect to Pod via SSH

From your Mac terminal, connect using your RunPod SSH key:

```bash
ssh [pod-id]@ssh.runpod.io -i ~/.ssh/id_ed25519_runpod
```

**Example:**
```bash
ssh 6gpur3lb2h5pzi-6441128f@ssh.runpod.io -i ~/.ssh/id_ed25519_runpod
```

Replace `[pod-id]` with the actual pod ID from RunPod dashboard.

---

## Step 3: Run Setup Script (First Time Only)

This installs everything needed (~2-3 minutes):

```bash
wget https://raw.githubusercontent.com/eriksjaastad/3d-pose-factory/main/scripts/setup_pod.sh && bash setup_pod.sh
```

**What this installs:**
- Blender 4.0.2 + graphics libraries
- Python packages (OpenCV, MediaPipe)
- Clones GitHub repo
- Configures rclone for R2
- Downloads automation scripts

---

## Step 4: Upload Images to R2 (From Your Mac)

Before processing, upload images from your Mac to R2:

```bash
rclone copy "/path/to/your/images/" r2_pose_factory:pose-factory/input/ -v
```

**Example:**
```bash
rclone copy "/Users/eriksjaastad/Desktop/my-poses/" r2_pose_factory:pose-factory/input/ -v
```

---

## Step 5: Run Automated Processing (On Pod)

```bash
cd /workspace/pose-factory
./auto_process.sh
```

**This will:**
1. Download images from R2 input folder
2. Run pose detection on all images
3. Draw skeleton overlays
4. Upload results to R2 (timestamped folder)
5. Clean up temporary files

---

## Step 6: Download Results (From Your Mac)

Check what's available:
```bash
rclone ls r2_pose_factory:pose-factory/output/
```

Download a specific processed batch:
```bash
rclone copy r2_pose_factory:pose-factory/output/processed-[timestamp]/ "/Users/eriksjaastad/projects/3D Pose Factory/data/raw/" -v
```

---

## Step 7: Terminate Pod

When processing is complete:
1. Go to RunPod dashboard
2. Click **"Stop"** or **"Terminate"** on your pod
3. Confirm termination

**Important:** Terminate pods when not in use to avoid charges!

---

## Quick Reference Commands

### Check if GPU is working:
```bash
nvidia-smi
```

### Test single image:
```bash
python3 pose_test.py input/test_image.jpg
```

### List files in R2:
```bash
rclone ls r2_pose_factory:pose-factory/input/
rclone ls r2_pose_factory:pose-factory/output/
```

### Pull latest code from GitHub:
```bash
cd /workspace/pose-factory && git pull
```

---

## Troubleshooting

**"Permission denied (publickey)"**
- Make sure you're using: `-i ~/.ssh/id_ed25519_runpod` (with `_runpod` at the end)

**"nvidia-smi: command not found"**
- Pod started without GPU (zero GPU issue)
- Terminate and start a new pod

**"No images to process"**
- Check R2 input folder: `rclone ls r2_pose_factory:pose-factory/input/`
- Upload images from Mac first (Step 4)

**Setup script fails**
- SSH into pod and run commands manually from setup_pod.sh
- Or wait and try a different pod

---

## Cost Tracking

- **A40 GPU:** ~$0.40/hour
- **Typical session:** 30-60 minutes = $0.20-0.40
- **R2 storage:** ~$0.01/month for hundreds of images
- **No charges when pod is stopped**

---

## What's Persistent vs What's Not

**✅ Persists (always available):**
- Your GitHub repo
- Your R2 cloud storage
- Your local Mac files
- SSH keys

**❌ Lost when pod terminates:**
- Installed packages (Blender, Python libs)
- Files outside `/workspace/`
- Pod configuration

**That's why we run setup_pod.sh each time!**

