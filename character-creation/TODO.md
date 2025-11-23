# Character Creation TODO

**Last Updated:** 2025-11-23

---

## ✅ What We Accomplished Today

1. **Project Reorganization**
   - Split into two independent workflows (pose-rendering / character-creation)
   - Created clean directory structure
   - Updated all READMEs with correct paths

2. **RunPod Setup**
   - Discovered RunPod SSH only works interactively (not remote execution)
   - Set up persistent rclone config in `/workspace/.config/`
   - Installed Blender 4.0.2 on pod
   - Created working upload/download workflow via R2

3. **CharMorph Investigation**
   - ✅ CharMorph installed successfully
   - ✅ 30 operators available in headless Blender
   - ❌ Missing base mesh data files
   - **Status:** Tool works, just needs data

---

## 🚧 Current Blockers

### CharMorph Base Mesh Data
- CharMorph needs base human meshes to modify
- Data repository doesn't exist at expected location
- **Next steps:**
  - Search CharMorph forums/docs for base mesh downloads
  - Check if base meshes are in addon updater
  - Alternative: Find compatible base mesh elsewhere

---

## 📋 Next Steps (Priority Order)

### High Priority
1. **Find CharMorph Base Mesh**
   - Check CharMorph GitHub issues/wiki
   - Look for addon data downloads
   - Check Blender Artists forum threads
   - Alternative: Download MB-Lab base mesh (compatible?)

2. **Create Pod Init Script**
   - One command to set up new pod
   - Auto-creates rclone symlink
   - Downloads all needed scripts
   - No more Mac ↔ Pod jumping

3. **Test Character Generation**
   - Once base mesh found, test CharMorph headless
   - Create simple "generate random character" script
   - Export to FBX

### Medium Priority
4. **Build Character Workflow**
   - Upload → Generate → Download automation
   - Integrate with pose rendering pipeline
   - Document in README

5. **Alternative Research**
   - MB-Lab (archived but might work)
   - Procedural generation (hard mode)
   - Pre-made base mesh + modifications

---

## 💡 Key Learnings

1. **RunPod SSH:**
   - Only interactive sessions work
   - Must SSH in, then run commands on pod
   - Can't execute commands remotely

2. **Persistence:**
   - Only `/workspace` survives pod restarts
   - Store rclone config there, symlink to `~/.config`
   - Scripts must be re-downloaded or kept in `/workspace`

3. **CharMorph:**
   - Not a mesh generator, it's a mesh MODIFIER
   - Needs base human mesh data
   - Works great headless once data is available

---

## 🎯 End Goal

**Working character creation workflow:**
1. Run one script locally (upload)
2. SSH to pod
3. Run character generation command
4. Download FBX character
5. Use with pose rendering pipeline

**Status:** 70% there - just need base mesh data!

---

## 📝 Notes for Tomorrow

- Don't forget: rclone config is in `/workspace/.config/rclone/`
- CharMorph is at `~/.config/blender/4.0/scripts/addons/CharMorph/`
- Blender version: 4.0.2
- Pod setup script exists: `/workspace/setup_pod.sh`

**Mood:** Productive day despite hitting the data wall. Close to breakthrough!

