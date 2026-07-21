"""Centralized drag state for LiveRig views."""

from __future__ import annotations

from typing import Optional

from models import Song


class DragController:
    """Keeps drag state independent from concrete widgets."""

    def __init__(self) -> None:
        self.song: Optional[Song] = None
        self.x = 0
        self.y = 0

    def start_drag(self, song: Song) -> None:
        self.song = song

    def move_drag(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def end_drag(self) -> Optional[Song]:
        song = self.song
        self.song = None
        return song

    def is_dragging(self) -> bool:
        return self.song is not None
