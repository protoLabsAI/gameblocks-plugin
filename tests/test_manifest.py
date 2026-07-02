"""Manifest coherence: data-only invariants the host relies on."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _manifest() -> dict:
    return yaml.safe_load((ROOT / "protoagent.plugin.yaml").read_text(encoding="utf-8"))


def test_identity_and_trust_posture():
    m = _manifest()
    assert m["id"] == "gameblocks"
    assert m["enabled"] is False  # ships disabled — enabling is the operator's call
    assert m["config_section"] == "gameblocks"  # a string, not a list
    assert "views" not in m  # v0.1 is lean: the artifact panel is the play surface


def test_version_lockstep_with_pyproject():
    m = _manifest()
    py = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', py, re.M)
    assert match, "pyproject.toml has no version"
    assert m["version"] == match.group(1)


def test_capabilities_declared():
    m = _manifest()
    caps = m["capabilities"]
    assert caps["network"] == []  # the server itself makes no outbound calls
    assert caps["filesystem"] == "scoped"
    assert m["config"]["export_enabled"] is True


def test_no_secrets_no_pip():
    m = _manifest()
    assert not m.get("secrets")
    assert not m.get("requires_pip")
    assert not m.get("requires_env")
