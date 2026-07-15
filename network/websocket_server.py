from __future__ import annotations


class WebSocketServer:
    """
    Servidor WebSocket do LiveRig.

    Nesta fase é apenas um placeholder.
    A implementação real será adicionada ao longo da Fase 3.
    """

    def __init__(self) -> None:
        self._running = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running