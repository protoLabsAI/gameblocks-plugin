"""Test bootstrap — import the plugin with NO protoAgent host.

The host loads a plugin as a package; the suite registers the same shape as a
synthetic package (``gameblocks_plugin``) whose __path__ is the repo root, so the
relative imports (``from . import blocks``) resolve standalone. Executing
``__init__.py`` is safe: host-only wiring lives inside ``register()``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PKG = "gameblocks_plugin"

if PKG not in sys.modules:
    _spec = importlib.util.spec_from_file_location(PKG, ROOT / "__init__.py", submodule_search_locations=[str(ROOT)])
    assert _spec and _spec.loader
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[PKG] = _mod
    _spec.loader.exec_module(_mod)


class FakeRegistry:
    """Records contributions the way the host registry would receive them."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.tools: list = []
        self.routers: list[tuple[object, str]] = []
        self.skill_dirs: list[str] = []

    def register_tool(self, t):
        self.tools.append(t)

    def register_router(self, router, prefix):
        self.routers.append((router, prefix))

    def register_skill_dir(self, path):
        self.skill_dirs.append(str(path))


@pytest.fixture
def plugin():
    return sys.modules[PKG]


@pytest.fixture
def registry(plugin):
    reg = FakeRegistry()
    plugin.register(reg)
    return reg


@pytest.fixture
def client(registry):
    """An app serving EXACTLY what register() mounted — the actual registered path,
    not the rule-compliant one."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    for router, prefix in registry.routers:
        app.include_router(router, prefix=prefix)
    return TestClient(app)
