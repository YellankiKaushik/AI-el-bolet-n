"""SQLite persistence for Signal Daily. Requires Python 3.11+."""

import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from validation import canonical_url, verify_issue

DB_PATH = Path(
    os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parent / "data/signal_daily.db"))
)
if not DB_PATH.is_absolute():
    DB_PATH = Path(__file__).resolve().parent / DB_PATH


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ClosingConnection(sqlite3.Connection):
    """Commit or roll back, then close cleanly on context manager exit."""

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=15, factory=ClosingConnection)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA busy_timeout=15000")
    return c


def init():
    with connect() as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version > 2:
            raise RuntimeError("Database schema is newer than this application; do not downgrade")
        db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
                published_at TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
                subject TEXT NOT NULL, intro TEXT NOT NULL DEFAULT '',
                closing TEXT NOT NULL DEFAULT '', items_json TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','review','approved','published')),
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL, published_at TEXT
            );
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','active','unsubscribed')),
                verify_hash TEXT, unsubscribe_token TEXT NOT NULL,
                created_at TEXT NOT NULL, confirmed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS deliveries (
                id INTEGER PRIMARY KEY, issue_id INTEGER NOT NULL REFERENCES issues(id),
                subscriber_id INTEGER NOT NULL REFERENCES subscribers(id),
                status TEXT NOT NULL CHECK(status IN ('sending','sent','failed','uncertain')),
                error TEXT, created_at TEXT NOT NULL,
                UNIQUE(issue_id, subscriber_id)
            );
            CREATE INDEX IF NOT EXISTS ix_stories_created ON stories(created_at DESC);
            CREATE INDEX IF NOT EXISTS ix_issues_status ON issues(status, published_at DESC);
        """)
        # Versioned, transactional table rebuilds preserve existing records and foreign keys.
        if version < 1:
            db.executescript("""
                PRAGMA foreign_keys=OFF;
                BEGIN IMMEDIATE;
                CREATE TABLE issues_v1 (
                    id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
                    subject TEXT NOT NULL, intro TEXT NOT NULL DEFAULT '', closing TEXT NOT NULL DEFAULT '',
                    items_json TEXT NOT NULL DEFAULT '[]',
                    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','review','approved','published')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, published_at TEXT,
                    topic TEXT NOT NULL DEFAULT 'AI', version INTEGER NOT NULL DEFAULT 1);
                INSERT INTO issues_v1(id,slug,title,subject,intro,closing,items_json,status,created_at,updated_at,published_at)
                    SELECT id,slug,title,subject,intro,closing,items_json,status,created_at,updated_at,published_at FROM issues;
                DROP TABLE issues;
                ALTER TABLE issues_v1 RENAME TO issues;
                CREATE TABLE deliveries_v1 (
                    id INTEGER PRIMARY KEY, issue_id INTEGER NOT NULL REFERENCES issues(id),
                    subscriber_id INTEGER NOT NULL REFERENCES subscribers(id),
                    status TEXT NOT NULL CHECK(status IN ('sending','sent','failed','uncertain')),
                    error TEXT, created_at TEXT NOT NULL, UNIQUE(issue_id,subscriber_id));
                INSERT INTO deliveries_v1 SELECT * FROM deliveries;
                DROP TABLE deliveries;
                ALTER TABLE deliveries_v1 RENAME TO deliveries;
                ALTER TABLE subscribers ADD COLUMN verify_expires INTEGER;
                CREATE INDEX ix_issues_status ON issues(status,published_at DESC);
                PRAGMA user_version=1;
                COMMIT;
                PRAGMA foreign_keys=ON;
            """)
        db.executescript("""
            CREATE TABLE IF NOT EXISTS issue_events (
                id INTEGER PRIMARY KEY, issue_id INTEGER NOT NULL REFERENCES issues(id),
                action TEXT NOT NULL, snapshot_json TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY, kind TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL);
        """)
        if version < 2:
            db.executescript("""
                BEGIN IMMEDIATE;
                CREATE TABLE IF NOT EXISTS rate_limits (
                    identity TEXT PRIMARY KEY, started INTEGER NOT NULL, attempts INTEGER NOT NULL);
                PRAGMA user_version=2;
                COMMIT;
            """)
        if db.execute("PRAGMA foreign_key_check").fetchone():
            raise RuntimeError("Database foreign-key validation failed; restore a verified backup")


def rate_limited(identity, limit, window, timestamp):
    """Atomic fixed-window limits survive restarts; identity is a keyed hash, never an IP."""
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM rate_limits WHERE started<=?", (timestamp - 3600,))
        record = conn.execute("SELECT * FROM rate_limits WHERE identity=?", (identity,)).fetchone()
        if record and record["started"] > timestamp - window:
            if record["attempts"] >= limit:
                return True
            conn.execute("UPDATE rate_limits SET attempts=attempts+1 WHERE identity=?", (identity,))
        else:
            if conn.execute("SELECT COUNT(*) FROM rate_limits").fetchone()[0] >= 10000:
                return True
            conn.execute("INSERT OR REPLACE INTO rate_limits VALUES(?,?,1)", (identity, timestamp))
    return False


def row(r):
    if r is None:
        return None
    out = dict(r)
    if "items_json" in out:
        out["items"] = json.loads(out.pop("items_json"))
    return out


def get_issues(published_only=False, limit=30, search="", topic="", offset=0):
    with connect() as db:
        sql = """SELECT * FROM issues WHERE (?=0 OR status='published')
            AND (?='' OR instr(lower(title),lower(?))>0 OR instr(lower(intro),lower(?))>0)
            AND (?='' OR topic=?) ORDER BY COALESCE(published_at,created_at) DESC,id DESC
            LIMIT ? OFFSET ?"""
        return [
            row(x)
            for x in db.execute(
                sql,
                (
                    int(published_only),
                    search[:120],
                    search[:120],
                    search[:120],
                    topic,
                    topic,
                    min(5000, max(1, limit)),
                    max(0, offset),
                ),
            )
        ]


def get_issue(issue_id=None, slug=None, published_only=False):
    if not issue_id and not slug:
        return None
    with connect() as db:
        q = "SELECT * FROM issues WHERE (id=? OR slug=?) AND (?=0 OR status='published')"
        return row(
            db.execute(
                q, (issue_id, slug if issue_id is None else None, int(published_only))
            ).fetchone()
        )


def get_stories(limit=80):
    with connect() as db:
        return [
            dict(x)
            for x in db.execute("SELECT * FROM stories ORDER BY created_at DESC LIMIT ?", (limit,))
        ]


def insert_stories(stories):
    inserted = 0
    with connect() as db:
        for s in stories:
            try:
                url = canonical_url(s["url"])
                cur = db.execute(
                    "INSERT OR IGNORE INTO stories(title,url,source,description,published_at,created_at) VALUES(?,?,?,?,?,?)",
                    (
                        s["title"][:240],
                        url,
                        s["source"][:100],
                        s.get("description", "")[:1200],
                        s.get("published_at", "")[:90],
                        now(),
                    ),
                )
                inserted += cur.rowcount
            except (ValueError, KeyError, sqlite3.IntegrityError):
                pass
    return inserted


def new_slug(title):
    import re

    cleaned = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "edition"
    return cleaned + "-" + secrets.token_hex(3)


def create_issue(data):
    data = verify_issue(data)
    ts = now()
    title = str(data.get("title", "Untitled edition"))[:180]
    with connect() as db:
        cur = db.execute(
            "INSERT INTO issues(slug,title,subject,intro,closing,items_json,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (
                new_slug(title),
                title,
                str(data.get("subject", title))[:200],
                str(data.get("intro", ""))[:2500],
                str(data.get("closing", ""))[:1200],
                json.dumps(data.get("items", [])),
                "draft",
                ts,
                ts,
            ),
        )
        issue_id = cur.lastrowid
        db.execute("UPDATE issues SET topic=? WHERE id=?", (data["topic"], issue_id))
        event(db, issue_id, "created")
        return issue_id


def update_issue(issue_id, data):
    expected = data.get("version")
    data = verify_issue(data)
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        issue = db.execute("SELECT status,version FROM issues WHERE id=?", (issue_id,)).fetchone()
        if not issue:
            raise ValueError("Edition not found")
        if issue["status"] == "published":
            raise ValueError("Published editions cannot be edited")
        if expected is not None and expected != issue["version"]:
            raise ValueError("Edition changed. Reload before saving.")
        db.execute(
            "UPDATE issues SET title=?,subject=?,intro=?,closing=?,items_json=?,status=?,updated_at=?,topic=?,version=version+1 WHERE id=?",
            (
                data["title"],
                data["subject"],
                data["intro"],
                data["closing"],
                json.dumps(data["items"]),
                "draft",
                now(),
                data["topic"],
                issue_id,
            ),
        )
        event(db, issue_id, "saved")


def approve(issue_id):
    transition(issue_id, "review", "approved")


def review(issue_id):
    transition(issue_id, "draft", "review")


def revise(issue_id):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        cur = db.execute(
            "UPDATE issues SET status='draft',updated_at=?,version=version+1 WHERE id=? AND status IN ('review','approved')",
            (now(), issue_id),
        )
        if not cur.rowcount:
            raise ValueError("Only reviewed or approved editions can return to draft")
        event(db, issue_id, "revision_requested")


def transition(issue_id, expected, target):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        issue = db.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone()
        if not issue:
            raise ValueError("Edition not found")
        if issue["status"] != expected:
            raise ValueError(f"Edition must be {expected} before {target}")
        verify_issue(row(issue), complete=True)
        db.execute(
            "UPDATE issues SET status=?,updated_at=?,version=version+1 WHERE id=?",
            (target, now(), issue_id),
        )
        if target == "published":
            db.execute("UPDATE issues SET published_at=? WHERE id=?", (now(), issue_id))
        event(db, issue_id, target)


def publish(issue_id):
    transition(issue_id, "approved", "published")


def event(conn, issue_id, action):
    snapshot = row(conn.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone())
    conn.execute(
        "INSERT INTO issue_events(issue_id,action,snapshot_json,created_at) VALUES(?,?,?,?)",
        (issue_id, action, json.dumps(snapshot), now()),
    )


def history(issue_id):
    with connect() as conn:
        return [
            dict(x)
            for x in conn.execute(
                "SELECT id,action,created_at FROM issue_events WHERE issue_id=? ORDER BY id DESC LIMIT 100",
                (issue_id,),
            )
        ]


def log_operation(kind, detail):
    with connect() as conn:
        conn.execute(
            "INSERT INTO operations(kind,detail,created_at) VALUES(?,?,?)",
            (kind, str(detail)[:500], now()),
        )


def stats():
    with connect() as db:
        return {
            "stories": db.execute("SELECT COUNT(*) FROM stories").fetchone()[0],
            "drafts": db.execute(
                "SELECT COUNT(*) FROM issues WHERE status!='published'"
            ).fetchone()[0],
            "published": db.execute(
                "SELECT COUNT(*) FROM issues WHERE status='published'"
            ).fetchone()[0],
            "subscribers": db.execute(
                "SELECT COUNT(*) FROM subscribers WHERE status='active'"
            ).fetchone()[0],
            "pending": db.execute(
                "SELECT COUNT(*) FROM subscribers WHERE status='pending'"
            ).fetchone()[0],
        }


def delivery_targets(issue_id, limit=100):
    with connect() as db:
        return [
            dict(x)
            for x in db.execute(
                """SELECT s.id,s.email,s.unsubscribe_token FROM subscribers s
              LEFT JOIN deliveries d ON d.subscriber_id=s.id AND d.issue_id=? AND d.status IN ('sending','sent','uncertain')
              WHERE s.status='active' AND d.id IS NULL ORDER BY s.id LIMIT ?""",
                (issue_id, min(100, max(1, limit))),
            )
        ]


def delivery_target_count(issue_id):
    with connect() as conn:
        return conn.execute(
            """SELECT COUNT(*) FROM subscribers s LEFT JOIN deliveries d
            ON d.subscriber_id=s.id AND d.issue_id=? AND d.status IN ('sending','sent','uncertain')
            WHERE s.status='active' AND d.id IS NULL""",
            (issue_id,),
        ).fetchone()[0]


def record_delivery(issue_id, subscriber_id, status, error=None):
    with connect() as db:
        db.execute(
            """INSERT INTO deliveries(issue_id,subscriber_id,status,error,created_at) VALUES(?,?,?,?,?)
            ON CONFLICT(issue_id,subscriber_id) DO UPDATE SET status=excluded.status,error=excluded.error,created_at=excluded.created_at""",
            (issue_id, subscriber_id, status, (error or "")[:400], now()),
        )


def claim_delivery(issue_id, subscriber_id):
    """Reserve once under SQLite's write lock, including across processes."""
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if not conn.execute(
            "SELECT 1 FROM issues WHERE id=? AND status='published'", (issue_id,)
        ).fetchone():
            raise ValueError("Publish the approved edition before delivery")
        if not conn.execute(
            "SELECT 1 FROM subscribers WHERE id=? AND status='active'", (subscriber_id,)
        ).fetchone():
            return False
        cur = conn.execute(
            """INSERT INTO deliveries(issue_id,subscriber_id,status,error,created_at) VALUES(?,?,'sending','',?)
            ON CONFLICT(issue_id,subscriber_id) DO UPDATE SET status='sending',error='',created_at=excluded.created_at
            WHERE deliveries.status='failed' """,
            (issue_id, subscriber_id, now()),
        )
        return bool(cur.rowcount)
