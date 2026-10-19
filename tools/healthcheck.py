"""Private container probe: check SQLite directly, without forging proxy headers."""

import sqlite3
import sys
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db


def main():
    try:
        with closing(
            sqlite3.connect(db.DB_PATH.as_uri() + "?mode=ro", uri=True, timeout=3)
        ) as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            conn.execute("SELECT id FROM issues LIMIT 1").fetchone()
        # A DB-only probe cannot prove the HTTP process is responsive; also open the socket.
        import os
        import socket

        with socket.create_connection(("127.0.0.1", int(os.getenv("PORT", "8787"))), timeout=3):
            pass
        return 0 if version == 2 else 1
    except (OSError, sqlite3.Error):
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
