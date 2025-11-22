#!/bin/bash

###############################################################################
# Character Creation Pipeline - Automation Script
#
# This script automates the full character creation workflow:
# 1. Upload scripts to R2
# 2. SSH to RunPod and run character creation
# 3. Download generated characters
#
# Status: 🚧 Template - Not yet functional
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Configuration ---
LOCAL_PROJECT_DIR="/Users/eriksjaastad/projects/3D Pose Factory/character-creation"
R2_REMOTE="r2_pose_factory:pose-factory/character-creation"
POD_WORKSPACE="/workspace/pose-factory/character-creation"
SSH_KEY="~/.ssh/id_ed25519_runpod"
CREATE_SCRIPT="create_character.py"

# RunPod connection (must be set by user or detected)
POD_ID="${RUNPOD_POD_ID:-}"
SSH_PORT="${RUNPOD_SSH_PORT:-22}"

# --- Helper Functions ---
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

exit_on_error() {
    echo -e "${RED}ERROR: $1${NC}"
    exit 1
}

check_pod_connection() {
    if [ -z "$POD_ID" ]; then
        exit_on_error "RUNPOD_POD_ID not set. Please set it or pass --pod-id"
    fi
    echo -e "${GREEN}✓ Pod ID: ${POD_ID}${NC}"
}

# --- Main Functions ---
upload_scripts() {
    echo -e "${BLUE}Uploading character creation scripts to R2...${NC}"
    
    rclone copy "${LOCAL_PROJECT_DIR}/scripts/${CREATE_SCRIPT}" \
        "${R2_REMOTE}/scripts/" --progress || exit_on_error "Failed to upload scripts."
    
    echo -e "${GREEN}✓ Scripts uploaded to R2.${NC}"
}

ssh_and_create() {
    local description="$1"
    
    print_header "Connecting to RunPod and creating character"
    
    ssh_command="ssh -i ${SSH_KEY} root@${POD_ID}-ssh.runpod.io -p ${SSH_PORT} \"
        mkdir -p ${POD_WORKSPACE} &&
        cd ${POD_WORKSPACE} &&
        rclone copy ${R2_REMOTE}/scripts/${CREATE_SCRIPT} ./ --progress &&
        blender --background --python ./${CREATE_SCRIPT} -- --description '${description}' &&
        rclone copy ${POD_WORKSPACE}/characters/ ${R2_REMOTE}/output/characters/ --progress
    \""
    
    eval "${ssh_command}" || exit_on_error "Character creation failed on pod."
    
    echo -e "${GREEN}✓ Character created and uploaded to R2.${NC}"
}

download_characters() {
    echo -e "${BLUE}Downloading characters from R2...${NC}"
    
    TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
    LOCAL_OUTPUT_DIR="${LOCAL_PROJECT_DIR}/data/working/characters_${TIMESTAMP}"
    
    mkdir -p "${LOCAL_OUTPUT_DIR}" || exit_on_error "Failed to create output directory."
    
    rclone copy "${R2_REMOTE}/output/characters/" \
        "${LOCAL_OUTPUT_DIR}/" --progress || exit_on_error "Failed to download characters."
    
    echo -e "${GREEN}✓ Characters downloaded to ${LOCAL_OUTPUT_DIR}${NC}"
    
    # Offer to open folder
    read -p "Open output folder? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "${LOCAL_OUTPUT_DIR}"
    fi
}

show_usage() {
    cat << EOF
${BLUE}Character Creation Pipeline${NC}

Usage:
  $0 --create "description"    Create character with AI
  $0 --download-only           Only download existing characters
  $0 --help                    Show this help

Examples:
  $0 --create "athletic woman, age 25, brown hair"
  $0 --create "elderly man, tall, gray beard"
  $0 --download-only

Environment:
  RUNPOD_POD_ID     - Your RunPod instance ID
  RUNPOD_SSH_PORT   - SSH port (default: 22)

EOF
}

# --- Argument Parsing ---
CREATE_MODE=false
DOWNLOAD_ONLY=false
CHARACTER_DESCRIPTION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --create)
            CREATE_MODE=true
            CHARACTER_DESCRIPTION="$2"
            shift 2
            ;;
        --download-only)
            DOWNLOAD_ONLY=true
            shift
            ;;
        --pod-id)
            POD_ID="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# --- Main Execution ---
print_header "Character Creation Pipeline"

if [ "$DOWNLOAD_ONLY" = true ]; then
    download_characters
elif [ "$CREATE_MODE" = true ]; then
    if [ -z "$CHARACTER_DESCRIPTION" ]; then
        exit_on_error "Character description required. Use --create \"description\""
    fi
    
    check_pod_connection
    upload_scripts
    ssh_and_create "$CHARACTER_DESCRIPTION"
    download_characters
else
    show_usage
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Pipeline complete!${NC}"
echo -e "${GREEN}========================================${NC}"

