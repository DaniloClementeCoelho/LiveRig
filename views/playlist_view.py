"""Playlist column with a small public API."""

from __future__ import annotations

from collections.abc import Callable
from typing import Optional

import customtkinter as ctk

from models import Song
from widgets.playlist_item import PlaylistItem


class PlaylistView(ctk.CTkFrame):
    """Independent playlist view prepared for drag and reorder workflows."""

    def __init__(
        self,
        master: object,
        on_select: Optional[Callable[[Song], None]] = None,
        on_drag_start: Optional[Callable[[Song, int], None]] = None,
    ) -> None:
        super().__init__(master, width=320, corner_radius=0)
        self.on_select = on_select
        self.on_drag_start = on_drag_start
        self.playlist: list[Song] = []
        self.selected_song: Optional[Song] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(self, text="Playlist", font=("Arial", 20, "bold"), anchor="w")
        title.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")

        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.list_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

    def add(self, song: Song) -> None:
        self.playlist.append(song)
        self.selected_song = song
        self._refresh()

    def remove(self, song: Song) -> None:
        try:
            self.playlist.remove(song)
        except ValueError:
            return
        if self.selected_song == song:
            self.selected_song = None
        self._refresh()

    def move(self, old: int, new: int) -> None:
        if old < 0 or old >= len(self.playlist):
            return
        new = max(0, min(new, len(self.playlist) - 1))
        if old == new:
            return
        song = self.playlist.pop(old)
        self.playlist.insert(new, song)
        self.selected_song = song
        self._refresh()

    def clear(self) -> None:
        self.playlist = []
        self.selected_song = None
        self._refresh()

    def set_playlist(self, playlist: list[Song]) -> None:
        self.playlist = list(playlist)
        if self.selected_song not in self.playlist:
            self.selected_song = None
        self._refresh()

    def select(self, song: Optional[Song], notify: bool = True) -> None:
        self.selected_song = song
        self._refresh()
        if notify and song is not None and self.on_select is not None:
            self.on_select(song)

    def items(self) -> list[Song]:
        return list(self.playlist)

    def index_at_pointer(self, pointer_y: int, moving_index: Optional[int] = None) -> Optional[int]:
        if not self.playlist:
            return None

        children = sorted(
            self.list_frame.winfo_children(),
            key=lambda child: int(child.grid_info().get("row", 0)),
        )
        if not children:
            return None

        for index, child in enumerate(children):
            top = child.winfo_rooty()
            middle = top + (child.winfo_height() // 2)
            if pointer_y < middle:
                return self._drop_index_to_final_index(index, moving_index)

        return self._drop_index_to_final_index(len(children), moving_index)

    def _drop_index_to_final_index(self, drop_index: int, moving_index: Optional[int]) -> int:
        if moving_index is not None and moving_index < drop_index:
            drop_index -= 1
        return max(0, min(drop_index, len(self.playlist) - 1))

    def _refresh(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()

        for index, song in enumerate(self.playlist):
            item = PlaylistItem(
                self.list_frame,
                song=song,
                index=index,
                selected=song == self.selected_song,
                on_click=self.select,
                on_remove=self.remove,
                on_drag_start=self.on_drag_start,
            )
            item.grid(row=index, column=0, padx=4, pady=4, sticky="ew")
