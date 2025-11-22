#!/bin/bash
# Auto-run script for 3D Pose Factory
# This script runs automatically when the pod starts

set -e  # Exit on any error

echo "================================"
echo "3D Pose Factory - Auto Processing"
echo "================================"
echo ""

# Change to workspace
cd /workspace/pose-factory

# Step 1: Download inputs from R2
echo "[1/5] Downloading inputs from R2..."
rclone sync r2_pose_factory:pose-factory/input/ ./input/ -v
INPUT_COUNT=$(ls -1 input/*.{jpg,jpeg,png} 2>/dev/null | wc -l)
echo "Found $INPUT_COUNT images to process"

if [ "$INPUT_COUNT" -eq 0 ]; then
    echo "No images to process. Exiting."
    exit 0
fi

# Step 2: Run pose detection on all inputs
echo "[2/5] Running pose detection..."
python3 batch_process.py

# Step 3: Upload results to R2
echo "[3/5] Uploading results to R2..."
rclone copy ./output/poses/ r2_pose_factory:pose-factory/output/processed-$(date +%Y%m%d-%H%M%S)/ -v

# Step 4: Clean up processed files
echo "[4/5] Cleaning up..."
rm -f input/*.{jpg,jpeg,png} 2>/dev/null || true
rm -f output/frames/*.{jpg,jpeg,png} 2>/dev/null || true

# Step 5: Shutdown (optional - comment out if you want to keep pod running)
echo "[5/5] Processing complete! Results uploaded to R2."
echo ""
echo "To shutdown automatically, uncomment the shutdown line in this script."
# echo "Shutting down pod in 30 seconds..."
# sleep 30
# runpodctl stop pod

echo "================================"
echo "DONE! Pod is still running."
echo "================================"

