"""Synthetic assertions executed inside disposable acceptance containers only."""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def ensure(condition, message="Container probe assertion failed"):
    if not condition:
        raise AssertionError(message)


def require_verification():
    if (
        os.getenv("PUBLIC_URL") != "https://pilot.example.org"
        or os.getenv("DATABASE_PATH") != "/data/verification.db"
        or os.getenv("EMAIL_DELIVERY_ENABLED") != "false"
        or os.getenv("ENABLE_LOCAL_GENERATION") != "false"
    ):
        raise RuntimeError("Requires the isolated synthetic container configuration")


def runtime():
    require_verification()
    ensure(os.getuid() == 10001, "Application must run as the image's unprivileged user")
    ensure(not Path("/app/.env").exists(), "Private configuration entered the image")
    ensure(not os.getenv("SMTP_HOST"), "Acceptance must not configure outbound SMTP")
    try:
        Path("/app/.acceptance-write").write_text("unexpected", encoding="utf-8")
    except OSError:
        pass
    else:
        raise AssertionError("Application filesystem was writable")
    target = Path("/data/.acceptance-write")
    target.write_text("synthetic", encoding="utf-8")
    target.unlink()
    print("Non-root runtime, private configuration exclusion and filesystem controls verified")


def seed():
    require_verification()
    import db

    with db.connect() as conn:
        identity = conn.execute("SELECT id FROM issues WHERE status='published'").fetchone()[0]
        subscriber = conn.execute(
            "INSERT INTO subscribers(email,status,unsubscribe_token,created_at,confirmed_at) VALUES(?,?,?,?,?)",
            (
                "fictional-container@example.org",
                "active",
                "synthetic-container-token",
                db.now(),
                db.now(),
            ),
        ).lastrowid
    ensure(db.claim_delivery(identity, subscriber))
    db.record_delivery(identity, subscriber, "sent")  # Ledger fixture only; never calls SMTP.
    print("Synthetic consent and simulated delivery ledger seeded without SMTP")


def fingerprint():
    require_verification()
    with sqlite3.connect("/data/verification.db") as conn:
        ensure(conn.execute("PRAGMA integrity_check").fetchall() == [("ok",)])
        ensure(not conn.execute("PRAGMA foreign_key_check").fetchone())
        ensure(conn.execute("PRAGMA user_version").fetchone()[0] == 2)
        ensure(
            conn.execute("SELECT count(*) FROM issues WHERE status='published'").fetchone()[0] == 1
        )
        ensure(
            conn.execute(
                "SELECT count(*) FROM subscribers WHERE status='active' AND confirmed_at IS NOT NULL"
            ).fetchone()[0]
            == 1
        )
        ensure(
            conn.execute("SELECT count(*) FROM deliveries WHERE status='sent'").fetchone()[0] == 1
        )
        # Rate-limit attempts deliberately change across logins and v1 migration. Compare
        # every business table, including source evidence, history, consent and the ledger.
        payload = "\n".join(
            line
            for line in conn.iterdump()
            if line.startswith("INSERT INTO") and not line.startswith('INSERT INTO "rate_limits"')
        ).encode()
    print(hashlib.sha256(payload).hexdigest())


def proxy():
    # This client has no credentials and can contact only the internal Docker test network.
    def call(path, data=None):
        request = Request(
            "http://proxy" + path,
            headers={"Host": "pilot.example.org", "X-Forwarded-Proto": "http"},
            data=data,
        )
        try:
            # Fixed internal container alias on a network without external access.
            response = urlopen(request, timeout=10)  # nosec B310
        except HTTPError as exc:
            response = exc
        with response:
            return response.code, response.read()

    ensure(call("/health")[0] == 200, "Caddy did not forward canonical HTTPS metadata")
    status, body = call("/archive")
    ensure(status == 200 and b"SYNTHETIC" in body)
    for path in ("/admin", "/api/admin/data", "/api/login", "/api/logout"):
        ensure(call(path)[0] == 403, "Editor CIDR restriction was bypassed")
    ensure(call("/api/subscribe", b"x" * 140001)[0] == 413)
    print(json.dumps({"proxy_checks": 7, "public_tls": "NOT_TESTED", "external_ports": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("runtime", "seed", "fingerprint", "proxy"))
    args = parser.parse_args()
    globals()[args.action]()


if __name__ == "__main__":
    main()
