#!/bin/bash
###############################################################################
# Bootstrap Fresh RunPod - One-Time Setup
#
# This script ONLY sets up rclone so you can download setup_pod.sh
# Run this ONCE on a brand new pod, then run setup_pod.sh
#
# ⚠️  SECURITY NOTE: Before running, replace YOUR_R2_ACCESS_KEY and YOUR_R2_SECRET
#     with your actual Cloudflare R2 credentials.
#
# Usage (after editing credentials):
#   Copy-paste entire script into fresh pod terminal
###############################################################################

echo "🔧 Bootstrapping rclone config..."

# Store in /workspace for persistence
mkdir -p /workspace/.config/rclone
mkdir -p ~/.config/rclone

cat > /workspace/.config/rclone/rclone.conf << 'EOF'
[r2_pose_factory]
type = s3
provider = Other
access_key_id = YOUR_R2_ACCESS_KEY_HERE
secret_access_key = YOUR_R2_SECRET_KEY_HERE
endpoint = YOUR_R2_ENDPOINT_HERE
acl = private
no_check_bucket = true
EOF

# Symlink to standard location
ln -sf /workspace/.config/rclone/rclone.conf ~/.config/rclone/rclone.conf

echo "✅ rclone configured!"
echo ""
echo "Test it:"
echo "  rclone lsd r2_pose_factory:pose-factory"
echo ""
echo "Now download and run full setup:"
echo "  cd /workspace"
echo "  rclone copy r2_pose_factory:pose-factory/shared/scripts/setup_pod.sh /workspace/scripts/"
echo "  chmod +x scripts/setup_pod.sh"
echo "  rclone copy r2_pose_factory:pose-factory/shared/.env /workspace/"
echo "  ./scripts/setup_pod.sh"
echo ""

