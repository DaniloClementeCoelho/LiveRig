"""Application configuration."""

from pathlib import Path


APP_NAME = "LiveRig"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHOWS_DIR = PROJECT_ROOT / "shows"
LOGS_DIR = PROJECT_ROOT / "logs"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
SETTINGS_FILE = PROJECT_ROOT / "settings.json"
