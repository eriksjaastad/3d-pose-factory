# ARCHIVED — 2026-04-15

**Why mothballed:** No longer an active focus. The Blender-based pose pipeline work is paused; current effort is on other projects (flo-fi, ai-memory, holoscape).

**Why kept, not deleted:** The Blender pipeline code and pose presets represent real engineering work worth preserving for future reference or resurrection.

**If resurrecting:** Read `PROGRESS.md` and `DECISIONS.md` first, then check git log for the last active period. Do not assume tooling or dependencies still work without verification.

---

## Cleanup pass — 2026-08-12

Deletions that had been sitting uncommitted in the working tree (made outside git sometime after
the 2026-05-13 archive commit) were reviewed and committed. Nothing here is recoverable from this
repo alone, so read this before assuming a file went missing by accident.

**Removed — regenerable:**
- `pose-rendering/downloads/*.fbx` (6 Mixamo rigs, ~14 MB). Safe: `shared/scripts/pod_agent.sh`
  re-fetches them from R2 with `rclone` whenever the directory is empty. Now gitignored so a
  re-download does not get re-committed.

**Removed — retired scaffolding, referenced only by docs:**
- `.agent/instructions.md`, `.agent/rules/code-review-standard.md`,
  `.agent/rules/learning-loop-pattern.md`
- `scripts/pre_review_scan.sh`, `scripts/validate_project.py`, `scripts/warden_audit.py`

These came from `project-scaffolding`, which is itself being retired. No code path invoked them.

**Removed — dead credential:**
- `runpod`, `runpod.pub`. An SSH keypair swept into the initial commit (`81b5987`) by a bulk add.
  Never registered on the RunPod account and referenced by no script in any commit — nothing ever
  trusted it. Untracked in `99a7cfc`, then deleted from disk.

**Known stale, deliberately left alone:** `REVIEWS_AND_GOVERNANCE_PROTOCOL.md` still describes
`pre_review_scan.sh`, `validate_project.py`, and `audit_all_projects.py` as active gates. They are
gone. The doc is a copy of `project-scaffolding`'s and describes an active-development workflow
that no longer applies to an archived project. Rewrite it or delete it if this project is ever
resurrected.
