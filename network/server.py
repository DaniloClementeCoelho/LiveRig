from __future__ import annotations
from .http_server import HttpServer
from models import Song
from playback.playback_state import PlaybackState


class NetworkServer:
    """
    Responsável por coordenar todos os serviços de rede do LiveRig.

    Nesta fase, gerencia apenas o servidor HTTP.
    """

    def __init__(self) -> None:
        self._http_server = HttpServer()

    def start(self) -> None:
        self._http_server.start()

    def stop(self) -> None:
        self._http_server.stop()

    def is_running(self) -> bool:
        return self._http_server.is_running()

    @property
    def playback_state(self) -> PlaybackState:
        return self._http_server.playback_state

    def notify_playback_changed(self) -> None:
        self._http_server.notify_playback_changed()

    def register_song(self, song_id: str, song: Song) -> None:
        self._http_server.register_song(song_id, song)
