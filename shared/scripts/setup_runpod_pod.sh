#!/usr/bin/env bash
set -euo pipefail

# 3D Pose Factory – RunPod pod bootstrap script
#
# Usage (inside a fresh RunPod pod, as root):
#   apt update && apt install -y git
#   git clone <your-git-url> /workspace/3d-pose-factory
#   cd /workspace/3d-pose-factory/scripts
#   bash setup_runpod_pod.sh
#
# This script:
# - Updates the system
# - Installs core tools (wget, curl, git, build-essential, etc.)
# - Installs Blender from apt
# - Installs Python 3 + pip + venv
# - Installs rclone
# - Creates a project workspace at /workspace/3d_pose_factory
# - Sets up a Python virtualenv and installs pose-related Python packages

echo "[setup] Updating system packages..."
apt update
apt upgrade -y

echo "[setup] Installing core dependencies..."
DEBIAN_FRONTEND=noninteractive apt install -y \
  wget \
  git \
  curl \
  build-essential \
  software-properties-common

echo "[setup] Installing Blender (apt)..."
apt install -y blender

echo "[setup] Installing Python 3, pip and venv..."
apt install -y python3 python3-pip python3-venv

echo "[setup] Installing rclone..."
apt install -y rclone

WORKDIR="/workspace/3d_pose_factory"
echo "[setup] Creating workspace at ${WORKDIR}..."
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

if [ ! -d ".venv" ]; then
  echo "[setup] Creating Python virtual environment..."
  python3 -m venv .venv
fi

echo "[setup] Activating virtual environment..."
set +u
source .venv/bin/activate
set -u

echo "[setup] Upgrading pip and installing Python libraries..."
pip install --upgrade pip
pip install \
  numpy \
  pillow \
  opencv-python \
  mediapipe \
  boto3

echo "[setup] Done. To use this environment next time, run:"
echo "  ssh <pod-id>@ssh.runpod.io -i ~/.ssh/id_ed25519"
echo "  cd ${WORKDIR}"
echo "  source .venv/bin/activate"


