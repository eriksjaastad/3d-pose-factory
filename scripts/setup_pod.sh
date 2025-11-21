#!/bin/bash
# 3D Pose Factory - Pod Setup Script
# Run this once on a fresh RunPod pod to set up everything

set -e  # Exit on error

echo "================================"
echo "3D Pose Factory - Pod Setup"
echo "================================"
echo ""

# Update system
echo "[1/6] Updating system packages..."
apt update -qq

# Install Blender and graphics libraries
echo "[2/6] Installing Blender + graphics libraries..."
DEBIAN_FRONTEND=noninteractive apt install -y -qq blender libegl1 libgl1 libgomp1

# Install Python packages for pose detection
echo "[3/6] Installing Python packages..."
pip3 install -q opencv-python mediapipe pillow numpy

# Clone GitHub repo to workspace
echo "[4/6] Cloning GitHub repo..."
cd /workspace
if [ -d "pose-factory" ]; then
    echo "   Repository already exists, pulling latest..."
    cd pose-factory && git pull
else
    git clone https://github.com/eriksjaastad/3d-pose-factory.git pose-factory
    cd pose-factory
fi

# Configure rclone for R2 access
echo "[5/6] Configuring rclone..."
rclone config create r2_pose_factory s3 \
  provider=Cloudflare \
  access_key_id=6ffa2bb8334ca011410364f0ab442c0b \
  secret_access_key=f5dc7ca04f894d418eb39949161840da29a40b50ee4a7f9b2b4e171de0058913 \
  endpoint=https://a9b0b4bfbfb9c185b43236f1f95b919b.r2.cloudflarestorage.com \
  acl=private \
  no_check_bucket=true \
  --non-interactive 2>/dev/null || echo "   rclone already configured"

# Download automation scripts from R2
echo "[6/6] Downloading automation scripts from R2..."
rclone copy r2_pose_factory:pose-factory/scripts/ /workspace/pose-factory/ --include "*.py" --include "*.sh" -q
chmod +x /workspace/pose-factory/*.sh

# Create directory structure
mkdir -p /workspace/pose-factory/input
mkdir -p /workspace/pose-factory/output/frames
mkdir -p /workspace/pose-factory/output/poses

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Installed:"
echo "  • Blender $(blender --version | head -n1)"
echo "  • OpenCV, MediaPipe, NumPy, Pillow"
echo "  • rclone configured for R2"
echo "  • GitHub repo cloned"
echo ""
echo "Ready to run:"
echo "  cd /workspace/pose-factory"
echo "  ./auto_process.sh"
echo ""

