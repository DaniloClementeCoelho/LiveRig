from __future__ import annotations


class PlaybackState:

    def __init__(self) -> None:

        self.playing = False
        self.current_song_id: str | None = None
        self.current_song_title: str | None = None
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

    def set_current_song(
        self,
        song_id: str | None,
        song_title: str | None,
    ) -> bool:

        if (
            self.current_song_id == song_id
            and self.current_song_title == song_title
        ):
            return False

        self.current_song_id = song_id
        self.current_song_title = song_title
        self._version += 1

        return True

    @property
    def version(self) -> int:
        return self._version

    def to_dict(self) -> dict:

        return {
            "playing": self.playing,
            "current_song": self.current_song_title,
            "current_song_id": self.current_song_id,
            "current_song_title": self.current_song_title,
            "position": self.position,
            "version": self._version,
        }
