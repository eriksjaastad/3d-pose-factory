# Dashboard TODO

## Phase 2 - Enhanced Features
- [ ] Add thumbnail previews of rendered images
- [ ] Add pod agent heartbeat monitoring (real-time status)
- [ ] Add live logs viewer (stream pod_agent.log)

## Phase 3 - Cost Calculation System ✅ COMPLETE!
**Critical for preventing explosive costs in batch processing!**

- [x] Install AI Render (Stable Diffusion) plugin on pod
- [x] Build cost-calculation module (Python class, importable)
  - [x] DreamStudio pricing logic
  - [x] Stability AI pricing logic
  - [x] Local render (RunPod GPU, $0 API cost)
  - [x] Resolution, steps, model version variables
- [x] Create cost calculation config file (pricing data, easy to update)
- [x] Integrate into dashboard as first-class component
  - [x] Show estimated cost BEFORE job submission
  - [x] Show running total during batch processing
  - [x] Alert if cost exceeds threshold
- [x] Add provider switching (local/DreamStudio/Stability)
- [x] Add cost safeguards
  - [x] Max cost per job limit
  - [x] Max cost per batch limit
  - [x] Confirm dialog for high-cost jobs

## Phase 4 - SSH Agent & Golden Script ✅ COMPLETE!
**Automated command execution and production-ready demo!**

- [x] Build SSH agent with pexpect (persistent shell for RunPod)
- [x] Create `generate_character_from_cube.py` golden script
- [x] Document pipeline in `PIPELINE_OVERVIEW.md`
- [x] Name the system: **Pose Factory Render Agent**
- [x] Test end-to-end AI character generation
- [x] Verify autosave configuration for headless mode

## Future Enhancements
- [ ] Web-based terminal (xterm.js) for SSH-free pod access
- [ ] Email/Slack notifications when jobs complete
- [ ] Multi-pod support (distribute jobs across multiple pods)
- [ ] Job history with search/filter
- [ ] Export job results as ZIP

---

**Status:** Phase 1 (MVP) Complete ✅
- ✅ Pod management (start/stop via API)
- ✅ Job submission form
- ✅ Real-time status updates
- ✅ One-click downloads
- ✅ Dynamic pricing from RunPod API
- ✅ Dark mode UI

