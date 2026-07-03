from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RppItem:
    track_name: str
    position: float
    length: float
    notes: str = ""
    source: str = ""

    @property
    def end(self) -> float:
        return self.position + self.length


@dataclass
class Song:
    title: str
    artist: str
    duration: int
    bpm: int
    source_file: Path
    start_position: float = 0.0
    lyrics: list[RppItem] = field(default_factory=list)
    notes: str = ""
    warnings: list[str] = field(default_factory=list)
