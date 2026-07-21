from reaper_controller import ReaperController
from settings import AppSettings
from views.ui import run_app


def main() -> None:
    settings = AppSettings()
    reaper = ReaperController()

    run_app(settings, reaper)


if __name__ == "__main__":
    main()
