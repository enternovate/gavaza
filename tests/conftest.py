"""Shared fixtures and sys.path setup for the Gavaza test suite.

The package is laid out under ``src/``; tests insert it on ``sys.path`` so the
suite runs without an editable install.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def company():
    """A realistic responsible-party configuration for document tests."""
    from gavaza.config import Company

    return Company(
        name="Springbok Solutions (Pty) Ltd",
        reg_no="2026/123456/07",
        address="1 Fynbos Avenue, Cape Town, 8001",
        email="info@springboksolutions.co.za",
        info_officer="Thandi Nkosi",
        contact="+27 21 555 0100",
    )


@pytest.fixture
def gavaza_home(tmp_path, monkeypatch):
    """Point GAVAZA_HOME at a fresh temporary directory for CLI tests."""
    home = tmp_path / "gavaza_home"
    monkeypatch.setenv("GAVAZA_HOME", str(home))
    return home
