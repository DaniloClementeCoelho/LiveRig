"""Persisted application settings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import SETTINGS_FILE, SHOWS_DIR


class AppSettings:
    """Loads and saves simple user preferences."""

    def __init__(self, path: Path = SETTINGS_FILE) -> None:
        self.path = path

    def load_shows_dir(self) -> Path:
        """Return the configured shows directory or the project default."""
        data = self._read()
        value = data.get("shows_dir")
        if isinstance(value, str) and value.strip():
            return Path(value)

        return SHOWS_DIR

    def save_shows_dir(self, shows_dir: Path) -> None:
        """Persist the shows directory."""
        self.path.write_text(
            json.dumps({"shows_dir": str(shows_dir)}, indent=4),
            encoding="utf-8",
        )

    def _read(self) -> dict[str, Any]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

        if not isinstance(data, dict):
            return {}

        return data
