# gameblocks-plugin

[GameBlocks](https://github.com/xt4d/GameBlocks) for [protoAgent](https://github.com/protoLabsAI/protoAgent):
74 self-contained three.js building-block modules — coordinate frames, actor-motion
controllers, camera rigs, behaviors, gameplay loops, world builders, HUDs — vendored
and wired up so the agent **composes proven 3D blocks instead of deriving 3D math
from scratch**, then renders the game right in the console.

## The pairing

This plugin deliberately ships **no console view**. It pairs with the first-party
**artifact plugin**: the agent assembles a single-file HTML game whose import map pulls
unmodified blocks from this plugin's module server, and renders it with
`show_artifact(kind="html")` — the sandboxed artifact panel becomes the play surface,
with the artifact version chain giving update/rollback iteration for free. The pairing
is soft (by tool name, never a cross-plugin import); without the artifact plugin,
project mode still works.

## What it contributes

| Contribution | What it does |
| --- | --- |
| `gameblocks_index` (tool) | The module catalog with one-line capabilities — the agent's entry point. |
| `gameblocks_read_module` (tool) | Source of one or more blocks, for studying or adapting. |
| `gameblocks_game_template` (tool) | A complete, working starter HTML shell (import map, renderer, resize, focus-fixing start overlay, input, clamped-dt loop) with two marked replace-me sections — the agent never writes the boilerplate by hand. |
| `gameblocks_export_modules` (tool) | Copies blocks into a real project dir, preserving relative layout (project mode). Gate it off with `export_enabled: false`. |
| `gameblocks` (skill) | The compose-don't-derive workflow: WorldBasis as coordinate truth, artifact mode (with the runtime import-map preamble), project mode, controller↔camera pairings. |
| Module server (public router) | `GET /plugins/gameblocks/modules/<path>` + `/summary.md`, served with `Access-Control-Allow-Origin: *` so the opaque-origin artifact sandbox can import blocks over HTTP. Strictly allowlisted to the vendored tree. |

## Install

```
plugin install https://github.com/protoLabsAI/gameblocks-plugin
```

Ships `enabled: false` — enable it in Settings ▸ Plugins (install ≠ enable ≠ trust).

### Capabilities, honestly

The **server** makes no outbound calls and serves only vendored files. Game **pages**
reference pinned `cdn.jsdelivr.net` URLs for three.js 0.161 / Rapier3D 0.14 in the
browser (the pins come from upstream's `summary.md`). `gameblocks_export_modules` is
the only filesystem writer and has a config kill switch.

## Vendoring

`vendor/gameblocks/` is a verbatim copy of upstream's skill folder (MIT, © Weihao
Cheng), pinned in `vendor/UPSTREAM`. Re-vendor with:

```
scripts/sync_upstream.sh [ref]
```

then run `pytest` — the coherence tests catch summary↔disk drift and skill↔summary
CDN-pin drift. Upstream's own `SKILL.md` stays vendored for reference but is never
registered or served; the protoAgent-adapted skill lives in `skills/gameblocks/`.

## Dev

```
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt ruff
.venv/bin/pytest -q
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```

The suite is host-free: no protoAgent checkout needed (the host provides
`langchain-core` + `fastapi` at runtime; the plugin adds no runtime pip deps).
