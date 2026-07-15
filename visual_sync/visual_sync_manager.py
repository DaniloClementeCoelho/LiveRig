from __future__ import annotations

from network import NetworkServer
from playback.playback_state import PlaybackState


class VisualSyncManager:
    """
    Coordena todo o módulo Visual Sync.

    Nesta primeira versão, ele apenas cria e controla
    o PlaybackState e a infraestrutura de rede.
    """

    def __init__(self) -> None:

        self._playback_state = PlaybackState()
        self._network = NetworkServer()

    def start(self) -> None:
        self._network.start()

    def stop(self) -> None:
        self._network.stop()

    @property
    def playback_state(self) -> PlaybackState:
        return self._playback_state

    @property
    def network(self) -> NetworkServer:
        return self._network