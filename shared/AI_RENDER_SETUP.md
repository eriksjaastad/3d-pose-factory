# AI Render Setup Instructions

**Goal:** Install AI Render (Stable Diffusion in Blender) on the pod, with persistence across restarts.

---

## Step 1: Upload AI Render to R2 (Do Once)

On your Mac, where you downloaded AI Render:

```bash
cd ~/Downloads  # Or wherever AI-Render folder is
rclone copy AI-Render/ r2_pose_factory:pose-factory/blender-addons/AI-Render/ --progress
```

**Verify upload:**
```bash
rclone lsd r2_pose_factory:pose-factory/blender-addons/
# Should show: AI-Render
```

---

## Step 2: Get API Keys

### DreamStudio (Stability AI's interface)
1. Go to: https://beta.dreamstudio.ai/account
2. Sign up / Log in
3. Navigate to "API Keys"
4. Generate new key
5. Copy the key

### Stability AI (Direct API)
1. Go to: https://platform.stability.ai/account/keys
2. Sign up / Log in
3. Generate new key
4. Copy the key

**Save these keys!** You'll need them in Step 3.

---

## Step 3: Create `.env` File (Do Once)

On your Mac:

```bash
cd "${PROJECTS_ROOT}/3d-pose-factory/shared"
cp .env.example .env
```

Edit `.env` and add your real keys:
```bash
DREAMSTUDIO_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STABILITY_API_KEY=sk-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

Upload to R2:
```bash
rclone copy .env r2_pose_factory:pose-factory/shared/ --progress
```

---

## Step 4: Update setup_pod.sh on R2

Upload the updated setup script:

```bash
cd "${PROJECTS_ROOT}/3d-pose-factory"
rclone copy shared/scripts/setup_pod.sh r2_pose_factory:pose-factory/shared/scripts/ --progress
```

---

## Step 5: Install on Pod

### Option A: Fresh Pod (Recommended)
1. Stop current pod (if running)
2. Start new pod from dashboard
3. SSH in:
   ```bash
   ssh YOUR_POD_ID@ssh.runpod.io -i ~/.ssh/id_ed25519
   ```
4. Run setup:
   ```bash
   rclone copy r2_pose_factory:pose-factory/shared/.env /workspace/
   rclone copy r2_pose_factory:pose-factory/shared/scripts/ /workspace/scripts/
   cd /workspace
   chmod +x scripts/setup_pod.sh
   ./scripts/setup_pod.sh
   ```

### Option B: Update Existing Pod
If you already have a pod running:

```bash
# SSH to pod
ssh YOUR_POD_ID@ssh.runpod.io -i ~/.ssh/id_ed25519

# Download .env
rclone copy r2_pose_factory:pose-factory/shared/.env /workspace/

# Download updated setup script
rclone copy r2_pose_factory:pose-factory/shared/scripts/setup_pod.sh /workspace/scripts/
chmod +x /workspace/scripts/setup_pod.sh

# Re-run setup (will install AI Render)
cd /workspace
./scripts/setup_pod.sh
```

---

## Step 6: Verify Installation

On the pod:

```bash
# Check if AI Render is installed
ls -la ~/.config/blender/4.0/scripts/addons/AI-Render

# Check if config was created
cat ~/.config/blender/4.0/scripts/addons/AI-Render/config.py
```

Should show your API keys (masked).

---

## How It Works (Persistence)

```
R2 Storage (Permanent)
  ├── blender-addons/AI-Render/  ← Plugin files
  └── shared/.env                ← API keys

      ↓ (on pod startup)

Pod /workspace (Persistent)
  ├── blender-addons/AI-Render/  ← Downloaded from R2
  └── .env                       ← Downloaded from R2

      ↓ (setup_pod.sh copies)

Pod ~/.config/blender/ (Wiped on restart)
  └── 4.0/scripts/addons/AI-Render/  ← Copied from /workspace
      └── config.py  ← Generated from .env
```

**Every time the pod restarts:**
1. /workspace (persistent) keeps the addon
2. setup_pod.sh copies it to Blender
3. Credentials loaded from /workspace/.env

---

## Testing

Once installed, test in Blender (headless):

```bash
blender --background --python - << 'EOF'
import bpy
import sys

# Check if AI Render is available
if 'ai_render' in bpy.context.preferences.addons:
    print("✅ AI Render installed!")
    sys.exit(0)
else:
    print("❌ AI Render not found")
    sys.exit(1)
EOF
```

---

## Troubleshooting

### "API key not found"
- Check `/workspace/.env` exists and has correct keys
- Re-run `setup_pod.sh`

### "AI Render addon not found"
- Check `/workspace/blender-addons/AI-Render` exists
- Check `~/.config/blender/4.0/scripts/addons/AI-Render` exists
- Re-run `setup_pod.sh`

### "Wrong Blender version"
- AI Render installed to 4.0 (RunPod uses Blender 4.0.2)
- Check version: `blender --version`
- Adjust paths if different version

---

**Once this is done, AI Render will:**
- ✅ Auto-install on every pod restart
- ✅ Have credentials ready
- ✅ Be accessible to our cost calculator
- ✅ Work in headless mode

**Ready to start!** 🚀

## Related Documentation

- [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md) - secrets management
- [Cost Management](Documents/reference/MODEL_COST_COMPARISON.md) - cost management
- [README](README) - 3D Pose Factory
