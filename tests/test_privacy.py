"""Privacy guards for Gavaza: zero telemetry, private permissions."""

from __future__ import annotations

import os
import socket
from pathlib import Path

from gavaza.cli import main
from gavaza.config import data_dir

REPO = Path(__file__).resolve().parents[1]

_NETWORK_MARKERS = ("import socket", "import urllib", "import httplib", "import http.client",
                    "import requests", "import aiohttp", "urlopen", "getaddrinfo")


def test_no_network_imports_anywhere() -> None:
    """No gavaza module may import networking primitives."""
    for module in sorted((REPO / "src" / "gavaza").glob("*.py")):
        source = module.read_text(encoding="utf-8")
        for marker in _NETWORK_MARKERS:
            assert marker not in source, f"{module.name} contains {marker!r}"


def test_home_dir_is_0700(gavaza_home) -> None:
    """The Gavaza home must use mode 0700."""
    assert os.stat(data_dir()).st_mode & 0o777 == 0o700


def test_offline_cli_commands_never_touch_network(gavaza_home, capsys, monkeypatch) -> None:
    """Reference commands must succeed with the network blocked."""
    def blocked(*args, **kwargs):  # noqa: ARG001 - deliberate blocker
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", blocked)
    assert main(["conditions"]) == 0
    assert main(["sections"]) == 0
    assert main(["gdpr-map"]) == 0
