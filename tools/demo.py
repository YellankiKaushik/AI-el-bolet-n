"""Run an isolated fictional workspace on loopback, with no real email or .env access."""

import argparse
import copy
import json
import os
import re
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def workspace(name):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", name):
        raise ValueError("Demo name must contain 1–40 letters, numbers, hyphens or underscores")
    base = (ROOT / ".tmp").resolve()
    directory = (base / name).resolve()
    if not directory.is_relative_to(base):
        raise ValueError("Demo workspace must remain inside .tmp")
    return directory


def seed_demo(database):
    """Seed only an empty database explicitly inside a private demo workspace."""
    import db

    database = Path(database).resolve()
    base = (ROOT / ".tmp").resolve()
    if not database.is_relative_to(base) or database.name != "demo.db":
        raise ValueError("Refusing to seed outside an isolated .tmp demo.db")
    if db.DB_PATH.resolve() != database:
        raise ValueError("Active database does not match the demo target")
    with db.connect() as conn:
        if conn.execute("SELECT COUNT(*) FROM issues").fetchone()[0]:
            return False  # A restart never resets edits or republishes user work.
        occupied = conn.execute(
            "SELECT (SELECT COUNT(*) FROM stories) + (SELECT COUNT(*) FROM subscribers) + (SELECT COUNT(*) FROM deliveries)"
        ).fetchone()[0]
        if occupied:
            raise ValueError("Refusing to seed a non-empty workspace")
    fixture = json.loads(
        (ROOT / "docs/examples/synthetic-newsletter.json").read_text(encoding="utf-8")
    )
    editions = [
        ("Demo: Build with evidence, not hype", "Research", "published"),
        ("Demo: Useful tools, thoughtful choices", "Tools", "published"),
        ("Demo: A quieter kind of AI briefing", "AI", "published"),
        ("Demo: Your next briefing starts here", "AI", "draft"),
        ("Demo: A field guide to useful AI", "Industry", "review"),
    ]
    for index, (title, topic, status) in enumerate(editions):
        payload = copy.deepcopy(fixture)
        payload.update(title=title, topic=topic)
        identity = db.create_issue(payload)
        if status in ("review", "published"):
            db.review(identity)
        if status == "published":
            db.approve(identity)
            db.publish(identity)
            stamp = (datetime.now(timezone.utc) - timedelta(days=3 - index)).isoformat(
                timespec="seconds"
            )
            with db.connect() as conn:
                conn.execute("UPDATE issues SET published_at=? WHERE id=?", (stamp, identity))
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--name", default="demo", help="Private .tmp workspace name; reused without resetting"
    )
    parser.add_argument("--port", default=8789, type=int)
    parser.add_argument(
        "--empty",
        action="store_true",
        help="Do not seed fictional editions; useful for manual acceptance",
    )
    args = parser.parse_args()
    if args.port == 8787 or not 1024 <= args.port <= 65535:
        parser.error("Choose an unprivileged demo port other than the real app's 8787")
    directory = workspace(args.name)
    directory.mkdir(parents=True, exist_ok=True)
    database = directory / "demo.db"
    credentials = directory / "credentials.json"
    if credentials.exists():
        config = json.loads(credentials.read_text(encoding="utf-8"))
    else:
        config = {
            "ADMIN_PASSWORD": secrets.token_urlsafe(24),
            "SESSION_SECRET": secrets.token_urlsafe(48),
        }
        descriptor = os.open(credentials, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(config, handle)
    # Do not load the real .env. Deliberately override inherited mail/host/data settings.
    os.environ.update(
        {
            **config,
            "HOST": "127.0.0.1",
            "PORT": str(args.port),
            "APP_ENV": "development",
            "PUBLIC_URL": f"http://127.0.0.1:{args.port}",
            "DATABASE_PATH": str(database),
            "EMAIL_DELIVERY_ENABLED": "false",
            "ENABLE_LOCAL_GENERATION": "false",
            "DEMO_MODE": "true",
        }
    )
    import db
    import server
    from instance import instance_lock

    server.validate_config()
    with instance_lock(database):
        db.init()
        if not args.empty:
            seed_demo(database)
        print(f"Demo: http://127.0.0.1:{args.port} | editor: /admin", flush=True)
        print(
            f"Fictional workspace only. Email and generation disabled. Credentials: {credentials}",
            flush=True,
        )
        server.BoundedHTTPServer(("127.0.0.1", args.port), server.Handler).serve_forever()


if __name__ == "__main__":
    main()
