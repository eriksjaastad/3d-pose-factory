#!/bin/bash
###############################################################################
# Sync Results to R2
# 
# Run this before terminating a pod to push all outputs back to R2.
#
# Usage:
#   ./sync_results_to_r2.sh [--include-logs] [--include-scratch]
###############################################################################

set -e

INCLUDE_LOGS=false
INCLUDE_SCRATCH=false

# Parse args
for arg in "$@"; do
    case $arg in
        --include-logs) INCLUDE_LOGS=true ;;
        --include-scratch) INCLUDE_SCRATCH=true ;;
    esac
done

echo "========================================"
echo "  Syncing Results to R2"
echo "========================================"
echo ""

# Main outputs (always sync)
echo "📤 Syncing /workspace/output/ → R2..."
rclone copy /workspace/output/ r2_pose_factory:pose-factory/output/ --progress
echo "   ✅ Outputs synced"

# Logs (optional)
if [ "$INCLUDE_LOGS" = true ]; then
    echo ""
    echo "📤 Syncing /workspace/logs/ → R2..."
    rclone copy /workspace/logs/ r2_pose_factory:pose-factory/logs/ --progress
    echo "   ✅ Logs synced"
fi

# Scratch (optional)
if [ "$INCLUDE_SCRATCH" = true ]; then
    echo ""
    echo "📤 Syncing /workspace/scratch/ → R2..."
    rclone copy /workspace/scratch/ r2_pose_factory:pose-factory/scratch/ --progress
    echo "   ✅ Scratch synced"
fi

echo ""
echo "========================================"
echo "  ✅ Sync Complete!"
echo "========================================"
echo ""
echo "Safe to terminate pod."
echo ""

