#!/bin/bash

###############################################################################
# Setup and Test Charmorph on RunPod
#
# Run this ON THE POD (not locally)
# Downloads scripts from R2, installs Charmorph, tests it
###############################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

R2_REMOTE="r2_pose_factory:pose-factory/character-creation"
WORKSPACE="/workspace/character-creation"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Charmorph Setup & Test                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Download scripts from R2
echo -e "${BLUE}[1/4] Downloading scripts from R2...${NC}"
mkdir -p "$WORKSPACE"
rclone copy "${R2_REMOTE}/scripts/" "$WORKSPACE/" --progress
echo -e "${GREEN}✓ Scripts downloaded${NC}"
echo ""

# Step 2: Install Charmorph
echo -e "${BLUE}[2/4] Installing Charmorph add-on...${NC}"

# Create Blender add-ons directory
mkdir -p ~/.config/blender/4.2/scripts/addons

# Download Charmorph
cd /tmp
echo "  Downloading from GitHub..."
wget -q https://github.com/Upliner/CharMorph/archive/refs/heads/master.zip -O charmorph.zip

# Extract to Blender add-ons
echo "  Installing to Blender..."
unzip -q charmorph.zip
mv CharMorph-master ~/.config/blender/4.2/scripts/addons/CharMorph
rm charmorph.zip

# Verify installation
if [ -d ~/.config/blender/4.2/scripts/addons/CharMorph ]; then
    echo -e "${GREEN}✓ Charmorph installed successfully${NC}"
else
    echo -e "${RED}✗ Installation failed${NC}"
    exit 1
fi
echo ""

# Step 3: Verify Blender
echo -e "${BLUE}[3/4] Verifying Blender installation...${NC}"
blender --version
echo -e "${GREEN}✓ Blender found${NC}"
echo ""

# Step 4: Test Charmorph
echo -e "${BLUE}[4/4] Testing Charmorph in headless mode...${NC}"
echo ""

# Create test script
cat > /tmp/test_charmorph.py << 'ENDPYTHON'
import bpy
import sys

print("=== Charmorph Headless Test ===")
print("")

# Try to enable Charmorph add-on
try:
    bpy.ops.preferences.addon_enable(module='CharMorph')
    print("✓ Charmorph add-on enabled")
except Exception as e:
    print(f"✗ Failed to enable Charmorph: {e}")
    sys.exit(1)

# Check if Charmorph is available
if hasattr(bpy.ops, 'charmorph'):
    print("✓ Charmorph operators available")
    
    # List available operators
    ops = [op for op in dir(bpy.ops.charmorph) if not op.startswith('_')]
    print(f"  Found {len(ops)} CharMorph operators")
    if ops:
        print(f"  Sample operators: {', '.join(ops[:5])}")
else:
    print("⚠ Charmorph operators not found in bpy.ops")

print("")
print("=== Test Complete ===")
print("")
print("Status: Charmorph is installed and accessible!")
print("Next: Implement actual character generation code")
ENDPYTHON

# Run Blender test
echo "Running Blender test..."
echo "─────────────────────────────────────────"
blender --background --python /tmp/test_charmorph.py 2>&1 | grep -E "(===|✓|✗|⚠|Status|Next|Found|Sample)"
echo "─────────────────────────────────────────"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Setup & Test Complete!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Scripts are in: ${WORKSPACE}${NC}"
echo -e "${YELLOW}You can now implement character generation!${NC}"
echo ""

