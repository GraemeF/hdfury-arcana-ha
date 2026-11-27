"""Tests for the integration's manifest."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MANIFEST = json.loads(
    (REPO_ROOT / "custom_components/hdfury_arcana/manifest.json").read_text()
)


def test_manifest_requires_what_the_tests_install():
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())

    assert MANIFEST["requirements"] == pyproject["project"]["dependencies"]
