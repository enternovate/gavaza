"""Tests for the data subject request workflow."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from gavaza.cli import main
from gavaza.config import data_dir
from gavaza.requests import (
    REQUEST_STATUSES,
    REQUEST_RIGHTS,
    list_requests,
    new_request,
    overdue_requests,
    update_status,
)


def test_new_request_creates_with_deadline(gavaza_home) -> None:
    """A new request must carry a 30-day deadline."""
    request = new_request(
        "A. Person", "a@example.com", "access", "Please send my records"
    )
    assert request.id.startswith("req-")
    received = datetime.fromisoformat(request.received_at)
    deadline = datetime.fromisoformat(request.deadline)
    assert deadline.date() == received.date() + timedelta(days=30)
    assert request.status == "open"


def test_new_request_validates_right(gavaza_home) -> None:
    """An unknown right must be rejected."""
    with pytest.raises(ValueError, match="right"):
        new_request("A. Person", "a@example.com", "nope", "x")


def test_list_requests_and_status_filter(gavaza_home) -> None:
    """List must return all requests and filter by status."""
    new_request("A. Person", "a@example.com", "access", "First")
    new_request("B. Person", "b@example.com", "objection", "Second")
    assert len(list_requests()) == 2
    assert len(list_requests(status="open")) == 2
    assert len(list_requests(status="completed")) == 0


def test_update_status_transitions(gavaza_home) -> None:
    """Status must transition through the allowed values."""
    request = new_request("A. Person", "a@example.com", "correction", "Fix my name")
    assert update_status(request.id, "in_progress") is True
    updated = list_requests()[0]
    assert updated.status == "in_progress"
    with pytest.raises(ValueError, match="status"):
        update_status(request.id, "bogus")


def test_overdue_requests_flags_past_deadline(gavaza_home) -> None:
    """Requests past their deadline must be flagged overdue."""
    new_request("A. Person", "a@example.com", "access", "Old request")
    store_path = data_dir() / "requests.json"
    entries = json.loads(store_path.read_text(encoding="utf-8"))
    past = (datetime.now(UTC).date() - timedelta(days=45)).isoformat()
    entries[0]["received_at"] = past
    entries[0]["deadline"] = past
    store_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    overdue = overdue_requests()
    assert len(overdue) == 1
    assert overdue[0].id == entries[0]["id"]


def test_request_statuses_and_rights_defined() -> None:
    """The status and right vocabularies must be non-empty."""
    assert {"open", "in_progress", "completed", "rejected"} <= set(REQUEST_STATUSES)
    assert {"access", "correction", "objection", "consent_withdrawal"} <= set(REQUEST_RIGHTS)


def test_cli_requests_flow(gavaza_home, capsys) -> None:
    """The requests subcommands must work end to end."""
    assert main([
        "requests", "new", "--name", "A. Person", "--email", "a@example.com",
        "--right", "access", "--description", "Send my records",
    ]) == 0
    assert "req-1" in capsys.readouterr().out
    assert main(["requests", "list"]) == 0
    out = capsys.readouterr().out
    assert "A. Person" in out
    assert "open" in out
    assert main(["requests", "status", "req-1", "completed"]) == 0
    assert main(["requests", "list", "--status", "completed"]) == 0
    out = capsys.readouterr().out
    assert "req-1" in out
    assert main(["requests", "overdue"]) == 0
    assert "No overdue" in capsys.readouterr().out
