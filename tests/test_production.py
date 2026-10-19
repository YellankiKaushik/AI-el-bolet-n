"""Production transport, persistence, recovery and mail regression tests; synthetic data only."""

import json
import os
import smtplib
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import closing
from http.client import HTTPConnection, HTTPResponse
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import db
import mailer
import production
import server
from instance import instance_lock
from tools.database_backup import copy_database, restore_database, read_only, validate


def synthetic():
    return {
        "title": "SYNTHETIC pilot verification",
        "subject": "SYNTHETIC test only",
        "intro": "Fictional content for application checks.",
        "closing": "No real news is represented.",
        "items": [
            {
                "headline": "Synthetic AI test",
                "summary": "A fictional test event.",
                "why": "Checks the editorial workflow.",
                "source": "Test fixture",
                "url": "https://example.org/synthetic",
            }
        ],
    }


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = db.DB_PATH
        db.DB_PATH = Path(self.temp.name) / "app.db"
        db.init()

    def tearDown(self):
        db.DB_PATH = self.previous
        self.temp.cleanup()


class TestRecovery(DatabaseTest):
    def test_online_backup_restore_preserves_all_data_and_state(self):
        identity = db.create_issue(synthetic())
        db.review(identity)
        db.approve(identity)
        db.publish(identity)
        with db.connect() as conn:
            subscriber = conn.execute(
                "INSERT INTO subscribers(email,status,unsubscribe_token,created_at) VALUES(?,?,?,?)",
                ("fictional-backup@example.org", "active", "synthetic-backup-token", db.now()),
            ).lastrowid
        self.assertTrue(db.claim_delivery(identity, subscriber))
        db.record_delivery(identity, subscriber, "sent")  # Simulated acceptance; no SMTP call.
        # Include committed WAL contents while the source connection remains open.
        with db.connect() as live:
            live.execute(
                "INSERT INTO operations(kind,detail,created_at) VALUES('test','WAL',?)", (db.now(),)
            )
            live.commit()
            backup = copy_database(db.DB_PATH, Path(self.temp.name) / "backup.db")
        restored = restore_database(backup, Path(self.temp.name) / "restored.db")
        with closing(read_only(restored)) as conn, closing(read_only(db.DB_PATH)) as original:
            validate(conn)
            self.assertEqual(list(conn.iterdump()), list(original.iterdump()))
        with self.assertRaises(FileExistsError):
            restore_database(backup, restored)
        self.assertEqual(db.get_issue(issue_id=identity)["status"], "published")

    def test_backup_rejects_missing_invalid_and_same_path(self):
        root = Path(self.temp.name)
        with self.assertRaises(FileNotFoundError):
            copy_database(root / "missing.db", root / "backup.db")
        with self.assertRaises(ValueError):
            copy_database(db.DB_PATH, db.DB_PATH)
        invalid = root / "invalid.db"
        with closing(sqlite3.connect(invalid)):
            pass
        with self.assertRaises(ValueError):
            copy_database(invalid, root / "backup.db")
        self.assertFalse((root / "backup.db").exists())

    def test_restore_rejects_running_target_and_orphan_sidecars(self):
        root = Path(self.temp.name)
        backup = copy_database(db.DB_PATH, root / "backup.db")
        target = root / "new.db"
        with instance_lock(target), self.assertRaises(RuntimeError):
            restore_database(backup, target)
        Path(str(target) + "-wal").write_bytes(b"stale")
        with self.assertRaises(ValueError):
            restore_database(backup, target)

    def test_single_instance_across_processes_and_restart(self):
        code = "from instance import instance_lock; import sys;\nwith instance_lock(sys.argv[1]): print('locked')"
        with instance_lock(db.DB_PATH):
            process = subprocess.run(
                [sys.executable, "-c", code, str(db.DB_PATH)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(process.returncode, 0)
        process = subprocess.run(
            [sys.executable, "-c", code, str(db.DB_PATH)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)

    def test_rate_limit_survives_new_connections_and_expires(self):
        for _ in range(3):
            self.assertFalse(db.rate_limited("hashed-identity", 3, 60, 1000))
        db.init()
        self.assertTrue(db.rate_limited("hashed-identity", 3, 60, 1001))
        self.assertFalse(db.rate_limited("hashed-identity", 3, 60, 1061))

    def test_v1_migration_preserves_draft_and_is_repeatable(self):
        identity = db.create_issue(synthetic())
        with db.connect() as conn:
            conn.execute("DROP TABLE rate_limits")
            conn.execute("PRAGMA user_version=1")
        db.init()
        db.init()
        self.assertEqual(db.get_issue(issue_id=identity)["status"], "draft")
        with db.connect() as conn:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 2)

    def test_newer_schema_is_rejected(self):
        with db.connect() as conn:
            conn.execute("PRAGMA user_version=99")
        with self.assertRaises(RuntimeError):
            db.init()


class TestProductionHTTP(DatabaseTest):
    def setUp(self):
        super().setUp()
        self.env = patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "EMAIL_DELIVERY_ENABLED": "false",
                "ENABLE_LOCAL_GENERATION": "false",
            },
        )
        self.env.start()
        self.origin = patch.object(server, "PUBLIC_URL", "https://pilot.example.org")
        self.origin.start()
        self.https = patch.object(server, "HTTPS", True)
        self.https.start()
        from waitress import create_server

        options = production.waitress_options()
        options.update(host="127.0.0.1", port=0, trusted_proxy="127.0.0.1")
        self.host = create_server(production.application, **options)
        self.thread = threading.Thread(target=self.host.run, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.host.effective_port}"
        self.cookie = ""

    def tearDown(self):
        self.host.close()
        self.host.task_dispatcher.shutdown()
        self.thread.join(timeout=2)
        self.https.stop()
        self.origin.stop()
        self.env.stop()
        super().tearDown()

    def request(self, path, data=None, headers=None, method=None):
        values = {
            "Host": "pilot.example.org",
            "X-Forwarded-Proto": "https",
            "X-Forwarded-For": "192.0.2.10",
            "Content-Type": "application/json",
            "X-Signal-Request": "1",
            "Origin": "https://pilot.example.org",
            "Cookie": self.cookie,
        }
        values.update(headers or {})
        body = json.dumps(data).encode() if data is not None else None
        request = Request(self.base + path, data=body, headers=values, method=method)
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            return response.code, response.read(), response.headers

    def login(self):
        code, _, headers = self.request("/api/login", {"password": server.ADMIN_PASSWORD})
        self.assertEqual(code, 200)
        self.cookie = headers["Set-Cookie"].split(";", 1)[0]
        return headers

    def test_host_https_origin_and_secure_cookie(self):
        self.assertEqual(self.request("/", headers={"Host": "evil.example.org"})[0], 400)
        self.assertEqual(self.request("/", headers={"X-Forwarded-Proto": "http"})[0], 400)
        self.assertEqual(
            self.request("/api/login", {}, {"Origin": "https://evil.example.org"})[0], 403
        )
        headers = self.login()
        for flag in ("Secure", "HttpOnly", "SameSite=Strict"):
            self.assertIn(flag, headers["Set-Cookie"])
        self.assertIn("max-age=", headers["Strict-Transport-Security"])
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_authenticated_import_and_synthetic_publication(self):
        payload = {**synthetic(), "status": "published"}
        self.assertEqual(self.request("/api/admin/import", payload)[0], 401)
        self.login()
        status, body, _ = self.request("/api/admin/import", payload)
        self.assertEqual(status, 200)
        identity = json.loads(body)["issue_id"]
        issue = db.get_issue(issue_id=identity)
        self.assertEqual(issue["status"], "draft")
        self.assertEqual(self.request("/issue/" + issue["slug"])[0], 404)
        self.assertEqual(self.request(f"/api/admin/issue/{identity}/publish", {})[0], 400)
        for action in ("review", "approve", "publish"):
            self.assertEqual(self.request(f"/api/admin/issue/{identity}/{action}", {})[0], 200)
        for path in ("/", "/archive", "/issue/" + issue["slug"], "/sitemap.xml"):
            status, body, _ = self.request(path)
            self.assertEqual(status, 200)
            self.assertIn((issue["slug"] if path == "/sitemap.xml" else "SYNTHETIC").encode(), body)
        self.assertEqual(len(db.history(identity)), 4)

    def test_body_header_method_limits_and_disabled_generation(self):
        self.login()
        # Waitress rejects the declared size before reading the body. Sending the body
        # anyway can race its close and cause Windows to reset urllib's connection.
        connection = HTTPConnection("127.0.0.1", self.host.effective_port, timeout=5)
        try:
            connection.putrequest("POST", "/api/admin/import", skip_host=True)
            connection.putheader("Host", "pilot.example.org")
            connection.putheader("Content-Type", "application/json")
            connection.putheader("Content-Length", "140001")
            connection.endheaders()
            response = connection.getresponse()
            self.assertEqual(response.status, 413)
            response.read()
        finally:
            connection.close()
        # Stop exactly at the parser's rejection boundary. Extra bytes after an
        # early rejection can cause Windows to reset the connection on close.
        prefix = b"GET / HTTP/1.1\r\nHost: pilot.example.org\r\nX-Long: "
        limit = self.host.adj.max_request_header_size
        with socket.create_connection(("127.0.0.1", self.host.effective_port), timeout=5) as sock:
            sock.sendall(prefix + b"x" * (limit - len(prefix)))
            with HTTPResponse(sock) as response:
                response.begin()
                self.assertEqual(response.status, 431)
                response.read()
        self.assertEqual(self.request("/", method="TRACE")[0], 405)
        self.assertEqual(self.request("/", method="HEAD")[1], b"")
        with patch.object(server.llm, "generate") as generate:
            self.assertEqual(self.request("/api/admin/draft", {})[0], 503)
            generate.assert_not_called()

    def test_real_waitress_distrusts_unrecognized_proxy(self):
        self.host.adj.trusted_proxy = "127.0.0.2"
        # Existing middleware captured its proxy options; create a second server explicitly.
        from waitress import create_server

        options = production.waitress_options()
        options.update(host="127.0.0.1", port=0, trusted_proxy="127.0.0.2")
        host = create_server(production.application, **options)
        thread = threading.Thread(target=host.run, daemon=True)
        thread.start()
        old_base = self.base
        self.base = f"http://127.0.0.1:{host.effective_port}"
        try:
            self.assertEqual(self.request("/", headers={"X-Forwarded-Proto": "https"})[0], 400)
        finally:
            self.base = old_base
            host.close()
            host.task_dispatcher.shutdown()
            thread.join(timeout=2)

    def test_login_rate_limit_survives_restart_state_and_uses_proxy_client(self):
        for _ in range(10):
            self.assertEqual(self.request("/api/login", {"password": "wrong"})[0], 401)
        db.init()
        self.assertEqual(self.request("/api/login", {"password": "wrong"})[0], 429)
        self.assertEqual(
            self.request("/api/login", {"password": "wrong"}, {"X-Forwarded-For": "192.0.2.11"})[0],
            401,
        )
        with db.connect() as conn:
            values = list(conn.execute("SELECT identity FROM rate_limits"))
        self.assertTrue(all(len(row[0]) == 64 and "192.0.2" not in row[0] for row in values))

    def test_readiness_checks_database(self):
        self.assertEqual(self.request("/health")[0], 200)
        with patch.object(db, "connect", side_effect=sqlite3.OperationalError("private path")):
            status, body, _ = self.request("/health")
        self.assertEqual(status, 503)
        self.assertNotIn(b"private path", body)

    def test_confirmation_delivery_and_unsubscribe_with_mock_tls_smtp(self):
        smtp = MagicMock()
        self.login()
        with (
            patch.dict(
                os.environ,
                {
                    "EMAIL_DELIVERY_ENABLED": "true",
                    "SMTP_HOST": "smtp.example.org",
                    "MAIL_FROM": "news@example.org",
                },
            ),
            patch.object(smtplib, "SMTP", return_value=smtp),
        ):
            self.assertEqual(
                self.request("/api/subscribe", {"email": "fixture@example.org"})[0], 200
            )
            message = smtp.send_message.call_args.args[0]
            token = (
                message.get_body(preferencelist=("plain",))
                .get_content()
                .strip()
                .split("/confirm/")[1]
            )
            self.assertEqual(self.request("/confirm/" + token, method="HEAD")[0], 200)
            with db.connect() as conn:
                self.assertEqual(
                    conn.execute("SELECT status FROM subscribers").fetchone()[0], "pending"
                )
            self.assertEqual(self.request("/confirm/" + token)[0], 200)
            self.assertEqual(
                self.request("/api/subscribe", {"email": "fixture@example.org"})[0], 200
            )
            self.assertEqual(smtp.send_message.call_count, 1)
            _, body, _ = self.request("/api/admin/import", synthetic())
            identity = json.loads(body)["issue_id"]
            for action in ("review", "approve", "publish", "send"):
                self.assertEqual(self.request(f"/api/admin/issue/{identity}/{action}", {})[0], 200)
            self.assertEqual(smtp.send_message.call_count, 2)
            with db.connect() as conn:
                unsubscribe = conn.execute("SELECT unsubscribe_token FROM subscribers").fetchone()[
                    0
                ]
            self.assertEqual(self.request("/unsubscribe/" + unsubscribe)[0], 200)
            with db.connect() as conn:
                self.assertEqual(
                    conn.execute("SELECT status FROM subscribers").fetchone()[0], "active"
                )
            self.assertEqual(self.request("/unsubscribe/" + unsubscribe, {})[0], 200)
            with db.connect() as conn:
                self.assertEqual(
                    conn.execute("SELECT status FROM subscribers").fetchone()[0], "unsubscribed"
                )
            self.assertEqual(self.request(f"/api/admin/issue/{identity}/send", {})[0], 200)
            self.assertEqual(smtp.send_message.call_count, 2)


class TestProductionMail(unittest.TestCase):
    def test_production_defaults_to_no_outgoing_email(self):
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "SMTP_HOST": "smtp.example.org",
                "MAIL_FROM": "news@example.org",
            },
            clear=True,
        ):
            self.assertFalse(mailer.configured())
            with patch.object(smtplib, "SMTP") as smtp:
                with self.assertRaises(RuntimeError):
                    mailer.send("reader@example.org", "Test", "Test")
                smtp.assert_not_called()

    def test_invalid_smtp_settings_fail_before_connection(self):
        base = {
            "SMTP_HOST": "smtp.example.org",
            "MAIL_FROM": "news@example.org",
            "EMAIL_DELIVERY_ENABLED": "true",
        }
        for invalid in (
            {"SMTP_PORT": "25"},
            {"SMTP_SSL": "true"},
            {"SMTP_USER": "user"},
            {"MAIL_FROM": "bad\r\nBcc:x@example.org"},
            {"SMTP_HOST": "https://smtp.example.org"},
            {"EMAIL_DELIVERY_ENABLED": "maybe"},
        ):
            with (
                self.subTest(invalid=invalid),
                patch.dict(os.environ, {**base, **invalid}, clear=True),
            ):
                with self.assertRaises(ValueError):
                    mailer.validate_config()

    def test_tls_and_implicit_tls_with_one_click_headers(self):
        for port in ("587", "465"):
            smtp = MagicMock()
            smtp.__enter__.return_value = smtp
            with (
                patch.dict(
                    os.environ,
                    {
                        "SMTP_HOST": "smtp.example.org",
                        "MAIL_FROM": "Signal Daily <news@example.org>",
                        "SMTP_PORT": port,
                        "SMTP_USER": "user",
                        "SMTP_PASSWORD": "test-only",
                        "EMAIL_DELIVERY_ENABLED": "true",
                    },
                    clear=True,
                ),
                patch.object(smtplib, "SMTP", return_value=smtp) as starttls,
                patch.object(smtplib, "SMTP_SSL", return_value=smtp) as implicit,
            ):
                mailer.send(
                    "reader@example.org",
                    "Test",
                    "Plain",
                    "<p>HTML</p>",
                    "https://example.org/unsubscribe/test",
                )
            smtp.login.assert_called_once_with("user", "test-only")
            if port == "587":
                starttls.assert_called_once()
                smtp.starttls.assert_called_once()
            else:
                implicit.assert_called_once()
                smtp.starttls.assert_not_called()
            self.assertEqual(
                smtp.send_message.call_args.args[0]["List-Unsubscribe-Post"],
                "List-Unsubscribe=One-Click",
            )

    def test_unsafe_proxy_and_development_server_rejected(self):
        with patch.dict(os.environ, {"TRUSTED_PROXY": "*"}):
            with self.assertRaises(ValueError):
                production.waitress_options()
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            with self.assertRaises(RuntimeError):
                server.main()

    def test_smoke_tool_refuses_a_real_host(self):
        from tools.pilot_smoke import main

        with (
            patch.dict(os.environ, {"PUBLIC_URL": "https://real.example.com"}),
            patch.object(sys, "argv", ["pilot_smoke.py"]),
        ):
            with self.assertRaisesRegex(SystemExit, "Refusing"):
                main()

    def test_quit_failure_does_not_retry_accepted_message(self):
        smtp = MagicMock()
        smtp.quit.side_effect = smtplib.SMTPServerDisconnected("after accepted DATA")
        with (
            patch.dict(
                os.environ,
                {
                    "SMTP_HOST": "smtp.example.org",
                    "MAIL_FROM": "news@example.org",
                    "EMAIL_DELIVERY_ENABLED": "true",
                },
                clear=True,
            ),
            patch.object(smtplib, "SMTP", return_value=smtp),
        ):
            mailer.send("fixture@example.org", "Synthetic", "Test")
        smtp.send_message.assert_called_once()
        smtp.close.assert_called_once()

    def test_data_disconnect_remains_uncertain_even_if_quit_fails(self):
        smtp = MagicMock()
        smtp.send_message.side_effect = smtplib.SMTPServerDisconnected("during DATA")
        smtp.quit.side_effect = smtplib.SMTPServerDisconnected("during QUIT")
        with (
            patch.dict(
                os.environ,
                {
                    "SMTP_HOST": "smtp.example.org",
                    "MAIL_FROM": "news@example.org",
                    "EMAIL_DELIVERY_ENABLED": "true",
                },
                clear=True,
            ),
            patch.object(smtplib, "SMTP", return_value=smtp),
            self.assertRaises(mailer.DeliveryUncertain),
        ):
            mailer.send("fixture@example.org", "Synthetic", "Test")


if __name__ == "__main__":
    unittest.main()
