from reaper_controller import ReaperController
from settings import AppSettings
from views.ui import run_app
from version import APP_NAME, APP_VERSION
from visual_sync import VisualSyncManager
from network import NetworkServer

def main() -> None:

    settings = AppSettings()
    reaper = ReaperController()
    network = NetworkServer()
    #visual_sync = VisualSyncManager()


    try:
        network.start()
    except Exception as ex:
        print(f"[Network] Não foi possível iniciar o servidor HTTP: {ex}")


    reaper.install_lua_script()


    try:
        run_app(settings, reaper)
    finally:
        network.stop()

if __name__ == "__main__":
    main()
