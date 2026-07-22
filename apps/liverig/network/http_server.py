from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path
from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from lyrics_loader import load_lyrics
from models import Song
from network.connection_manager import ConnectionManager
from playback.playback_state import PlaybackState

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v"}
DEFAULT_VISUAL_MEDIA_FOLDER = "Media"
DEFAULT_SHUFFLE_INTERVAL = 12


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
        self._songs: dict[str, Song] = {}
        self._songs_lock = threading.Lock()

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

        @self._app.get("/api/playback")
        async def playback_endpoint():

            return self._playback_state.to_dict()

        @self._app.get("/api/songs/{song_id}/sync")
        async def song_sync_endpoint(song_id: str):

            payload = self.song_sync_payload(song_id)
            if payload is None:
                raise HTTPException(status_code=404, detail="Musica nao encontrada.")

            return payload

        web_folder = Path(__file__).resolve().parent.parent / "web"

        @self._app.get("/video")
        async def video_endpoint():

            return FileResponse(web_folder / "video.html")

        @self._app.get("/pano_de_fundo.jpg")
        async def video_background_endpoint():

            background = web_folder.parent / "pano_de_fundo.jpg"
            if not background.exists() or not background.is_file():
                raise HTTPException(status_code=404, detail="Pano de fundo nao encontrado.")

            return FileResponse(background)

        @self._app.get("/api/songs/{song_id}/media/{media_path:path}")
        async def song_media_endpoint(song_id: str, media_path: str):

            path = self.song_media_path(song_id, media_path)
            if path is None:
                raise HTTPException(status_code=404, detail="Midia nao encontrada.")

            return FileResponse(path)

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

    def register_song(self, song_id: str, song: Song) -> None:

        with self._songs_lock:
            self._songs[song_id] = song

    def song_sync_payload(self, song_id: str) -> dict | None:

        with self._songs_lock:
            song = self._songs.get(song_id)

        if song is None:
            return None

        lyrics_timeline = load_lyrics(song.project_path)

        return {
            "id": song_id,
            "title": song.title,
            "artist": song.artist,
            "bpm": song.bpm,
            "patch": song.patch,
            "tuning": song.tuning,
            "duration": song.duration,
            "notes": song.notes,
            "lyrics": [
                {
                    "index": item.index,
                    "start": item.start,
                    "end": item.end,
                    "text": item.text,
                }
                for item in lyrics_timeline.items
            ],
            "videos": self._videos(song_id, song),
            "visual": self._visual(song_id, song),
        }

    def song_media_path(self, song_id: str, media_path: str) -> Path | None:

        with self._songs_lock:
            song = self._songs.get(song_id)

        if song is None:
            return None

        requested = Path(media_path)
        if requested.is_absolute():
            return None

        root = song.folder.resolve()
        path = (root / requested).resolve()
        if not path.is_relative_to(root):
            return None

        if not path.exists() or not path.is_file():
            return None

        return path

    def _visual(self, song_id: str, song: Song) -> dict:

        config = song.extra.get("visual") if song.extra is not None else None
        config = config if isinstance(config, dict) else {}

        media_folder = config.get("media_folder", DEFAULT_VISUAL_MEDIA_FOLDER)
        if not isinstance(media_folder, str) or not media_folder.strip():
            media_folder = DEFAULT_VISUAL_MEDIA_FOLDER

        shuffle_interval = config.get("shuffle_interval", DEFAULT_SHUFFLE_INTERVAL)
        try:
            shuffle_interval = max(1, int(shuffle_interval))
        except (TypeError, ValueError):
            shuffle_interval = DEFAULT_SHUFFLE_INTERVAL

        return {
            "mode": config.get("mode") if config.get("mode") == "manual" else "auto",
            "manifest": self._visual_manifest(song_id, song, config),
            "media_folder": media_folder,
            "shuffle_interval": shuffle_interval,
            "media": self._auto_media(song_id, song, media_folder),
            "cues": self._visual_cues(song_id, song),
        }

    def _visual_manifest(
        self,
        song_id: str,
        song: Song,
        config: dict,
    ) -> dict | None:

        manifest = config.get("manifest")
        if not isinstance(manifest, str) or not manifest.strip():
            return None

        normalized_path = manifest.strip().replace("\\", "/")
        if self.song_media_path(song_id, normalized_path) is None:
            return None

        return {
            "file": normalized_path,
            "src": self._media_src(song_id, normalized_path),
        }

    def _auto_media(
        self,
        song_id: str,
        song: Song,
        media_folder: str,
    ) -> list[dict]:

        requested = Path(media_folder)
        if requested.is_absolute():
            return []

        root = song.folder.resolve()
        folder = (root / requested).resolve()
        if not folder.is_relative_to(root):
            return []

        if not folder.exists() or not folder.is_dir():
            return []

        items = []

        for path in sorted(folder.iterdir(), key=lambda item: item.name.casefold()):
            if not path.is_file():
                continue

            media_type = self._media_type(path)
            if media_type is None:
                continue

            relative_path = path.relative_to(root).as_posix()
            items.append(
                {
                    "type": media_type,
                    "file": relative_path,
                    "src": self._media_src(song_id, relative_path),
                }
            )

        return items

    def _visual_cues(self, song_id: str, song: Song) -> list[dict]:

        if song.extra is None:
            return []

        cues = song.extra.get("visual_cues")
        if not isinstance(cues, list):
            return []

        payload = []

        for cue in cues:
            if not isinstance(cue, dict):
                continue

            item = dict(cue)
            cue_type = item.get("type")
            if cue_type not in {"message", "lyrics", "media"}:
                continue

            file_media = self._cue_media(song_id, song, item.get("file"))
            if file_media is not None:
                item["media"] = file_media

            background_media = self._cue_media(song_id, song, item.get("background"))
            if background_media is not None:
                item["background_media"] = background_media

            payload.append(item)

        return payload

    def _cue_media(self, song_id: str, song: Song, value: object) -> dict | None:

        if not isinstance(value, str) or not value.strip():
            return None

        path = self.song_media_path(song_id, value.strip())
        if path is None:
            return None

        media_type = self._media_type(path)
        if media_type is None:
            return None

        normalized_path = value.strip().replace("\\", "/")
        return {
            "type": media_type,
            "file": normalized_path,
            "src": self._media_src(song_id, normalized_path),
        }

    def _videos(self, song_id: str, song: Song) -> list[dict]:

        if song.extra is None:
            return []

        videos = song.extra.get("videos")
        if not isinstance(videos, list):
            return []

        payload = []

        for video in videos:
            if not isinstance(video, dict):
                continue

            media_path = video.get("file")
            if not isinstance(media_path, str) or not media_path.strip():
                continue

            item = dict(video)
            normalized_path = media_path.strip().replace("\\", "/")
            item["src"] = self._media_src(song_id, normalized_path)
            payload.append(item)

        return payload

    def _media_type(self, path: Path) -> str | None:

        suffix = path.suffix.casefold()
        if suffix in IMAGE_EXTENSIONS:
            return "image"
        if suffix in VIDEO_EXTENSIONS:
            return "video"
        return None

    def _media_src(self, song_id: str, media_path: str) -> str:

        return (
            f"/api/songs/{quote(song_id)}/media/"
            f"{quote(media_path, safe='/')}"
        )

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
