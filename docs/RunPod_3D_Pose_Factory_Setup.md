# Project B – 3D Pose Factory (Cloud Version)
## Full Setup Guide: RunPod GPU Instance + Blender + Pose Extraction + Cloudflare R2 Storage

This document contains everything you need to **set up, run, and maintain** a cloud‑based “3D Pose Factory” using:

- **RunPod** for GPU compute  
- **Blender** for 3D scene + rig control  
- **OpenPose / Pose Extraction Tools** for skeleton output  
- **Cloudflare R2** for cheap, reliable storage  
- **A strict $100/month budget framework**  
- **Auto-shutdown recommendations** for cost control  

After this is set up, you can follow **Step 7** (full deployment) and start generating skeletons/poses today.

---

# 1. Overview
The **3D Pose Factory** is a separate, cloud‑based project designed to:

- Generate **skeletons, poses, depth maps, normal maps** from 3D rigs  
- Produce unlimited **2D pose references** for your ComfyUI pipeline  
- Run on a **budget‑friendly, burst‑only GPU**  
- Store outputs in **Cloudflare R2**, which is extremely cheap  
- Shut down when not in use  

This pipeline does **NOT generate NSFW content** — only structure, geometry, and skeleton maps.  
Your local ComfyUI pipeline handles the rest.

---

# 2. Monthly Budget Model (Target: $100/mo)
Your monthly costs break down like this:

| Component | Expected Cost |
|----------|----------------|
| GPU compute | **$60–80/mo** (10–20 hours/month) |
| Storage (Cloudflare R2) | **$3–10/mo** |
| Misc/Network | **$5–10/mo** |
| **Total** | **$70–100/mo** |

You stay under $100 by:
- using **on-demand GPUs**  
- running them only during batch jobs  
- shutting them down immediately afterward  

---

# 3. Why RunPod is Perfect for This
RunPod gives you:

### ✔ Easy UI (beginner friendly)  
### ✔ Low-cost NVIDIA GPUs (RTX/A-series)  
### ✔ Simple setup with Ubuntu  
### ✔ Automatic volume mounts  
### ✔ Shutdown buttons & API  
### ✔ Pay-as-you-go (no commitment)  

For your project, RunPod is the best balance of:
- cost  
- simplicity  
- stability  

---

# 4. Why Cloudflare R2 for Storage
Cloudflare R2 is:

### ✔ Extremely cheap  
### ✔ No egress fees (rare!)  
### ✔ Always-on  
### ✔ Great for sync between cloud + local  
### ✔ Perfect for storing skeletons, poses, depth/normal maps  

It’s also simple to integrate with Python scripts or rclone.

Your RunPod instance will upload all pose outputs automatically to R2.

---

# 5. What This Pipeline Will Produce
This system will create:

### **Core Outputs**
- 2D skeleton maps (OpenPose style)  
- JSON keypoint files  
- Depth maps  
- Surface normal maps  
- Segmentation masks  
- Pose metadata  

### **Optional Outputs**
- Multi-angle skeleton sets  
- Multi-frame sequences for animation  
- Shaded anatomical reference renders  

These outputs feed directly into your **ComfyUI + SDXL** structure-first workflow.

---

# 6. Architecture Diagram
```
             ┌──────────────────────────┐
             │        RunPod GPU        │
             │  (Ubuntu + Blender +     │
             │   Pose Extraction Tools) │
             └───────────┬──────────────┘
                         │
            Generate 3D Poses / Skeletons
                         │
     ┌───────────────────┴──────────────────┐
     │                                      │
  Upload                                 Download
     │                                      │
┌────▼─────┐                         ┌──────▼────────┐
│Cloudflare│                         │  Local Laptop │
│   R2     │                         │ (ComfyUI/SDXL)│
└────▲─────┘                         └──────▲────────┘
     │                                      │
     │             Feedback Loop             │
     └──────────────────────────────────────┘
```

---

# 7. FULL RUNPOD SETUP GUIDE

## 7.1 Create RunPod Account
1. Visit **https://runpod.io**  
2. Sign up with email or GitHub  
3. Add a payment method  
4. Set a monthly budget alert (optional but recommended)

---

## 7.2 Select and Launch a GPU Instance
### Recommended GPU Types:
- RTX 3060 / 3070 / 3080  
- RTX A4000 / A5000  
- A10 / L40 / L4  
- T4 (budget option)

### Recommended Pod Template:
- **Community Pod — Ubuntu 22.04**
- Check **ssh enabled**
- Select GPU + RAM options

Good starting point:
- RTX 3070 or A4000  
- 1 GPU  
- 16–24GB VRAM  
- 8–12 vCPUs  
- 30–50GB SSD  

Cost: **$0.35–$0.65/hr**

---

## 7.3 Connect via SSH
Once it starts:
```
ssh root@<your-runpod-ip>
```

---

## 7.4 Install Blender
```
sudo apt update
sudo apt install blender -y
```

Or for latest version:
```
sudo snap install blender --classic
```

---

## 7.5 Install Python Tools
```
sudo apt install python3 python3-pip -y
pip3 install numpy pillow opencv-python boto3
```

---

## 7.6 Set Up Cloudflare R2 Storage
1. Go to Cloudflare → R2  
2. Create bucket (e.g., `pose-factory`)  
3. Generate API key with read/write  
4. Save Access Key + Secret Key  

### Install rclone:
```
sudo apt install rclone -y
```

### Configure:
```
rclone config
```

Choose:
- New remote  
- S3-compatible  
- Endpoint: `https://<accountid>.r2.cloudflarestorage.com`

Upload example:
```
rclone copy output/ r2:pose-factory
```

---

## 7.7 Install Pose Extraction Tools
Example: MediaPipe
```
pip3 install mediapipe
```

---

## 7.8 Test Script
```
# generate_pose.py
import cv2, mediapipe as mp

pose = mp.solutions.pose.Pose()
img = cv2.imread("frame.png")
results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

mp.solutions.drawing_utils.draw_landmarks(
    img, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

cv2.imwrite("pose_out.png", img)
```

Run:
```
python3 generate_pose.py
```

---

## 7.9 Upload to R2
```
rclone copy output/ r2:pose-factory
```

---

## 7.10 Optional Auto-Shutdown
```
sudo crontab -e
```
Add:
```
0 * * * * shutdown -h now
```

---

# 8. Launch Checklist for Today
- [ ] Launch RunPod instance  
- [ ] Install Blender  
- [ ] Install Python + pose extractor  
- [ ] Configure Cloudflare R2  
- [ ] Run pose extraction on sample  
- [ ] Upload test output  
- [ ] Shut down pod  

---

# 9. Summary
You now have a complete, ready-to-run guide for setting up:

- RunPod GPU instance  
- Blender  
- Pose extraction tools  
- Cloudflare R2 sync  
- $100/month cloud budget plan  

This document is your full onboarding guide for the **3D Pose Factory** project.
