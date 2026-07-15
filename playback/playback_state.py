from __future__ import annotations


class PlaybackState:

    def __init__(self) -> None:

        self.playing = False
        self.current_song: str | None = None
        self.position = 0.0

    def to_dict(self) -> dict:

        return {
            "playing": self.playing,
            "current_song": self.current_song,
            "position": self.position,
        }