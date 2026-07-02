"""User interface for LiveRig."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from  models import Song
from  reaper_controller import ReaperController
from  settings import AppSettings
from  song_manager import SongManager
from  lyrics_loader import load_lyrics
from  playback_clock import PlaybackClock
import platform


def print_song_list(songs: list[Song]) -> None:
    """Print songs found in the shows directory."""
    if not songs:
        print("Nenhuma musica encontrada em shows/.")
        return

    for index, song in enumerate(songs, start=1):
        artist = f" - {song.artist}" if song.artist else ""
        print(f"{index}. {song.title}{artist}")


def run_app(settings: AppSettings, reaper: ReaperController) -> None:
    """Start the graphical interface."""
    try:
        import customtkinter as ctk
        from tkinter import filedialog
    except ModuleNotFoundError as exc:
        raise RuntimeError("CustomTkinter nao esta instalado.") from exc

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = LiveRigApp(ctk, filedialog, settings, reaper)
    app.mainloop()


class LiveRigApp:
    """Main CustomTkinter application."""

    def __init__(self, ctk: object, filedialog: object, settings: AppSettings, reaper: ReaperController) -> None:
        self.ctk = ctk
        self.filedialog = filedialog
        self.settings = settings
        self.reaper = reaper
        self.shows_dir = settings.load_shows_dir()
        self.song_manager = SongManager(self.shows_dir)
        self.songs = self.song_manager.load_songs()
        self.filtered_songs = list(self.songs)
        self.selected_song: Optional[Song] = self.filtered_songs[0] if self.filtered_songs else None

        self.root = ctk.CTk()
        self.root.title("LiveRig")
        self.root.geometry("1100x760")
        self.root.minsize(900, 620)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.search_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Pronto")
        self.folder_status_var = ctk.StringVar()
        self.song_buttons: list[object] = []

        self._build_folder_layout()

        if platform.system() == "Windows":
            position_file = (
                Path.home()
                / "AppData"
                / "Roaming"
                / "REAPER"
                / "position.txt"
            )
        else:
            position_file = (
                Path.home()
                / "Library"
                / "Application Support"
                / "REAPER"
                / "LiveRig"
                / "position.txt"
            )

        self.clock = PlaybackClock(position_file)



    def mainloop(self) -> None:
        """Run the window loop."""
        self.root.mainloop()

    def _build_folder_layout(self) -> None:
        self._clear_root()
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        panel = self.ctk.CTkFrame(self.root, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        content = self.ctk.CTkFrame(panel, corner_radius=0)
        content.grid(row=1, column=0, padx=80, pady=80, sticky="ew")
        content.grid_columnconfigure(0, weight=1)

        title = self.ctk.CTkLabel(content, text="LiveRig", anchor="w", font=("Arial", 36, "bold"))
        title.grid(row=0, column=0, pady=(0, 12), sticky="ew")

        current = self.ctk.CTkLabel(
            content,
            text=f"Pasta atual: {self.shows_dir}",
            anchor="w",
            font=("Arial", 16),
            wraplength=760,
        )
        current.grid(row=1, column=0, pady=(0, 22), sticky="ew")

        choose_button = self.ctk.CTkButton(
            content,
            text="Escolher Pasta Shows",
            height=54,
            font=("Arial", 18, "bold"),
            command=self._choose_shows_dir,
        )
        choose_button.grid(row=2, column=0, pady=(0, 14), sticky="ew")

        if self._is_usable_shows_dir(self.shows_dir):
            self.folder_status_var.set("Pasta valida. Escolha a pasta para iniciar.")
        else:
            self.folder_status_var.set("Selecione a pasta que contem as musicas.")
        folder_status = self.ctk.CTkLabel(content, textvariable=self.folder_status_var, anchor="w", font=("Arial", 14))
        folder_status.grid(row=3, column=0, sticky="ew")

    def _build_main_layout(self) -> None:
        self._clear_root()
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        sidebar = self.ctk.CTkFrame(self.root, width=320, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(1, weight=1)

        search = self.ctk.CTkEntry(
            sidebar,
            textvariable=self.search_var,
            placeholder_text="Buscar...",
            height=44,
            font=("Arial", 16),
        )
        search.grid(row=0, column=0, padx=16, pady=16, sticky="ew")
        self.search_var.trace_add("write", self._on_search_change)

        self.song_list_frame = self.ctk.CTkScrollableFrame(sidebar, corner_radius=0)
        self.song_list_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.song_list_frame.grid_columnconfigure(0, weight=1)

        content = self.ctk.CTkFrame(self.root, corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        header = self.ctk.CTkFrame(content, corner_radius=0)
        header.grid(row=0, column=0, padx=24, pady=(24, 14), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0, minsize=280)

        song_header = self.ctk.CTkFrame(header, corner_radius=0)
        song_header.grid(row=0, column=0, padx=(0, 18), sticky="nsew")
        song_header.grid_columnconfigure(0, weight=1)

        self.title_label = self.ctk.CTkLabel(song_header, text="Nenhuma musica", anchor="w", font=("Arial", 32, "bold"))
        self.title_label.grid(row=0, column=0, pady=(0, 4), sticky="ew")

        self.artist_label = self.ctk.CTkLabel(song_header, text="", anchor="w", font=("Arial", 18))
        self.artist_label.grid(row=1, column=0, pady=(0, 12), sticky="ew")

        self.meta_label = self.ctk.CTkLabel(song_header, text="", anchor="w", font=("Arial", 16))
        self.meta_label.grid(row=2, column=0, sticky="ew")

        notes_panel = self.ctk.CTkFrame(header, corner_radius=0)
        notes_panel.grid(row=0, column=1, sticky="ne")
        notes_panel.grid_columnconfigure(0, weight=1)

        notes_label = self.ctk.CTkLabel(notes_panel, text="Observacoes", anchor="w", font=("Arial", 14, "bold"))
        notes_label.grid(row=0, column=0, pady=(0, 6), sticky="ew")

        self.notes_text = self.ctk.CTkTextbox(notes_panel, width=280, height=96, font=("Arial", 14), wrap="word")
        self.notes_text.grid(row=1, column=0, sticky="ew")

        self.lyrics_text = self.ctk.CTkTextbox(content, font=("Arial", 32, "bold"), wrap="word")
        self.lyrics_text.grid(row=1, column=0, padx=24, pady=(0, 18), sticky="nsew")

        controls = self.ctk.CTkFrame(content, corner_radius=0)
        controls.grid(row=2, column=0, padx=24, pady=(0, 16), sticky="ew")
        controls.grid_columnconfigure(0, weight=1)

        self.open_and_play_button = self.ctk.CTkButton(
            controls,
            text="▶ TOCAR(do inicio) / Pause",
            height=64,
            font=("Arial", 22, "bold"),
            command=self._open_and_play,
        )
        self.open_and_play_button.grid(row=0, column=0, sticky="ew")

        self.status_label = self.ctk.CTkLabel(content, textvariable=self.status_var, anchor="w")
        self.status_label.grid(row=3, column=0, padx=24, pady=(0, 18), sticky="ew")

    def _clear_root(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

        for index in range(4):
            self.root.grid_columnconfigure(index, weight=0)
            self.root.grid_rowconfigure(index, weight=0)

    def _choose_shows_dir(self) -> None:
        selected = self.filedialog.askdirectory(
            title="Escolha a pasta shows",
            initialdir=str(self.shows_dir if self.shows_dir.exists() else Path.cwd()),
        )
        if selected:
            self._set_shows_dir(Path(selected))

    def _set_shows_dir(self, shows_dir: Path) -> None:
        resolved_dir = shows_dir.resolve()
        if not self._is_usable_shows_dir(resolved_dir):
            self.folder_status_var.set("Esta pasta nao contem musicas validas.")
            return

        self.shows_dir = resolved_dir
        self.settings.save_shows_dir(self.shows_dir)
        self._maximize_window()
        self._start_main_screen()

    def _maximize_window(self) -> None:
        try:
            self.root.state("zoomed")
        except Exception:
            self.root.attributes("-zoomed", True)

    def _start_main_screen(self) -> None:
        if not self._is_usable_shows_dir(self.shows_dir):
            self.folder_status_var.set("Escolha uma pasta shows valida antes de continuar.")
            return

        self.song_manager = SongManager(self.shows_dir)
        self.songs = self.song_manager.load_songs()
        self.filtered_songs = list(self.songs)
        self.selected_song = self.filtered_songs[0] if self.filtered_songs else None
        self._build_main_layout()
        self._refresh_song_list()
        self._show_song(self.selected_song)
        self._start_reaper_engine()
        self._update_lyrics()

    def _is_usable_shows_dir(self, shows_dir: Path) -> bool:
        return bool(SongManager(shows_dir).load_songs())

    def _refresh_song_list(self) -> None:
        for button in self.song_buttons:
            button.destroy()
        self.song_buttons.clear()

        for index, song in enumerate(self.filtered_songs):
            button = self.ctk.CTkButton(
                self.song_list_frame,
                text=self._song_button_text(song),
                height=46,
                anchor="w",
                fg_color=self._song_button_color(song),
                command=lambda item=song: self._select_song(item),
            )
            button.grid(row=index, column=0, pady=(0, 8), sticky="ew")
            self.song_buttons.append(button)

    def _on_search_change(self, *_args: object) -> None:
        query = self.search_var.get().strip().lower()
        self.filtered_songs = [
            song for song in self.songs if query in song.title.lower() or query in song.artist.lower()
        ]
        if self.selected_song not in self.filtered_songs:
            self.selected_song = self.filtered_songs[0] if self.filtered_songs else None
        self._refresh_song_list()
        self._show_song(self.selected_song)

    def _select_song(self, song: Song) -> None:
        self.selected_song = song
        self._refresh_song_list()
        self._show_song(song)

    def _show_song(self, song: Optional[Song]) -> None:
        if song is None:
            self.title_label.configure(text="Nenhuma musica")
            self.artist_label.configure(text="")
            self.meta_label.configure(text="")
            self._set_text(self.notes_text, "")
            self._set_text(self.lyrics_text, "")
            self.status_var.set("Nenhuma musica encontrada.")
            return

        self.title_label.configure(text=song.title)
        self.artist_label.configure(text=song.artist)
        self.meta_label.configure(text=self._meta_text(song))
        self._set_text(self.notes_text, song.notes)

        self._lyrics_timeline = load_lyrics(song.project_path)

        first = self._lyrics_timeline.current(0)
        self._current_lyric_index = -1

        if first is None:
            self._set_text(self.lyrics_text, "")
        else:
            self._set_text(self.lyrics_text, first.text)

        self.status_var.set("Musica selecionada.")

    def _open_and_play(self) -> None:
        if self.selected_song is None:
            self.status_var.set("Selecione uma musica primeiro.")
            return

        try:
            self.reaper.play_from_start(self.selected_song)
        except (OSError, RuntimeError) as exc:
            self.status_var.set(f"Erro ao abrir projeto: {exc}")
            return

        self.status_var.set(f"Tocando: {self.selected_song.title}")

    def _pause(self) -> None:
        self.reaper.pause()
        self.status_var.set("Playback pausado.")

    def _stop(self) -> None:
        self.reaper.stop()
        self.status_var.set("Playback parado. Projeto fechado.")

    def _start_reaper_engine(self) -> None:
        try:
            self.reaper.start()
        except RuntimeError as exc:
            self.status_var.set(f"REAPER nao iniciado: {exc}")
            return

        if not self.reaper.is_ready():
            self.status_var.set("REAPER sera iniciado ao abrir a musica.")
            return

        self.status_var.set("REAPER pronto.")

    def _on_close(self) -> None:
        try:
            self.reaper.shutdown()
        finally:
            self.root.destroy()

    def _set_text(self, widget: object, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _song_button_text(self, song: Song) -> str:
        return f"{song.title}\n{song.artist}" if song.artist else song.title

    def _song_button_color(self, song: Song) -> str:
        return "#1f6aa5" if song == self.selected_song else "#2b2b2b"

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


    def _update_lyrics(self) -> None:
        if self.selected_song is None:
            self.root.after(100, self._update_lyrics)
            return

        if not self.clock.is_playing():
            self.root.after(100, self._update_lyrics)
            return

        if not hasattr(self, "_lyrics_timeline"):
            self.root.after(100, self._update_lyrics)
            return

        position = self.clock.position()
        #print(position)
        current = self._lyrics_timeline.current(position)

        if current is not None:
            if getattr(self, "_current_lyric_index", -1) != current.index:
                self._current_lyric_index = current.index
                self._set_text(self.lyrics_text, current.text)

        self.root.after(100, self._update_lyrics)