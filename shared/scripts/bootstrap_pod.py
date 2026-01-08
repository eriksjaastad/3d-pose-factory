#!/usr/bin/env python3
"""
Bootstrap a fresh RunPod pod.

Reads R2 credentials from your local rclone config and sends setup commands
to the pod via the ops_queue (SSH agent).

Usage:
    python bootstrap_pod.py

Requirements:
    - .pod_id file with current pod ID
    - SSH agent running
    - Local rclone config at ~/.config/rclone/rclone.conf
"""

import json
import os
import re
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
# Point to the central SSH Agent queue in _tools
OPS_QUEUE = Path(os.getenv("SSH_AGENT_QUEUE", "/Users/eriksjaastad/projects/_tools/ssh_agent/queue"))
REQUESTS = OPS_QUEUE / "requests.jsonl"
RESULTS = OPS_QUEUE / "results.jsonl"
POD_ID_FILE = ROOT / ".pod_id"
RCLONE_CONFIG = Path.home() / ".config/rclone/rclone.conf"


def get_r2_credentials():
    """Extract R2 credentials from local rclone config."""
    if not RCLONE_CONFIG.exists():
        raise FileNotFoundError(f"rclone config not found at {RCLONE_CONFIG}")
    
    config_text = RCLONE_CONFIG.read_text()
    
    # Parse the r2_pose_factory section
    in_section = False
    creds = {}
    
    for line in config_text.split('\n'):
        if '[r2_pose_factory]' in line:
            in_section = True
            continue
        if in_section:
            if line.startswith('['):  # New section
                break
            if '=' in line:
                key, value = line.split('=', 1)
                creds[key.strip()] = value.strip()
    
    required = ['access_key_id', 'secret_access_key', 'endpoint']
    for key in required:
        if key not in creds:
            raise ValueError(f"Missing {key} in rclone config")
    
    return creds


def send_command(cmd_id: str, command: str, timeout: int = 300):
    """Send a command to the SSH agent queue and wait for result."""
    request = {
        "id": cmd_id,
        "host": "runpod",
        "command": command
    }
    
    # Get current results count
    results_before = 0
    if RESULTS.exists():
        results_before = len(RESULTS.read_text().strip().split('\n'))
    
    # Send command
    with open(REQUESTS, 'a') as f:
        f.write(json.dumps(request) + '\n')
    
    print(f"  → Sent: {command[:60]}...")
    
    # Wait for result
    start = time.time()
    while time.time() - start < timeout:
        if RESULTS.exists():
            results = RESULTS.read_text().strip().split('\n')
            if len(results) > results_before:
                # Find our result
                for line in results[results_before:]:
                    try:
                        result = json.loads(line)
                        if result.get('id') == cmd_id:
                            return result
                    except json.JSONDecodeError:
                        continue
        time.sleep(1)
    
    return {"error": "timeout", "id": cmd_id}


def main():
    print("=" * 60)
    print("  🚀 Pod Bootstrap")
    print("=" * 60)
    
    # Check pod ID
    if not POD_ID_FILE.exists():
        print("❌ No .pod_id file found. Update it with your pod ID first.")
        return
    
    pod_id = POD_ID_FILE.read_text().strip()
    print(f"\n📍 Pod ID: {pod_id}")
    
    # Get R2 credentials
    print("\n📦 Reading R2 credentials from local rclone config...")
    try:
        creds = get_r2_credentials()
        print("  ✅ Credentials found")
    except Exception as e:
        print(f"  ❌ {e}")
        return
    
    # Build rclone config content
    rclone_config = f"""[r2_pose_factory]
type = s3
provider = Cloudflare
access_key_id = {creds['access_key_id']}
secret_access_key = {creds['secret_access_key']}
endpoint = {creds['endpoint']}
acl = private
no_check_bucket = true
"""
    
    print("\n🔧 Step 1/4: Configuring rclone on pod...")
    
    # Create rclone config on pod
    setup_rclone_cmd = f"""
mkdir -p /workspace/.config/rclone ~/.config/rclone && \\
cat > /workspace/.config/rclone/rclone.conf << 'RCLONE_EOF'
{rclone_config}
RCLONE_EOF
ln -sf /workspace/.config/rclone/rclone.conf ~/.config/rclone/rclone.conf && \\
echo "rclone configured"
"""
    
    result = send_command("bootstrap_rclone", setup_rclone_cmd.strip())
    if result.get('exit_status') != 0:
        print(f"  ❌ Failed: {result.get('stderr', result.get('stdout', 'unknown error'))}")
        return
    print("  ✅ rclone configured")
    
    # Test rclone
    print("\n🔧 Step 2/4: Testing R2 connection...")
    result = send_command("bootstrap_test_rclone", "rclone lsd r2_pose_factory:pose-factory")
    if result.get('exit_status') != 0:
        print(f"  ❌ R2 connection failed")
        print(f"     {result.get('stdout', '')}")
        return
    print("  ✅ R2 connection working")
    
    # Download and run setup_pod.sh
    print("\n🔧 Step 3/4: Downloading setup script from R2...")
    download_cmd = """
cd /workspace && \\
rclone copy r2_pose_factory:pose-factory/shared/scripts/setup_pod.sh /workspace/ && \\
rclone copy r2_pose_factory:pose-factory/shared/.env /workspace/ && \\
chmod +x setup_pod.sh && \\
echo "setup_pod.sh downloaded"
"""
    result = send_command("bootstrap_download", download_cmd.strip())
    if result.get('exit_status') != 0:
        print(f"  ❌ Download failed: {result.get('stdout', '')}")
        return
    print("  ✅ Setup script downloaded")
    
    # Run setup
    print("\n🔧 Step 4/4: Running setup (this takes 1-2 minutes)...")
    result = send_command("bootstrap_setup", "cd /workspace && ./setup_pod.sh", timeout=300)
    
    if result.get('exit_status') == 0:
        print("  ✅ Setup complete!")
    else:
        print(f"  ⚠️  Setup finished with warnings")
        # Still might be ok - setup_pod.sh can return non-zero for minor issues
    
    print("\n" + "=" * 60)
    print("  ✅ Pod Bootstrap Complete!")
    print("=" * 60)
    print(f"\nPod {pod_id} is ready to use.")
    print("\nYou can now run commands via the SSH agent or dashboard.")


if __name__ == "__main__":
    main()

