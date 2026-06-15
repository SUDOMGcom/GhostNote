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
        conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")

def add_entry(note_text, source="Right-Click", created_at=None, tags=""):
    note_text = note_text.strip()
    if not note_text: return
    ensure_db_exists()
    created_at = created_at or datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute("INSERT INTO entries (created_at, content, tags, source) VALUES (?, ?, ?, ?)", (created_at, note_text, tags, source))

def get_entries(start_date=None, end_date=None, search_text=None):
    ensure_db_exists()
    query, params = "SELECT id, created_at, content, tags FROM entries WHERE 1=1", []
    if start_date: query, params = query + " AND date(created_at) >= ?", params + [start_date]
    if end_date: query, params = query + " AND date(created_at) <= ?", params + [end_date]
    if search_text: query, params = query + " AND (content LIKE ? OR tags LIKE ? OR source LIKE ?)", params + [f"%{search_text}%"] * 3
    query += " ORDER BY date(created_at) DESC, time(created_at) ASC"
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, params).fetchall()

def get_entry(entry_id):
    ensure_db_exists()
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT id, created_at, content, tags, source FROM entries WHERE id = ?", (entry_id,)).fetchone()

def get_latest_entry_date():
    ensure_db_exists()
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn: row = conn.execute(
        "SELECT date(created_at) FROM entries ORDER BY created_at DESC LIMIT 1").fetchone()
    return row[0] if row else None

def get_setting(key, default=None):
    ensure_db_exists()
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row[0] if row else default

def set_setting(key, value):
    ensure_db_exists()
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, str(value)))
        conn.commit()

def reset_popup_settings():
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute("DELETE FROM settings WHERE key LIKE 'popup_%'")
        conn.commit()

def restore_default_settings():
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute("DELETE FROM settings")
        conn.commit()

def update_entry(entry_id, content, created_at, tags=None):
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute("UPDATE entries SET content = ?, created_at = ?, tags = COALESCE(?, tags) WHERE id = ?", (content, created_at, tags, entry_id))
        conn.commit()

def delete_entry(entry_id):
    with sqlite3.connect(str(DB_FILE), timeout=5) as conn:
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()

if __name__ == "__main__":
    set_setting("popup_prompt", "What are you working on?")
    print(get_setting("popup_prompt"))

