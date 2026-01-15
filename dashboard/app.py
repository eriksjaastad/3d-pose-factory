#!/usr/bin/env python3
r"""
Mission Control Dashboard - Flask Backend
Provides web UI for managing RunPod jobs

USAGE (copy-paste ready):
    cd "${PROJECTS_ROOT}/3d-pose-factory/dashboard"
    source venv/bin/activate
    python3 app.py

First time setup:
    cd "${PROJECTS_ROOT}/3d-pose-factory/dashboard"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python3 app.py

Opens browser to: http://localhost:5001
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import subprocess
import json
from pathlib import Path
from datetime import datetime
import uuid
import sys
import webbrowser
import threading
import os
import time
from dotenv import load_dotenv
import runpod

# Import shared utilities
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))
from utils import get_env_var, safe_slug

# Load environment variables
load_dotenv()

# Configure RunPod
runpod.api_key = get_env_var('RUNPOD_API_KEY')

# Add parent directory to path to import mission_control and cost_calculator
sys.path.insert(0, str(Path(__file__).parent.parent / "shared" / "scripts"))

from cost_calculator import CostCalculator

app = Flask(__name__)
CORS(app)

# Initialize cost calculator
cost_calc = CostCalculator()

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
R2_REMOTE = "r2_pose_factory:pose-factory"
JOBS_PATH = "jobs"
RESULTS_PATH = "results"

def run_rclone(args):
    """Run rclone command and return result"""
    cmd = ["rclone"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def get_job_status(job_id):
    """Check job status in R2"""
    # Check if result exists
    result = run_rclone(["lsf", f"{R2_REMOTE}/{RESULTS_PATH}/{job_id}/"])
    if result.returncode == 0 and result.stdout.strip():
        return "completed"
    
    # Check if pending
    result = run_rclone(["lsf", f"{R2_REMOTE}/{JOBS_PATH}/pending/{job_id}.json"])
    if result.returncode == 0 and result.stdout.strip():
        return "pending"
    
    # Check if processing
    result = run_rclone(["lsf", f"{R2_REMOTE}/{JOBS_PATH}/processing/{job_id}.json"])
    if result.returncode == 0 and result.stdout.strip():
        return "processing"
    
    return "unknown"

def list_local_jobs():
    """List all jobs from local manifest directory"""
    manifest_dir = PROJECT_ROOT / "data" / "jobs"
    if not manifest_dir.exists():
        return []
    
    jobs = []
    for manifest_file in sorted(manifest_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            with open(manifest_file) as f:
                manifest = json.load(f)
            
            # Get current status from R2
            status = get_job_status(manifest['job_id'])
            manifest['status'] = status
            
            jobs.append(manifest)
        except Exception as e:
            print(f"Error reading {manifest_file}: {e}")
            continue
    
    return jobs

def upload_to_r2(local_path, r2_path):
    """Upload file or directory to R2"""
    result = run_rclone(["copy", str(local_path), f"{R2_REMOTE}/{r2_path}"])
    return result.returncode == 0

def create_job(job_type, params):
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
    manifest_dir = PROJECT_ROOT / "data" / "jobs"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = manifest_dir / f"{job_id}.json"
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Upload to R2
    upload_to_r2(manifest_file, f"{JOBS_PATH}/pending/{job_id}.json")
    
    return job_id, manifest

# Routes

@app.route('/')
def index():
    """Render dashboard UI"""
    return render_template('index.html')

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get list of all jobs"""
    jobs = list_local_jobs()
    return jsonify(jobs)

@app.route('/api/jobs', methods=['POST'])
def submit_job():
    """Submit a new job"""
    data = request.json
    
    job_type = data.get('job_type', 'render')
    
    if job_type == 'render':
        # Upload scripts first
        upload_to_r2(
            PROJECT_ROOT / "pose-rendering" / "scripts",
            "pose-rendering/scripts"
        )
        
        params = {
            "script": "pose-rendering/scripts/render_simple_working.py",
            "characters": data.get('characters', []),
            "output_dir": data.get('output_dir', 'output/simple_multi_angle')
        }
    else:
        return jsonify({"error": f"Unknown job type: {job_type}"}), 400
    
    job_id, manifest = create_job(job_type, params)
    
    return jsonify({
        "success": True,
        "job_id": job_id,
        "manifest": manifest
    })

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get details for a specific job"""
    # DNA Fix: Sanitize input to prevent path traversal
    job_id = safe_slug(job_id)
    manifest_file = PROJECT_ROOT / "data" / "jobs" / f"{job_id}.json"
    
    if not manifest_file.exists():
        return jsonify({"error": "Job not found"}), 404
    
    with open(manifest_file) as f:
        manifest = json.load(f)
    
    # Get current status
    manifest['status'] = get_job_status(job_id)
    
    return jsonify(manifest)

@app.route('/api/jobs/<job_id>/download', methods=['POST'])
def download_job(job_id):
    """Download job results from R2"""
    # DNA Fix: Sanitize input to prevent path traversal
    job_id = safe_slug(job_id)
    # Check if completed
    status = get_job_status(job_id)
    if status != "completed":
        return jsonify({"error": f"Job not completed (status: {status})"}), 400
    
    # Download results
    output_dir = PROJECT_ROOT / "data" / "working" / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    result = run_rclone(["copy", f"{R2_REMOTE}/{RESULTS_PATH}/{job_id}/", str(output_dir), "--progress"])
    
    if result.returncode == 0:
        return jsonify({
            "success": True,
            "path": str(output_dir)
        })
    else:
        return jsonify({"error": "Download failed"}), 500

@app.route('/api/pod/status', methods=['GET'])
def get_pod_status():
    """Get pod agent status (check for recent activity in R2)"""
    # For now, just return a placeholder
    # We could enhance this by having the pod agent write a heartbeat file to R2
    return jsonify({
        "agent_running": "unknown",
        "last_poll": "unknown",
        "note": "Pod heartbeat monitoring coming in Phase 2"
    })

@app.route('/api/pod/id', methods=['GET'])
def get_pod_id():
    """Get saved Pod ID"""
    pod_id_file = PROJECT_ROOT / ".pod_id"
    if pod_id_file.exists():
        with open(pod_id_file) as f:
            pod_id = f.read().strip()
        return jsonify({"pod_id": pod_id})
    return jsonify({"pod_id": None})

@app.route('/api/pod/id', methods=['POST'])
def save_pod_id():
    """Save Pod ID"""
    data = request.json
    pod_id = data.get('pod_id', '').strip()
    
    if not pod_id:
        return jsonify({"error": "Pod ID required"}), 400
    
    # Save to file
    pod_id_file = PROJECT_ROOT / ".pod_id"
    with open(pod_id_file, 'w') as f:
        f.write(pod_id)
    
    return jsonify({
        "success": True,
        "pod_id": pod_id
    })

@app.route('/api/pod/start', methods=['POST'])
def start_pod():
    """Start a new RunPod instance"""
    try:
        # Create pod with our custom setup
        pod = runpod.create_pod(
            name="3d-pose-factory",
            image_name="runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
            gpu_type_id="NVIDIA A40",
            cloud_type="SECURE",
            # Note: Setup must be run manually via SSH after pod starts
            # SSH in and run: rclone copy r2_pose_factory:pose-factory/shared/scripts/setup_pod.sh /workspace/scripts/ && cd /workspace && ./scripts/setup_pod.sh
            container_disk_in_gb=50,
            volume_in_gb=100,
            ports="22/tcp"
        )
        
        # Save pod ID
        pod_id = pod['id']
        pod_id_file = PROJECT_ROOT / ".pod_id"
        with open(pod_id_file, 'w') as f:
            f.write(pod_id)
        
        return jsonify({
            "success": True,
            "pod_id": pod_id,
            "status": "starting",
            "message": "Pod is starting. Agent will auto-start in ~2 minutes."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pod/stop', methods=['POST'])
def stop_pod():
    """Stop the current RunPod instance"""
    try:
        pod_id_file = PROJECT_ROOT / ".pod_id"
        if not pod_id_file.exists():
            return jsonify({"error": "No pod ID found"}), 404
        
        with open(pod_id_file) as f:
            pod_id = f.read().strip()
        
        runpod.stop_pod(pod_id)
        
        return jsonify({
            "success": True,
            "message": "Pod stopped successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pod/current', methods=['GET'])
def get_current_pod():
    """Get current pod status from RunPod API"""
    try:
        pod_id_file = PROJECT_ROOT / ".pod_id"
        if not pod_id_file.exists():
            return jsonify({"pod": None})
        
        with open(pod_id_file) as f:
            pod_id = f.read().strip()
        
        pod = runpod.get_pod(pod_id)
        
        # Get actual cost per hour from pod data
        cost_per_hr = pod.get('costPerHr', 0.42)  # Fallback to 0.42 if not available
        
        return jsonify({
            "pod": {
                "id": pod['id'],
                "name": pod.get('name'),
                "status": pod.get('desiredStatus'),
                "gpu": pod.get('gpuCount'),
                "runtime": pod.get('runtime', {}),
                "cost_per_hr": cost_per_hr
            }
        })
    except Exception as e:
        return jsonify({"pod": None, "error": str(e)})

@app.route('/api/gpu/pricing', methods=['GET'])
def get_gpu_pricing():
    """Get GPU pricing from RunPod API"""
    try:
        # Query RunPod for available GPUs and pricing
        gpus = runpod.get_gpus()
        
        # Find A40 pricing
        a40_pricing = None
        for gpu in gpus:
            if 'A40' in gpu.get('displayName', ''):
                a40_pricing = {
                    "name": gpu.get('displayName'),
                    "cost_per_hr": gpu.get('securePrice', 0.42),
                    "available": gpu.get('secureCount', 0) > 0
                }
                break
        
        return jsonify({
            "a40": a40_pricing,
            "all_gpus": gpus if a40_pricing is None else None
        })
    except Exception as e:
        return jsonify({"error": str(e), "fallback": 0.42})

# Cost Calculator API Endpoints

@app.route('/api/cost/providers', methods=['GET'])
def get_cost_providers():
    """Get list of available rendering providers"""
    try:
        providers = cost_calc.list_providers()
        return jsonify({"providers": providers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cost/resolutions', methods=['GET'])
def get_cost_resolutions():
    """Get available resolutions for a provider"""
    provider = request.args.get('provider', 'stability')
    try:
        resolutions = cost_calc.get_resolutions(provider)
        return jsonify({"resolutions": resolutions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cost/models', methods=['GET'])
def get_cost_models():
    """Get available models for a provider"""
    provider = request.args.get('provider', 'stability')
    try:
        models = cost_calc.get_models(provider)
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cost/estimate', methods=['POST'])
def estimate_cost():
    """Estimate cost for a rendering job"""
    try:
        data = request.json
        
        provider = data.get('provider', 'local')
        resolution = data.get('resolution', '512x512')
        steps = data.get('steps', 30)
        model = data.get('model', 'sd_1_5')
        count = data.get('count', 1)
        
        # Calculate cost
        cost = cost_calc.estimate_cost(
            provider=provider,
            resolution=resolution,
            steps=steps,
            model=model,
            count=count
        )
        
        # Validate cost
        is_safe, message = cost_calc.validate_cost(cost['total'])
        
        return jsonify({
            "success": True,
            "cost": cost,
            "validation": {
                "is_safe": is_safe,
                "message": message
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)  # Wait for Flask to start
    webbrowser.open('http://localhost:5001')

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 Mission Control Dashboard")
    print("=" * 60)
    print()
    print("Dashboard running at: http://localhost:5001")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Track if we've already opened the browser using a temp file
    browser_flag = Path("/tmp/mission_control_browser_opened")
    
    # Open browser ONLY on first start (not on auto-reload)
    # In debug mode, Flask spawns a reloader process with WERKZEUG_RUN_MAIN="true"
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        if not browser_flag.exists():
            print("Opening browser...")
            browser_flag.touch()
            threading.Thread(target=open_browser, daemon=True).start()
        else:
            print("Browser already open (use http://localhost:5001)")
    
    # Clean up flag on exit
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    finally:
        if browser_flag.exists():
            browser_flag.unlink()

