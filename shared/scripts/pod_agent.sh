#!/bin/bash
###############################################################################
# Pod Agent - RunPod-side job executor
# 
# This script runs continuously on the pod, polling R2 for new jobs.
# When a job is found:
#   1. Download job manifest
#   2. Move to "processing"
#   3. Execute the job
#   4. Upload results
#   5. Mark as complete
#
# Usage:
#   ./pod_agent.sh          # Run in foreground (for testing)
#   ./pod_agent.sh &        # Run in background
#   nohup ./pod_agent.sh &  # Run in background, persist after logout
###############################################################################

set -e

# Configuration
R2_REMOTE="r2_pose_factory:pose-factory"
JOBS_PENDING="jobs/pending"
JOBS_PROCESSING="jobs/processing"
RESULTS="results"
POLL_INTERVAL=30
WORKSPACE="/workspace"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ✅ $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ❌ $1"
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ⚠️  $1"
}

# Check if rclone is configured
check_rclone() {
    if ! rclone lsd "$R2_REMOTE" &>/dev/null; then
        log_error "rclone not configured for $R2_REMOTE"
        log "Please configure rclone with: rclone config"
        exit 1
    fi
}

# Find pending jobs in R2
find_pending_jobs() {
    rclone lsf "$R2_REMOTE/$JOBS_PENDING/" 2>/dev/null || echo ""
}

# Download job manifest
download_job() {
    local job_file="$1"
    local local_path="$WORKSPACE/jobs/pending/$job_file"
    
    mkdir -p "$WORKSPACE/jobs/pending"
    rclone copy "$R2_REMOTE/$JOBS_PENDING/$job_file" "$WORKSPACE/jobs/pending/" --progress
    
    echo "$local_path"
}

# Move job to processing
move_to_processing() {
    local job_file="$1"
    
    rclone move "$R2_REMOTE/$JOBS_PENDING/$job_file" "$R2_REMOTE/$JOBS_PROCESSING/" 2>/dev/null || true
}

# Execute render job
execute_render_job() {
    local manifest_file="$1"
    local job_id="$2"
    
    # Parse manifest
    local script=$(jq -r '.params.script' "$manifest_file")
    local characters=$(jq -r '.params.characters // [] | join(",")' "$manifest_file")
    local output_dir=$(jq -r '.params.output_dir' "$manifest_file")
    
    log "Executing render job:"
    log "  Script: $script"
    log "  Characters: ${characters:-all}"
    log "  Output: $output_dir"
    
    # Download script if needed
    local script_dir=$(dirname "$script")
    mkdir -p "$WORKSPACE/$script_dir"
    rclone copy "$R2_REMOTE/$script_dir/" "$WORKSPACE/$script_dir/" --progress
    
    # Download FBX files
    mkdir -p "$WORKSPACE/downloads"
    if [ ! "$(ls -A $WORKSPACE/downloads/*.fbx 2>/dev/null)" ]; then
        log "Downloading FBX files..."
        rclone copy "$R2_REMOTE/downloads/" "$WORKSPACE/downloads/" --include "*.fbx" --progress
    fi
    
    # Run the render script
    cd "$WORKSPACE"
    
    if [ -n "$characters" ]; then
        blender --background --python "$WORKSPACE/$script" -- --characters "$characters" --output "$output_dir"
    else
        blender --background --python "$WORKSPACE/$script" -- --output "$output_dir"
    fi
    
    # Upload results
    log "Uploading results to R2..."
    if [ -d "$WORKSPACE/$output_dir" ]; then
        rclone copy "$WORKSPACE/$output_dir/" "$R2_REMOTE/$RESULTS/$job_id/" --progress
        log_success "Results uploaded to R2/$RESULTS/$job_id/"
    else
        log_error "Output directory not found: $WORKSPACE/$output_dir"
        return 1
    fi
}

# Execute character creation job
execute_character_job() {
    local manifest_file="$1"
    local job_id="$2"
    
    # Parse manifest
    local script=$(jq -r '.params.script' "$manifest_file")
    local params=$(jq -r '.params.character_params // {}' "$manifest_file")
    
    log "Executing character creation job:"
    log "  Script: $script"
    
    # Download script
    local script_dir=$(dirname "$script")
    mkdir -p "$WORKSPACE/$script_dir"
    rclone copy "$R2_REMOTE/$script_dir/" "$WORKSPACE/$script_dir/" --progress
    
    # Run the character creation script
    cd "$WORKSPACE"
    blender --background --python "$WORKSPACE/$script" -- --params "$params" --output "output/$job_id"
    
    # Upload results
    log "Uploading results to R2..."
    rclone copy "$WORKSPACE/output/$job_id/" "$R2_REMOTE/$RESULTS/$job_id/" --progress
    log_success "Results uploaded"
}

# Execute a job
execute_job() {
    local manifest_file="$1"
    
    # Parse job type and ID
    local job_type=$(jq -r '.job_type' "$manifest_file")
    local job_id=$(jq -r '.job_id' "$manifest_file")
    
    log "🚀 Starting job: $job_id (type: $job_type)"
    
    # Execute based on type
    case "$job_type" in
        render)
            execute_render_job "$manifest_file" "$job_id"
            ;;
        character)
            execute_character_job "$manifest_file" "$job_id"
            ;;
        *)
            log_error "Unknown job type: $job_type"
            return 1
            ;;
    esac
    
    log_success "Job completed: $job_id"
}

# Cleanup old jobs
cleanup_old_jobs() {
    # Remove local job files older than 24 hours
    find "$WORKSPACE/jobs" -type f -mtime +1 -delete 2>/dev/null || true
}

# Main polling loop
main() {
    log "🤖 Pod Agent starting..."
    log "Polling R2 for jobs every ${POLL_INTERVAL}s"
    log "Press Ctrl+C to stop"
    
    # Check rclone config
    check_rclone
    log_success "rclone configured"
    
    # Ensure workspace directories exist
    mkdir -p "$WORKSPACE/jobs/pending" "$WORKSPACE/jobs/processing" "$WORKSPACE/output"
    
    # Main loop
    while true; do
        # Find pending jobs
        pending_jobs=$(find_pending_jobs)
        
        if [ -n "$pending_jobs" ]; then
            # Process first job found
            job_file=$(echo "$pending_jobs" | head -n 1)
            log "📋 Found pending job: $job_file"
            
            # Download job manifest
            manifest_file=$(download_job "$job_file")
            
            # Move to processing in R2
            move_to_processing "$job_file"
            
            # Execute job
            if execute_job "$manifest_file"; then
                log_success "Job execution completed successfully"
            else
                log_error "Job execution failed"
            fi
            
            # Cleanup
            cleanup_old_jobs
        fi
        
        # Wait before next poll
        sleep $POLL_INTERVAL
    done
}

# Handle Ctrl+C gracefully
trap 'log "Pod Agent stopped"; exit 0' INT TERM

# Run main loop
main

