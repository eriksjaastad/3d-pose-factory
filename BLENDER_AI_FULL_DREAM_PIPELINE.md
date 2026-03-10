# Blender → AI Characters: Full Dream Pipeline

This document outlines the vision and technical details for a project that leverages Blender as a structured 3D environment for generating AI characters. The core idea is to use AI to control Blender, render scenes, and then use those renders as input for AI image generation models. This allows for a controllable and iterative process for creating character art.

## Core Idea

> **Teach AI to use Blender as a “3D camera,” then feed those renders into AI models to generate characters.**

This involves:

- **Blender (Remote GPU):** A structured 3D staging area running on a remote GPU server (e.g., RunPod).
- **AI Control (Claude + Others):** AI models (like Claude) learn to manipulate Blender: setting up scenes, posing characters, adjusting lighting, and rendering images.
- **Image Generation (SDXL, etc.):** Blender renders serve as inputs to image models (e.g., Stability AI SDXL), which generate the final character art.
- **Automation (SSH Agent):** The entire workflow is automated, allowing the AI to run the process with minimal human intervention.

---

## End-to-End Pipeline

The following describes the complete pipeline, from initial scene creation to final character generation:

### 1. AI-Driven 3D Scene Creation in Blender

- **AI Scripting:** AI (e.g., via Claude in Cursor) edits Blender Python scripts within the project repository. Examples include:
  - `make_base_scene.py`: Creates the initial scene setup.
  - `generate_pose_scene.py`: Defines character poses and camera angles.
- **Remote Execution:** The Python scripts are executed on a remote GPU server (e.g., RunPod). These scripts perform actions such as:
  - Loading or creating rigged character models or basic geometric shapes.
  - Positioning the camera and adjusting lighting.
  - Optionally setting up backgrounds, props, and composition framing.
- **Script Triggering:** The AI triggers the script execution using commands like:
  ```bash
  cd /workspace && blender --background --python make_base_scene.py
  ```
- **Base Image Rendering:** Blender renders one or more base images to a designated folder:
  - `/workspace/renders/base_0001.png`
  - `/workspace/renders/base_0002.png`

**Goal:** To treat Blender as a controllable 3D camera that the AI can aim and "click." The output is a set of structured renders containing poses, silhouettes, and basic lighting information.

---

### 2. Base Render → AI Character Generation

The base images generated in the previous step are then used as input for an image generation model. Two primary methods exist for this:

#### Option A: Blender AI Render Addon

- **Configuration:** The Blender AI Render addon is configured to use a specific image generation model, such as Stability AI SDXL 1024.
- **Headless Execution:** In a headless/remote environment:
  - The addon calls the Stability API directly from within Blender.
  - The computationally intensive diffusion process is performed on Stability's cloud infrastructure.
- **Critical Headless Settings:** The following settings are crucial for headless operation:
  - `scene.air_props.do_autosave_after_images = True`
  - `scene.air_props.autosave_image_path = "/workspace/output/"`
- **Image Generation:** The image model uses the Blender render as input and generates stylized images, creating characters, artwork, and variations.
- **Output:** Final images are saved to a directory such as:
  - `/workspace/output/char_0001_variant_01.png`
  - `/workspace/output/char_0001_variant_02.png`

#### Option B: Direct API Client

- **Standalone Script:** A standalone Python script (e.g., `stability_client.py`) runs on the RunPod server.
- **Image Loading:** The script loads the base images from `/workspace/renders/base_*.png`.
- **API Call:** The script directly calls the Stability API (or another model provider's API).
- **Output:** The script saves the generated images to `/workspace/output/`.
- **Benefits:** This approach provides greater control over the image generation pipeline, as it's managed directly in Python rather than solely through the Blender addon. Blender remains the source of structured 3D input.

**Goal:** To transform the structured Blender views into visually appealing AI character images. Blender provides composition and pose information, while the image model adds style, detail, and artistic flair.

---

### 3. Automation & Iteration

The true potential of this pipeline lies in enabling the AI to autonomously iterate on the process.

Using the SSH agent, RunPod, and Claude-in-Cursor:

- **AI Capabilities:** The AI can:
  1. **Edit Blender Scripts:** Modify a Blender script (e.g., `make_base_scene.py`) to adjust:
     - Character pose
     - Camera angle
     - Lighting
     - Overall scene setup
  2. **Trigger Background Renders:** Initiate a background render on RunPod via the SSH agent:
     ```bash
     cd /workspace && blender --background --python make_base_scene.py
     ```
  3. **Run AI Render/API Client:** Execute the AI Render step (or the direct API client) to generate images:
     ```bash
     cd /workspace && blender --background --python generate_ai_characters.py
     ```
     or, using the Python client:
     ```bash
     cd /workspace && python stability_client.py
     ```

This iterative loop allows the AI to explore different scene configurations and generate a wide range of character variations with minimal human intervention.
