"""The adapted skill: registered shape + the load-bearing content the agent follows."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "gameblocks" / "SKILL.md"


def _parts() -> tuple[dict, str]:
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    front, body = text.split("---\n", 2)[1:]
    meta = {}
    for line in front.strip().splitlines():
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip()
    return meta, body


def test_frontmatter():
    meta, _ = _parts()
    assert meta["name"] == "gameblocks"
    assert "3D game" in meta["description"]


def test_body_teaches_the_pairing_and_the_preamble():
    _, body = _parts()
    # The tool loop
    assert "gameblocks_index" in body
    assert "gameblocks_read_module" in body
    assert "gameblocks_export_modules" in body
    # Artifact pairing (soft — by tool name, never a cross-plugin import)
    assert "show_artifact" in body
    # The import-map preamble and its two invariants
    assert "importmap" in body
    assert "document.baseURI" in body
    assert "/plugins/gameblocks" in body
    # Coordinate discipline
    assert "WorldBasis" in body


def test_pins_match_vendored_summary():
    """The CDN pins in the skill must match the deps upstream declares in summary.md."""
    from gameblocks_plugin import blocks

    _, body = _parts()
    summary = blocks.summary_text()
    for lib in ("three@", "rapier3d-compat@"):
        pin_in_summary = [ln for ln in summary.splitlines() if lib in ln]
        assert pin_in_summary, f"summary.md no longer pins {lib}"
        version = pin_in_summary[0].split(lib)[1].split("/")[0]
        assert f"{lib}{version}" in body, f"skill pin for {lib} drifted from summary.md ({version})"
