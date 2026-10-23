"""Explicit export of one approved AND published edition. Never pushes or sends email."""

import argparse
import json
import os
import re
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validation import verify_issue


def public_edition(database, issue_id, version):
    with closing(
        sqlite3.connect(Path(database).resolve(strict=True).as_uri() + "?mode=ro", uri=True)
    ) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("BEGIN")
        row = conn.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone()
        if not row or row["status"] != "published" or row["version"] != version:
            raise ValueError(
                "Choose the current version of an explicitly approved, published edition"
            )
        approval = conn.execute(
            "SELECT snapshot_json FROM issue_events WHERE issue_id=? AND action='approved' ORDER BY id DESC LIMIT 1",
            (issue_id,),
        ).fetchone()
        if not approval or json.loads(approval[0])["version"] != version - 1:
            raise ValueError("Matching human approval history is required")
        issue = dict(row)
        issue["items"] = json.loads(issue.pop("items_json"))
        validated = verify_issue(issue, complete=True)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", issue["slug"]):
            raise ValueError("Unsafe public slug")
        return {
            "id": f"signal-{issue_id}",
            "version": version,
            "slug": issue["slug"],
            "publishedAt": issue["published_at"],
            **{key: validated[key] for key in ("title", "topic", "intro", "closing")},
            "items": [
                {
                    key: item.get(key, "")
                    for key in ("headline", "summary", "why", "source", "url", "published_at")
                }
                for item in validated["items"]
            ],
        }


def export(database, issue_id, version, destination):
    edition = public_edition(database, issue_id, version)
    destination = Path(destination)
    if destination.suffix != ".json" or destination.resolve() == Path(database).resolve():
        raise ValueError("Choose a public JSON destination")
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock = destination.with_suffix(".json.lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    temporary = None
    try:
        os.close(descriptor)
        records = (
            json.loads(destination.read_text(encoding="utf-8")) if destination.exists() else []
        )
        if not isinstance(records, list):
            raise ValueError("Public catalog must be an array")
        for record in records:
            if record["id"] == edition["id"] or record["slug"] == edition["slug"]:
                if record == edition:
                    return False
                raise ValueError(
                    "Conflicting public revision; do not overwrite an existing publication"
                )
        records.append(edition)
        records.sort(key=lambda record: record["publishedAt"], reverse=True)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=destination.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(records, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        return True
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
        lock.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--output", required=True, help="Portfolio src/data/newsletters.json")
    args = parser.parse_args()
    print(
        "Exported public edition"
        if export(args.database, args.issue, args.version, args.output)
        else "Already exported; no change"
    )
