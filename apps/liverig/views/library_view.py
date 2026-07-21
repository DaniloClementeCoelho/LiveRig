"""Library column for browsing and searching songs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Optional

import customtkinter as ctk

from models import Song
from widgets.library_item import LibraryItem


class LibraryView(ctk.CTkFrame):
    """Searchable library with its own rendering and selection API."""

    def __init__(
        self,
        master: object,
        on_select: Optional[Callable[[Song], None]] = None,
        on_drag_start: Optional[Callable[[Song], None]] = None,
    ) -> None:
        super().__init__(master, width=320, corner_radius=0)
        self.on_select = on_select
        self.on_drag_start = on_drag_start
        self.songs: list[Song] = []
        self.filtered_songs: list[Song] = []
        self.selected_song: Optional[Song] = None
        self.search_var = ctk.StringVar()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text="Buscar...",
            height=44,
            font=("Arial", 16),
        )
        self.search_entry.grid(row=0, column=0, padx=16, pady=16, sticky="ew")
        self.search_var.trace_add("write", self._search_changed)

        self.list_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.list_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

    def set_songs(self, songs: list[Song]) -> None:
        self.songs = list(songs)
        self.filter(self.search_var.get())

    def filter(self, text: str) -> None:
        query = text.strip().lower()
        if not query:
            self.filtered_songs = list(self.songs)
        else:
            self.filtered_songs = [
                song
                for song in self.songs
                if query in song.title.lower() or query in (song.artist or "").lower()
            ]

        if self.selected_song not in self.filtered_songs:
            self.selected_song = self.filtered_songs[0] if self.filtered_songs else None
            if self.selected_song is not None and self.on_select is not None:
                self.on_select(self.selected_song)

        self._refresh()

    def select(self, song: Optional[Song], notify: bool = True) -> None:
        self.selected_song = song
        self._refresh()
        if notify and song is not None and self.on_select is not None:
            self.on_select(song)

    def first_song(self) -> Optional[Song]:
        return self.filtered_songs[0] if self.filtered_songs else None

    def _search_changed(self, *_args: object) -> None:
        self.filter(self.search_var.get())

    def _select_from_item(self, song: Song) -> None:
        self.select(song)

    def _refresh(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()

        for row, song in enumerate(self.filtered_songs):
            item = LibraryItem(
                self.list_frame,
                song=song,
                selected=song == self.selected_song,
                on_click=self._select_from_item,
                on_drag_start=self.on_drag_start,
            )
            item.grid(row=row, column=0, padx=4, pady=4, sticky="ew")
