#!/bin/bash

###############################################################################
# Upload Character Creation Scripts to R2
#
# Run this from your Mac to sync scripts to Cloudflare R2
# Then RunPod can download them
###############################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
R2_REMOTE="r2_pose_factory:pose-factory/character-creation"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Uploading to Cloudflare R2            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Upload Python scripts
echo -e "${BLUE}Uploading create_character.py...${NC}"
rclone copy "${SCRIPT_DIR}/create_character.py" "${R2_REMOTE}/scripts/" --progress

# Upload pod-side setup script
echo -e "${BLUE}Uploading setup_and_test_charmorph.sh...${NC}"
rclone copy "${SCRIPT_DIR}/setup_and_test_charmorph.sh" "${R2_REMOTE}/scripts/" --progress

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Upload Complete!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo -e "${BLUE}# 1. SSH to RunPod${NC}"
echo "ssh to6i4tul7p9hk2-644113d9@ssh.runpod.io -i ~/.ssh/id_ed25519"
echo ""
echo -e "${BLUE}# 2. On RunPod, run:${NC}"
echo "cd /workspace && rclone copy ${R2_REMOTE}/scripts/setup_and_test_charmorph.sh ./ && chmod +x setup_and_test_charmorph.sh && ./setup_and_test_charmorph.sh"
echo ""

