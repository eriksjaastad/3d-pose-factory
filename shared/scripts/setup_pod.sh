#!/bin/bash
###############################################################################
# 3D Pose Factory - Pod Setup Script
# 
# Run this once on a fresh RunPod pod to set up everything:
#   - Blender + graphics libraries
#   - Python packages
#   - rclone configuration
#   - Standardized directory layout
#   - Pod Agent (auto-executes jobs from R2)
#
# Usage:
#   ./setup_pod.sh
#
# This script is IDEMPOTENT - safe to re-run any time.
###############################################################################

set -e  # Exit on error

echo "========================================"
echo "  3D Pose Factory - Pod Setup v2.0"
echo "========================================"
echo ""

# =============================================================================
# Phase 1: System packages
# =============================================================================
echo "[1/8] Updating system packages..."
apt-get update -qq

echo "[2/8] Installing Blender + dependencies..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    blender libegl1 libgl1 libgomp1 \
    jq curl wget unzip ffmpeg tmux \
    python3 python3-pip python3-venv

# =============================================================================
# Phase 2: Python packages
# =============================================================================
echo "[3/8] Installing Python packages..."
pip3 install -q --upgrade pip
pip3 install -q opencv-python==4.8.1.78 mediapipe==0.10.8 pillow==10.1.0 numpy==1.26.2 requests==2.31.0

# =============================================================================
# Phase 3: Create standardized directory layout
# =============================================================================
echo "[4/8] Creating workspace directories..."

# Assets (inputs from R2)
mkdir -p /workspace/assets/animations
mkdir -p /workspace/assets/characters
mkdir -p /workspace/assets/meshes

# Outputs (results to R2) - organized by project
mkdir -p /workspace/output/pose-rendering
mkdir -p /workspace/output/character-creation
mkdir -p /workspace/output/scratch

# Scripts (downloaded from R2)
mkdir -p /workspace/scripts/pose-rendering
mkdir -p /workspace/scripts/character-creation
mkdir -p /workspace/scripts/shared

# Other
mkdir -p /workspace/logs
mkdir -p /workspace/config
mkdir -p /workspace/scratch
mkdir -p /workspace/jobs/{pending,processing}

# Legacy compatibility (symlinks for old paths)
[ ! -e /workspace/meshes ] && ln -sf /workspace/assets/meshes /workspace/meshes
[ ! -e /workspace/downloads ] && ln -sf /workspace/assets /workspace/downloads

echo "   ✅ Directory layout created"

# =============================================================================
# Phase 4: rclone configuration
# =============================================================================
echo "[5/8] Configuring rclone..."
mkdir -p /workspace/.config/rclone
mkdir -p ~/.config/rclone

if [ ! -f "/workspace/.config/rclone/rclone.conf" ]; then
    echo "   ❌ rclone config not found in /workspace/.config/rclone/rclone.conf"
    echo ""
    echo "   Run bootstrap_pod.py from your Mac first, or manually configure rclone."
    echo ""
    exit 1
fi

# Symlink to standard location (needed each pod start)
ln -sf /workspace/.config/rclone/rclone.conf ~/.config/rclone/rclone.conf

# Test rclone
if rclone lsd r2_pose_factory:pose-factory &>/dev/null; then
    echo "   ✅ rclone configured and working"
else
    echo "   ❌ rclone connection failed"
    exit 1
fi

# =============================================================================
# Phase 5: Create config.yaml
# =============================================================================
echo "[6/8] Setting up config.yaml..."

if [ ! -f "/workspace/config/config.yaml" ]; then
    cat > /workspace/config/config.yaml << 'EOF'
# 3D Pose Factory - Pod Configuration
# This file tells scripts where things are located

paths:
  # Inputs (from R2)
  assets_root: /workspace/assets
  animations_dir: /workspace/assets/animations
  characters_dir: /workspace/assets/characters
  meshes_dir: /workspace/assets/meshes
  
  # Outputs (to R2)
  output_root: /workspace/output
  pose_rendering_output: /workspace/output/pose-rendering
  character_creation_output: /workspace/output/character-creation
  scratch_output: /workspace/output/scratch
  
  # Other
  logs_dir: /workspace/logs
  scripts_dir: /workspace/scripts
  config_dir: /workspace/config

r2:
  bucket: pose-factory
  remote: r2_pose_factory

blender:
  version: "4.0"
  addons_dir: ~/.config/blender/4.0/scripts/addons
EOF
    echo "   ✅ config.yaml created"
else
    echo "   ✅ config.yaml already exists (not overwriting)"
fi

# =============================================================================
# Phase 6: AI Render addon
# =============================================================================
echo "[7/8] Installing AI Render addon..."
mkdir -p /workspace/blender-addons
mkdir -p ~/.config/blender/4.0/scripts/addons

# Download AI Render from R2 (if not already there)
if [ ! -d "/workspace/blender-addons/AI-Render" ]; then
    rclone copy r2_pose_factory:pose-factory/blender-addons/AI-Render/ /workspace/blender-addons/AI-Render/ 2>/dev/null || true
fi

# Copy to Blender addons directory
if [ -d "/workspace/blender-addons/AI-Render" ]; then
    cp -r /workspace/blender-addons/AI-Render ~/.config/blender/4.0/scripts/addons/
    
    # Add API keys if .env exists
    if [ -f "/workspace/.env" ]; then
        source /workspace/.env
        cat >> ~/.config/blender/4.0/scripts/addons/AI-Render/config.py << EOF

# API Keys - Auto-appended by setup_pod.sh
DREAMSTUDIO_API_KEY = "${DREAMSTUDIO_API_KEY:-}"
STABILITY_API_KEY = "${STABILITY_API_KEY:-}"
EOF
        echo "   ✅ AI Render installed with API keys"
    else
        echo "   ⚠️  AI Render installed (no API keys - missing /workspace/.env)"
    fi
else
    echo "   ⚠️  AI Render not found on R2 (skipping)"
fi

# =============================================================================
# Phase 7: Smoke tests
# =============================================================================
echo "[8/8] Running smoke tests..."

# Test 1: Blender version
BLENDER_VERSION=$(blender --version 2>/dev/null | head -n1 || echo "FAILED")
if [[ "$BLENDER_VERSION" == *"Blender"* ]]; then
    echo "   ✅ Blender: $BLENDER_VERSION"
else
    echo "   ❌ Blender test FAILED"
fi

# Test 2: Blender Python
BLENDER_PYTHON_TEST=$(blender --background --python-expr "import bpy; print('BLENDER_PYTHON_OK')" 2>&1 | grep -c "BLENDER_PYTHON_OK" || echo "0")
if [ "$BLENDER_PYTHON_TEST" -gt 0 ]; then
    echo "   ✅ Blender Python: Working"
else
    echo "   ⚠️  Blender Python: Could not verify"
fi

# Test 3: GPU (optional)
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n1 || echo "Unknown")
    echo "   ✅ GPU: $GPU_NAME"
else
    echo "   ⚠️  GPU: nvidia-smi not found"
fi

# Test 4: R2 connection
R2_TEST=$(rclone lsd r2_pose_factory:pose-factory 2>/dev/null | wc -l || echo "0")
if [ "$R2_TEST" -gt 0 ]; then
    echo "   ✅ R2: Connected ($R2_TEST directories)"
else
    echo "   ❌ R2 test FAILED"
fi

# Log results
echo "$(date -Iseconds) - Setup complete" >> /workspace/logs/setup.log

# =============================================================================
# Start Pod Agent (optional)
# =============================================================================
echo ""
read -p "Start Pod Agent for automatic job processing? [y/N] " -n 1 -r -t 5 || REPLY="n"
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Download latest pod agent
    rclone copy r2_pose_factory:pose-factory/shared/scripts/pod_agent.sh /workspace/ 2>/dev/null || true
    chmod +x /workspace/pod_agent.sh 2>/dev/null || true
    
    if [ -f "/workspace/pod_agent.sh" ]; then
        if pgrep -f "pod_agent.sh" > /dev/null; then
            echo "   ⚠️  Pod Agent already running"
        else
            nohup /workspace/pod_agent.sh > /workspace/logs/pod_agent.log 2>&1 &
            echo "   ✅ Pod Agent started (logs: /workspace/logs/pod_agent.log)"
        fi
    else
        echo "   ⚠️  Pod Agent not found on R2"
    fi
else
    echo "   ⏭️  Pod Agent skipped"
fi

# =============================================================================
# Done!
# =============================================================================
echo ""
echo "========================================"
echo "  ✅ Setup Complete!"
echo "========================================"
echo ""
echo "Directory Layout:"
echo "  /workspace/assets/      ← Inputs (from R2)"
echo "  /workspace/output/      ← Results (to R2)"
echo "  /workspace/scripts/     ← Code"
echo "  /workspace/logs/        ← Logs"
echo "  /workspace/scratch/     ← Experiments"
echo "  /workspace/config/      ← config.yaml"
echo ""
echo "Quick Commands:"
echo "  # Sync assets from R2:"
echo "  rclone copy r2_pose_factory:pose-factory/assets/ /workspace/assets/"
echo ""
echo "  # Push results to R2:"
echo "  rclone copy /workspace/output/ r2_pose_factory:pose-factory/output/"
echo ""
echo "  # View config:"
echo "  cat /workspace/config/config.yaml"
echo ""
