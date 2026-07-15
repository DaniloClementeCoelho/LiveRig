from __future__ import annotations
from .http_server import HttpServer


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