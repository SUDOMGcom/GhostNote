from pathlib import Path
import json

APP_NAME = "GhostNote"
APP_VERSION = "1.0"
APP_VENDOR = "SUDOMG"
APP_URL = "https://sudomg.com/ghostnote/"
VENDOR_URL = "https://sudomg.com"
DOWNLOAD_URL = "https://www.github.com/SUDOMGcom/ghostnote/latest"

DEFAULT_APP_FOLDER = Path.home() / "AppData" / "Roaming" / "GhostNote"
DATABASE_CONFIG_FILE = DEFAULT_APP_FOLDER / "database.json"

DEFAULT_SETTINGS = {
    "db_file": str(DEFAULT_APP_FOLDER / "ghostnote.db")
}

THEMES = {
    "light": {
        "bg": "#eef2f6",
        "panel": "#f8fafc",
        "text": "#1e293b",
        "muted": "#64748b",
        "entry_bg": "#e9eef7",
        "entry_fg": "#0f172a",

        "title_outline": "#70747A",
        "title_ghost": "#FFFFFF",
        "title_note": "#B8BCC2",

        "button_bg": "#4f7a65",
        "button_fg": "#ffffff",
        "button_hover": "#5c8b74",
        "button_pressed": "#436756",
        "button_disabled": "#cbd5e1",
        "button_disabled_fg": "#94a3b8",
        "active_filter_fg": "#f97316",

        "border": "#8A8F96",
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

        "title_outline": "#70747A",
        "title_ghost": "#FFFFFF",
        "title_note": "#B8BCC2",

        "button_bg": "#166534",
        "button_fg": "#f8fafc",
        "button_hover": "#1f7a3f",
        "button_pressed": "#14532d",
        "button_disabled": "#2a3142",
        "button_disabled_fg": "#6b7280",
        "active_filter_fg": "#f97316",

        "border": "#2c3444",
        "focus": "#7aa2ff",
        "selection": "#2f4b7c"
    }
}

def load_settings():
    DEFAULT_APP_FOLDER.mkdir(parents=True, exist_ok=True)

    if not DATABASE_CONFIG_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    with DATABASE_CONFIG_FILE.open("r", encoding="utf-8") as file:
        saved_settings = json.load(file)

    return {**DEFAULT_SETTINGS, **saved_settings}


def save_settings(settings):
    DEFAULT_APP_FOLDER.mkdir(parents=True, exist_ok=True)

    with DATABASE_CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)

def get_theme():
    try:
        from src.sqlite_store import get_setting
        theme_name = get_setting("general_theme", "dark")
    except Exception:
        theme_name = "dark"

    return THEMES.get(theme_name, THEMES["dark"])

SETTINGS = load_settings()

APP_FOLDER = DEFAULT_APP_FOLDER
DB_FILE = Path(SETTINGS["db_file"])
THEME = "dark"
