# Mission Control Quick Start

**You're 5 minutes away from never copy-pasting terminal commands again.** 🎉

---

## What Just Got Built

**Mission Control** = Single command from your Mac that orchestrates everything:
- Uploads scripts to R2
- Pod automatically picks up jobs
- Executes on GPU
- Downloads results back to you

**No SSH. No terminal switching. No copy-paste hell.**

---

## How It Works (30 Second Overview)

```
Your Mac                    Cloudflare R2               RunPod Pod
  │                              │                          │
  │  Submit job                  │                          │
  ├─────────────────────────────►│                          │
  │                              │                          │
  │                              │  Pod Agent (polling)     │
  │                              │◄─────────────────────────┤
  │                              │  "Any jobs?"             │
  │                              │                          │
  │                              │  Download job            │
  │                              ├─────────────────────────►│
  │                              │                          │
  │                              │                       [Execute]
  │                              │                          │
  │                              │  Upload results          │
  │                              │◄─────────────────────────┤
  │                              │                          │
  │  Download results            │                          │
  │◄─────────────────────────────┤                          │
  │                              │                          │
  ✅ Done!
```

**Key:** Pod constantly polls R2 (every 30s) looking for jobs. When found, it executes and uploads results.

---

## First Time Setup (Do Once)

### Step 1: Upload Setup Scripts

From your Mac:

```bash
cd /path/to/3D\ Pose\ Factory
./shared/scripts/mission_control.py setup-pod
```

**Output:**
```
📤 Uploading shared/scripts → R2/shared/scripts
✅ Upload complete

📌 Next steps:
   1. SSH to your pod: ssh YOUR_POD_ID@ssh.runpod.io -i ~/.ssh/id_ed25519
   2. Run: rclone copy r2_pose_factory:pose-factory/shared/scripts/ /workspace/scripts/ && cd /workspace && ./scripts/setup_pod.sh
```

### Step 2: Run Setup on Pod

SSH to your pod:

```bash
ssh YOUR_POD_ID@ssh.runpod.io -i ~/.ssh/id_ed25519
```

On the pod, run:

```bash
rclone copy r2_pose_factory:pose-factory/shared/scripts/ /workspace/scripts/
cd /workspace
./scripts/setup_pod.sh
```

**What this does:**
- Installs Blender, Python, jq
- Configures rclone
- Starts Pod Agent in background (polls R2 for jobs)

**Output:**
```
[1/7] Updating system packages...
[2/7] Installing Blender + graphics libraries + jq...
[3/7] Installing Python packages...
[4/7] Creating workspace directories...
[5/7] Configuring rclone...
   ✅ rclone configured successfully
[6/7] Downloading Pod Agent...
[7/7] Starting Pod Agent...
   ✅ Pod Agent started (PID: 12345)
   📋 Logs: /workspace/pod_agent.log

================================
✅ Setup Complete!
================================
```

### Step 3: Verify Agent is Running

On the pod:

```bash
tail -f /workspace/pod_agent.log
```

**Should see:**
```
[2023-11-24 15:30:45] 🤖 Pod Agent starting...
[2023-11-24 15:30:45] Polling R2 for jobs every 30s
[2023-11-24 15:30:45] ✅ rclone configured
```

Press `Ctrl+C` to exit the log view. **Leave the pod terminal open or exit - agent keeps running.**

---

## Daily Usage (From Your Mac)

### Render All Characters

```bash
./shared/scripts/mission_control.py render --wait
```

**What happens:**
1. Uploads scripts to R2
2. Creates job manifest
3. Pod picks up job (within 30s)
4. Executes render on GPU
5. Uploads results to R2
6. Mission Control downloads to your Mac

**You see:**
```
📦 Preparing render job...
📤 Uploading pose-rendering/scripts → R2/pose-rendering/scripts
✅ Upload complete
📋 Created job: render_20231124_153045_a1b2c3d4
⏳ Waiting for job render_20231124_153045_a1b2c3d4 to complete...
   (Pod agent polls every 30 seconds)
   ... still waiting (30s elapsed)
🔄 Job is now processing on pod...
   ... still waiting (120s elapsed)
✅ Job completed!
📥 Downloading R2/results/render_20231124_153045_a1b2c3d4/ → data/working/simple_multi_angle
✅ Download complete: data/working/simple_multi_angle
```

**Results:** `data/working/simple_multi_angle/`

### Render Specific Characters

```bash
./shared/scripts/mission_control.py render --characters "X Bot,Salsa Dancing" --wait
```

### Submit Job and Check Later

```bash
# Submit without waiting
./shared/scripts/mission_control.py render

# Later, check status
./shared/scripts/mission_control.py status

# Download when ready
./shared/scripts/mission_control.py download --job render_20231124_153045_a1b2c3d4
```

---

## Commands Cheat Sheet

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `./shared/scripts/mission_control.py setup-pod` | Upload setup scripts to R2 | First time, or after updating pod scripts |
| `./shared/scripts/mission_control.py render --wait` | Render all chars, wait, download | Daily usage, full automation |
| `./shared/scripts/mission_control.py render --characters "X Bot"` | Render specific chars | Testing single character |
| `./shared/scripts/mission_control.py status` | List all jobs | Check what's running/completed |
| `./shared/scripts/mission_control.py status --job JOB_ID` | Check specific job | Monitor long-running job |
| `./shared/scripts/mission_control.py download --job JOB_ID` | Download results | Get results without waiting |

---

## Troubleshooting

### "Job stuck in pending"

**Possible causes:**
1. Pod agent not running
2. Pod is turned off
3. rclone not configured

**Fix:**

SSH to pod and check:
```bash
# Check agent logs
tail -f /workspace/pod_agent.log

# If not running, restart
cd /workspace
./scripts/setup_pod.sh
```

### "rclone not configured"

On the pod:
```bash
cd /workspace
./scripts/setup_pod.sh
```

This will reconfigure rclone and restart the agent.

### "Can't find mission_control.py"

You're in the wrong directory.

**Fix:**
```bash
# Always run from project root
cd /path/to/3D\ Pose\ Factory
./shared/scripts/mission_control.py render --wait
```

**Or:** Make it globally available:
```bash
chmod +x shared/scripts/mission_control.py
ln -s $(pwd)/shared/scripts/mission_control.py /usr/local/bin/mission_control

# Now from anywhere:
mission_control render --wait
```

---

## What Files Were Created

```
shared/
├── scripts/
│   ├── mission_control.py       ← Mac-side orchestrator (you run this)
│   ├── pod_agent.sh             ← Pod-side job executor (runs in background)
│   └── setup_pod.sh             ← Updated: installs agent on pod
├── docs/
│   ├── MISSION_CONTROL.md       ← Full documentation
│   └── MISSION_CONTROL_QUICKSTART.md  ← This file
└── examples/
    ├── job_manifest_render.json       ← Example render job
    └── job_manifest_character.json    ← Example character job
```

---

## Next Steps

1. **Try it out:**
   ```bash
   ./shared/scripts/mission_control.py render --characters "X Bot" --wait
   ```

2. **Read full docs:**
   - [MISSION_CONTROL.md](MISSION_CONTROL.md) - Complete documentation
   - [../README.md](../../README.md) - Updated project overview

3. **Customize:**
   - Add character creation job type
   - Adjust poll interval (default: 30s)
   - Add email notifications

---

**Questions?** Check [MISSION_CONTROL.md](MISSION_CONTROL.md) for advanced usage, architecture notes, and customization.

**Enjoy never copy-pasting terminal commands again!** 🎉

