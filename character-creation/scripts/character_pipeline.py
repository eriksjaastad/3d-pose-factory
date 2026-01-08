#!/usr/bin/env python3
"""
Character Pipeline - Full Mesh to AI Images Pipeline

This orchestrator runs the complete pipeline:
1. Render variations (Blender) - multiple colors/lighting/angles
2. AI enhance (Stability AI) - multiple AI variations per render
3. Sync results to R2

Usage (on pod):
    python character_pipeline.py \
        --mesh /workspace/assets/meshes/character.blend \
        --blender-variations 5 \
        --ai-variations 3

Or run via SSH agent from Mac.
"""

import argparse
import subprocess
import os
import sys
import json
import shutil
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="Run full character pipeline")
    parser.add_argument("--mesh", type=str, required=True,
                        help="Path to input .blend mesh file")
    parser.add_argument("--blender-variations", type=int, default=5,
                        help="Number of Blender render variations")
    parser.add_argument("--ai-variations", type=int, default=3,
                        help="Number of AI variations per Blender render")
    parser.add_argument("--output-base", type=str, default="/workspace/output/character-creation",
                        help="Base output directory")
    parser.add_argument("--prompt", type=str,
                        default="Beautiful anime character, detailed, vibrant colors, professional lighting, 8k quality",
                        help="AI generation prompt")
    parser.add_argument("--image-similarity", type=float, default=0.5,
                        help="AI image similarity (0.0-1.0)")
    parser.add_argument("--resolution", type=int, default=1024,
                        help="Render resolution")
    parser.add_argument("--samples", type=int, default=32,
                        help="Blender render samples")
    parser.add_argument("--skip-ai", action="store_true",
                        help="Skip AI enhancement stage (Blender only)")
    parser.add_argument("--sync-to-r2", action="store_true",
                        help="Sync results to R2 when complete")
    
    return parser.parse_args()


def run_command(cmd, description):
    """Run a command and handle output."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd[:5])}...")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,  # Let output stream to console
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    args = parse_args()
    
    # Generate unique run ID
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\n" + "🎨" * 30)
    print("  CHARACTER PIPELINE")
    print("🎨" * 30)
    print(f"\nRun ID: {run_id}")
    print(f"Mesh: {args.mesh}")
    print(f"Blender variations: {args.blender_variations}")
    print(f"AI variations per image: {args.ai_variations}")
    print(f"Total expected images: {args.blender_variations * args.ai_variations}")
    print(f"Estimated cost: ~${args.blender_variations * args.ai_variations * 0.04:.2f}")
    print("=" * 60)
    
    # Check mesh exists
    if not os.path.exists(args.mesh):
        print(f"\n❌ ERROR: Mesh file not found: {args.mesh}")
        sys.exit(1)
    
    # Create output directories
    run_output = os.path.join(args.output_base, f"run_{run_id}")
    blender_output = os.path.join(run_output, "blender_renders")
    ai_output = os.path.join(run_output, "ai_enhanced")
    
    os.makedirs(blender_output, exist_ok=True)
    os.makedirs(ai_output, exist_ok=True)
    
    print(f"\n📁 Output directory: {run_output}")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # =========================================================================
    # STAGE 1: Blender Variations
    # =========================================================================
    print("\n\n" + "=" * 60)
    print("  STAGE 1: BLENDER VARIATIONS")
    print("=" * 60)
    
    stage1_script = os.path.join(script_dir, "render_variations.py")
    
    stage1_cmd = [
        "blender", "--background", "--python", stage1_script, "--",
        "--file", args.mesh,
        "--output-dir", blender_output,
        "--variations", str(args.blender_variations),
        "--resolution", str(args.resolution),
        "--samples", str(args.samples)
    ]
    
    if not run_command(stage1_cmd, "Rendering Blender Variations"):
        print("\n❌ Stage 1 failed!")
        sys.exit(1)
    
    # Count Blender outputs
    blender_images = [f for f in os.listdir(blender_output) if f.endswith('.png') and f.startswith('variation_')]
    print(f"\n✅ Stage 1 complete: {len(blender_images)} Blender renders")
    
    # =========================================================================
    # STAGE 2: AI Enhancement (optional)
    # =========================================================================
    if args.skip_ai:
        print("\n⏭️  Skipping AI enhancement (--skip-ai flag)")
    else:
        print("\n\n" + "=" * 60)
        print("  STAGE 2: AI ENHANCEMENT")
        print("=" * 60)
        
        stage2_script = os.path.join(script_dir, "ai_enhance_batch.py")
        
        stage2_cmd = [
            "blender", "--background", "--python", stage2_script, "--",
            "--input-dir", blender_output,
            "--output-dir", ai_output,
            "--variations-per-image", str(args.ai_variations),
            "--prompt", args.prompt,
            "--image-similarity", str(args.image_similarity)
        ]
        
        if not run_command(stage2_cmd, "Creating AI Variations"):
            print("\n⚠️  Stage 2 had errors (continuing...)")
        
        # Count AI outputs
        ai_images = [f for f in os.listdir(ai_output) if f.endswith('.png')]
        print(f"\n✅ Stage 2 complete: {len(ai_images)} AI images")
    
    # =========================================================================
    # STAGE 3: Sync to R2 (optional)
    # =========================================================================
    if args.sync_to_r2:
        print("\n\n" + "=" * 60)
        print("  STAGE 3: SYNC TO R2")
        print("=" * 60)
        
        sync_cmd = [
            "rclone", "copy", run_output,
            f"r2_pose_factory:pose-factory/output/character-creation/run_{run_id}/",
            "--progress"
        ]
        
        run_command(sync_cmd, "Syncing to R2")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n\n" + "🎉" * 30)
    print("  PIPELINE COMPLETE!")
    print("🎉" * 30)
    
    # Final counts
    blender_count = len([f for f in os.listdir(blender_output) if f.endswith('.png')]) if os.path.exists(blender_output) else 0
    ai_count = len([f for f in os.listdir(ai_output) if f.endswith('.png')]) if os.path.exists(ai_output) else 0
    
    print(f"\n📊 Results:")
    print(f"   • Blender renders: {blender_count}")
    print(f"   • AI enhanced: {ai_count}")
    print(f"   • Total images: {blender_count + ai_count}")
    print(f"\n📁 Output location: {run_output}")
    
    if args.sync_to_r2:
        print(f"☁️  R2 location: r2_pose_factory:pose-factory/output/character-creation/run_{run_id}/")
    
    print("\n📥 To download results to your Mac:")
    print(f"   rclone copy r2_pose_factory:pose-factory/output/character-creation/run_{run_id}/ \\")
    print(f"       character-creation/data/working/run_{run_id}/")
    
    print("\n" + "=" * 60 + "\n")
    
    # Output run info for scripts
    print(f"RUN_ID={run_id}")
    print(f"RUN_OUTPUT={run_output}")


if __name__ == "__main__":
    main()
