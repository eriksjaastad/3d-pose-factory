# Character Creation TODO

## Current Focus 🎯
**Goal:** Create proper 3D characters from reference images (not stretched!)

- [ ] **Fix image-to-image pipeline** - Crop instead of stretch reference images
- [ ] **Create 3D character from reference image** (Tomorrow's goal!)
  - [ ] Smart crop (extract center square from portrait images)
  - [ ] Test different image_similarity values (0.3, 0.5, 0.7, 0.9)
  - [ ] Refine prompts for better style matching
  - [ ] Generate test batch (5-10 variations)
  - [ ] Compare quality vs text-only generation

## AI Image Generation ✅ COMPLETE!
- [x] Install AI Render (Stable Diffusion) plugin on pod
- [x] Configure Stability AI API integration
- [x] Create text-to-image golden script
- [x] Create image-to-image pipeline script
- [x] Test end-to-end generation (successful!)
- [x] Document autosave requirements for headless mode

## Auto-Rigging Research 🔬
**Goal:** Find the best solution for automatically rigging humanoid meshes

- [ ] **Research & Compare Options:**
  - [ ] Rigify (Built into Blender, free) - requires manual bone placement
  - [ ] Mixamo (Adobe, web-only) - no API, manual upload required
  - [ ] Tripo AI (Has API) - AI-driven auto-rigging, requires account
  - [ ] Auto-Rig Pro (~$50 addon) - has "Smart" auto-placement feature
- [ ] **Evaluate Rigify for our needs:**
  - [ ] Can we automate bone placement with mesh analysis?
  - [ ] Test Rigify Python API for scripting
  - [ ] Assess manual effort required per character
- [ ] **Decision:** Choose auto-rigging approach
- [ ] **Implementation:** Build dashboard integration

**Notes:**
- Meshy.ai exports are NOT rigged (no skeleton)
- For animations, we need: Mesh → Rig → Apply Mixamo animations
- For static renders, rigging not required ✅

## Tool Selection & Setup
- [x] Research character creation tools (CharMorph, MB-Lab)
- [x] Choose CharMorph as primary tool
- [ ] Find and install CharMorph base mesh data
- [ ] Test CharMorph in headless mode
- [ ] Verify parametric controls work programmatically

## Character Generation Script
- [ ] Create `create_character.py` script
- [ ] Implement parameter randomization
- [ ] Add preset templates (athletic, slim, muscular, etc.)
- [ ] Export to FBX with proper rigging
- [ ] Integration with Mixamo for animation

## Pipeline Integration
- [ ] Mission Control job type: "character"
- [ ] Character → Animate → Render full pipeline
- [ ] Batch character generation (create 10, 50, 100 chars)
- [ ] Character library management

## Quality Improvements
- [ ] Implement proper image cropping (preserve aspect ratio)
- [ ] Add resolution upscaling option (512→1024)
- [ ] Create prompt templates for different styles
- [ ] Test different SDXL models/settings

---

**Status:** AI Generation Working! 🎨✅
- SSH Agent operational (automated command execution)
- AI Render integrated with Stability AI SDXL
- Text-to-image: Working perfectly
- Image-to-image: Working but needs crop improvement
- Cost: ~$0.04 per 1024x1024 image
- **Next:** Fix cropping, refine quality

---

## Mesh Preparation 🔧
**Goal:** Prepare imported meshes for proper AI colorization and rigging

- [ ] **Separate mesh into component groups:**
  - [ ] Research how to split single mesh into clothing vs body
  - [ ] Create script to detect/separate clothing geometry
  - [ ] Create script to detect/separate body/skin geometry
  - [ ] Test with meshy.ai Spring_Stroll character
- [ ] **UV Mapping:** Verify mesh has proper UV maps for texturing
- [ ] **Material Zones:** Assign material slots for skin, hair, clothing

**Why this matters:**
- Current mesh is ONE object (253K verts) with no material separation
- AI colorization works better with defined regions
- Rigging requires body mesh separate from clothing for proper deformation

---

## Recent Progress (2025-11-25)
- ✅ Imported Meshy.ai character (`Spring_Stroll_1125161439_generate.blend`)
- ✅ Inspected mesh: 253K vertices, 506K faces, NO armature
- ✅ Created `inspect_mesh.py` script for analyzing imported meshes
- ✅ Created `bootstrap_pod.py` for automated pod setup
- ✅ **Discovered Structure Control API** - correct approach for mesh → AI colorization
- ✅ Created `stability_enhance.py` with Structure Control endpoint
- ✅ Generated colorful AI characters from gray renders (pose preserved!)
- 📝 Mesh is static-only until we implement auto-rigging
- 📝 Structure Control follows pose but interprets clothing freely
- 📝 Need mesh separation for better clothing/body adherence

## Recent Progress (2025-11-29)
- ✅ Created `mesh_cleanup_smooth_and_separate.py` - layered body/clothing tool
- ✅ Tested multiple approaches for body/clothing separation:
  - Boolean difference with various shrink amounts
  - Vertex-Weight-Proximity masking (failed - caused spikes)
  - Distance-based vertex removal (too aggressive)
  - Fat body proxy containment testing
- ✅ **Winner: 8mm shrink + boolean + moderate smoothing**
  - Produces cleanest BodyMesh with minimal artifacts
  - DressedMesh preserved perfectly intact
- ✅ Final output: `Spring_Stroll_FINAL.blend`
  - BodyMesh: 236K verts (for rigging)
  - DressedMesh: 253K verts (for rendering)
- 📝 Script runs headlessly on local Blender 5.0
- 📝 Ready to sync to RunPod for pipeline integration
