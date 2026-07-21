"""Scan song packages from the filesystem."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from models import Song


class SongManager:
    """Loads songs from a directory of independent song folders."""

    def __init__(self, shows_dir: Path) -> None:
        self.shows_dir = shows_dir

    def load_songs(self) -> list[Song]:
        """Return all valid songs found in the shows directory."""
        if not self.shows_dir.exists():
            return []

        songs: list[Song] = []
        for folder in sorted(self.shows_dir.iterdir(), key=lambda path: path.name.lower()):
            if not folder.is_dir():
                continue

            song = self._load_song(folder)
            if song is not None:
                songs.append(song)

        return songs

    def _load_song(self, folder: Path) -> Optional[Song]:
        config_path = folder / "config.json"
        if not config_path.exists():
            return None

        data = self._read_json(config_path)
        if data is None:
            return None

        title = str(data.get("title") or folder.name)
        artist = str(data.get("artist") or "")
        project_path = self._resolve_required_file(folder, data.get("project"))
        if project_path is None:
            return None

        lyrics_path = self._resolve_optional_file(folder, data.get("lyrics"))
        notes_path = self._resolve_optional_file(folder, data.get("notes"))
        cover_path = self._resolve_optional_file(folder, data.get("cover"))

        known_fields = {
            "title",
            "artist",
            "project",
            "lyrics",
            "notes",
            "cover",
            "patch",
            "tuning",
            "bpm",
            "duration",
        }

        return Song(
            title=title,
            artist=artist,
            folder=folder,
            project_path=project_path,
            lyrics_path=lyrics_path,
            notes_path=notes_path,
            cover_path=cover_path,
            patch=self._optional_int(data.get("patch")),
            tuning=self._optional_str(data.get("tuning")),
            bpm=self._optional_int(data.get("bpm")),
            duration=self._optional_int(data.get("duration")),
            lyrics=self._read_text(lyrics_path),
            notes=self._read_text(notes_path),
            extra={key: value for key, value in data.items() if key not in known_fields},
        )

    def _read_json(self, path: Path) -> Optional[dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return None

        if not isinstance(data, dict):
            return None

        return data

    def _resolve_required_file(self, folder: Path, value: object) -> Optional[Path]:
        if not isinstance(value, str) or not value.strip():
            return None

        path = folder / value
        if not path.exists() or not path.is_file():
            return None

        return path

    def _resolve_optional_file(self, folder: Path, value: object) -> Optional[Path]:
        if not isinstance(value, str) or not value.strip():
            return None

        path = folder / value
        if not path.exists() or not path.is_file():
            return None

        return path

    def _read_text(self, path: Optional[Path]) -> str:
        if path is None:
            return ""

        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def _optional_int(self, value: object) -> Optional[int]:
        if value is None or value == "":
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _optional_str(self, value: object) -> Optional[str]:
        if value is None:
            return None

        text = str(value).strip()
        return text or None

