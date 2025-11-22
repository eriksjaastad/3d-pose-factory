# AI Character Creation Workflow

**Status:** 🚧 Research & Development Phase

---

## Goal

Use AI + Blender Python API to create custom 3D characters for pose rendering.

---

## Why?

Mixamo characters are great for testing, but limited in variety:
- Generic "robot" aesthetic
- Limited body types
- No control over appearance

**Custom characters enable:**
- ✅ Diverse body types (age, gender, build)
- ✅ Realistic human appearance
- ✅ AI-driven parametric generation
- ✅ Unlimited variety for training data

---

## Research Notes

### Tools Under Consideration:
1. **Charmorph** (Blender add-on)
   - Status: Actively maintained (supports Blender 4.x)
   - Features: Parametric human generation, Python API
   - Pros: Free, scriptable, modern
   - Cons: Requires texturing for realism
   
2. **MB-Lab** (Blender add-on)
   - Status: ❌ Archived July 2024, no longer maintained
   - Not recommended due to lack of updates

3. **Procedural Modeling** (Pure Python)
   - Generate meshes directly via `bpy`
   - Full control but very time-intensive

4. **Manual Blender Sculpting + AI Guidance**
   - AI writes Blender scripts based on user descriptions
   - Most flexible but requires Blender expertise

---

## Next Steps

1. **Research Charmorph capabilities** - Can it be fully scripted?
2. **Test installation on RunPod** - Add to `setup_pod.sh`
3. **Create proof-of-concept** - Generate 1 character via AI-written script
4. **Evaluate quality** - Is it good enough for pose detection training?

---

## Technical Requirements

- Blender 4.0+ with Python API
- Charmorph add-on (or alternative)
- Parametric control via Python
- Export to FBX for rendering pipeline

---

**Last Updated:** 2025-11-22

**Status:** Waiting for tool selection decision

