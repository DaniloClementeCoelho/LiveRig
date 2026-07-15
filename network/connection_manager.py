from __future__ import annotations

from fastapi import WebSocket

from playback.playback_state import PlaybackState


class ConnectionManager:

    def __init__(self, playback_state: PlaybackState) -> None:

        self._playback_state = playback_state
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:

        await websocket.accept()

        self._connections.append(websocket)

        await websocket.send_json(
            {
                "type": "playback_state",
                "payload": self._playback_state.to_dict(),
            }
        )

    def disconnect(self, websocket: WebSocket) -> None:

        if websocket in self._connections:
            self._connections.remove(websocket)

    @property
    def count(self) -> int:
        return len(self._connections)