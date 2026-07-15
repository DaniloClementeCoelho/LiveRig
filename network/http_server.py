from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from network.connection_manager import ConnectionManager
from playback.playback_state import PlaybackState

logger = logging.getLogger(__name__)


class HttpServer:

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8080

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
    ) -> None:

        self._host = host
        self._port = port

        self._thread: threading.Thread | None = None
        self._server: uvicorn.Server | None = None
        self._running = False

        self._loop: asyncio.AbstractEventLoop | None = None

        self._app = FastAPI(
            title="LiveRig Visual Sync",
            docs_url=None,
            redoc_url=None,
        )

        self._playback_state = PlaybackState()

        self._connections = ConnectionManager(
            self._playback_state
        )

        @self._app.on_event("startup")
        async def startup():

            self._loop = asyncio.get_running_loop()

        @self._app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):

            await self._connections.connect(websocket)

            try:

                while True:
                    await websocket.receive_text()

            except WebSocketDisconnect:

                self._connections.disconnect(websocket)

        web_folder = Path(__file__).resolve().parent.parent / "web"

        self._app.mount(
            "/",
            StaticFiles(
                directory=web_folder,
                html=True,
            ),
            name="web",
        )

    @property
    def app(self) -> FastAPI:
        return self._app

    @property
    def playback_state(self) -> PlaybackState:
        return self._playback_state

    def notify_playback_changed(self) -> None:

        if not self._running:
            return

        if self._loop is None:
            return

        asyncio.run_coroutine_threadsafe(
            self._connections.broadcast_playback_state(),
            self._loop,
        )

    def start(self) -> None:

        if self._running:
            return

        config = uvicorn.Config(
            app=self._app,
            host=self._host,
            port=self._port,
            log_level="warning",
            access_log=False,
        )

        self._server = uvicorn.Server(config)

        self._thread = threading.Thread(
            target=self._server.run,
            daemon=True,
            name="LiveRigHttpServer",
        )

        self._thread.start()

        self._running = True

    def stop(self) -> None:

        if not self._running:
            return

        if self._server is not None:
            self._server.should_exit = True

        if self._thread is not None:
            self._thread.join(timeout=5)

        self._thread = None
        self._server = None
        self._running = False

    def is_running(self) -> bool:
        return self._running