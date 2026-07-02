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


def test_body_teaches_the_pairing_and_the_template():
    _, body = _parts()
    # The tool loop, template-first
    assert "gameblocks_index" in body
    assert "gameblocks_read_module" in body
    assert "gameblocks_game_template" in body
    assert "gameblocks_export_modules" in body
    # Artifact pairing (soft — by tool name, never a cross-plugin import)
    assert "show_artifact" in body
    # The sandbox invariant the template encodes
    assert "document.baseURI" in body
    # Coordinate discipline
    assert "WorldBasis" in body


def _template() -> str:
    return (ROOT / "templates" / "game.html").read_text(encoding="utf-8")


def test_template_shell_is_complete():
    """The single source of the boilerplate: preamble + the pieces the agent must not
    have to rewrite, and the two sections it must."""
    t = _template()
    assert 'type = "importmap"' in t or "importmap" in t
    assert "document.baseURI" in t
    assert '"/plugins/"' in t  # slug-safe base split
    assert '"gameblocks/": GB_ROOT + "/plugins/gameblocks/"' in t
    assert "GAME SETUP (replace)" in t
    assert "UPDATE (replace)" in t
    assert "requestPointerLock" in t  # the mouse-look hint lives where it's used
    # The preamble script precedes the module script (import map before any module load).
    assert t.index("importmap") < t.index('type="module"')


def test_template_pins_match_vendored_summary():
    """The CDN pins in the template must match the deps upstream declares in summary.md."""
    from gameblocks_plugin import blocks

    t = _template()
    summary = blocks.summary_text()
    for lib in ("three@", "rapier3d-compat@"):
        pin_in_summary = [ln for ln in summary.splitlines() if lib in ln]
        assert pin_in_summary, f"summary.md no longer pins {lib}"
        version = pin_in_summary[0].split(lib)[1].split("/")[0]
        assert f"{lib}{version}" in t, f"template pin for {lib} drifted from summary.md ({version})"
