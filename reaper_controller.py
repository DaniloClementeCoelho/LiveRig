"""Single communication point with REAPER."""

from __future__ import annotations

import ctypes
import os
import platform
import subprocess
import time
from collections.abc import Callable
from typing import Optional
from pathlib import Path
import shutil
from  models import Song
from osc_transport import OSCTransport

ProjectLauncher = Callable[[Path], Optional[subprocess.Popen]]
ReaperLauncher = Callable[[], Optional[subprocess.Popen]]
ActionSender = Callable[[int], bool]
ReadyChecker = Callable[[], bool]
WindowMinimizer = Callable[[], None]

LIVERIG_POSITION_SCRIPT = "_RS0bfde4727b638896a9f9361963f166631c496ad6"

ACTION_PLAY = 1007
ACTION_PAUSE = 1008
ACTION_STOP = 1016
ACTION_CLOSE_PROJECT = 40860
ACTION_QUIT = 40004
ACTION_GO_TO_START = 40042
WINDOWS_REAPER_CANDIDATES = [
    Path("C:/Program Files/REAPER (x64)/reaper.exe"),
    Path("C:/Program Files/REAPER/reaper.exe"),
    Path("C:/Program Files (x86)/REAPER/reaper.exe"),
    Path("D:/Programas Instalados/Reaper/reaper.exe"),
]
MACOS_REAPER_CANDIDATES = [
    Path("/Applications/REAPER.app/Contents/MacOS/REAPER"),
    Path("/Applications/REAPER64.app/Contents/MacOS/REAPER"),
]


class ReaperController:
    """Single controller for REAPER-related actions."""

    def __init__(
        self,
        reaper_launcher: Optional[ReaperLauncher] = None,
        project_launcher: Optional[ProjectLauncher] = None,
        action_sender: Optional[ActionSender] = None,
        ready_checker: Optional[ReadyChecker] = None,
        window_minimizer: Optional[WindowMinimizer] = None,
        reaper_ready_timeout: float = 12.0,
        project_load_minimize_seconds: float = 1.2,
    ) -> None:
        self._reaper_launcher = reaper_launcher or self._launch_reaper
        self._project_launcher = project_launcher or self._launch_project_file
        self._action_sender = action_sender or self._send_reaper_action
        self._ready_checker = ready_checker or self._is_reaper_action_target_ready
        self._window_minimizer = window_minimizer or self._minimize_reaper_window
        self._reaper_ready_timeout = reaper_ready_timeout
        self._project_load_minimize_seconds = project_load_minimize_seconds
        self._process: Optional[subprocess.Popen] = None
        self._current_song: Optional[Song] = None
        self._playing = False
        self._osc = OSCTransport() if platform.system() == "Darwin" else None

    def _go_to_start(self):
        self._osc.goto_marker(1)



    def start(self) -> None:
        """Launch REAPER if it is not already running."""
        if self.is_running() or self.is_ready():
            return

        self._process = self._reaper_launcher()
        if self._process is None:
            return

        self._wait_until_reaper_ready()
        self._window_minimizer()



    def open_project(self, song: Song) -> None:

        """Open the song project file."""
        if not song.project_path.exists():
            raise FileNotFoundError(f"Projeto nao encontrado: {song.project_path}")

        if self._current_song == song:
            return

        if not self.is_running() and not self.is_ready():
            self.start()

        project_process = self._project_launcher(song.project_path)

        self._minimize_reaper_during_project_load()
        if self._process is None:
            self._process = project_process
        self._current_song = song
        self._playing = False

    def play_from_start(self, song: Song) -> None:
        """Open a project and start playback from the beginning."""
        if self._current_song is not None and self._current_song != song:
            self.close_project()

        self.open_project(song)
        self._wait_until_project_loaded()
        self.play()
        time.sleep(0.15)
        self._go_to_start()

    def close_project(self) -> None:
        """Close the current project while keeping REAPER open."""

        if self._current_song is None:
            return

        if platform.system() == "Darwin":
            self._close_current_project()
        else:
            self._send_action_or_raise(ACTION_CLOSE_PROJECT)

        self._current_song = None
        self._playing = False

    def _close_current_project(self) -> None:
        """Close the current project without closing REAPER."""

        executable = self._find_reaper_executable()
        if executable is None:
            return

        subprocess.run(
            [str(executable), "-close:nosave"],
            check=False,
        )


    def play(self) -> None:
        """Start playback in REAPER."""
        if self._current_song is None:
            return

        if self._osc is not None:
            self._osc.play()
        else:
            self._send_action_or_raise(ACTION_PLAY)

        self._playing = True

    def pause(self) -> None:
        """Pause playback in REAPER."""
        if self._current_song is None:
            return

        if self._osc is not None:
            self._osc.pause()
        else:
            self._send_action_or_raise(ACTION_PAUSE)

        self._playing = False

    def stop(self) -> None:
        """Stop playback and close the current project, keeping REAPER open."""
        if self._current_song is not None:
            self._send_action_or_raise(ACTION_STOP)

        self.close_project()

    def shutdown(self) -> None:

        if platform.system() == "Darwin":
            subprocess.run([
                "osascript",
                "-e",
                'tell application "REAPER" to quit'
            ])
        else:
            if self.is_running() or self._ready_checker():
                self._send_action(ACTION_QUIT)

        self._close_process()

        self._current_song = None
        self._playing = False

    def current_project(self) -> Optional[Song]:
        """Return the current song project reference."""
        return self._current_song

    def is_playing(self) -> bool:
        """Return whether playback is marked as active."""
        return self._playing

    def is_running(self) -> bool:
        """Return whether the REAPER process started by LiveRig is still running."""
        return self._process is not None and self._process.poll() is None

    def is_ready(self) -> bool:
        """Return whether REAPER can receive commands."""
        if platform.system() == "Darwin":
            return self.is_running()
        return self._ready_checker()

    def _wait_until_reaper_ready(self) -> None:
        deadline = time.monotonic() + self._reaper_ready_timeout
        while time.monotonic() < deadline:
            if self._ready_checker():
                return
            time.sleep(0.1)

        raise RuntimeError("REAPER nao ficou pronto para receber comandos.")


    def _wait_until_project_loaded(self) -> None:
        """Wait until REAPER is ready to receive OSC commands."""

        deadline = time.monotonic() + 10

        while time.monotonic() < deadline:
            if self.is_ready():
                return

            time.sleep(0.05)

        raise RuntimeError("Projeto não ficou pronto para reprodução.")


    def _send_action_or_raise(self, action_id: int) -> None:
        if not self._action_sender(action_id):
            raise RuntimeError(f"REAPER nao aceitou o Action ID {action_id}.")

    def _close_process(self) -> None:
        if self._process is None or self._process.poll() is not None:
            self._process = None
            return

        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
        finally:
            self._process = None

    def _launch_project_file(
        self, 
        project_path: Optional[Path]
    ) -> Optional[subprocess.Popen]:

        system = platform.system()
        if system == "Windows":
            os.startfile(project_path)  # type: ignore[attr-defined]
            return None

        executable = self._find_reaper_executable()
        if executable is not None and project_path is None:
            return self._launch_reaper_executable(
                executable, 
                None, 
                reuse_instance=True,
            )

        if system == "Darwin":
            return subprocess.Popen(["open", "-gj", str(project_path)])

        return subprocess.Popen(["xdg-open", str(project_path)])

    def _launch_reaper(self) -> Optional[subprocess.Popen]:
        executable = self._find_reaper_executable()
        if executable is not None:
            return self._launch_reaper_executable(executable, None, reuse_instance=False)
        system = platform.system()
        if system == "Windows":
            raise RuntimeError(
                "REAPER nao encontrado. Adicione o caminho do reaper.exe "
                "em WINDOWS_REAPER_CANDIDATES no arquivo liverrig/reaper_controller.py."
            )
        if system == "Darwin":
            return subprocess.Popen(["open", "-gj", "-a", "REAPER"])
        return subprocess.Popen(["reaper"])

    def _find_reaper_executable(self) -> Optional[Path]:
        system = platform.system()
        candidates: list[Path] = []
        if system == "Windows":
            candidates = WINDOWS_REAPER_CANDIDATES
        elif system == "Darwin":
            candidates = MACOS_REAPER_CANDIDATES
        return next((path for path in candidates if path.exists()), None)

    def _launch_reaper_executable(
        self,
        executable: Path,
        project_path: Optional[Path],
        reuse_instance: bool,
    ) -> subprocess.Popen:
        startupinfo = None
        creationflags = 0
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 7
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        command = [str(executable)]
        if reuse_instance:
            command.append("-nonewinst")
        if project_path is not None:
            command.append(str(project_path))

        return subprocess.Popen(
            command,
            cwd=str(project_path.parent if project_path is not None else executable.parent),
            startupinfo=startupinfo,
            creationflags=creationflags,
        )

    def _is_reaper_action_target_ready(self) -> bool:
        if platform.system() != "Windows":
            return self._process is None or self._process.poll() is None

        return self._find_reaper_window() is not None

    def _send_reaper_action(self, action_id: int) -> bool:
        if platform.system() != "Windows":
            return False

        hwnd = self._find_reaper_window()
        if hwnd is None:
            return False

        user32 = ctypes.windll.user32
        user32.SendMessageW(hwnd, 0x0111, action_id, 0)
        return True

    def _minimize_reaper_window(self) -> None:
        if platform.system() != "Windows":
            return

        hwnd = self._find_reaper_window()
        if hwnd is None:
            return

        ctypes.windll.user32.ShowWindow(hwnd, 6)

    def _minimize_reaper_during_project_load(self) -> None:
        if platform.system() != "Windows":
            self._window_minimizer()
            return

        if self._project_load_minimize_seconds <= 0:
            self._window_minimizer()
            return

        deadline = time.monotonic() + self._project_load_minimize_seconds
        while time.monotonic() < deadline:
            self._window_minimizer()
            time.sleep(0.05)

    def _find_reaper_window(self) -> Optional[int]:
        user32 = ctypes.windll.user32
        target_pid = self._process.pid if self._process is not None else None
        found_hwnd: list[int] = []

        enum_windows_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def callback(hwnd: int, _lparam: int) -> bool:
            class_name = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_name, len(class_name))
            if class_name.value != "REAPERwnd":
                return True

            if target_pid is not None:
                pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value != target_pid:
                    return True

            found_hwnd.append(hwnd)
            return False

        user32.EnumWindows(enum_windows_proc(callback), 0)
        return found_hwnd[0] if found_hwnd else None


    def install_lua_script(self) -> Path:
        """
        Instala o script LiveRigPosition.lua na pasta Scripts do REAPER.
        Retorna o caminho onde o script foi instalado.
        """

        # Pasta de recursos do REAPER
        system = platform.system()

        if system == "Windows":
            reaper_scripts = (
                Path.home()
                / "AppData"
                / "Roaming"
                / "REAPER"
                / "Scripts"
                / "LiveRig"
            )

        elif system == "Darwin":
            reaper_scripts = (
                Path.home()
                / "Library"
                / "Application Support"
                / "REAPER"
                / "Scripts"
                / "LiveRig"
            )

        else:
            reaper_scripts = (
                Path.home()
                / ".config"
                / "REAPER"
                / "Scripts"
                / "LiveRig"
            )

        reaper_scripts.mkdir(parents=True, exist_ok=True)

        # Script distribuído com o LiveRig
        source = Path(__file__).resolve().parent / "assets" / "LiveRigPosition.lua"

        if not source.exists():
            raise FileNotFoundError(f"Script não encontrado: {source}")

        destination = reaper_scripts / "LiveRigPosition.lua"

        shutil.copy2(source, destination)
        startup = reaper_scripts.parent / "__startup.lua"

        startup.write_text(
            'dofile(reaper.GetResourcePath() .. "/Scripts/LiveRig/LiveRigPosition.lua")',
            encoding="utf-8",
        )

        return destination
