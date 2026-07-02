"""The three tools, driven the way the agent drives them (tool.invoke)."""

from __future__ import annotations

from conftest import FakeRegistry


def test_docstrings_are_real_descriptions(plugin):
    # The @tool description is the docstring; an f-string "docstring" would ship None.
    for t in (
        plugin.gameblocks_index,
        plugin.gameblocks_read_module,
        plugin.gameblocks_game_template,
        plugin.gameblocks_export_modules,
    ):
        assert isinstance(t.description, str) and len(t.description) > 40


def test_game_template_tool_returns_the_shell(plugin):
    out = plugin.gameblocks_game_template.invoke({})
    assert out.lower().startswith("<!doctype html>")
    assert "GAME SETUP (replace)" in out
    assert "UPDATE (replace)" in out


def test_index_returns_catalog(plugin):
    out = plugin.gameblocks_index.invoke({})
    assert "WorldBasis" in out
    assert "modules/" in out
    assert "gameblocks_read_module" in out  # the header teaches the next step


def test_read_module_single_and_multi(plugin):
    one = plugin.gameblocks_read_module.invoke({"paths": "modules/math/WorldBasis.js"})
    assert "── modules/math/WorldBasis.js ──" in one
    assert "WorldBasis" in one

    multi = plugin.gameblocks_read_module.invoke(
        {"paths": "modules/math/WorldBasis.js, modules/camera/BaseCameraRig.js"}
    )
    assert "── modules/math/WorldBasis.js ──" in multi
    assert "── modules/camera/BaseCameraRig.js ──" in multi


def test_read_module_unknown_suggests(plugin):
    out = plugin.gameblocks_read_module.invoke({"paths": "modules/math/WorldBases.js"})
    assert "No vendored module" in out
    assert "WorldBasis.js" in out  # close-match hint


def test_export_tool_writes(plugin, tmp_path):
    plugin.register(FakeRegistry({"export_enabled": True}))
    out = plugin.gameblocks_export_modules.invoke({"paths": "modules/math/WorldBasis.js", "dest_dir": str(tmp_path)})
    assert "Exported 1 module(s)" in out
    assert (tmp_path / "modules/math/WorldBasis.js").is_file()


def test_export_all(plugin, tmp_path):
    plugin.register(FakeRegistry({"export_enabled": True}))
    from gameblocks_plugin import blocks

    out = plugin.gameblocks_export_modules.invoke({"paths": "all", "dest_dir": str(tmp_path)})
    assert f"Exported {len(blocks.catalog())} module(s)" in out


def test_export_respects_kill_switch(plugin, tmp_path):
    plugin.register(FakeRegistry({"export_enabled": False}))
    try:
        out = plugin.gameblocks_export_modules.invoke(
            {"paths": "modules/math/WorldBasis.js", "dest_dir": str(tmp_path)}
        )
        assert "disabled" in out
        assert not (tmp_path / "modules").exists()
    finally:
        plugin.register(FakeRegistry())  # restore live-config default for other tests
