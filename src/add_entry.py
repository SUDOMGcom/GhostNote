import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.sqlite_store import add_entry
from src.ui.prompt_window import PromptWindow


def handle_submit(note_text, tags=""):
    add_entry(note_text, source="Right-Click", tags=tags)


if __name__ == "__main__":
    app = PromptWindow(handle_submit)
    app.run()