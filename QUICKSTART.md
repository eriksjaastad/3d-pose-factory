# Pose Factory Render Agent - Quick Start

**One command to rule them all.** 🏭

---

## Prerequisites

1. **RunPod GPU instance running** (A40 or similar)
2. **Pod ID saved** in `.pod_id` file
3. **SSH Agent running** locally

---

## The Golden Script

**What it does:**
- Sets up a Blender scene (cube, camera, light)
- Renders a base image
- Calls Stability AI SDXL to generate an AI-enhanced character
- Saves everything to `/workspace/output/`

**Cost:** ~$0.04 per generation

---

## Running It (3 Steps)

### Step 1: Start SSH Agent (once per session)

```bash
cd "${PROJECTS_ROOT}/3d-pose-factory"
cd "${PROJECTS_ROOT}/_tools/ssh_agent"
./start_agent.sh
```

**Leave this running in a terminal.**

---

### Step 2: Run Golden Script on Pod

**Option A: Via SSH Agent (Recommended)**

In a new terminal:

```bash
cd "${PROJECTS_ROOT}/3d-pose-factory"

# Queue the command
echo '{"id":"generate-'$(date +%s)'","host":"runpod","command":"cd /workspace && rclone copy r2_pose_factory:pose-factory/scripts/generate_character_from_cube.py scripts/ && blender --background --python scripts/generate_character_from_cube.py 2>&1 | tail -50"}' >> "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl"

# Watch the results (in real-time)
tail -f "${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl"
```

**Option B: Manual SSH (if agent isn't running)**

```bash
# Connect to pod
ssh $(cat .pod_id)@ssh.runpod.io -i ~/.ssh/id_ed25519

# On the pod:
cd /workspace
rclone copy r2_pose_factory:pose-factory/scripts/generate_character_from_cube.py scripts/
blender --background --python scripts/generate_character_from_cube.py
```

---

### Step 3: Download Results

**Check what was generated:**

```bash
echo '{"id":"list-output-'$(date +%s)'","host":"runpod","command":"ls -lh /workspace/output/*.png | tail -5"}' >> "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl"

# Wait a few seconds, then:
tail -1 "${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl" | jq -r '.stdout'
```

**Download everything:**

```bash
# Pod → R2
echo '{"id":"upload-results-'$(date +%s)'","host":"runpod","command":"rclone copy /workspace/output/ r2_pose_factory:pose-factory/output/"}' >> "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl"

# R2 → Local
rclone copy r2_pose_factory:pose-factory/output/ data/output/ --progress
```

**Open the files:**

```bash
open data/output/
```

---

## What You'll Get

1. **Base Render:**
   - `character_base.png` - The original Blender render (gray cube)

2. **AI-Generated:**
   - `ai-render-{timestamp}-{prompt}-2-after.png` - The SDXL-enhanced version

**Example:**
- Input: Gray cube on dark background
- Output: Photorealistic 3D character with professional lighting

---

## Customizing the Script

Edit `shared/scripts/generate_character_from_cube.py`:

```python
CONFIG = {
    'prompt': 'Your custom prompt here',
    'negative_prompt': 'Things to avoid',
    'resolution': (1024, 1024),  # SDXL requires 1024x1024
    'steps': 20,                  # More steps = better quality, higher cost
    'cfg_scale': 7.0,            # Prompt adherence (1-20)
    'seed': 42,                  # For reproducibility
    'output_dir': '/workspace/output/',
}
```

Then re-upload:

```bash
rclone copy shared/scripts/generate_character_from_cube.py r2_pose_factory:pose-factory/scripts/ --progress
```

---

## Troubleshooting

### "SSH agent not running"
**Fix:**
```bash
cd "${PROJECTS_ROOT}/_tools/ssh_agent"
./start_agent.sh
```

### "No AI-generated image found"
**Cause:** Autosave not configured  
**Fix:** The golden script already has this. But if writing your own:
```python
scene.air_props.do_autosave_after_images = True
scene.air_props.autosave_image_path = "/workspace/output/"
```

### "Invalid dimensions"
**Cause:** Not using 1024x1024  
**Fix:** SDXL only supports 1024x1024. Update `CONFIG['resolution']`.

### "Command timed out"
**Cause:** Stability AI API is slow (30-90 seconds)  
**Solution:** Just wait. The command will complete.

---

## Next Steps

- **Batch Processing:** Modify script to loop and generate multiple characters
- **Custom Prompts:** Experiment with different character descriptions
- **Integration:** Use with the web dashboard for easier management
- **Cost Tracking:** Monitor Stability AI usage in your account

---

**Read the full pipeline docs:** [PIPELINE_OVERVIEW.md](PIPELINE_OVERVIEW.md)

**Questions?** Check the overview or review `shared/scripts/generate_character_from_cube.py` source code.

---

🏭 **Pose Factory Render Agent** - Making AI character generation easy since 2024.

