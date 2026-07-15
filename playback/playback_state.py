from __future__ import annotations


class PlaybackState:
    """
    Representa o estado atual do show.

    Esta é a única fonte de verdade do LiveRig.

    Nenhum módulo deve manter uma cópia dessas informações.
    """

    def __init__(self) -> None:

        self._playing = False
        self._current_song: str | None = None
        self._position = 0.0

    @property
    def playing(self) -> bool:
        return self._playing

    @playing.setter
    def playing(self, value: bool) -> None:
        self._playing = value

    @property
    def current_song(self) -> str | None:
        return self._current_song

    @current_song.setter
    def current_song(self, value: str | None) -> None:
        self._current_song = value

    @property
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, value: float) -> None:
        self._position = float(value)

    def reset(self) -> None:
        self._playing = False
        self._current_song = None
        self._position = 0.0

    def to_dict(self) -> dict:

        return {
            "playing": self._playing,
            "current_song": self._current_song,
            "position": self._position,
        }