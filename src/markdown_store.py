from datetime import datetime
from config import APP_FOLDER, LOG_FILE


def ensure_log_exists():
    """
    Creates the GhostNote folder and markdown file if they do not exist.
    """

    APP_FOLDER.mkdir(parents=True, exist_ok=True)

    if not LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")


def add_entry(note_text):
    """
    Adds a timestamped entry to the markdown log.
    """

    ensure_log_exists()

    now = datetime.now()

    date_header = now.strftime("## %Y-%m-%d")
    time_stamp = now.strftime("%I:%M %p").lstrip("0")

    entry_line = f"- {time_stamp} - {note_text}\n"

    existing_content = LOG_FILE.read_text(encoding="utf-8")

    if date_header not in existing_content:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(f"\n{date_header}\n\n")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(entry_line)