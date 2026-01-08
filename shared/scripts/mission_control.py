#!/usr/bin/env python3
"""
Mission Control - Unified command center for RunPod operations
Handles: upload → job dispatch → monitoring → download

USAGE (copy-paste ready):
    cd "${PROJECTS_ROOT}/3D Pose Factory"
    ./shared/scripts/mission_control.py render --wait

Examples:
    ./shared/scripts/mission_control.py render --characters "X Bot,Dancer" --wait
    ./shared/scripts/mission_control.py setup-pod
    ./shared/scripts/mission_control.py status
    ./shared/scripts/mission_control.py download --job JOB_ID

Note: No venv needed - uses system Python
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import uuid

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import DEFAULT_JOB_TIMEOUT

# Configuration
R2_REMOTE = "r2_pose_factory:pose-factory"
JOBS_PATH = "jobs"
RESULTS_PATH = "results"
SCRIPTS_PATH = "shared/scripts"

class MissionControl:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        
    def run_rclone(self, args, check=True):
        """Run rclone command and return result"""
        cmd = ["rclone"] + args
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result
    
    def upload_to_r2(self, local_path, r2_path, show_progress=True):
        """Upload file or directory to R2"""
        args = ["copy", str(local_path), f"{R2_REMOTE}/{r2_path}"]
        if show_progress:
            args.append("--progress")
        
        print(f"📤 Uploading {local_path} → R2/{r2_path}")
        result = self.run_rclone(args)
        if result.returncode == 0:
            print(f"✅ Upload complete")
        return result.returncode == 0
    
    def download_from_r2(self, r2_path, local_path, show_progress=True):
        """Download file or directory from R2"""
        args = ["copy", f"{R2_REMOTE}/{r2_path}", str(local_path)]
        if show_progress:
            args.append("--progress")
        
        print(f"📥 Downloading R2/{r2_path} → {local_path}")
        result = self.run_rclone(args)
        if result.returncode == 0:
            print(f"✅ Download complete: {local_path}")
        return result.returncode == 0
    
    def create_job(self, job_type, params):
        """Create a job manifest and upload to R2"""
        job_id = f"{job_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        manifest = {
            "job_id": job_id,
            "job_type": job_type,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "params": params
        }
        
        # Save manifest locally
        manifest_dir = self.project_root / "data" / "jobs"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = manifest_dir / f"{job_id}.json"
        
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"📋 Created job: {job_id}")
        
        # Upload to R2
        self.upload_to_r2(manifest_file, f"{JOBS_PATH}/pending/{job_id}.json", show_progress=False)
        
        return job_id, manifest_file
    
    def check_job_status(self, job_id):
        """Check if job has completed by looking for result in R2"""
        # Check if result exists
        result = self.run_rclone([
            "lsf", 
            f"{R2_REMOTE}/{RESULTS_PATH}/{job_id}/"
        ], check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            return "completed"
        
        # Check if job is still pending
        result = self.run_rclone([
            "lsf",
            f"{R2_REMOTE}/{JOBS_PATH}/pending/{job_id}.json"
        ], check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            return "pending"
        
        # Check if job is processing
        result = self.run_rclone([
            "lsf",
            f"{R2_REMOTE}/{JOBS_PATH}/processing/{job_id}.json"
        ], check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            return "processing"
        
        return "unknown"
    
    def wait_for_job(self, job_id, timeout=DEFAULT_JOB_TIMEOUT):
        """Wait for job to complete, showing progress"""
        print(f"⏳ Waiting for job {job_id} to complete...")
        print(f"   (Pod agent polls every 30 seconds)")
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout:
            status = self.check_job_status(job_id)
            
            if status != last_status:
                if status == "processing":
                    print(f"🔄 Job is now processing on pod...")
                elif status == "completed":
                    print(f"✅ Job completed!")
                    return True
                last_status = status
            
            if status == "completed":
                return True
            
            # Show a heartbeat every 30 seconds
            time.sleep(30)
            print(f"   ... still waiting ({int(time.time() - start_time)}s elapsed)")
        
        print(f"⚠️  Timeout waiting for job after {timeout}s")
        return False
    
    def cmd_render(self, args):
        """Handle render command"""
        # Prepare job parameters
        params = {
            "script": "pose-rendering/scripts/render_simple_working.py",
            "characters": args.characters.split(",") if args.characters else None,
            "output_dir": args.output or "output/simple_multi_angle"
        }
        
        # Upload necessary scripts
        print("📦 Preparing render job...")
        self.upload_to_r2(
            self.project_root / "pose-rendering" / "scripts",
            "pose-rendering/scripts",
            show_progress=False
        )
        
        # Create job
        job_id, manifest_file = self.create_job("render", params)
        
        # Wait for completion
        if args.wait:
            if self.wait_for_job(job_id):
                # Download results
                output_dir = self.project_root / "data" / "working" / args.output.replace("output/", "")
                self.download_from_r2(f"{RESULTS_PATH}/{job_id}/", output_dir)
            else:
                print(f"💡 Job may still be running. Check status with: ./mission_control.py status --job {job_id}")
        else:
            print(f"🚀 Job dispatched: {job_id}")
            print(f"   Check status: ./mission_control.py status --job {job_id}")
            print(f"   Download: ./mission_control.py download --job {job_id}")
    
    def cmd_setup_pod(self, args):
        """Upload and trigger pod setup"""
        print("🔧 Setting up pod...")
        
        # Upload shared scripts
        self.upload_to_r2(
            self.project_root / "shared" / "scripts",
            "shared/scripts"
        )
        
        print("\n✅ Setup scripts uploaded to R2")
        print("📌 Next steps:")
        print("   1. SSH to your pod: ssh YOUR_POD_ID@ssh.runpod.io -i ~/.ssh/id_ed25519")
        print("   2. Run: rclone copy r2_pose_factory:pose-factory/shared/scripts/ /workspace/scripts/ && cd /workspace && ./scripts/setup_pod.sh")
        print("   3. The pod agent will start automatically and begin polling for jobs")
    
    def cmd_status(self, args):
        """Check job status"""
        if args.job:
            status = self.check_job_status(args.job)
            print(f"Job {args.job}: {status}")
        else:
            # List all recent jobs
            manifest_dir = self.project_root / "data" / "jobs"
            if manifest_dir.exists():
                manifests = sorted(manifest_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                print(f"📋 Recent jobs (last 10):\n")
                for manifest_file in manifests[:10]:
                    with open(manifest_file) as f:
                        manifest = json.load(f)
                    status = self.check_job_status(manifest['job_id'])
                    print(f"   {manifest['job_id']}: {status} ({manifest['created_at']})")
    
    def cmd_download(self, args):
        """Download job results"""
        job_id = args.job
        
        # Check if completed
        status = self.check_job_status(job_id)
        if status != "completed":
            print(f"⚠️  Job {job_id} is not completed (status: {status})")
            if not args.force:
                print(f"   Use --force to download anyway")
                return
        
        # Download results
        output_dir = self.project_root / "data" / "working" / job_id
        self.download_from_r2(f"{RESULTS_PATH}/{job_id}/", output_dir)

def main():
    parser = argparse.ArgumentParser(description="Mission Control - RunPod orchestrator")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Render command
    render_parser = subparsers.add_parser('render', help='Submit render job')
    render_parser.add_argument('--characters', help='Comma-separated character names')
    render_parser.add_argument('--output', default='output/simple_multi_angle', help='Output directory')
    render_parser.add_argument('--wait', action='store_true', help='Wait for completion and auto-download')
    
    # Setup pod command
    setup_parser = subparsers.add_parser('setup-pod', help='Upload setup scripts to R2')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check job status')
    status_parser.add_argument('--job', help='Specific job ID')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download job results')
    download_parser.add_argument('--job', required=True, help='Job ID')
    download_parser.add_argument('--force', action='store_true', help='Download even if not completed')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    mc = MissionControl()
    
    if args.command == 'render':
        mc.cmd_render(args)
    elif args.command == 'setup-pod':
        mc.cmd_setup_pod(args)
    elif args.command == 'status':
        mc.cmd_status(args)
    elif args.command == 'download':
        mc.cmd_download(args)

if __name__ == '__main__':
    main()

