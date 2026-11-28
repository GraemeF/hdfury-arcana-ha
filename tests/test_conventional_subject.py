"""Tests for the check CI makes on a pull request's title."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts/conventional-subject.sh"


def check(subject: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [SCRIPT, subject], capture_output=True, text=True, check=False
    )


@pytest.mark.parametrize(
    "subject",
    [
        "fix: read an unanswered signal parameter as unknown",
        "feat(config_flow): set the integration up by its esphome:// URL",
        "chore!: drop support for Home Assistant 2025",
        "ci(deps): pin every action to a commit sha",
        "docs: name HACS as the way to install",
        "fix: " + "a" * 67,
    ],
)
def test_accepts_a_conventional_commit(subject):
    result = check(subject)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("subject", "reason"),
    [
        ("Read an unanswered signal parameter as unknown", "type(scope): description"),
        ("Release v0.5.0-beta.1", "type(scope): description"),
        ("wip: try something", "type(scope): description"),
        ("fix:no space", "type(scope): description"),
        ("fix(): empty scope", "type(scope): description"),
        ("fix: ", "type(scope): description"),
        ("fix: end with a full stop.", "full stop"),
        ("fix: " + "a" * 68, "72 characters"),
    ],
)
def test_refuses_anything_else(subject, reason):
    result = check(subject)

    assert result.returncode == 1
    assert reason in result.stderr
    assert "CONTRIBUTING.md" in result.stderr
