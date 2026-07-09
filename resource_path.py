from pathlib import Path
import sys


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", None)
        if base:
            return Path(base)
        return Path(sys.executable).parent

    return Path(__file__).resolve().parent


def resource_path(*parts) -> Path:
    return app_root().joinpath(*parts)