"""Tests for the integration's manifest."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from awesomeversion import AwesomeVersion
from homeassistant.const import __version__ as HA_VERSION

REPO_ROOT = Path(__file__).parent.parent
MANIFEST = json.loads(
    (REPO_ROOT / "custom_components/hdfury_arcana/manifest.json").read_text()
)
HACS = json.loads((REPO_ROOT / "hacs.json").read_text())


def test_manifest_requires_what_the_tests_install():
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())

    assert MANIFEST["requirements"] == pyproject["project"]["dependencies"]


def test_tests_run_on_a_home_assistant_the_integration_supports():
    assert AwesomeVersion(HA_VERSION) >= AwesomeVersion(HACS["homeassistant"])
