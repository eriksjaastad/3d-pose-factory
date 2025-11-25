#!/bin/bash
###############################################################################
# 3D Pose Factory - Pod Setup Script
# 
# Run this once on a fresh RunPod pod to set up everything:
#   - Blender + graphics libraries
#   - Python packages
#   - rclone configuration
#   - Pod Agent (auto-executes jobs from R2)
#
# Usage:
#   ./setup_pod.sh
###############################################################################

set -e  # Exit on error

echo "================================"
echo "3D Pose Factory - Pod Setup"
echo "================================"
echo ""

# Update system
echo "[1/8] Updating system packages..."
apt update -qq

# Install Blender, graphics libraries, and jq (for JSON parsing)
echo "[2/8] Installing Blender + graphics libraries + jq..."
DEBIAN_FRONTEND=noninteractive apt install -y -qq blender libegl1 libgl1 libgomp1 jq

# Install Python packages for pose detection
echo "[3/8] Installing Python packages..."
pip3 install -q opencv-python mediapipe pillow numpy

# Create workspace directory structure
echo "[4/8] Creating workspace directories..."
mkdir -p /workspace/{jobs/{pending,processing},output,downloads,scripts}

# Configure rclone for R2 access (store in /workspace for persistence)
echo "[5/8] Configuring rclone..."
mkdir -p /workspace/.config/rclone
mkdir -p ~/.config/rclone

# Check if rclone config exists in workspace
if [ ! -f "/workspace/.config/rclone/rclone.conf" ]; then
    echo "   ❌ rclone config not found in /workspace/.config/rclone/rclone.conf"
    echo ""
    echo "   Please run bootstrap_fresh_pod.sh first to configure rclone."
    echo "   See: shared/scripts/bootstrap_fresh_pod.sh"
    echo ""
    exit 1
else
    echo "   ✅ Using existing rclone config from /workspace"
fi

# Symlink to ~/.config/rclone (gets recreated on each pod start)
ln -sf /workspace/.config/rclone/rclone.conf ~/.config/rclone/rclone.conf

# Test rclone
if rclone lsd r2_pose_factory:pose-factory &>/dev/null; then
    echo "   ✅ rclone configured successfully"
else
    echo "   ❌ rclone configuration failed"
    exit 1
fi

# Download Pod Agent and make it executable
echo "[6/8] Downloading Pod Agent..."
cd /workspace
rclone copy r2_pose_factory:pose-factory/shared/scripts/pod_agent.sh /workspace/ --progress
chmod +x /workspace/pod_agent.sh

# Install AI Render addon (Stable Diffusion in Blender)
echo "[7/8] Installing AI Render addon..."
mkdir -p /workspace/blender-addons
mkdir -p ~/.config/blender/4.0/scripts/addons

# Download AI Render from R2 to workspace (persistent storage)
if [ ! -d "/workspace/blender-addons/AI-Render" ]; then
    rclone copy r2_pose_factory:pose-factory/blender-addons/AI-Render/ /workspace/blender-addons/AI-Render/ --progress
fi

# Copy to Blender addons directory (needs to be done each startup)
cp -r /workspace/blender-addons/AI-Render ~/.config/blender/4.0/scripts/addons/

# Add API keys to the existing config.py (append, don't replace)
if [ -f "/workspace/.env" ]; then
    source /workspace/.env
    # Append API keys to the end of the original config.py
    cat >> ~/.config/blender/4.0/scripts/addons/AI-Render/config.py << EOF

# API Keys - Auto-appended by setup_pod.sh
DREAMSTUDIO_API_KEY = "${DREAMSTUDIO_API_KEY:-}"
STABILITY_API_KEY = "${STABILITY_API_KEY:-}"
EOF
    echo "   ✅ AI Render configured with API keys from /workspace/.env"
else
    echo "   ⚠️  No /workspace/.env found - AI Render will need manual API key setup"
fi

# Start Pod Agent in background
echo "[8/8] Starting Pod Agent..."
if pgrep -f "pod_agent.sh" > /dev/null; then
    echo "   ⚠️  Pod Agent already running"
else
    nohup /workspace/pod_agent.sh > /workspace/pod_agent.log 2>&1 &
    AGENT_PID=$!
    echo "   ✅ Pod Agent started (PID: $AGENT_PID)"
    echo "   📋 Logs: /workspace/pod_agent.log"
fi

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Installed:"
echo "  • Blender $(blender --version | head -n1)"
echo "  • OpenCV, MediaPipe, NumPy, Pillow"
echo "  • rclone configured for R2"
echo "  • jq for JSON parsing"
echo ""
echo "Pod Agent Status:"
echo "  • Running in background"
echo "  • Polling R2 every 30 seconds for jobs"
echo "  • Logs: /workspace/pod_agent.log"
echo ""
echo "From your Mac, submit jobs with:"
echo "  cd /path/to/3D\\ Pose\\ Factory"
echo "  ./shared/scripts/mission_control.py render --characters 'X Bot' --wait"
echo ""
echo "Check agent logs:"
echo "  tail -f /workspace/pod_agent.log"
echo ""

