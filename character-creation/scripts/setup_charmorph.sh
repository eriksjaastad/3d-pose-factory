#!/bin/bash

###############################################################################
# Charmorph Setup Script
#
# Installs Charmorph add-on in Blender on RunPod
# Saves POD_ID for future script use
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Config
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
POD_ID_FILE="${SCRIPT_DIR}/.pod_id"
SSH_KEY="$HOME/.ssh/id_ed25519_runpod"
SSH_PORT="${RUNPOD_SSH_PORT:-22}"

# Get POD_ID (from file, env var, or prompt)
POD_ID=""

if [ "$1" == "--new-pod" ] || [ ! -f "$POD_ID_FILE" ]; then
    # Prompt for new POD_ID
    if [ -n "$RUNPOD_POD_ID" ]; then
        POD_ID="$RUNPOD_POD_ID"
        echo -e "${GREEN}Using POD_ID from environment: ${POD_ID}${NC}"
    else
        echo -e "${YELLOW}Enter your RunPod ID (e.g., 6gpur3lb2h5pzi-6441128f):${NC}"
        read POD_ID
    fi
    
    if [ -z "$POD_ID" ]; then
        echo -e "${RED}ERROR: POD_ID is required${NC}"
        exit 1
    fi
    
    # Save for future use
    echo "$POD_ID" > "$POD_ID_FILE"
    echo -e "${GREEN}✓ Saved POD_ID to ${POD_ID_FILE}${NC}"
else
    # Read from file
    POD_ID=$(cat "$POD_ID_FILE")
    echo -e "${GREEN}✓ Using saved POD_ID: ${POD_ID}${NC}"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Charmorph Setup for RunPod            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# SSH and install Charmorph
echo -e "${BLUE}Connecting to pod and installing Charmorph...${NC}"

ssh -i "$SSH_KEY" root@${POD_ID}-ssh.runpod.io -p $SSH_PORT << 'ENDSSH'
set -e

echo "=== Installing Charmorph Add-on ==="

# Create Blender add-ons directory
mkdir -p ~/.config/blender/4.2/scripts/addons

# Download Charmorph
cd /tmp
echo "Downloading Charmorph..."
wget -q https://github.com/Upliner/CharMorph/archive/refs/heads/master.zip -O charmorph.zip

# Extract to Blender add-ons
echo "Installing to Blender..."
unzip -q charmorph.zip
mv CharMorph-master ~/.config/blender/4.2/scripts/addons/CharMorph
rm charmorph.zip

# Verify installation
if [ -d ~/.config/blender/4.2/scripts/addons/CharMorph ]; then
    echo "✓ Charmorph installed successfully"
else
    echo "✗ Installation failed"
    exit 1
fi

# Test Blender can see the add-on
echo ""
echo "=== Verifying Blender Installation ==="
blender --version
echo ""
echo "✓ Setup complete!"

ENDSSH

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Charmorph Setup Complete!          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next step: Run ./test_charmorph.sh to verify it works${NC}"
echo ""

