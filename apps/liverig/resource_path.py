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
    root = app_root()
    path = root.joinpath(*parts)
    if path.exists():
        return path

    if parts and parts[0] == "visual-studio":
        return root.parent.joinpath(*parts)

    return path
