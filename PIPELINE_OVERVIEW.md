# Pose Factory Render Agent - Pipeline Overview

**Version:** 1.0  
**Status:** Operational ✅  
**Last Updated:** 2024-11-24

---

## 🎯 What This Is

The **Pose Factory Render Agent** is a fully automated pipeline for generating AI-enhanced 3D character renders. It combines:

- **Blender** (headless 3D rendering)
- **AI Render** (Stable Diffusion integration)
- **Stability AI SDXL** (image generation)
- **SSH Agent** (automated command execution on RunPod)
- **R2 Storage** (file transfer and persistence)

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Local Machine  │
│   (Mac/Linux)   │
└────────┬────────┘
         │
         │ SSH Agent (pexpect)
         │ requests.jsonl → results.jsonl
         ▼
┌─────────────────┐
│     RunPod      │
│   GPU Instance  │
│                 │
│  ┌──────────┐   │
│  │ Blender  │   │
│  │ Headless │   │
│  └────┬─────┘   │
│       │         │
│  ┌────▼─────┐   │
│  │AI Render │   │
│  │ Plugin   │   │
│  └────┬─────┘   │
│       │         │
└───────┼─────────┘
        │
        │ HTTPS API
        ▼
┌─────────────────┐
│  Stability AI   │
│   SDXL 1024     │
└─────────────────┘
        │
        │ Generated Image
        ▼
┌─────────────────┐
│  R2 Storage     │
│ (Cloudflare)    │
└─────────────────┘
```

---

## 🔧 Components

### 1. SSH Agent (`_tools/ssh_agent/agent.py`)

**Purpose:** Execute commands on RunPod without manual SSH interaction.

**How It Works:**
- Watches "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl" for new commands
- Maintains a **persistent interactive SSH shell** using `pexpect`
- Executes commands and captures output + exit codes
- Writes results to "${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl"

**Why We Need It:**
- RunPod's SSH doesn't support direct command execution (`ssh user@host command`)
- Standard SSH libraries (paramiko) fail with RunPod's protocol
- Solution: `pexpect` maintains a live shell and "types" commands into it

**Key Files:**
- `_tools/ssh_agent/agent.py` - Main agent code
- `_tools/ssh_agent/ssh_hosts.yaml` - Host configurations
- `_tools/ssh_agent/start_agent.sh` - Startup script
- "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl" - Command queue (input)
- "${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl" - Results log (output)

**Usage:**
```bash
# Start the agent (in one terminal)
./ssh_agent/start_agent.sh

# Send commands (in another terminal or from code)
echo '{"id":"test_cmd","host":"runpod","command":"pwd"}' >> "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl"

# Read results
tail -1 "${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl" | jq .
```

### 2. AI Render Plugin

**Purpose:** Integrate Stable Diffusion into Blender's render pipeline.

**Critical Discovery:** AI Render only saves images to disk in headless mode if **autosave is enabled**.

**Required Settings:**
```python
scene.air_props.do_autosave_after_images = True
scene.air_props.autosave_image_path = "/workspace/output/"
```

**Model Limitations:**
- Only **SDXL 1024** is available
- Requires **1024x1024** resolution
- Images must be multiples of 64 (128, 256, 512, 1024, 2048)

**Headless Mode Fix:**
```python
# AI Render expects Render Result to have pixel data
# In headless mode, it doesn't populate automatically
render_result = bpy.data.images.get('Render Result')
if render_result and not render_result.has_data:
    # Load the rendered PNG and replace Render Result
    temp_img = bpy.data.images.load(rendered_path)
    temp_img.update()
    bpy.data.images.remove(render_result)
    temp_img.name = 'Render Result'
```

**Cost:**
- ~$0.04 per 1024x1024 image (20 steps, SDXL)
- Billed by Stability AI

### 3. RunPod Persistence

**Critical:** Only `/workspace` persists across pod restarts!

**Persistent Files:**
- `/workspace/.config/rclone/rclone.conf` (symlinked to `~/.config/rclone/rclone.conf`)
- `/workspace/blender-addons/AI-Render/` (plugin installation)
- `/workspace/.env` (API keys)
- `/workspace/scripts/` (our code)
- `/workspace/output/` (generated images)

**Lost on Restart:**
- Everything outside `/workspace`
- System packages (need to reinstall)
- Blender installation (need to reinstall)

**Solution:** `setup_pod.sh` reinstalls everything on each pod start.

---

## 📋 Happy Path Workflow

### Local → RunPod → AI Generation → Local

**1. Start SSH Agent (once per session):**
```bash
cd "${PROJECTS_ROOT}/_tools/ssh_agent"
./start_agent.sh
```

**2. Upload Golden Script to R2:**
```bash
rclone copy shared/scripts/generate_character_from_cube.py r2_pose_factory:pose-factory/scripts/
```

**3. Run on RunPod (via SSH Agent):**
```bash
echo '{"id":"gen_char_001","host":"runpod","command":"cd /workspace && rclone copy r2_pose_factory:pose-factory/scripts/generate_character_from_cube.py scripts/ && blender --background --python scripts/generate_character_from_cube.py"}' >> "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl"
```

**4. Check Results:**
```bash
tail -1 "${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl" | jq -r '.stdout'
```

**5. Download Generated Images:**
```bash
# Pod → R2
echo '{"id":"download_001","host":"runpod","command":"rclone copy /workspace/output/ai-render-*.png r2_pose_factory:pose-factory/output/"}' >> "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl"

# R2 → Local
rclone copy r2_pose_factory:pose-factory/output/ data/output/
```

---

## 🐛 Common Issues & Solutions

### Issue: "SSH session closed unexpectedly"
**Cause:** RunPod's SSH is interactive-only  
**Solution:** SSH Agent uses `pexpect` with persistent shell

### Issue: "AI-generated image not found"
**Cause:** Autosave not enabled  
**Solution:** Set `do_autosave_after_images = True` and `autosave_image_path`

### Issue: "Please set width and height to valid values"
**Cause:** Using 512x512 with SDXL model  
**Solution:** Use 1024x1024 (SDXL requirement)

### Issue: "Rendered image is not ready"
**Cause:** `Render Result` has no pixel data in headless mode  
**Solution:** Manually load rendered PNG into `Render Result` (see code above)

### Issue: "rclone not configured" on pod
**Cause:** Pod restarted, `/workspace/.config/rclone/` missing  
**Solution:** Run `setup_pod.sh` to restore config from `/workspace` backup

---

## 💰 Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| RunPod GPU (A40) | ~$0.40/hr | Only when running |
| Stability AI SDXL | ~$0.04/image | 1024x1024, 20 steps |
| R2 Storage | <$0.01/month | ~10GB storage, minimal egress |

**Estimated:** ~$0.50 per character generation session (setup + 5-10 images)

---

## 📁 Project Structure

```
3d-pose-factory/
├── _tools/ssh_agent/          # Automated SSH command execution (central)
│   ├── agent.py             # Main agent (pexpect-based)
│   ├── ssh_hosts.yaml       # Host configurations
│   └── start_agent.sh       # Startup script
│
├── _tools/ssh_agent/queue/    # Command queue (central)
│   ├── requests.jsonl       # Input: commands to execute
│   └── results.jsonl        # Output: command results
│
├── shared/                  # Code used on both local & pod
│   ├── scripts/
│   │   ├── generate_character_from_cube.py  # GOLDEN SCRIPT
│   │   ├── setup_pod.sh     # Pod initialization
│   │   └── pod_agent.sh     # Pod-side job executor
│   ├── cost_calculator.py   # Cost estimation
│   └── cost_config.yaml     # Pricing data
│
├── pose-rendering/          # Original pose detection pipeline
├── character-creation/      # Character generation workflow
├── dashboard/               # Web UI (Flask)
└── data/                    # Local outputs
```

---

## 🚀 Next Steps

1. **Integrate with Dashboard:** Add "Generate Character" button to web UI
2. **Batch Processing:** Generate multiple variations in one run
3. **Character Library:** Save/organize generated characters
4. **Prompt Engineering:** Experiment with better prompts for specific character types
5. **Cost Monitoring:** Real-time cost tracking in dashboard
6. **Animation Integration:** Apply AI enhancement to animated sequences

---

## 🎓 Lessons Learned

### 1. **RunPod SSH is Special**
Standard SSH assumptions don't apply. Interactive-only. `pexpect` is the way.

### 2. **Blender Plugins Have Hidden Requirements**
AI Render's autosave requirement wasn't documented. Always check source code.

### 3. **Headless Mode is Different**
UI-dependent features (like `Render Result` auto-population) don't work. Manual workarounds needed.

### 4. **Persistence is Critical**
Plan for pod restarts. Everything outside `/workspace` is ephemeral.

### 5. **Name Things Early**
"Pose Factory Render Agent" > "that blender thing we're working on"

---

## 📞 Contact / Support

**Built by:** Erik (with Claude Sonnet 4.5)  
**Date:** November 2024  
**License:** Private / Experimental

---

**Remember:** This pipeline is called the **Pose Factory Render Agent**. It's not a hack. It's a named system. Treat it with respect. 🏭✨

## Related Documentation

- [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md) - secrets management
- [Cost Management](Documents/reference/MODEL_COST_COMPARISON.md) - cost management
- [Tiered AI Sprint Planning](patterns/tiered-ai-sprint-planning.md) - prompt engineering
- [AI Model Cost Comparison](Documents/reference/MODEL_COST_COMPARISON.md) - AI models
- [README](README) - 3D Pose Factory
