"""Bounded, one-shot RSS collection. Safe to schedule; never generates or publishes."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import load_env

load_env()
import db
import feeds


def main():
    db.init()
    stories, errors = feeds.fetch_all()
    count = db.insert_stories(stories)
    db.log_operation("scheduled_ingestion", f"{count} added; {len(errors)} errors")
    print(json.dumps({"added": count, "found": len(stories), "errors": errors}))
    return 1 if errors and not stories else 0


if __name__ == "__main__":
    raise SystemExit(main())
