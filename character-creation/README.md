# Character Creation Workflow

**AI-driven 3D character generation using Blender**

---

## Status: 🚧 Research & Development

This workflow uses Blender's Python API + AI to create custom 3D characters for pose rendering and training data generation.

---

## Quick Start

**Coming soon!** Currently researching the best approach for AI-driven character creation.

Planned workflow:
```bash
# 1. Create character via AI script
./scripts/character_pipeline.sh --create "athletic woman, age 25"

# 2. Results sync to R2, download locally
./scripts/character_pipeline.sh --download-only
```

---

## Why Custom Characters?

### Limitations of Mixamo:
- ❌ Generic "robot" aesthetic
- ❌ Limited body type variety
- ❌ No control over appearance

### Benefits of Custom Characters:
- ✅ Diverse body types (age, gender, build)
- ✅ Realistic human appearance
- ✅ AI-driven parametric generation
- ✅ Unlimited variety for training data

---

## Current Research

### Tool Options:
1. **Charmorph** (Blender add-on) - Leading candidate
   - Actively maintained (Blender 4.x compatible)
   - Parametric human generation
   - Python API for scripting
   
2. **Procedural Modeling** - Pure Python approach
   - Full control via `bpy` API
   - Time-intensive but flexible

See [docs/CHARACTER_CREATION_WORKFLOW.md](docs/CHARACTER_CREATION_WORKFLOW.md) for detailed research notes.

---

## Project Structure

```
character-creation/
├── scripts/
│   ├── character_pipeline.sh      ← Main automation (coming soon)
│   ├── create_character.py        ← Character generation script
│   └── test_character_creation.py ← Test suite
├── docs/
│   └── CHARACTER_CREATION_WORKFLOW.md
├── downloads/                      ← Textures, assets, etc.
├── data/
│   ├── working/                    ← Generated characters
│   └── archive/                    ← Old characters
└── README.md                       ← You are here
```

---

## Integration with Pose Rendering

Once characters are created, they can be used with the pose-rendering workflow:

1. Generate character → Export as FBX
2. Apply Mixamo animations to custom character
3. Use `../pose-rendering/scripts/render_simple_working.py` to render
4. Create training data as usual

---

## Next Steps

1. ✅ Set up project structure
2. ⏳ Research and select character creation tool (Charmorph vs procedural)
3. ⏳ Install chosen tool on RunPod
4. ⏳ Create proof-of-concept character generation script
5. ⏳ Build automation pipeline (similar to render_pipeline.sh)
6. ⏳ Test integration with pose rendering workflow

---

**Last Updated:** 2025-11-22

**Status:** Project structure ready, awaiting tool selection

