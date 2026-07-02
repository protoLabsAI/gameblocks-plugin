"""Access to the vendored GameBlocks tree (vendor/gameblocks/).

Pure stdlib — no host imports — so the test suite runs with no protoAgent present.
All paths the tools and the module server accept are *vendored-relative* POSIX paths
("modules/math/WorldBasis.js", "summary.md") and resolve strictly inside the vendor
root: no traversal, no symlink escape, .js modules + summary.md only. Upstream's own
SKILL.md is deliberately NOT servable — this plugin registers its adapted skill from
skills/gameblocks/ instead.
"""

from __future__ import annotations

import difflib
import shutil
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent
VENDOR_ROOT = PLUGIN_DIR / "vendor" / "gameblocks"


def catalog() -> list[str]:
    """Sorted vendored-relative paths of every block module."""
    root = VENDOR_ROOT / "modules"
    if not root.is_dir():
        return []
    return sorted(p.relative_to(VENDOR_ROOT).as_posix() for p in root.rglob("*.js") if p.is_file())


def summary_text() -> str:
    try:
        return (VENDOR_ROOT / "summary.md").read_text(encoding="utf-8")
    except OSError:
        return ""


def resolve(rel: str) -> Path | None:
    """A vendored-relative path -> the real file, or None for anything else."""
    rel = (rel or "").strip().lstrip("/")
    if not rel:
        return None
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts:
        return None
    f = VENDOR_ROOT / p
    try:
        f = f.resolve()
        f.relative_to(VENDOR_ROOT.resolve())
    except (OSError, ValueError):
        return None
    if not f.is_file():
        return None
    if f.suffix != ".js" and f.name != "summary.md":
        return None
    return f


def read_module(rel: str) -> str | None:
    f = resolve(rel)
    if f is None:
        return None
    try:
        return f.read_text(encoding="utf-8")
    except OSError:
        return None


def suggest(rel: str, n: int = 5) -> list[str]:
    """Closest catalog paths to a mistyped one (for tool error messages)."""
    return difflib.get_close_matches((rel or "").strip(), catalog(), n=n, cutoff=0.4)


def split_paths(raw: str) -> list[str]:
    """One-or-more paths from a tool argument: comma / newline / whitespace separated."""
    parts = (raw or "").replace(",", "\n").split()
    return [p for p in parts if p]


def export(paths: list[str], dest_dir: str | Path) -> list[str]:
    """Copy modules into ``dest_dir`` preserving their relative layout.

    ``paths`` are catalog paths (or the whole catalog for "all" — the caller expands
    it). Validates every path BEFORE writing anything, so a bad list is atomic-ish:
    nothing is copied. Returns the vendored-relative paths written.
    """
    resolved: list[tuple[str, Path]] = []
    for rel in paths:
        f = resolve(rel)
        if f is None or f.suffix != ".js":
            raise ValueError(f"unknown module {rel!r}")
        resolved.append((Path(rel).as_posix(), f))
    dest = Path(dest_dir).expanduser()
    written: list[str] = []
    for rel, src in resolved:
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, out)
        written.append(rel)
    return written
