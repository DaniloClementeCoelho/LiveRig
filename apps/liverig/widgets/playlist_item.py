"""Song row used by the playlist view."""

from __future__ import annotations

from collections.abc import Callable
from typing import Optional

import customtkinter as ctk

from models import Song


class PlaylistItem(ctk.CTkFrame):
    """Visual representation of a song in the playlist."""

    def __init__(
        self,
        master: object,
        song: Song,
        index: int,
        selected: bool = False,
        on_click: Optional[Callable[[Song], None]] = None,
        on_remove: Optional[Callable[[Song], None]] = None,
        on_drag_start: Optional[Callable[[Song, int], None]] = None,
    ) -> None:
        super().__init__(
            master,
            corner_radius=8,
            fg_color="#1f6fff" if selected else ("gray86", "gray22"),
        )
        self.song = song
        self.index = index
        self.on_click = on_click
        self.on_remove = on_remove
        self.on_drag_start = on_drag_start
        self._press_x = 0
        self._press_y = 0
        self._drag_started = False

        self.grid_columnconfigure(1, weight=1)

        number = ctk.CTkLabel(self, text=str(index + 1), width=28, font=("Arial", 13, "bold"))
        number.grid(row=0, column=0, rowspan=2, padx=(10, 4), pady=8, sticky="ns")

        title = ctk.CTkLabel(self, text=song.title, anchor="w", font=("Arial", 15, "bold"))
        title.grid(row=0, column=1, padx=(4, 8), pady=(8, 0), sticky="ew")

        artist = ctk.CTkLabel(self, text=song.artist, anchor="w", font=("Arial", 13))
        artist.grid(row=1, column=1, padx=(4, 8), pady=(0, 8), sticky="ew")

        remove = ctk.CTkButton(self, text="x", width=28, height=28, command=self._remove)
        remove.grid(row=0, column=2, rowspan=2, padx=(0, 8), pady=8, sticky="e")

        for widget in (self, number, title, artist):
            widget.bind("<ButtonPress-1>", self._pressed)
            widget.bind("<B1-Motion>", self._dragged)
            widget.bind("<ButtonRelease-1>", self._released)

    def _released(self, _event: object) -> None:
        if not self._drag_started and self.on_click is not None:
            self.on_click(self.song)
        self._drag_started = False

    def _pressed(self, event: object) -> None:
        self._press_x = event.x_root
        self._press_y = event.y_root
        self._drag_started = False

    def _dragged(self, event: object) -> None:
        if self._drag_started:
            return
        moved_x = abs(event.x_root - self._press_x)
        moved_y = abs(event.y_root - self._press_y)
        if moved_x < 6 and moved_y < 6:
            return

        self._drag_started = True
        if self.on_drag_start is not None:
            self.on_drag_start(self.song, self.index)

    def _remove(self) -> None:
        if self.on_remove is not None:
            self.on_remove(self.song)
