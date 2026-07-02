"""gameblocks — GameBlocks building blocks for browser 3D games (xt4d/GameBlocks).

Contributes: three tools (index / read / export over the vendored block library), a
skill teaching the agent the compose-don't-derive workflow, and a public CORS module
server so a game artifact can import blocks over HTTP instead of inlining 500 KB of
source. Rendering is the artifact plugin's job (soft pairing — nothing imports across
plugins): the skill tells the agent to ship the game via ``show_artifact``.

Module top stays stdlib+langchain-core only, and even the relative imports are lazy:
pytest's Package collector imports this file bare (no package context), and the host
suite must import it with no protoAgent present.
"""

from __future__ import annotations

import logging

from langchain_core.tools import tool

log = logging.getLogger("protoagent.plugins.gameblocks")

# Set at register() so tools read live config (Settings edits apply without restart).
_REGISTRY = None


def _cfg() -> dict:
    try:
        return dict(getattr(_REGISTRY, "config", None) or {})
    except Exception:  # noqa: BLE001 — config read must never break a tool
        return {}


def _export_enabled() -> bool:
    v = _cfg().get("export_enabled", True)
    return str(v).strip().lower() not in {"0", "false", "no", "off"}


_INDEX_HEADER = """\
GameBlocks: proven three.js building blocks for browser 3D games — compose these
instead of deriving coordinate frames / motion / camera math from scratch.
Load the `gameblocks` skill for the full workflow (artifact mode vs project mode).
Read source with gameblocks_read_module(path); copy into a real project with
gameblocks_export_modules(paths, dest_dir). A running game page can also import a
block over HTTP: <host>/plugins/gameblocks/modules/<path-under-modules>.

"""


@tool
def gameblocks_index() -> str:
    """List the GameBlocks catalog: 74 vendored three.js building-block modules for
    browser 3D games — coordinate frames, actor-motion controllers, camera rigs,
    behaviors (path planning, steering, combat), gameplay loops (combat, racing,
    flight), world/environment builders, and HUD/minimap UI — each with a one-line
    capability summary. Call this FIRST when building or revising a 3D game, then
    read or export the modules you pick; prefer an existing block over writing new
    3D math."""
    from . import blocks

    text = blocks.summary_text()
    if not text:
        return "GameBlocks vendor tree is missing — reinstall the gameblocks plugin."
    return _INDEX_HEADER + text


@tool
def gameblocks_read_module(paths: str) -> str:
    """Return the source of one or more vendored GameBlocks modules. `paths` takes
    catalog paths from gameblocks_index (e.g. 'modules/math/WorldBasis.js'),
    comma- or newline-separated for several at once. Use it to study a block's
    contract before importing it over HTTP, or to adapt a copy before inlining it
    into a game artifact."""
    from . import blocks

    wanted = blocks.split_paths(paths)
    if not wanted:
        return "No paths given — pass catalog paths from gameblocks_index."
    out: list[str] = []
    for rel in wanted:
        src = blocks.read_module(rel)
        if src is None:
            close = blocks.suggest(rel)
            hint = f" Did you mean: {', '.join(close)}?" if close else ""
            out.append(f"// !! No vendored module {rel!r}.{hint}")
        else:
            out.append(f"// ── {rel} ──\n{src}")
    return "\n\n".join(out)


@tool
def gameblocks_export_modules(paths: str, dest_dir: str) -> str:
    """Copy vendored GameBlocks modules into a project directory, preserving their
    relative layout so inter-module imports keep working (project mode — building a
    game in a real repo rather than an artifact). `paths` is comma- or
    newline-separated catalog paths, or 'all' for the whole library; `dest_dir` is
    the project source directory to copy into. Returns the files written."""
    from . import blocks

    if not _export_enabled():
        return (
            "Module export is disabled (gameblocks.export_enabled=false). "
            "Read modules with gameblocks_read_module instead."
        )
    raw = (paths or "").strip()
    wanted = blocks.catalog() if raw.lower() == "all" else blocks.split_paths(raw)
    if not wanted:
        return "No paths given — pass catalog paths from gameblocks_index, or 'all'."
    if not (dest_dir or "").strip():
        return "No dest_dir given — pass the project source directory to copy into."
    try:
        written = blocks.export(wanted, dest_dir)
    except ValueError as e:
        return f"Export aborted (nothing written): {e}. Check paths against gameblocks_index."
    except OSError as e:
        return f"Export failed: {e}"
    listing = "\n".join(f"  {p}" for p in written)
    return f"Exported {len(written)} module(s) into {dest_dir}:\n{listing}"


def register(registry) -> None:
    global _REGISTRY
    _REGISTRY = registry

    for t in (gameblocks_index, gameblocks_read_module, gameblocks_export_modules):
        registry.register_tool(t)

    try:
        # The adapted skill (skills/gameblocks/SKILL.md) — teaches compose-don't-derive
        # plus the artifact-mode import-map preamble. Upstream's SKILL.md stays vendored
        # for reference but is never registered or served.
        registry.register_skill_dir("skills")
    except Exception:  # noqa: BLE001
        log.exception("[gameblocks] registering skill dir failed")

    try:
        from .routes import build_public_router

        registry.register_router(build_public_router(), prefix="/plugins/gameblocks")
    except Exception:  # noqa: BLE001
        log.exception("[gameblocks] mounting module server failed")

    try:
        from . import blocks

        log.info("[gameblocks] registered (%d modules vendored)", len(blocks.catalog()))
    except Exception:  # noqa: BLE001
        log.info("[gameblocks] registered")
