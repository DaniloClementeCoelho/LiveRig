"""Main user interface orchestration for LiveRig."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Optional

from lyrics_loader import load_lyrics
from models import Song
from playback_clock import PlaybackClock
from reaper_controller import ReaperController
from settings import AppSettings
from song_manager import SongManager
import json


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

        from controllers.drag_controller import DragController
        from views.library_view import LibraryView
        from views.player_view import PlayerView
        from views.playlist_view import PlaylistView
    except ModuleNotFoundError as exc:
        raise RuntimeError("CustomTkinter nao esta instalado.") from exc

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = LiveRigApp(
        ctk=ctk,
        filedialog=filedialog,
        settings=settings,
        reaper=reaper,
        drag_controller_cls=DragController,
        library_view_cls=LibraryView,
        playlist_view_cls=PlaylistView,
        player_view_cls=PlayerView,
    )
    app.mainloop()


class LiveRigApp:
    """Main CustomTkinter application controller."""

    def __init__(
        self,
        ctk: object,
        filedialog: object,
        settings: AppSettings,
        reaper: ReaperController,
        drag_controller_cls: type,
        library_view_cls: type,
        playlist_view_cls: type,
        player_view_cls: type,
    ) -> None:
        self.ctk = ctk
        self.filedialog = filedialog
        self.settings = settings
        self.reaper = reaper
        self.DragController = drag_controller_cls
        self.LibraryView = library_view_cls
        self.PlaylistView = playlist_view_cls
        self.PlayerView = player_view_cls

        self.shows_dir = settings.load_shows_dir()
        self.song_manager = SongManager(self.shows_dir)
        self.songs: list[Song] = []
        self.selected_song: Optional[Song] = None
        self._lyrics_timeline = None
        self._current_lyric_index = -1
        self._drag_source: Optional[str] = None
        self._drag_playlist_index: Optional[int] = None

        self.root = ctk.CTk()
        self.root.title("LiveRig")
        self.root.minsize(900, 620)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._maximize_window()

        self.status_var = ctk.StringVar(value="Pronto")
        self.folder_status_var = ctk.StringVar()
        self.drag = self.DragController()

        self.library_view = None
        self.playlist_view = None
        self.player_view = None

        self.root.bind_all("<space>", self._handle_space_pause, add="+")
        self.root.bind_all("<KeyPress-space>", self._handle_space_pause, add="+")

        self.clock = PlaybackClock(self._position_file())
        self.root.bind("<Motion>", self._mouse_move)
        self.root.bind("<ButtonRelease-1>", self._mouse_release)

        self._build_folder_layout()

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

        message = "Pasta valida. Escolha a pasta para iniciar."
        if not self._is_usable_shows_dir(self.shows_dir):
            message = "Selecione a pasta que contem as musicas."
        self.folder_status_var.set(message)

        folder_status = self.ctk.CTkLabel(
            content,
            textvariable=self.folder_status_var,
            anchor="w",
            font=("Arial", 14),
        )
        folder_status.grid(row=3, column=0, sticky="ew")

    def _build_main_layout(self) -> None:
        self._clear_root()
        self.root.grid_columnconfigure(0, weight=0, minsize=320)
        self.root.grid_columnconfigure(1, weight=0, minsize=320)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.library_view = self.LibraryView(
            self.root,
            on_select=self._select_song,
            on_drag_start=self._start_library_drag,
        )
        self.library_view.grid(row=0, column=0, sticky="nsew")

        self.playlist_view = self.PlaylistView(
            self.root,
            on_select=self._select_song,
            on_drag_start=self._start_playlist_drag,
        )
        self.playlist_view.grid(row=0, column=1, sticky="nsew")

        player_shell = self.ctk.CTkFrame(self.root, corner_radius=0)
        player_shell.grid(row=0, column=2, sticky="nsew")
        player_shell.grid_columnconfigure(0, weight=1)
        player_shell.grid_rowconfigure(1, weight=1)

        toolbar = self.ctk.CTkFrame(player_shell, corner_radius=0)
        toolbar.grid(row=0, column=0, padx=24, pady=(12, 0), sticky="ew")
        toolbar.grid_columnconfigure(0, weight=0)
        toolbar.grid_columnconfigure(1, weight=0)
        toolbar.grid_columnconfigure(2, weight=0)
        toolbar.grid_columnconfigure(3, weight=1)

        self.toggle_library_button = self.ctk.CTkButton(
            toolbar,
            text="Ocultar Biblioteca",
            width=160,
            command=self._toggle_library,
        )
        self.toggle_library_button.grid(row=0, column=0, padx=(0,10), sticky="w")

        self.player_view = self.PlayerView(
            player_shell,
            status_var=self.status_var,
            on_play=self._open_and_play,
            on_pause=self._pause,
        )
        self.player_view.grid(row=1, column=0, sticky="nsew")

        self.save_playlist_button = self.ctk.CTkButton(
            toolbar,
            text="Salvar",
            width=140,
            command=self._save_playlist,
        )
        self.save_playlist_button.grid(row=0, column=1, padx=(0,10), sticky="w")

        self.load_playlist_button = self.ctk.CTkButton(
            toolbar,
            text="Abrir",
            width=140,
            command=self._load_playlist,
        )
        self.load_playlist_button.grid(row=0, column=2, sticky="w")

    def _clear_root(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

        for index in range(4):
            self.root.grid_columnconfigure(index, weight=0, minsize=0)
            self.root.grid_rowconfigure(index, weight=0, minsize=0)

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
        self._start_main_screen()

    def _start_main_screen(self) -> None:
        if not self._is_usable_shows_dir(self.shows_dir):
            self.folder_status_var.set("Escolha uma pasta shows valida antes de continuar.")
            return

        self.song_manager = SongManager(self.shows_dir)
        self.songs = self.song_manager.load_songs()
        self.selected_song = self.songs[0] if self.songs else None

        self._build_main_layout()
        self.library_view.set_songs(self.songs)
        self.library_view.select(self.selected_song, notify=False)
        self._show_song(self.selected_song)
        self._start_reaper_engine()
        self._update_lyrics()

    def _is_usable_shows_dir(self, shows_dir: Path) -> bool:
        return bool(SongManager(shows_dir).load_songs())

    def _select_song(self, song: Song) -> None:
        if self.selected_song == song:
            return
        self.selected_song = song
        if self.library_view is not None and self.library_view.selected_song != song:
            self.library_view.select(song, notify=False)
        if self.playlist_view is not None and self.playlist_view.selected_song != song:
            self.playlist_view.select(song, notify=False)
        self._show_song(song)

    def _show_song(self, song: Optional[Song]) -> None:
        if self.player_view is None:
            return

        self.player_view.show_song(song)
        if song is None:
            self._lyrics_timeline = None
            self._current_lyric_index = -1
            self.status_var.set("Nenhuma musica encontrada.")
            return

        self._lyrics_timeline = load_lyrics(song.project_path)
        first = self._lyrics_timeline.current(0)
        self._current_lyric_index = -1
        self.player_view.set_lyrics("" if first is None else first.text)
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

    def _update_lyrics(self) -> None:
        if self.player_view is None:
            return

        if self.selected_song is None or not self.clock.is_playing() or self._lyrics_timeline is None:
            self.root.after(100, self._update_lyrics)
            return

        current = self._lyrics_timeline.current(self.clock.position())
        if current is not None and self._current_lyric_index != current.index:
            self._current_lyric_index = current.index
            self.player_view.set_lyrics(current.text)

        self.root.after(100, self._update_lyrics)

    def _start_library_drag(self, song: Song) -> None:
        self._drag_source = "library"
        self._start_drag(song)

    def _start_playlist_drag(self, song: Song, index: int) -> None:
        self._drag_source = "playlist"
        self._drag_playlist_index = index
        self._start_drag(song)

    def _start_drag(self, song: Song) -> None:
        self.drag.start_drag(song)
        x, y = self._pointer_in_root()
        self.drag.move_drag(x, y)

    def _mouse_move(self, event: object) -> None:
        if not self.drag.is_dragging():
            return
        self.drag.move_drag(event.x, event.y)

    def _mouse_release(self, event: object) -> None:
        if not self.drag.is_dragging():
            return

        song = self.drag.end_drag()
        if (
            song is not None
            and self._drag_source == "library"
            and self.playlist_view is not None
            and self._widget_contains_pointer(self.playlist_view)
        ):
            self.playlist_view.add(song)
        elif (
            self._drag_source == "playlist"
            and self._drag_playlist_index is not None
            and self.playlist_view is not None
            and self._widget_contains_pointer(self.playlist_view)
        ):
            target_index = self.playlist_view.index_at_pointer(
                self.root.winfo_pointery(),
                self._drag_playlist_index,
            )
            if target_index is not None:
                self.playlist_view.move(self._drag_playlist_index, target_index)
        self._drag_source = None
        self._drag_playlist_index = None

    def _toggle_library(self) -> None:
        if self.library_view is None:
            return
        if self.library_view.winfo_ismapped():
            self.library_view.grid_remove()
            self.root.grid_columnconfigure(0, minsize=0)
            self.toggle_library_button.configure(text="Mostrar Biblioteca")
        else:
            self.root.grid_columnconfigure(0, minsize=320)
            self.library_view.grid()
            self.toggle_library_button.configure(text="Ocultar Biblioteca")

    def _widget_contains_pointer(self, widget: object) -> bool:
        pointer_x = self.root.winfo_pointerx()
        pointer_y = self.root.winfo_pointery()
        left = widget.winfo_rootx()
        top = widget.winfo_rooty()
        right = left + widget.winfo_width()
        bottom = top + widget.winfo_height()
        return left <= pointer_x <= right and top <= pointer_y <= bottom

    def _pointer_in_root(self) -> tuple[int, int]:
        return (
            self.root.winfo_pointerx() - self.root.winfo_rootx(),
            self.root.winfo_pointery() - self.root.winfo_rooty(),
        )

    def _position_file(self) -> Path:
        if platform.system() == "Windows":
            return Path.home() / "AppData" / "Roaming" / "REAPER" / "LiveRig" / "position.txt"
        return Path.home() / "Library" / "Application Support" / "REAPER" / "LiveRig" / "position.txt"

    def _maximize_window(self) -> None:
        system = platform.system()
        try:
            if system == "Windows":
                self.root.state("zoomed")
            elif system == "Darwin":
                self.root.attributes("-fullscreen", True)
            else:
                self.root.attributes("-zoomed", True)
        except Exception:
            self.root.after(100, self._fit_screen)

    def _fit_screen(self) -> None:
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{width}x{height}+0+0")

    def _on_close(self) -> None:
        try:
            self.reaper.shutdown()
        finally:
            self.root.destroy()

    def _save_playlist(self) -> None:
        filename = self.filedialog.asksaveasfilename(
            title="Salvar Playlist",
            defaultextension=".json",
            filetypes=[
                ("Playlist LiveRig", "*.json"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not filename:
            return

        songs = []

        for song in self.playlist_view.items():
            songs.append(str(song.folder.relative_to(self.shows_dir)))

        data = {
            "version": 1,
            "songs": songs,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.status_var.set("Playlist salva com sucesso.")

    def _load_playlist(self) -> None:
        filename = self.filedialog.askopenfilename(
            title="Abrir Playlist",
            filetypes=[
                ("Playlist LiveRig", "*.json"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.status_var.set(f"Erro ao abrir playlist: {e}")
            return

        # Índice das músicas disponíveis
        songs_by_folder = {
            str(song.folder.relative_to(self.shows_dir)): song
            for song in self.songs
        }

        playlist = []

        for folder in data.get("songs", []):
            song = songs_by_folder.get(folder)
            if song is not None:
                playlist.append(song)

        self.playlist_view.set_playlist(playlist)

        if playlist:
            self._select_song(playlist[0])

        self.status_var.set(f"Playlist carregada ({len(playlist)} músicas)")

    def _handle_space_pause(self, event: object) -> str | None:
        widget = self.root.focus_get()
        # Evita interferir quando o foco estiver em um campo editável
        if widget is not None:
            widget_class = widget.winfo_class()
            if widget_class in {"Entry", "Text"}:
                return None

        self._pause()
        return "break"