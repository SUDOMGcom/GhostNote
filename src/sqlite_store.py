from datetime import datetime
import sqlite3
from src.config import APP_FOLDER

DB_FILE = APP_FOLDER / "ghostnote.db"


def ensure_db_exists():
    APP_FOLDER.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                source TEXT
            )
        """)


def add_entry(note_text, source="Right-Click"):
    note_text = note_text.strip()

    if not note_text:
        return

    ensure_db_exists()

    created_at = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute(
            """
            INSERT INTO entries (created_at, content, tags, source)
            VALUES (?, ?, ?, ?)
            """,
            (created_at, note_text, "", source)
        )

def get_entries():
    ensure_db_exists()

    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT id, created_at, content
            FROM entries
            ORDER BY date(created_at) DESC, time(created_at) ASC
        """).fetchall()

    return rows