---
name: gameblocks
description: Use when building or revising a browser-based 3D game — coordinate frames, actor motion, camera rigs, collision-aware movement, gameplay state, world building. Compose the vendored GameBlocks three.js modules (gameblocks_index / gameblocks_read_module) instead of deriving 3D math from scratch; render the game with show_artifact.
---

# GameBlocks — build browser 3D games from proven blocks

Natural language is a lossy interface for 3D math: hand-derived coordinate frames and motion
controllers reliably produce inverted axes, unstable motion, and state that drifts from what's
on screen. GameBlocks is a library of 74 self-contained three.js modules (MIT, xt4d/GameBlocks)
that already got this right. **Compose them; don't re-derive them.**

## Workflow

1. **`gameblocks_index()` first.** It returns the module catalog with one-line capabilities.
   Pick blocks for motion, camera, behavior, gameplay, world, and HUD — prefer an existing
   module whenever one fits, *especially* motion controllers and camera rigs.
2. **`modules/math/WorldBasis.js` is the single source of truth** for gameplay-space
   coordinates: forward/right/up axes, planar movement, heading, and control-signal
   transforms. The coordinate system is right-handed. Never hand-roll Euler/axis math beside it.
3. Read any block you intend to adapt with `gameblocks_read_module(paths)` (several at once:
   comma-separated). Reuse as-is when possible; adapt from the existing implementation rather
   than rewriting.
4. Deliver in one of two modes below, then iterate.

## Artifact mode (default in chat)

Build the game as **one HTML file** and render it with `show_artifact(kind="html", ...)` — the
user plays it right in the artifact panel, and `update_artifact` gives you iteration/versioning
for free.

**Start from `gameblocks_game_template()` — never write the shell by hand.** The template is a
working page (it renders a placeholder scene as-is) with the fragile boilerplate already
correct: the runtime import-map preamble, renderer/camera/lights/resize, a click-to-start
overlay that fixes keyboard focus in the sandbox, a `keys` input set, and a clamped-dt loop.
Replace exactly two marked sections:

- `GAME SETUP (replace)` — compose blocks: a motion controller + its recommended camera rig,
  world/environment factories, gameplay directors.
- `UPDATE (replace)` — drive them with `dt` + the `keys` set each frame.

Rules that keep it working:

- The import-map preamble must stay the FIRST script: the artifact sandbox has **no own URL**,
  so the map is built at runtime from `document.baseURI` (inherited from the shell, slug-safe
  through the fleet proxy), and an import map must exist before any module loads.
- Unmodified blocks import over HTTP via the map's `gameblocks/` prefix — e.g.
  `import { WorldBasis } from "gameblocks/modules/math/WorldBasis.js"` — and pull their own
  relative dependencies automatically. An **adapted** block can't come over HTTP: read it with
  `gameblocks_read_module`, adapt, and inline the copy (and stop importing that one path).
- Mouse-look games: add `canvas.requestPointerLock()` in the start-overlay click handler (the
  sandbox allows pointer lock). WebGL works normally.
- Respect the artifact size cap (default 512 KB) — HTTP imports keep you far under it.
- The three.js / Rapier CDN pins live in the template and mirror the vendored `summary.md` —
  check it if versions move (browser-side network is required for those two).

## Project mode (a real repo)

When building in an actual project directory, copy blocks in with
`gameblocks_export_modules(paths, dest_dir)` (or `paths="all"`). It preserves the relative
layout so inter-module imports keep working. Then follow the upstream convention: write a
`gameblocks_usage.md` in the project documenting each selected module, its purpose,
reuse/adaptation status, key changes, and how it's integrated.

## Rules of thumb

- Motion controller + matching camera rig pairings are listed in the index (e.g.
  `MouseLookCharacterMotionController` ↔ `FirstPersonCameraRig`). Honor them.
- Physics/collision goes through Rapier via `KinematicBatchResolver` — don't write your own
  sweep tests.
- Start from the smallest playable loop (one actor, one camera, one input scheme), show it,
  then layer gameplay blocks (spawning, checkpoints, combat) in later versions.
