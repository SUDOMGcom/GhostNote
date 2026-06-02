from datetime import datetime
import sqlite3
from src.config import APP_FOLDER, DB_FILE

#DB_FILE = APP_FOLDER / "ghostnote.db"


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

def add_entry(note_text, source="Right-Click", created_at=None, tags=""):
    note_text = note_text.strip()
    if not note_text: return
    ensure_db_exists()
    created_at = created_at or datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute("INSERT INTO entries (created_at, content, tags, source) VALUES (?, ?, ?, ?)", (created_at, note_text, tags, source))

def get_entries(start_date=None, end_date=None, search_text=None):
    ensure_db_exists()
    query, params = "SELECT id, created_at, content FROM entries WHERE 1=1", []
    if start_date: query, params = query + " AND date(created_at) >= ?", params + [start_date]
    if end_date: query, params = query + " AND date(created_at) <= ?", params + [end_date]
    if search_text: query, params = query + " AND (content LIKE ? OR tags LIKE ? OR source LIKE ?)", params + [f"%{search_text}%"] * 3
    query += " ORDER BY date(created_at) DESC, time(created_at) ASC"
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, params).fetchall()

def get_latest_entry_date():
    ensure_db_exists()
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn: row = conn.execute(
        "SELECT date(created_at) FROM entries ORDER BY created_at DESC LIMIT 1").fetchone()
    return row[0] if row else None

    return rows