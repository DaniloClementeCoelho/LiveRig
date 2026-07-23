import logging

from config import LOGS_DIR
from reaper_controller import ReaperController
from settings import AppSettings
from views.ui import run_app


def setup_logging() -> None:
    logging.basicConfig(
        filename=LOGS_DIR / "liverig.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> None:
    setup_logging()
    logging.getLogger(__name__).info("LiveRig iniciando.")

    settings = AppSettings()
    reaper = ReaperController()

    run_app(settings, reaper)


if __name__ == "__main__":
    main()
