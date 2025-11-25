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
