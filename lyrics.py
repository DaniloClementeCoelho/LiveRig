from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LyricItem:
    index: int
    start: float
    end: float
    text: str


@dataclass
class LyricsTimeline:
    items: list[LyricItem]

    def current(self, position: float) -> Optional[LyricItem]:
        """Return the last lyric whose start time is before the current position."""

        current = None

        for item in self.items:
            if item.start <= position:
                current = item
            else:
                break

        return current
