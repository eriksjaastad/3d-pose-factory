# Mission Control - Unified RunPod Orchestrator

**No more terminal switching. No more copy-paste hell.** 🚀

Mission Control is a single command-line tool that manages your entire RunPod workflow from your Mac.

## The Problem It Solves

**Before:**
```
You: Copy this command
Terminal 1 (Mac): paste, run
You: Now copy this one
Terminal 2 (Pod): paste, run
Terminal 1 (Mac): Wait, was this for the pod or local?
*Repeat for 4 hours* 😩
```

**After:**
```bash
./shared/scripts/mission_control.py render --characters "X Bot" --wait
# ☕ Go make coffee, everything happens automatically
```

---

## How It Works

```
Your Mac                    R2 (Message Queue)              RunPod Pod
  │                              │                              │
  │  1. Upload scripts           │                              │
  ├────────────────────────────► │                              │
  │                              │                              │
  │  2. Create job manifest      │                              │
  ├────────────────────────────► │                              │
  │                              │                              │
  │                              │  3. Pod Agent polls (30s)    │
  │                              │ ◄────────────────────────────┤
  │                              │                              │
  │                              │  4. Download job             │
  │                              ├────────────────────────────► │
  │                              │                              │
  │                              │  5. Execute job              │
  │                              │                           [Blender]
  │                              │                              │
  │                              │  6. Upload results           │
  │                              │ ◄────────────────────────────┤
  │                              │                              │
  │  7. Download results         │                              │
  │ ◄────────────────────────────┤                              │
  │                              │                              │
  ✅ Done!
```

**Key Insight:** We use **R2 as a message queue**. The pod constantly polls for new jobs, executes them, and uploads results. Your Mac just submits jobs and downloads results.

---

## Quick Start

### 1. First Time Setup (One Time Only)

On your Mac, upload the setup scripts to R2:

```bash
cd /path/to/3D\ Pose\ Factory
./shared/scripts/mission_control.py setup-pod
```

Then SSH to your pod and run:

```bash
ssh YOUR_POD_ID@ssh.runpod.io -i ~/.ssh/id_ed25519

# On the pod:
rclone copy r2_pose_factory:pose-factory/shared/scripts/ /workspace/scripts/
cd /workspace
./scripts/setup_pod.sh
```

The pod agent will start automatically and begin polling for jobs.

### 2. Submit a Render Job

From your Mac:

```bash
# Render all characters and wait for completion
./shared/scripts/mission_control.py render --wait

# Render specific characters
./shared/scripts/mission_control.py render --characters "X Bot,Dancer" --wait

# Submit job and check status later
./shared/scripts/mission_control.py render
```

### 3. Check Job Status

```bash
# List all recent jobs
./shared/scripts/mission_control.py status

# Check specific job
./shared/scripts/mission_control.py status --job render_20231124_153045_a1b2c3d4
```

### 4. Download Results

```bash
# Download specific job results
./shared/scripts/mission_control.py download --job render_20231124_153045_a1b2c3d4

# Results will be in: data/working/{job_id}/
```

---

## Commands Reference

### `setup-pod`
Upload setup scripts to R2 for pod initialization.

```bash
./shared/scripts/mission_control.py setup-pod
```

**What it does:**
- Uploads `shared/scripts/` to R2
- Prints instructions for running setup on the pod

**When to use:**
- First time setup
- After updating pod_agent.sh or setup_pod.sh

---

### `render`
Submit a render job to the pod.

```bash
./shared/scripts/mission_control.py render [OPTIONS]
```

**Options:**
- `--characters "Name1,Name2"` - Comma-separated character names (default: all)
- `--output path/to/output` - Output directory (default: `output/simple_multi_angle`)
- `--wait` - Wait for completion and auto-download results

**Examples:**

```bash
# Render all characters, wait, and download
./shared/scripts/mission_control.py render --wait

# Render specific characters
./shared/scripts/mission_control.py render --characters "X Bot,Salsa Dancer"

# Custom output directory
./shared/scripts/mission_control.py render --output custom/path --wait

# Submit and check later
./shared/scripts/mission_control.py render
# Later:
./shared/scripts/mission_control.py status
./shared/scripts/mission_control.py download --job JOB_ID
```

---

### `status`
Check job status.

```bash
./shared/scripts/mission_control.py status [OPTIONS]
```

**Options:**
- `--job JOB_ID` - Check specific job (optional)

**Examples:**

```bash
# List all recent jobs
./shared/scripts/mission_control.py status

# Check specific job
./shared/scripts/mission_control.py status --job render_20231124_153045_a1b2c3d4
```

**Job States:**
- `pending` - Waiting for pod to pick it up
- `processing` - Currently executing on pod
- `completed` - Finished, results available
- `unknown` - Job not found (may have been cleaned up)

---

### `download`
Download job results from R2.

```bash
./shared/scripts/mission_control.py download --job JOB_ID [OPTIONS]
```

**Options:**
- `--job JOB_ID` - Job ID to download (required)
- `--force` - Download even if not completed

**Examples:**

```bash
# Download completed job
./shared/scripts/mission_control.py download --job render_20231124_153045_a1b2c3d4

# Force download (even if still processing)
./shared/scripts/mission_control.py download --job render_20231124_153045_a1b2c3d4 --force
```

**Where results go:**
```
data/working/{job_id}/
```

---

## Pod Agent

The **Pod Agent** runs continuously on your RunPod, polling R2 for new jobs every 30 seconds.

### Check Agent Status

SSH to your pod and check:

```bash
# View live logs
tail -f /workspace/pod_agent.log

# Check if running
ps aux | grep pod_agent
```

### Restart Agent

If the agent stops (pod restart, crash, etc.):

```bash
cd /workspace
./scripts/setup_pod.sh
```

This will restart the agent if it's not already running.

### Manual Start

```bash
cd /workspace
./pod_agent.sh &  # Run in background
```

---

## Troubleshooting

### "rclone not configured"

**Problem:** Pod agent can't access R2.

**Solution:**
```bash
# On the pod:
cd /workspace
./scripts/setup_pod.sh
```

This will reconfigure rclone and restart the agent.

---

### "Job stuck in pending"

**Problem:** Job submitted but never gets processed.

**Possible causes:**
1. Pod agent not running
2. rclone not configured
3. Pod is turned off

**Solution:**
```bash
# SSH to pod and check agent logs
tail -f /workspace/pod_agent.log

# Restart agent
cd /workspace
./scripts/setup_pod.sh
```

---

### "Job completed but no results"

**Problem:** Job shows as completed but download fails.

**Solution:**
```bash
# Check R2 directly
rclone lsd r2_pose_factory:pose-factory/results/

# Force download
./shared/scripts/mission_control.py download --job JOB_ID --force
```

---

### "Can't find mission_control.py"

**Problem:** Running from wrong directory.

**Solution:**
```bash
# Always run from project root
cd /path/to/3D\ Pose\ Factory
./shared/scripts/mission_control.py render --wait
```

Or make it executable and add to PATH:
```bash
chmod +x shared/scripts/mission_control.py
ln -s $(pwd)/shared/scripts/mission_control.py /usr/local/bin/mission_control
# Now you can run from anywhere:
mission_control render --wait
```

---

## Advanced Usage

### Job Manifests

Mission Control creates JSON manifests for each job. You can inspect them:

```bash
# View local job history
cat data/jobs/*.json | jq '.'

# View pending jobs in R2
rclone cat r2_pose_factory:pose-factory/jobs/pending/JOB_ID.json | jq '.'
```

**Example manifest:**
```json
{
  "job_id": "render_20231124_153045_a1b2c3d4",
  "job_type": "render",
  "created_at": "2023-11-24T15:30:45.123456",
  "status": "pending",
  "params": {
    "script": "pose-rendering/scripts/render_simple_working.py",
    "characters": ["X Bot", "Dancer"],
    "output_dir": "output/simple_multi_angle"
  }
}
```

### Custom Job Types

To add a new job type (e.g., `character` for character creation):

1. **Add handler in `mission_control.py`:**
   ```python
   def cmd_create_character(self, args):
       params = {
           "script": "character-creation/scripts/create_character.py",
           "character_params": {...}
       }
       job_id, _ = self.create_job("character", params)
       # ...
   ```

2. **Add executor in `pod_agent.sh`:**
   ```bash
   execute_character_job() {
       local manifest_file="$1"
       local job_id="$2"
       # Download scripts, run Blender, upload results
   }
   ```

3. **Add to case statement:**
   ```bash
   case "$job_type" in
       render)
           execute_render_job "$manifest_file" "$job_id"
           ;;
       character)
           execute_character_job "$manifest_file" "$job_id"
           ;;
   esac
   ```

---

## Architecture Notes

### Why R2 as Message Queue?

**Alternatives considered:**
1. **RunPod API** - Doesn't support arbitrary command execution
2. **Direct SSH** - RunPod's SSH is interactive-only (no exec, no SCP)
3. **Custom server** - Too much overhead

**R2 advantages:**
- Already configured for file storage
- Free egress to RunPod
- Simple polling model
- No additional infrastructure

### Polling Interval

Default: **30 seconds**

**Why not faster?**
- Jobs typically run for minutes/hours
- R2 API rate limits
- Minimal latency impact (jobs are long-running)

**To adjust:**
Edit `POLL_INTERVAL` in `pod_agent.sh`:
```bash
POLL_INTERVAL=10  # Poll every 10 seconds
```

### Job Cleanup

- Local manifests: Never deleted (full history)
- R2 pending/processing: Moved to completion (manual cleanup)
- Pod local files: Deleted after 24 hours

---

## What's Next?

Mission Control is built to expand:

- [ ] Character creation job type
- [ ] Batch processing (multiple jobs)
- [ ] Email notifications on completion
- [ ] Web dashboard for job monitoring
- [ ] Multiple pod support (job distribution)

---

**Questions or issues?** Check the main [README](../../README.md) or [RESOURCES](../../docs/RESOURCES.md).

