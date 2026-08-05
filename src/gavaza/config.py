"""Company configuration and Gavaza data directory handling.

Gavaza keeps its working data (company config, assessment results, generated
documents, breach register) in a data directory. The default is ``~/.gavaza``;
set the ``GAVAZA_HOME`` environment variable to override it.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_HOME_NAME = ".gavaza"
CONFIG_FILENAME = "company.json"
DOCS_DIRNAME = "docs"


@dataclass
class Company:
    """The organisation (responsible party) Gavaza produces documents for."""

    name: str
    reg_no: str = ""
    address: str = ""
    email: str = ""
    info_officer: str = ""
    contact: str = ""

    def to_dict(self) -> dict[str, str]:
        """Return the company as a plain JSON-serialisable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Company:
        """Build a Company from a dictionary, tolerating unknown keys."""
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{key: value for key, value in data.items() if key in known})


def data_dir() -> Path:
    """Return the Gavaza data directory, creating it if necessary.

    ``GAVAZA_HOME`` overrides the default ``~/.gavaza``.
    """
    override = os.environ.get("GAVAZA_HOME")
    base = Path(override).expanduser() if override else Path.home() / DEFAULT_HOME_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def config_path(home: Path | None = None) -> Path:
    """Return the path of the company configuration file."""
    return (home or data_dir()) / CONFIG_FILENAME


def docs_dir(home: Path | None = None) -> Path:
    """Return the directory generated documents are written to."""
    path = (home or data_dir()) / DOCS_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_config(path: Path | None = None) -> Company:
    """Load the company configuration from JSON.

    Raises FileNotFoundError when no configuration exists yet.
    """
    target = path or config_path()
    with target.open("r", encoding="utf-8") as handle:
        return Company.from_dict(json.load(handle))


def save_config(company: Company, path: Path | None = None) -> Path:
    """Persist the company configuration to JSON and return its path."""
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(company.to_dict(), handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return target
