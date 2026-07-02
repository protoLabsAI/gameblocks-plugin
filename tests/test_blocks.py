"""The vendored tree + strict path resolution (the module server's security seam)."""

from __future__ import annotations

import re
from pathlib import Path

from gameblocks_plugin import blocks

ROOT = Path(__file__).resolve().parent.parent


def test_catalog_shape():
    cat = blocks.catalog()
    assert len(cat) >= 60, "vendor tree looks truncated — re-run scripts/sync_upstream.sh"
    assert all(p.startswith("modules/") and p.endswith(".js") for p in cat)
    assert "modules/math/WorldBasis.js" in cat


def test_summary_references_exist_on_disk():
    """Every `modules/...` path summary.md cites must be a vendored file — the
    coherence check that catches a bad upstream sync."""
    summary = blocks.summary_text()
    assert summary
    cited = set(re.findall(r"`(modules/[^`]+\.js)`", summary))
    assert cited, "summary.md cites no modules — upstream format changed?"
    missing = cited - set(blocks.catalog())
    assert not missing, f"summary.md cites modules not on disk: {sorted(missing)}"


def test_resolve_accepts_only_vendored_content():
    assert blocks.resolve("modules/math/WorldBasis.js") is not None
    assert blocks.resolve("summary.md") is not None
    # Upstream's SKILL.md is vendored for reference but never servable — the
    # registered skill is the adapted one in skills/gameblocks/.
    assert blocks.resolve("SKILL.md") is None


def test_resolve_rejects_traversal_and_junk():
    for bad in (
        "",
        "   ",
        "../__init__.py",
        "modules/../../__init__.py",
        "/etc/passwd",
        "modules/math/../../../__init__.py",
        "modules/math/nope.js",
        "UPSTREAM",
    ):
        assert blocks.resolve(bad) is None, f"resolve({bad!r}) should be None"


def test_export_preserves_layout(tmp_path):
    written = blocks.export(["modules/math/WorldBasis.js", "modules/camera/BaseCameraRig.js"], tmp_path)
    assert sorted(written) == ["modules/camera/BaseCameraRig.js", "modules/math/WorldBasis.js"]
    assert (tmp_path / "modules/math/WorldBasis.js").is_file()
    assert (tmp_path / "modules/camera/BaseCameraRig.js").is_file()


def test_export_is_all_or_nothing(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        blocks.export(["modules/math/WorldBasis.js", "modules/nope.js"], tmp_path)
    assert not (tmp_path / "modules").exists(), "a bad list must write nothing"
