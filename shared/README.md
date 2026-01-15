# Shared Infrastructure

**Common scripts and documentation used by both workflows**

---

## What's Here

This directory contains infrastructure shared between:
- **pose-rendering/** workflow
- **character-creation/** workflow

---

## 📂 Structure

```
shared/
├── scripts/
│   ├── setup_pod.sh                  ← RunPod initialization (Blender, rclone, etc.)
│   ├── setup_runpod_pod.sh           ← Alternative setup script
│   ├── bootstrap_runpod_from_local.sh ← Bootstrap from local machine
│   └── requirements.txt              ← Python dependencies
│
└── docs/
    ├── RUNPOD_CONFIG.md              ← RunPod & R2 setup guide
    ├── START_RUNPOD.md               ← Quick start guide
    ├── RunPod_3D_Pose_Factory_Setup.md ← Detailed setup
    └── Local_Integration_Design.md   ← Local/cloud integration notes
```

---

## 🚀 Quick Reference

### Setting Up a New RunPod Instance:

```bash
# 1. Start RunPod instance (via web UI)
# 2. Note your POD_ID and SSH port

# 3. SSH in
ssh -i ~/.ssh/id_ed25519 root@YOUR_POD_ID-ssh.runpod.io -p PORT

# 4. Run setup script
cd /workspace
git clone YOUR_REPO_URL
cd "3d-pose-factory/shared/scripts"
./setup_pod.sh
```

**Result:** Blender, rclone, Python, MediaPipe all installed and ready.

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[RUNPOD_CONFIG.md](docs/RUNPOD_CONFIG.md)** | How to configure R2 and RunPod |
| **[START_RUNPOD.md](docs/START_RUNPOD.md)** | Quick start checklist |
| **[RunPod_3D_Pose_Factory_Setup.md](docs/RunPod_3D_Pose_Factory_Setup.md)** | Detailed setup walkthrough |
| **[Local_Integration_Design.md](docs/Local_Integration_Design.md)** | Architecture notes |

---

## 🔧 Setup Scripts

### `setup_pod.sh`
**Purpose:** One-command RunPod initialization  
**Installs:** Blender 4.0+, rclone, Python 3, MediaPipe, Git

**Usage:**
```bash
./setup_pod.sh
```

### `bootstrap_runpod_from_local.sh`
**Purpose:** Push local scripts to new RunPod instance  
**Usage:**
```bash
./bootstrap_runpod_from_local.sh YOUR_POD_ID
```

### `requirements.txt`
**Purpose:** Python dependencies for both workflows  
**Contents:** MediaPipe, NumPy, OpenCV, etc.

---

## 🔗 Integration

Both workflows use these shared resources:

**Pose Rendering:**
- Uses `setup_pod.sh` to configure RunPod
- Reads `RUNPOD_CONFIG.md` for R2 credentials
- Shares Python `requirements.txt`

**Character Creation:**
- Same RunPod setup process
- Same R2 storage backend
- Same infrastructure, different scripts

---

## 💡 Why Shared?

- **DRY Principle** - Don't duplicate RunPod setup code
- **Consistency** - Both workflows use identical infrastructure
- **Maintainability** - Update setup in one place
- **Efficiency** - One RunPod instance can run both workflows

---

**Last Updated:** 2025-11-22

