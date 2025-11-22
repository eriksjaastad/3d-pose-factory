#!/usr/bin/env bash
set -euo pipefail

# Run this on your Mac to bootstrap a fresh RunPod pod.
# It SSHes into the pod using $RUNPOD_3D_POSE_SSH and runs setup_runpod_pod.sh there.

if [[ -z "${RUNPOD_3D_POSE_SSH:-}" ]]; then
  echo "ERROR: RUNPOD_3D_POSE_SSH is not set. Update your ~/.zshrc first." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[local] Connecting to RunPod and running setup_runpod_pod.sh..."
${RUNPOD_3D_POSE_SSH} 'bash -s' < "${SCRIPT_DIR}/setup_runpod_pod.sh"

echo "[local] Setup script finished on pod."


