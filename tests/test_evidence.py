"""Tests for the local evidence store."""

from __future__ import annotations

import hashlib

import pytest

from gavaza.cli import main
from gavaza.evidence import add_evidence, list_evidence, remove_evidence


def _sha256(path) -> str:
    """Return the sha256 of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_add_evidence_copies_file(gavaza_home, tmp_path) -> None:
    """Adding evidence must copy the file and record its hash."""
    source = tmp_path / "policy.pdf"
    source.write_bytes(b"policy-content")
    entry = add_evidence("acc-1", str(source), note="Board policy")
    assert entry.item_id == "acc-1"
    assert entry.note == "Board policy"
    stored = gavaza_home / "evidence" / entry.file
    assert stored.exists()
    assert _sha256(str(stored)) == _sha256(str(source))
    assert entry.sha256 == _sha256(str(source))


def test_add_evidence_validates_item_id(gavaza_home, tmp_path) -> None:
    """An unknown checklist item id must be rejected."""
    source = tmp_path / "x.txt"
    source.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown item"):
        add_evidence("nope-1", str(source))


def test_add_evidence_missing_file(gavaza_home, tmp_path) -> None:
    """A missing source file must raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        add_evidence("acc-1", str(tmp_path / "missing.pdf"))


def test_list_evidence_and_filter(gavaza_home, tmp_path) -> None:
    """List must return all entries and filter by item id."""
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    a.write_bytes(b"aaa")
    b.write_bytes(b"bbb")
    add_evidence("acc-1", str(a))
    add_evidence("pl-1", str(b))
    assert len(list_evidence()) == 2
    filtered = list_evidence(item_id="acc-1")
    assert len(filtered) == 1
    assert filtered[0].item_id == "acc-1"


def test_remove_evidence_deletes_file(gavaza_home, tmp_path) -> None:
    """Removing evidence must delete the copy and the index entry."""
    source = tmp_path / "a.pdf"
    source.write_bytes(b"aaa")
    entry = add_evidence("acc-1", str(source))
    assert remove_evidence(entry.id) is True
    stored = gavaza_home / "evidence" / entry.file
    assert not stored.exists()
    assert list_evidence() == []
    assert remove_evidence(entry.id) is False


def test_cli_evidence_flow(gavaza_home, tmp_path, capsys) -> None:
    """The evidence subcommands must work end to end."""
    assert main(["init", "--name", "Acme (Pty) Ltd"]) == 0
    capsys.readouterr()
    source = tmp_path / "assessment-evidence.txt"
    source.write_text("evidence", encoding="utf-8")
    assert main(["evidence", "add", "acc-1", str(source), "--note", "Proof"]) == 0
    out = capsys.readouterr().out
    assert "Evidence added" in out
    assert main(["evidence", "list"]) == 0
    out = capsys.readouterr().out
    assert "acc-1" in out
    evidence_id = out.split("|")[0].strip()
    assert main(["evidence", "remove", evidence_id]) == 0
    assert "Removed" in capsys.readouterr().out
    assert main(["evidence", "list"]) == 0
    assert "No evidence" in capsys.readouterr().out
