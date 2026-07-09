"""Application configuration."""

from pathlib import Path
import os

APP_NAME = "LiveRig"

#
# Diretório da aplicação (somente leitura)
#
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#
# Diretório dos dados do usuário
#
if os.name == "nt":
    USER_DATA_DIR = Path(os.environ["APPDATA"]) / APP_NAME
else:
    USER_DATA_DIR = Path.home() / f".{APP_NAME.lower()}"

USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

SHOWS_DIR = USER_DATA_DIR / "shows"
LOGS_DIR = USER_DATA_DIR / "logs"
RUNTIME_DIR = USER_DATA_DIR / "runtime"
SETTINGS_FILE = USER_DATA_DIR / "settings.json"

SHOWS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
RUNTIME_DIR.mkdir(exist_ok=True)