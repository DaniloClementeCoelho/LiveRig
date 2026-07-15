from reaper_controller import ReaperController
from settings import AppSettings
from version import APP_NAME, APP_VERSION
from views.ui import run_app
from visual_sync import VisualSyncManager


def main() -> None:

    settings = AppSettings()
    reaper = ReaperController()

    visual_sync = VisualSyncManager(reaper)

    try:
        visual_sync.start()
    except Exception as ex:
        print(f"[VisualSync] Não foi possível iniciar: {ex}")

    reaper.install_lua_script()

    try:
        run_app(settings, reaper)
    finally:
        visual_sync.stop()


if __name__ == "__main__":
    main()