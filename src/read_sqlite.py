import sqlite3
from src.sqlite_store import DB_FILE

with sqlite3.connect(str(DB_FILE)) as conn:
    rows = conn.execute(
        "SELECT id, created_at, content, tags, source FROM entries ORDER BY created_at ASC"
    ).fetchall()

for row in rows:
    print(row)