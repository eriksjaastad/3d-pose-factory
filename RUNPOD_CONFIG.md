# RunPod Configuration Reference

## Recommended Pod Configuration

### GPU
- **Type:** A40 (48GB VRAM)
- **Alternatives:** RTX 3080, RTX 4090, A5000, or any NVIDIA GPU with 12GB+ VRAM
- **Cost:** ~$0.35-0.65/hour depending on GPU type

### Template
- **Recommended:** RunPod PyTorch 2.0.1 (or latest)
- **Alternative:** RunPod Ubuntu 22.04
- **Why:** These include Python 3, pip, and CUDA drivers pre-installed

### Container Disk
- **Minimum:** 30GB
- **Recommended:** 50GB (for Blender and temp files)

### Volume Storage
- **Not required** (we use R2 for persistence)
- Using volume storage adds monthly costs
- Fresh pod + setup script is faster and cheaper

### Network
- **Ports:** Default (SSH only needed)
- **Region:** Any (WNAM recommended for lower latency from US West)

## Pod Setup Process

1. **Template:** RunPod PyTorch or RunPod Ubuntu
2. **GPU:** A40 or equivalent (12GB+ VRAM)
3. **Disk:** 50GB container disk
4. **Volume:** None (skip this)
5. **Deploy:** On-Demand (not spot - more reliable)

## What Gets Installed by setup_pod.sh

- **Blender:** 4.0.2 (from apt)
- **Graphics libraries:** libegl1, libgl1, libgomp1
- **Python packages:** opencv-python, mediapipe, pillow, numpy
- **Tools:** rclone (pre-installed on RunPod)
- **Code:** GitHub repo cloned to /workspace/pose-factory

## SSH Access

**Key location:** `~/.ssh/id_ed25519_runpod`

**Connection format:**
```bash
ssh [POD-ID]@ssh.runpod.io -i ~/.ssh/id_ed25519_runpod
```

**Public key** (add to RunPod settings if not already there):
Contents of `~/.ssh/id_ed25519_runpod.pub`

## Example Pod Used in Development

- **Pod ID:** 6gpur3lb2h5pzi-6441128f
- **GPU:** NVIDIA A40 (48GB)
- **Template:** RunPod PyTorch
- **Region:** EU-SE-1
- **Cost:** $0.40/hour
- **Session duration:** ~1 hour total development + testing

## Cost Optimization Tips

1. **Terminate immediately after processing** - Don't leave pods running
2. **Use On-Demand, not Spot** - More reliable, worth the slight premium
3. **Skip volume storage** - Setup script is faster than paying monthly fees
4. **Batch your work** - Upload many images at once to maximize pod usage
5. **Monitor time** - Set a timer to remember to terminate the pod

## Future Considerations

If you end up processing daily for hours at a time:
- Consider network volumes (~$5/month for 50GB)
- Consider Secure Cloud (dedicated hardware, monthly commitment)
- Consider spot instances (cheaper but can be interrupted)

For now: Fresh pods + setup script is optimal.

