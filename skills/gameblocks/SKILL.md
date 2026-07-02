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
for free. Keep the file small by importing unmodified blocks over HTTP from this plugin instead
of inlining them.

The artifact runs in a sandboxed iframe with **no own URL**, so the import map must be built at
runtime from `document.baseURI` (inherited from the shell). Make this preamble the FIRST script
in the file — an import map must exist before any module loads:

```html
<script>
  // Host base: "" on the host window, "/agents/<slug>" through the fleet proxy.
  var GB_ROOT = document.baseURI.split("/plugins/")[0];
  var im = document.createElement("script");
  im.type = "importmap";
  im.textContent = JSON.stringify({ imports: {
    "three": "https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/",
    "@dimforge/rapier3d-compat": "https://cdn.jsdelivr.net/npm/@dimforge/rapier3d-compat@0.14.0/rapier.es.js",
    "gameblocks/": GB_ROOT + "/plugins/gameblocks/"
  }});
  document.currentScript.after(im);
</script>
<script type="module">
  import { WorldBasis } from "gameblocks/modules/math/WorldBasis.js";
  // … game setup: scene, renderer, blocks, loop …
</script>
```

- Blocks import each other by relative path, so importing one block over HTTP pulls its
  dependencies automatically. An **adapted** block can't be imported over HTTP — inline your
  adapted copy in the artifact (and stop importing that one path).
- Input: give the page a click-to-start overlay that focuses the canvas; the sandbox allows
  pointer lock for mouse-look games. WebGL works normally.
- Respect the artifact size cap (default 512 KB) — HTTP imports keep you far under it.
- Browser-side network is required for the three.js / Rapier CDN pins above (the pins come
  from the vendored `summary.md` — check it if versions move).

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
