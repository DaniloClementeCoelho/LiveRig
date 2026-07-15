from __future__ import annotations

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self, playback_state) -> None:

        self._playback_state = playback_state
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:

        await websocket.accept()

        self._connections.append(websocket)

        await self.send_playback_state(websocket)

    def disconnect(self, websocket: WebSocket) -> None:

        if websocket in self._connections:
            self._connections.remove(websocket)

    async def send_playback_state(self, websocket: WebSocket) -> None:

        await websocket.send_json(
            {
                "type": "playback_state",
                "payload": self._playback_state.to_dict(),
            }
        )

    async def broadcast_playback_state(self) -> None:

        message = {
            "type": "playback_state",
            "payload": self._playback_state.to_dict(),
        }

        disconnected = []

        for websocket in self._connections:

            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)

    @property
    def count(self) -> int:
        return len(self._connections)