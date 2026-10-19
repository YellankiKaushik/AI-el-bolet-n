"""Consistent online SQLite backups and non-destructive offline restores.

Backups contain private subscriber data. Store them on access-controlled encrypted storage.
Restore always creates a NEW database path; it never overwrites the live database.
"""

import argparse
import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from instance import instance_lock


def read_only(path):
    path = Path(path).resolve(strict=True)
    return sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=15)


def validate(connection):
    if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise ValueError("Database integrity check failed")
    if connection.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("Database foreign-key check failed")
    tables = {
        row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if not {"issues", "stories", "subscribers", "deliveries"}.issubset(tables):
        raise ValueError("Not a Signal Daily database")
    if connection.execute("PRAGMA user_version").fetchone()[0] > 2:
        raise ValueError("Backup needs a newer application version")


def copy_database(source, destination):
    source = Path(source).resolve(strict=True)
    destination = Path(destination).resolve()
    if source == destination:
        raise ValueError("Source and destination must differ")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if any(Path(str(destination) + suffix).exists() for suffix in ("-wal", "-shm", "-journal")):
        raise ValueError("Destination has SQLite sidecars; choose a new path")
    with closing(read_only(source)) as original:
        validate(original)
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(descriptor)
        try:
            with closing(sqlite3.connect(destination)) as backup:
                original.backup(backup, pages=256, sleep=0.05)
                validate(backup)
                backup.execute("PRAGMA journal_mode=DELETE")
            with destination.open("r+b") as handle:
                os.fsync(handle.fileno())
        except BaseException:
            destination.unlink(missing_ok=True)
            raise
    return destination


def restore_database(source, destination):
    with instance_lock(destination):
        return copy_database(source, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("backup", "restore", "check"))
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path, nargs="?")
    args = parser.parse_args()
    if args.action == "check":
        with closing(read_only(args.source)) as connection:
            validate(connection)
        print("Integrity and foreign keys verified")
    else:
        if args.destination is None:
            parser.error("destination is required; restore must use a new path")
        action = restore_database if args.action == "restore" else copy_database
        result = action(args.source, args.destination)
        print(f"Verified {args.action}: {result}")


if __name__ == "__main__":
    main()
