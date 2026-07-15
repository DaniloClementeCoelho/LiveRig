from __future__ import annotations

import threading
import time

from network import NetworkServer
from reaper_controller import ReaperController


class VisualSyncManager:

    def __init__(self, reaper: ReaperController) -> None:

        self._reaper = reaper
        self._network = NetworkServer()

        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:

        self._network.start()

        self._running = True

        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="VisualSyncWorker",
        )

        self._thread.start()

    def stop(self) -> None:

        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=2)

        self._network.stop()

    def _worker(self) -> None:

        playback = self._network._http_server.playback_state

        while self._running:

            changed = False

            #
            # Estado real do REAPER
            #

            if playback.set_playing(
                self._reaper.playback_is_playing()
            ):
                changed = True

            if playback.set_position(
                self._reaper.playback_position()
            ):
                changed = True

            song = self._reaper.current_project()

            song_name = None if song is None else song.title

            if playback.set_current_song(song_name):
                changed = True

            if changed:
                self._network._http_server.notify_playback_changed()

            time.sleep(0.05)