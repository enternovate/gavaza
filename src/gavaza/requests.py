"""Data subject request (DSR) workflow.

Tracks requests under POPIA sections 23-25: intake, status, and the
response deadline. The deadline follows the Information Regulator's
guidance convention of 30 days from receipt. All data lives in
``requests.json`` under the Gavaza home.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from gavaza.config import data_dir

STORE_FILENAME = "requests.json"

#: The 30-day response convention from the Information Regulator's guidance.
RESPONSE_DEADLINE_DAYS = 30

REQUEST_RIGHTS = ("access", "correction", "objection", "consent_withdrawal")
REQUEST_STATUSES = ("open", "in_progress", "completed", "rejected")


@dataclass
class DsrRequest:
    """One data subject request."""

    id: str
    requester_name: str
    requester_email: str
    right: str
    description: str
    received_at: str
    deadline: str
    status: str
    status_updated_at: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return the request as a plain dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> DsrRequest:
        """Build a request from a dict, tolerating missing notes."""
        return cls(
            id=str(raw["id"]),
            requester_name=str(raw["requester_name"]),
            requester_email=str(raw["requester_email"]),
            right=str(raw["right"]),
            description=str(raw.get("description", "")),
            received_at=str(raw["received_at"]),
            deadline=str(raw["deadline"]),
            status=str(raw["status"]),
            status_updated_at=str(raw.get("status_updated_at", "")),
            notes=str(raw.get("notes", "")),
        )

    @property
    def overdue(self) -> bool:
        """Return True when the request is open and past its deadline."""
        if self.status not in ("open", "in_progress"):
            return False
        try:
            deadline = date.fromisoformat(self.deadline)
        except ValueError:
            return False
        return deadline < datetime.now(UTC).date()


def _store_path(home: Path | None = None) -> Path:
    """Return the requests store path."""
    return (home or data_dir()) / STORE_FILENAME


def _load(home: Path | None = None) -> list[DsrRequest]:
    """Load the request list, returning an empty list when absent."""
    path = _store_path(home)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [DsrRequest.from_dict(entry) for entry in raw]


def _save(entries: list[DsrRequest], home: Path | None = None) -> None:
    """Atomically write the request list."""
    path = _store_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=".requests-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(
                [entry.to_dict() for entry in entries],
                fh,
                indent=2,
                ensure_ascii=False,
            )
            fh.write("\n")
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def new_request(
    requester_name: str,
    requester_email: str,
    right: str,
    description: str,
    notes: str = "",
    home: Path | None = None,
) -> DsrRequest:
    """Create a new data subject request with a 30-day deadline.

    Raises:
        ValueError: when the right is unknown or the name is empty.
    """
    if right not in REQUEST_RIGHTS:
        raise ValueError(
            f"unknown right {right!r}; expected one of {', '.join(REQUEST_RIGHTS)}"
        )
    if not requester_name.strip():
        raise ValueError("requester name must be non-empty")
    entries = _load(home)
    seq = len(entries) + 1
    today = datetime.now(UTC).date()
    request = DsrRequest(
        id=f"req-{seq}",
        requester_name=requester_name.strip(),
        requester_email=requester_email.strip(),
        right=right,
        description=description.strip(),
        received_at=today.isoformat(),
        deadline=(today + timedelta(days=RESPONSE_DEADLINE_DAYS)).isoformat(),
        status="open",
        status_updated_at=today.isoformat(),
        notes=notes.strip(),
    )
    entries.append(request)
    _save(entries, home)
    return request


def list_requests(
    status: str | None = None,
    home: Path | None = None,
) -> list[DsrRequest]:
    """Return requests, newest first, optionally filtered by status."""
    entries = _load(home)
    entries.sort(key=lambda entry: entry.received_at, reverse=True)
    if status is not None:
        entries = [entry for entry in entries if entry.status == status]
    return entries


def update_status(
    request_id: str,
    status: str,
    home: Path | None = None,
) -> bool:
    """Set the status of a request.

    Raises:
        ValueError: when the status is unknown.
    Returns True when the request existed and was updated.
    """
    if status not in REQUEST_STATUSES:
        raise ValueError(
            f"unknown status {status!r}; expected one of {', '.join(REQUEST_STATUSES)}"
        )
    entries = _load(home)
    for entry in entries:
        if entry.id == request_id:
            entry.status = status
            entry.status_updated_at = datetime.now(UTC).date().isoformat()
            _save(entries, home)
            return True
    return False


def overdue_requests(home: Path | None = None) -> list[DsrRequest]:
    """Return open requests past their response deadline."""
    return [entry for entry in _load(home) if entry.overdue]
