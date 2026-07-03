"""Player column with current song details and synchronized lyrics."""

from __future__ import annotations

from collections.abc import Callable
from typing import Optional

import customtkinter as ctk

from models import Song


class PlayerView(ctk.CTkFrame):
    """Displays the selected song and playback controls."""

    def __init__(
        self,
        master: object,
        status_var: object,
        on_play: Callable[[], None],
        on_pause: Callable[[], None],
    ) -> None:
        super().__init__(master, corner_radius=0)
        self.status_var = status_var

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, padx=24, pady=(24, 14), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0, minsize=280)

        song_header = ctk.CTkFrame(header, corner_radius=0)
        song_header.grid(row=0, column=0, padx=(0, 18), sticky="nsew")
        song_header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(song_header, text="Nenhuma musica", anchor="w", font=("Arial", 32, "bold"))
        self.title_label.grid(row=0, column=0, pady=(0, 4), sticky="ew")

        self.artist_label = ctk.CTkLabel(song_header, text="", anchor="w", font=("Arial", 18))
        self.artist_label.grid(row=1, column=0, pady=(0, 12), sticky="ew")

        self.meta_label = ctk.CTkLabel(song_header, text="", anchor="w", font=("Arial", 16))
        self.meta_label.grid(row=2, column=0, sticky="ew")

        notes_panel = ctk.CTkFrame(header, corner_radius=0)
        notes_panel.grid(row=0, column=1, sticky="ne")
        notes_panel.grid_columnconfigure(0, weight=1)

        notes_label = ctk.CTkLabel(notes_panel, text="Observacoes", anchor="w", font=("Arial", 14, "bold"))
        notes_label.grid(row=0, column=0, pady=(0, 6), sticky="ew")

        self.notes_text = ctk.CTkTextbox(notes_panel, width=280, height=96, font=("Arial", 14), wrap="word")
        self.notes_text.grid(row=1, column=0, sticky="ew")

        self.lyrics_text = ctk.CTkTextbox(self, font=("Arial", 32, "bold"), wrap="word")
        self.lyrics_text.grid(row=1, column=0, padx=24, pady=(0, 18), sticky="nsew")

        controls = ctk.CTkFrame(self, corner_radius=0)
        controls.grid(row=2, column=0, padx=24, pady=(0, 16), sticky="ew")
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(1, weight=0)

        play_button = ctk.CTkButton(
            controls,
            text="Tocar",
            height=64,
            font=("Arial", 22, "bold"),
            command=on_play,
        )
        play_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        pause_button = ctk.CTkButton(
            controls,
            text="Pause",
            width=140,
            height=64,
            font=("Arial", 22, "bold"),
            command=on_pause,
        )
        pause_button.grid(row=0, column=1, sticky="e")

        status_label = ctk.CTkLabel(self, textvariable=status_var, anchor="w")
        status_label.grid(row=3, column=0, padx=24, pady=(0, 18), sticky="ew")

    def show_song(self, song: Optional[Song]) -> None:
        if song is None:
            self.title_label.configure(text="Nenhuma musica")
            self.artist_label.configure(text="")
            self.meta_label.configure(text="")
            self.set_notes("")
            self.set_lyrics("")
            return

        self.title_label.configure(text=song.title)
        self.artist_label.configure(text=song.artist)
        self.meta_label.configure(text=self._meta_text(song))
        self.set_notes(song.notes)

    def set_lyrics(self, text: str) -> None:
        self._set_text(self.lyrics_text, text)

    def set_notes(self, text: str) -> None:
        self._set_text(self.notes_text, text)

    def _set_text(self, widget: object, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _meta_text(self, song: Song) -> str:
        parts = [
            self._format_meta("Afinacao", song.tuning),
            self._format_meta("BPM", song.bpm),
            self._format_meta("Patch", song.patch),
            self._format_meta("Duracao", self._format_duration(song.duration)),
        ]
        return "    ".join(part for part in parts if part)

    def _format_meta(self, label: str, value: object) -> str:
        if value is None or value == "":
            return ""
        return f"{label}: {value}"

    def _format_duration(self, duration: Optional[int]) -> Optional[str]:
        if duration is None:
            return None
        minutes, seconds = divmod(duration, 60)
        return f"{minutes}:{seconds:02d}"
