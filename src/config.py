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
        "bg": "#eef2f6",
        "panel": "#f8fafc",
        "text": "#1e293b",
        "muted": "#64748b",
        "entry_bg": "#e9eef7",
        "entry_fg": "#0f172a",

        "button_bg": "#4f7a65",
        "button_fg": "#ffffff",
        "button_hover": "#5c8b74",
        "button_pressed": "#436756",
        "button_disabled": "#cbd5e1",
        "button_disabled_fg": "#94a3b8",

        "border": "#d6deeb",
        "focus": "#7aa2ff",
        "selection": "#cfe0ff"
    },
    "dark": {
        "bg": "#0f1117",
        "panel": "#1a1f2b",
        "text": "#e8ecf3",
        "muted": "#94a3b8",
        "entry_bg": "#232938",
        "entry_fg": "#f8fafc",

        "button_bg": "#166534",
        "button_fg": "#f8fafc",
        "button_hover": "#1f7a3f",
        "button_pressed": "#14532d",
        "button_disabled": "#2a3142",
        "button_disabled_fg": "#6b7280",

        "border": "#2c3444",
        "focus": "#7aa2ff",
        "selection": "#2f4b7c"
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
