#!/bin/bash

###############################################################################
# Charmorph Test Script
#
# Tests if Charmorph works in headless Blender
# Uses saved POD_ID from setup_charmorph.sh
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
SSH_KEY="$HOME/.ssh/id_ed25519"
SSH_PORT="${RUNPOD_SSH_PORT:-22}"

# Get POD_ID from saved file
if [ ! -f "$POD_ID_FILE" ]; then
    echo -e "${RED}ERROR: No saved POD_ID found.${NC}"
    echo -e "${YELLOW}Run ./setup_charmorph.sh first${NC}"
    exit 1
fi

POD_ID=$(cat "$POD_ID_FILE")
echo -e "${GREEN}✓ Using POD_ID: ${POD_ID}${NC}"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Testing Charmorph in Blender          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Create test script
TEST_SCRIPT=$(cat << 'ENDPYTHON'
import bpy
import sys

print("=== Charmorph Headless Test ===")

# Try to enable Charmorph add-on
try:
    bpy.ops.preferences.addon_enable(module='CharMorph')
    print("✓ Charmorph add-on enabled")
except Exception as e:
    print(f"✗ Failed to enable Charmorph: {e}")
    sys.exit(1)

# Check if Charmorph is available
if 'CharMorph' in dir(bpy.ops):
    print("✓ Charmorph operators available")
else:
    print("⚠ Charmorph operators not found")
    print("Available ops:", [x for x in dir(bpy.ops) if not x.startswith('_')])

print("")
print("=== Test Complete ===")
print("Next: Implement actual character generation")
ENDPYTHON
)

# SSH and run test
echo -e "${BLUE}Running test on pod...${NC}"
echo ""
echo "=== Blender Test Output ==="

# Execute everything in one SSH command
ssh -i "$SSH_KEY" ${POD_ID}@ssh.runpod.io bash -s 2>&1 << 'ENDSSH' | grep -v "PTY"
# Create test script on remote
cat > /tmp/test_charmorph.py << 'ENDPYTHON'
import bpy
import sys

print("=== Charmorph Headless Test ===")

# Try to enable Charmorph add-on
try:
    bpy.ops.preferences.addon_enable(module='CharMorph')
    print("✓ Charmorph add-on enabled")
except Exception as e:
    print(f"✗ Failed to enable Charmorph: {e}")
    sys.exit(1)

# Check if Charmorph is available
if 'CharMorph' in dir(bpy.ops):
    print("✓ Charmorph operators available")
else:
    print("⚠ Charmorph operators not found")
    print("Available ops:", [x for x in dir(bpy.ops) if not x.startswith('_')])

print("")
print("=== Test Complete ===")
print("Next: Implement actual character generation")
ENDPYTHON

# Run Blender with the test script
blender --background --python /tmp/test_charmorph.py 2>&1
ENDSSH

echo "==========================="
echo ""

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Test Complete!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

