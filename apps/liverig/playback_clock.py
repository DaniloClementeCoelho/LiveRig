from __future__ import annotations

from pathlib import Path


class PlaybackClock:
    def __init__(self, position_file: Path) -> None:
        self.position_file = position_file
        self._last_position = 0.0
        self._last_playing = False
        self._last_project_ready = False
        self._last_project_path = ""
        self._last_track_count = 0

    def _read(self) -> None:
        try:
            with self.position_file.open("r", encoding="utf-8") as f:
                lines = f.readlines()

            if len(lines) < 3:
                return

            position = float(lines[0].strip())
            playing = lines[1].strip() == "1"
            project_ready = lines[2].strip() == "1"
            project_path = lines[3].strip() if len(lines) >= 4 else ""
            track_count = int(lines[4].strip()) if len(lines) >= 5 else 0

            self._last_position = position
            self._last_playing = playing
            self._last_project_ready = project_ready
            self._last_project_path = project_path
            self._last_track_count = track_count

        except Exception:
            pass

    def position(self) -> float:
        self._read()
        return self._last_position

    def is_playing(self) -> bool:
        self._read()
        return self._last_playing
    
    def project_ready(self) -> bool:
        self._read()
        return self._last_project_ready

    def project_path(self) -> str:
        self._read()
        return self._last_project_path

    def track_count(self) -> int:
        self._read()
        return self._last_track_count
