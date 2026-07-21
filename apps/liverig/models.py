"""Domain models for LiveRig."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class Song:
    """A song package found inside the shows directory."""

    title: str
    artist: str
    folder: Path
    project_path: Path
    lyrics_path: Optional[Path] = None
    notes_path: Optional[Path] = None
    cover_path: Optional[Path] = None
    patch: Optional[int] = None
    tuning: Optional[str] = None
    bpm: Optional[int] = None
    duration: Optional[int] = None
    lyrics: str = ""
    notes: str = ""
    extra: Optional[dict[str, Any]] = None

