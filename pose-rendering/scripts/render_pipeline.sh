#!/bin/bash
#
# 3D Pose Factory - Automated Render Pipeline
# 
# This script automates the entire workflow:
# 1. Upload Blender scripts to R2
# 2. SSH to RunPod and trigger batch render
# 3. Download results back to Mac
#
# Usage:
#   ./render_pipeline.sh                  # Render all characters
#   ./render_pipeline.sh --single         # Render just X Bot for testing
#   ./render_pipeline.sh --download-only  # Just download existing results

set -e  # Exit on any error

# Configuration
PROJECT_DIR="$HOME/projects/3D Pose Factory"
R2_REMOTE="r2_pose_factory:pose-factory"
POD_USER="root"
POD_HOST=""  # You'll need to fill this in each time (or we can make it interactive)
POD_KEY="$HOME/.ssh/id_ed25519"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
MODE="batch"
SKIP_UPLOAD=false
SKIP_RENDER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --single)
            MODE="single"
            shift
            ;;
        --download-only)
            SKIP_UPLOAD=true
            SKIP_RENDER=true
            shift
            ;;
        --pod)
            POD_HOST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get pod ID if not provided
if [ -z "$POD_HOST" ]; then
    echo -e "${YELLOW}Enter your RunPod ID (e.g., 6gpur3lb2h5pzi-6441128f):${NC}"
    read POD_HOST
fi

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  3D Pose Factory Render Pipeline      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Upload scripts to R2
if [ "$SKIP_UPLOAD" = false ]; then
    echo -e "${GREEN}[1/4] Uploading Blender scripts to R2...${NC}"
    cd "$PROJECT_DIR"
    rclone copy scripts/render_simple_working.py "$R2_REMOTE/scripts/" -v
    rclone copy scripts/blender_camera_utils.py "$R2_REMOTE/scripts/" -v
    echo -e "${GREEN}✓ Scripts uploaded${NC}"
    echo ""
fi

# Step 2: SSH to pod and execute render
if [ "$SKIP_RENDER" = false ]; then
    echo -e "${GREEN}[2/4] Connecting to RunPod and rendering...${NC}"
    
    if [ "$MODE" = "single" ]; then
        echo -e "${YELLOW}Mode: Single character test (X Bot only)${NC}"
        RENDER_CMD="cd /workspace/pose-factory && rclone copy $R2_REMOTE/scripts/ scripts/ && blender --background --python scripts/render_simple_working.py"
    else
        echo -e "${YELLOW}Mode: Batch render (all 6 characters)${NC}"
        RENDER_CMD="cd /workspace/pose-factory && rclone copy $R2_REMOTE/scripts/ scripts/ && blender --background --python scripts/render_simple_working.py -- --batch"
    fi
    
    # Execute on pod
    ssh -i "$POD_KEY" "$POD_USER@$POD_HOST@ssh.runpod.io" "$RENDER_CMD"
    
    echo -e "${GREEN}✓ Render complete${NC}"
    echo ""
    
    # Step 3: Upload results from pod to R2
    echo -e "${GREEN}[3/4] Uploading results from pod to R2...${NC}"
    ssh -i "$POD_KEY" "$POD_USER@$POD_HOST@ssh.runpod.io" \
        "cd /workspace/pose-factory && rclone copy output/simple_multi_angle/ $R2_REMOTE/output/simple_multi_angle/ --progress"
    echo -e "${GREEN}✓ Results uploaded to R2${NC}"
    echo ""
fi

# Step 4: Download results to Mac
echo -e "${GREEN}[4/4] Downloading results to Mac...${NC}"
cd "$PROJECT_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="data/working/renders_$TIMESTAMP"
mkdir -p "$OUTPUT_DIR"

rclone copy "$R2_REMOTE/output/simple_multi_angle/" "$OUTPUT_DIR/" --progress

echo -e "${GREEN}✓ Results downloaded${NC}"
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           PIPELINE COMPLETE!           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "Results saved to: ${YELLOW}$OUTPUT_DIR${NC}"
echo ""
echo "To view:"
echo -e "  ${BLUE}open \"$OUTPUT_DIR\"${NC}"
echo ""

# Optional: Open automatically
read -p "Open results folder now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "$OUTPUT_DIR"
fi


