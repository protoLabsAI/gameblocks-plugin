"""The module server, exercised on the ACTUAL registered prefix (not a re-mount)."""

from __future__ import annotations


def test_register_contributions(registry):
    assert [t.name for t in registry.tools] == [
        "gameblocks_index",
        "gameblocks_read_module",
        "gameblocks_game_template",
        "gameblocks_export_modules",
    ]
    assert registry.skill_dirs == ["skills"]
    # ONE public router, NO gated /api router — there is no mutable state to protect,
    # and the game sandbox (opaque origin, no bearer) must be able to import modules.
    assert [prefix for _, prefix in registry.routers] == ["/plugins/gameblocks"]


def test_module_served_with_cors(client):
    r = client.get("/plugins/gameblocks/modules/math/WorldBasis.js")
    assert r.status_code == 200
    assert "WorldBasis" in r.text
    assert r.headers["content-type"].startswith("text/javascript")
    assert r.headers["access-control-allow-origin"] == "*"
    assert "max-age" in r.headers.get("cache-control", "")


def test_summary_served(client):
    r = client.get("/plugins/gameblocks/summary.md")
    assert r.status_code == 200
    assert "GameBlocks Modules Summary" in r.text
    assert r.headers["access-control-allow-origin"] == "*"


def test_unknown_and_traversal_404(client):
    assert client.get("/plugins/gameblocks/modules/math/nope.js").status_code == 404
    # Encoded traversal reaches the handler un-normalized; resolve() must refuse it.
    assert client.get("/plugins/gameblocks/modules/..%2f..%2f__init__.py").status_code == 404
    assert client.get("/plugins/gameblocks/modules/%2e%2e/%2e%2e/blocks.py").status_code == 404
    # Upstream SKILL.md is vendored but not servable.
    assert client.get("/plugins/gameblocks/modules/../SKILL.md").status_code in (404, 400)


def test_nothing_under_api(client):
    assert client.get("/api/plugins/gameblocks/modules/math/WorldBasis.js").status_code == 404
