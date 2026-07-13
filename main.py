from reaper_controller import ReaperController
from settings import AppSettings
from views.ui import run_app
from version import APP_NAME, APP_VERSION


def main() -> None:

    settings = AppSettings()
    reaper = ReaperController()

    reaper.install_lua_script()

    try:
        run_app(settings, reaper)
    except RuntimeError as exc:
        print(str(exc))


if __name__ == "__main__":
    main()
