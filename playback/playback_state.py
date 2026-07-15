from __future__ import annotations


class PlaybackState:

    def __init__(self) -> None:

        self.playing = False
        self.current_song: str | None = None
        self.position = 0.0

        self._version = 0

    def set_playing(self, playing: bool) -> bool:

        if self.playing == playing:
            return False

        self.playing = playing
        self._version += 1

        return True

    def set_position(self, position: float) -> bool:

        position = float(position)

        if self.position == position:
            return False

        self.position = position
        self._version += 1

        return True

    def set_current_song(self, song: str | None) -> bool:

        if self.current_song == song:
            return False

        self.current_song = song
        self._version += 1

        return True

    @property
    def version(self) -> int:
        return self._version

    def to_dict(self) -> dict:

        return {
            "playing": self.playing,
            "current_song": self.current_song,
            "position": self.position,
            "version": self._version,
        }