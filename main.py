import sys
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(1)

from src.app import GhostnoteApp
from src import config

def launch_viewer(args=None):
    app = GhostnoteApp()
    app.mainloop()

def launch_new(args=None):
    from src.add_entry import launch
    launch(args)

def show_version(args=None):
    from src.sqlite_store import get_setting
    db_schema = get_setting("schema_version")
    print(f"{config.APP_NAME} version: {config.APP_VERSION}")
    print(f"Database Schema version: {db_schema}")

def show_settings(args=None):
    from src.config import DB_FILE
    from src.sqlite_store import get_all_settings

    print("GhostNote Settings\n")
    print("Database")
    print("--------")
    print(f"Location: {DB_FILE}\n")
    print("Settings")
    print("--------")

    for key, value in get_all_settings():
        print(f"{key} = {value}")

def show_help(args=None):
    print(f"GhostNote {config.APP_VERSION} CLI")

    def show_general_help():
        print("""
    Usage:
        GhostNote.exe <command> [args]

    Commands:
        viewer (or blank)   Launches GhostNote Viewer
        new                 Launches New GhostNote Popup
        settings            Outputs GhostNote settings
        version             Outputs GhostNote App and Database Schema version
        help                Outputs the information you are seeing right now

    For command-specific help:
        GhostNote.exe help <command>
    """)

    if not args: show_general_help()
    elif args[0] == "new":
        print("""
        Usage:
            GhostNote.exe new [options]
        
        Opens/Creates a new GhostNote.
        
        Options:
            (blank)             Launches New GhostNote Popup
            help                Shows this screen
            
        * MORE OPTIONS COMING SOON!
        """)
    elif args[0] == "settings":
        print("""
        Usage:
            GhostNote.exe settings
        
        Outputs Current GhostNote Settings.

        Options:
            (blank)             Outputs Current GhostNote Settings.
            help                Shows this screen
            
        * SPECIFIC SETTINGS CALLS AND EDITING COMING SOON!
        """)
    elif args[0] == "version":
        print("""
        Usage:
            GhostNote.exe version

        Outputs Current GhostNote App and Database Schema Version.
        """)
    elif args[0] == "viewer":
        print("""
        Usage:
            GhostNote.exe
            GhostNote.exe viewer

        Launches GhostNote Viewer.
        """)
    else: show_general_help()

def main():
    if len(sys.argv) == 1:
        launch_viewer()
        return

    command = sys.argv[1].lower().lstrip("-")
    args = sys.argv[2:]

    if args and args[0].lower().lstrip("-") in ("help", "/?"):
        args = [command]
        command = "help"

    commands = {
        "new": launch_new,
        "settings": show_settings,
        "version": show_version,
        "viewer" : launch_viewer,
        "help": show_help,
        "/?": show_help,
    }

    commands.get(command, show_help)(args)

if __name__ == "__main__":
    main()