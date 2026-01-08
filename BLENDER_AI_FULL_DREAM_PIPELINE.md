# Blender → AI Characters: Full Dream Pipeline (Project Vision)

This document captures the **high-level vision** for the project so it’s easy to remember what we’re actually trying to build, even when we’re deep in plumbing or debugging.

## Core Idea

> **Teach AI to use Blender as a “3D camera,” then feed those renders into AI models to generate characters.**

In other words:
- Blender (running on a remote GPU box) is the **structured 3D staging area**.
- AI (Claude + others) learns how to **set up scenes, pose things, and render images** in Blender.
- Those renders become **inputs** to image models (e.g. Stability SDXL), which then generate final character art.
- All of this is wired so the AI can run most of the workflow itself (via the SSH agent), instead of you copy‑pasting commands.

---

## End-to-End Dream Pipeline

Here’s the **full dream pipeline** in one pass.

### 1. AI uses Blender to create a base 3D scene

- AI (via Claude in Cursor) edits a Blender Python script in the repo, e.g.:
  - `make_base_scene.py`
  - `generate_pose_scene.py`
- The script runs on the **RunPod GPU box** and does things like:
  - Load or create a rigged character / basic geometry.
  - Position the camera and lighting.
  - Optionally set background, props, or composition framing.
- AI triggers the script with something like:
  ```bash
  cd /workspace && blender --background --python make_base_scene.py
  ```
- Blender renders one or more **base images** to a known folder, e.g.:
  - `/workspace/renders/base_0001.png`
  - `/workspace/renders/base_0002.png`

**Goal of this step:** Treat Blender like a **3D camera** that AI can aim and click. The output is “boring but structured” renders (poses, silhouettes, rough lighting).

---

### 2. Base render → AI character generation

Once the base images exist, they get fed into an image model.

There are two main ways to do this:

#### Option A: Through the Blender AI Render addon (current setup)

- AI Render in Blender is configured to use **Stability AI SDXL 1024**.
- In a headless/remote context:
  - The addon calls the **Stability API** from inside Blender.
  - The heavy diffusion compute happens on **Stability’s cloud**.
- Critical headless settings (discovered during debugging):
  - `scene.air_props.do_autosave_after_images = True`
  - `scene.air_props.autosave_image_path = "/workspace/output/"`
- The model uses the **Blender render as input** and generates stylized images (characters, art, variants).
- Final images are written to something like:
  - `/workspace/output/char_0001_variant_01.png`
  - `/workspace/output/char_0001_variant_02.png`

#### Option B: Direct API client (future option)

- A standalone Python script (e.g. `stability_client.py`) runs on RunPod and:
  - Loads `/workspace/renders/base_*.png`.
  - Calls the Stability API (or another model provider) directly.
  - Saves final outputs to `/workspace/output/`.
- Blender is still the source of the **structured 3D input**, but the image generation pipeline is fully under our control in Python instead of only via the addon.

**Goal of this step:** Turn structured Blender views into **beautiful AI character images**. Blender gives composition / pose; the image model adds style, detail, and “soul.”

---

### 3. Automation & iteration (AI runs the loop)

The real power comes when AI can **iterate** on the pipeline without you manually driving each step.

Using the SSH agent + RunPod + Claude-in-Cursor:

- AI can:
  1. Edit a Blender script (`make_base_scene.py`) to adjust:
     - Pose
     - Camera angle
     - Lighting
     - Scene setup
  2. Trigger a background render on RunPod via the SSH agent:
     ```bash
     cd /workspace && blender --background --python make_base_scene.py
     ```
  3. Run the AI Render step (or direct API client) to generate images:
     ```bash
     cd /workspace && blender --background --python generate_ai_characters.py
     ```
     or, for a Python client:
     ```bash
     cd /workspace && python stability_client.py
     ```
  4. Inspect `/workspace/output/` (via `ls`, `rclone`, etc.) to:
     - Verify images were created.
     - Optionally push them to R2 or other storage.
  5. Adjust scripts and repeat.

- The SSH agent provides a **controlled interface** for AI to run these commands on RunPod:
  - Requests go into "${PROJECTS_ROOT}/_tools/ssh_agent/queue/requests.jsonl".
  - Results come back via "${PROJECTS_ROOT}/_tools/ssh_agent/queue/results.jsonl".
  - AI reads outputs, reasons about them, and decides the next command or code change.

**Goal of this step:** Make the whole system **self-service for AI**: you specify the creative direction and constraints, and the AI iteratively updates Blender scenes + image generation until the outputs match your intent.

---

## What “Success” Looks Like for v1

For a solid **v1 milestone**, success can be defined as:

1. A single script (or small set of scripts) that can be run headlessly on RunPod to:
   - Create a simple Blender scene (even just a cube or basic character).
   - Render it to `/workspace/renders/`.
   - Use AI Render + Stability SDXL to generate stylized images.
   - Save the final character images to `/workspace/output/`.

2. Claude, via the SSH agent, can:
   - Run that script end-to-end on RunPod.
   - Inspect logs if something breaks.
   - Confirm that new images appear in `/workspace/output/`.
   - Make small code changes to tweak the pipeline (camera, resolution, prompts, etc.).

Once v1 is stable, future versions can:

- Swap the cube for rigged 3D characters and animations.
- Move from Stability’s cloud to a **local diffusion engine** running on the same GPU pod.
- Add metadata / manifests so each final image is fully traceable back to:
  - The Blender scene configuration.
  - The prompts / parameters used in the image model.

---

## TL;DR Vision Statement

> **A remote AI-driven 3D + image lab where Blender provides structured 3D views, and AI models transform those renders into final character art — all orchestrated by AI through a controlled SSH agent.**

This document is here so Future You remembers:  
the goal is not “SSH hacks” or “Blender plugin debugging” by themselves — those are just stepping stones toward a reusable **Blender → AI Characters** pipeline that AI can operate for you.
