"""Song row used by the library view."""

from __future__ import annotations

from collections.abc import Callable
from typing import Optional

import customtkinter as ctk

from models import Song


class LibraryItem(ctk.CTkFrame):
    """Visual representation of a song in the library."""

    def __init__(
        self,
        master: object,
        song: Song,
        selected: bool = False,
        on_click: Optional[Callable[[Song], None]] = None,
        on_drag_start: Optional[Callable[[Song], None]] = None,
    ) -> None:
        super().__init__(
            master,
            corner_radius=8,
            fg_color="#1f6fff" if selected else ("gray86", "gray22"),
        )
        self.song = song
        self.on_click = on_click
        self.on_drag_start = on_drag_start
        self._press_x = 0
        self._press_y = 0
        self._drag_started = False

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=song.title,
            anchor="w",
            font=("Arial", 15, "bold"),
        )
        self.title_label.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")

        self.artist_label = ctk.CTkLabel(
            self,
            text=song.artist,
            anchor="w",
            font=("Arial", 13),
        )
        self.artist_label.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")

        self._bind_mouse(self)
        self._bind_mouse(self.title_label)
        self._bind_mouse(self.artist_label)

    def _bind_mouse(self, widget: object) -> None:
        widget.bind("<ButtonPress-1>", self._pressed)
        widget.bind("<B1-Motion>", self._dragged)
        widget.bind("<ButtonRelease-1>", self._released)

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
            self.on_drag_start(self.song)

    def _released(self, _event: object) -> None:
        if not self._drag_started and self.on_click is not None:
            self.on_click(self.song)
        self._drag_started = False
