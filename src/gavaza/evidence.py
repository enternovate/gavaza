"""Local evidence store for compliance assessments.

Evidence links a file (or note) to one checklist item so the company
can demonstrate compliance. Files are copied into the Gavaza evidence
directory and hashed with SHA-256. The index lives in
``evidence/index.json`` under the Gavaza home. Everything stays local.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gavaza.config import data_dir
from gavaza.conditions import item_lookup
from gavaza.sections import section_lookup

INDEX_FILENAME = "index.json"


@dataclass
class EvidenceEntry:
    """One evidence record attached to a checklist item."""

    id: str
    item_id: str
    file: str
    sha256: str
    note: str
    date: str

    def to_dict(self) -> dict[str, str]:
        """Return the entry as a plain dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> EvidenceEntry:
        """Build an entry from a dict."""
        return cls(
            id=str(raw["id"]),
            item_id=str(raw["item_id"]),
            file=str(raw["file"]),
            sha256=str(raw["sha256"]),
            note=str(raw.get("note", "")),
            date=str(raw.get("date", "")),
        )


def _known_item_ids() -> set[str]:
    """Return every valid checklist item id across conditions and sections."""
    ids = set(item_lookup())
    ids.update(section_lookup())
    return ids


def _sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence_dir(home: Path | None = None) -> Path:
    """Return the evidence directory, creating it if necessary."""
    path = (home or data_dir()) / "evidence"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _index_path(home: Path | None = None) -> Path:
    """Return the evidence index path."""
    return evidence_dir(home) / INDEX_FILENAME


def _load_index(home: Path | None = None) -> list[EvidenceEntry]:
    """Load the evidence index, returning an empty list when absent."""
    path = _index_path(home)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [EvidenceEntry.from_dict(entry) for entry in raw]


def _save_index(entries: list[EvidenceEntry], home: Path | None = None) -> None:
    """Atomically write the evidence index."""
    path = _index_path(home)
    directory = path.parent
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".index-", suffix=".tmp")
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


def add_evidence(
    item_id: str,
    source_path: str | Path,
    note: str = "",
    home: Path | None = None,
) -> EvidenceEntry:
    """Copy ``source_path`` into the evidence store and index it.

    Raises:
        ValueError: when the item id is unknown.
        FileNotFoundError: when the source file does not exist.
    """
    if item_id not in _known_item_ids():
        raise ValueError(f"unknown item id {item_id!r}")
    source = Path(source_path)
    if not source.is_file():
        raise FileNotFoundError(f"no such file: {source}")
    target_dir = evidence_dir(home)
    entries = _load_index(home)
    seq = len(entries) + 1
    while True:
        file_name = f"ev-{seq}-{source.name}"
        target = target_dir / file_name
        if not target.exists():
            break
        seq += 1
    shutil.copy2(source, target)
    entry = EvidenceEntry(
        id=f"ev-{seq}",
        item_id=item_id,
        file=file_name,
        sha256=_sha256(target),
        note=note,
        date=datetime.now(UTC).date().isoformat(),
    )
    entries.append(entry)
    _save_index(entries, home)
    return entry


def list_evidence(
    item_id: str | None = None,
    home: Path | None = None,
) -> list[EvidenceEntry]:
    """Return evidence entries, optionally filtered by item id."""
    entries = _load_index(home)
    if item_id is not None:
        entries = [entry for entry in entries if entry.item_id == item_id]
    return entries


def remove_evidence(evidence_id: str, home: Path | None = None) -> bool:
    """Remove an evidence entry and its copied file.

    Returns True when the entry existed and was removed.
    """
    entries = _load_index(home)
    for index, entry in enumerate(entries):
        if entry.id == evidence_id:
            del entries[index]
            _save_index(entries, home)
            target = evidence_dir(home) / entry.file
            if target.exists():
                target.unlink()
            return True
    return False
