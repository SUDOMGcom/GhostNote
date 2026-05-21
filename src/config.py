from pathlib import Path
import json

DEFAULT_APP_FOLDER = Path.home() / "Documents" / "GhostNote"
SETTINGS_FILE = DEFAULT_APP_FOLDER / "settings.json"

DEFAULT_SETTINGS = {
    "app_folder": str(DEFAULT_APP_FOLDER),
    "log_file": str(DEFAULT_APP_FOLDER / "ghostnote.md"),
    "theme": "dark"
}

THEMES = {
    "light": {
        "bg": "#f5f5f5",
        "panel": "#ffffff",
        "text": "#1f1f1f",
        "muted": "#666666",
        "entry_bg": "#ffffff",
        "entry_fg": "#1f1f1f"
    },
    "dark": {
        "bg": "#1e1e1e",
        "panel": "#2b2b2b",
        "text": "#f2f2f2",
        "muted": "#b0b0b0",
        "entry_bg": "#252526",
        "entry_fg": "#f2f2f2"
    }
}

def load_settings():
    DEFAULT_APP_FOLDER.mkdir(parents=True, exist_ok=True)

    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    with SETTINGS_FILE.open("r", encoding="utf-8") as file:
        saved_settings = json.load(file)

    return {**DEFAULT_SETTINGS, **saved_settings}


def save_settings(settings):
    DEFAULT_APP_FOLDER.mkdir(parents=True, exist_ok=True)

    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


SETTINGS = load_settings()

APP_FOLDER = Path(SETTINGS["app_folder"])
LOG_FILE = Path(SETTINGS["log_file"])
THEME = SETTINGS["theme"]