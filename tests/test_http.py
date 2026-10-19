import http.cookiejar
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db
import mailer
import server
import feeds
import llm
from http.server import ThreadingHTTPServer


class TestHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(cls.tmp.name) / "db.sqlite3"
        db.init()
        cls.host = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.base = f"http://127.0.0.1:{cls.host.server_port}"
        cls.thread = threading.Thread(target=cls.host.serve_forever, daemon=True)
        cls.thread.start()
        cls.client = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))

    @classmethod
    def tearDownClass(cls):
        cls.host.shutdown()
        cls.host.server_close()
        cls.thread.join(timeout=2)
        cls.tmp.cleanup()

    def setUp(self):
        with db.connect() as conn:
            for table in (
                "deliveries",
                "issue_events",
                "operations",
                "subscribers",
                "issues",
                "stories",
            ):
                conn.execute("DELETE FROM " + table)
        self.__class__.client = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        server.REQUEST_COUNTS.clear()

    def login(self):
        self.assertEqual(self.call("/api/login", {"password": server.ADMIN_PASSWORD})[0], 200)

    @classmethod
    def call(cls, path, data=None):
        headers = {"X-Signal-Request": "1", "Content-Type": "application/json"}
        req = Request(
            cls.base + path,
            method="POST" if data is not None else "GET",
            data=json.dumps(data).encode() if data is not None else None,
            headers=headers,
        )
        try:
            response = cls.client.open(req, timeout=5)
            return response.status, response.read(), dict(response.headers)
        except HTTPError as exc:
            return exc.code, exc.read(), dict(exc.headers)

    def test_stale_editor_approval_and_publication_versions_are_rejected(self):
        self.login()
        payload = json.loads(
            (
                Path(__file__).resolve().parents[1] / "docs/examples/synthetic-newsletter.json"
            ).read_text(encoding="utf-8")
        )
        status, body, _ = self.call("/api/admin/import", payload)
        self.assertEqual(status, 200)
        identity = json.loads(body)["issue_id"]
        prefix = f"/api/admin/issue/{identity}"
        self.assertEqual(self.call(prefix + "/review", {})[0], 200)
        stale_review = db.get_issue(issue_id=identity)["version"]
        self.assertEqual(self.call(prefix + "/save", payload)[0], 200)
        self.assertEqual(self.call(prefix + "/review", {})[0], 200)
        self.assertEqual(self.call(prefix + "/approve", {"version": stale_review})[0], 400)
        self.assertEqual(db.get_issue(issue_id=identity)["status"], "review")
        version = db.get_issue(issue_id=identity)["version"]
        self.assertEqual(self.call(prefix + "/approve", {"version": version})[0], 200)
        stale_approval = db.get_issue(issue_id=identity)["version"]
        self.assertEqual(self.call(prefix + "/save", payload)[0], 200)
        self.assertEqual(self.call(prefix + "/review", {})[0], 200)
        self.assertEqual(self.call(prefix + "/approve", {})[0], 200)
        with patch.object(mailer, "email_issue") as dispatch:
            self.assertEqual(self.call(prefix + "/publish", {"version": stale_approval})[0], 400)
            dispatch.assert_not_called()
        self.assertEqual(db.get_issue(issue_id=identity)["status"], "approved")
        version = db.get_issue(issue_id=identity)["version"]
        self.assertEqual(self.call(prefix + "/publish", {"version": version})[0], 200)

    def test_complete_editor_and_subscriber_flow(self):
        status, body, _ = self.call("/")
        self.assertEqual(status, 200)
        self.assertIn(b"SIGNAL", body)
        status, body, _ = self.call("/api/admin/data")
        self.assertEqual(status, 401)
        status, body, _ = self.call("/api/login", {"password": server.ADMIN_PASSWORD})
        self.assertEqual(status, 200)
        with (
            patch.object(mailer, "configured", return_value=True),
            patch.object(mailer, "send") as sendmail,
        ):
            status, body, _ = self.call("/api/subscribe", {"email": "reader@example.org"})
            self.assertEqual(status, 200)
            confirm_url = sendmail.call_args.args[2].split("opening: ")[1]
            # PUBLIC_URL defaults to 8787; replace host with test server
            token = confirm_url.split("/confirm/")[1]
            status, body, _ = self.call("/confirm/" + token)
            self.assertEqual(status, 200)
            self.assertIn(b"on the list", body)
            with db.connect() as conn:
                self.assertEqual(
                    conn.execute(
                        "SELECT status FROM subscribers WHERE email='reader@example.org'"
                    ).fetchone()["status"],
                    "active",
                )
        item = {
            "headline": "Test headline",
            "summary": "Reported result.",
            "why": "Readers can learn.",
            "source": "Source",
            "url": "https://example.org/primary",
        }
        payload = {
            "title": "Integration edition",
            "subject": "Integration email",
            "intro": "Hello readers",
            "closing": "Read the sources",
            "items": [item],
        }
        status, body, _ = self.call("/api/admin/import", payload)
        self.assertEqual(status, 200)
        issue_id = json.loads(body)["issue_id"]
        status, body, _ = self.call(f"/api/admin/issue/{issue_id}/publish", {})
        self.assertEqual(status, 400)
        status, body, _ = self.call(f"/api/admin/issue/{issue_id}/approve", {})
        self.assertEqual(status, 400)
        status, body, _ = self.call(f"/api/admin/issue/{issue_id}/review", {})
        self.assertEqual(status, 200)
        status, body, _ = self.call(f"/api/admin/issue/{issue_id}/approve", {})
        self.assertEqual(status, 200)
        with (
            patch.object(mailer, "configured", return_value=True),
            patch.object(mailer, "email_issue") as dispatch,
        ):
            status, body, _ = self.call(f"/api/admin/issue/{issue_id}/publish", {})
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body)["sent"], 1)
            status, body, _ = self.call(f"/api/admin/issue/{issue_id}/send", {})
            self.assertEqual(json.loads(body)["sent"], 0)
            self.assertEqual(dispatch.call_count, 1)
        issue = db.get_issue(issue_id=issue_id)
        status, body, _ = self.call("/issue/" + issue["slug"])
        self.assertEqual(status, 200)
        self.assertIn(b"Test headline", body)
        status, body, _ = self.call("/archive")
        self.assertEqual(status, 200)
        self.assertIn(b"Integration edition", body)
        with db.connect() as conn:
            unsub = conn.execute(
                "SELECT unsubscribe_token FROM subscribers WHERE email='reader@example.org'"
            ).fetchone()["unsubscribe_token"]
        status, _, _ = self.call("/unsubscribe/" + unsub)
        self.assertEqual(status, 200)
        # unsubscribe confirmation requires POST (email security scanners won't trigger GET)
        req = Request(self.base + "/unsubscribe/" + unsub, data=b"", method="POST")
        self.client.open(req, timeout=5).close()
        with db.connect() as conn:
            self.assertEqual(
                conn.execute(
                    "SELECT status FROM subscribers WHERE email='reader@example.org'"
                ).fetchone()["status"],
                "unsubscribed",
            )
        future = db.create_issue(payload)
        db.review(future)
        db.approve(future)
        db.publish(future)
        with patch.object(mailer, "email_issue") as sender:
            handler = object.__new__(server.Handler)
            self.assertEqual(handler.deliver(future)["sent"], 0)
            sender.assert_not_called()

    def test_unauthorized_mutations_are_blocked(self):
        for path in (
            "/api/admin/ingest",
            "/api/admin/draft",
            "/api/admin/import",
            "/api/admin/issue/1/approve",
            "/api/admin/issue/1/publish",
            "/api/admin/issue/1/send",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.call(path, {})[0], 401)

    def test_csrf_and_bad_json_objects(self):
        for headers, raw in (
            ({}, b"{}"),
            (
                {
                    "X-Signal-Request": "1",
                    "Origin": "https://evil.example",
                    "Content-Type": "application/json",
                },
                b"{}",
            ),
            ({"X-Signal-Request": "1", "Content-Type": "application/json"}, b"[]"),
        ):
            req = Request(self.base + "/api/login", data=raw, headers=headers, method="POST")
            with self.assertRaises(HTTPError) as caught:
                self.client.open(req, timeout=5)
            self.assertIn(caught.exception.code, (400, 403))

    def test_login_rate_limit(self):
        for _ in range(10):
            self.assertEqual(self.call("/api/login", {"password": "wrong"})[0], 401)
        self.assertEqual(self.call("/api/login", {"password": "wrong"})[0], 429)

    def test_logout_invalidates_replayed_cookie(self):
        self.login()
        token = "sd_session=" + server.mk_session()
        self.assertEqual(self.call("/api/logout", {})[0], 200)
        req = Request(self.base + "/api/admin/data", headers={"Cookie": token})
        with self.assertRaises(HTTPError) as caught:
            self.client.open(req, timeout=5)
        self.assertEqual(caught.exception.code, 401)

    def test_confirmation_expiry_and_single_use(self):
        import hashlib
        import time

        token = "expired-token"
        hashed = hashlib.sha256(token.encode()).hexdigest()
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO subscribers(email,status,verify_hash,verify_expires,unsubscribe_token,created_at) VALUES(?,?,?,?,?,?)",
                (
                    "test@example.org",
                    "pending",
                    hashed,
                    int(time.time()) - 1,
                    "test-unsubscribe-token-123456",
                    db.now(),
                ),
            )
        self.assertIn(b"Link expired", self.call("/confirm/" + token)[1])
        with db.connect() as conn:
            conn.execute("UPDATE subscribers SET verify_expires=?", (int(time.time()) + 900,))
        self.assertIn(b"on the list", self.call("/confirm/" + token)[1])
        self.assertIn(b"Link expired", self.call("/confirm/" + token)[1])

    def test_subscription_duplicates_and_privacy(self):
        with (
            patch.object(mailer, "configured", return_value=True),
            patch.object(mailer, "send") as send,
        ):
            first = self.call("/api/subscribe", {"email": "reader@example.org"})
            with db.connect() as conn:
                conn.execute("UPDATE subscribers SET status='active'")
            second = self.call("/api/subscribe", {"email": "reader@example.org"})
            self.assertEqual(first[1], second[1])
            self.assertEqual(send.call_count, 1)
            with db.connect() as conn:
                self.assertEqual(conn.execute("SELECT count(*) FROM subscribers").fetchone()[0], 1)
        status, body, _ = self.call("/api/admin/status")
        self.assertNotIn(b"mailer", body)
        self.assertNotIn(b'model"', body)

    def test_unsubscribe_token_survives_pending_resubscribe(self):
        with patch.object(mailer, "configured", return_value=True), patch.object(mailer, "send"):
            self.call("/api/subscribe", {"email": "reader@example.org"})
            with db.connect() as conn:
                token = conn.execute("SELECT unsubscribe_token FROM subscribers").fetchone()[0]
                conn.execute("UPDATE subscribers SET status='unsubscribed'")
            self.call("/api/subscribe", {"email": "reader@example.org"})
            with db.connect() as conn:
                self.assertEqual(
                    conn.execute("SELECT unsubscribe_token FROM subscribers").fetchone()[0], token
                )

    def test_missing_smtp_and_email_validation(self):
        with patch.object(mailer, "configured", return_value=False):
            self.assertEqual(self.call("/api/subscribe", {"email": "reader@example.org"})[0], 503)
        with patch.object(mailer, "configured", return_value=True):
            self.assertEqual(self.call("/api/subscribe", {"email": "bad"})[0], 400)

    def test_public_routes_search_metadata_and_private_issue(self):
        from test_release import edition

        identity = db.create_issue(edition())
        draft = db.get_issue(issue_id=identity)
        self.assertEqual(self.call("/issue/" + draft["slug"])[0], 404)
        db.review(identity)
        db.approve(identity)
        db.publish(identity)
        for path in (
            "/",
            "/archive",
            "/issue/" + draft["slug"],
            "/sitemap.xml",
            "/robots.txt",
            "/static/app.js",
            "/static/style.css",
            "/health",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.call(path)[0], 200)
        self.assertIn(b"AI research briefing", self.call("/archive?q=research&topic=Research")[1])
        self.assertNotIn(b"AI research briefing", self.call("/archive?q=not-found")[1])
        self.assertEqual(self.call("/static/../server.py")[0], 404)

    def test_ingest_generate_review_publish_with_service_doubles(self):
        from test_release import stories, model_reply

        self.login()
        with patch.object(feeds, "fetch_all", return_value=(stories(), [])):
            self.assertEqual(json.loads(self.call("/api/admin/ingest", {})[1])["added"], 1)
        collected = db.get_stories()[0]
        reply = json.loads(model_reply().getvalue())
        content = json.loads(reply["message"]["content"])
        content["items"][0]["story_id"] = collected["id"]
        from test_release import Response

        with patch.object(
            llm,
            "urlopen",
            return_value=Response(
                json.dumps({"message": {"content": json.dumps(content)}}).encode()
            ),
        ):
            status, body, _ = self.call("/api/admin/draft", {})
        self.assertEqual(status, 200)
        identity = json.loads(body)["issue_id"]
        self.assertEqual(self.call(f"/api/admin/issue/{identity}/publish", {})[0], 400)
        for action in ("review", "approve", "publish"):
            with patch.object(mailer, "configured", return_value=False):
                self.assertEqual(self.call(f"/api/admin/issue/{identity}/{action}", {})[0], 200)
        self.assertIn(
            b"AI paper released", self.call("/issue/" + db.get_issue(issue_id=identity)["slug"])[1]
        )
        self.assertEqual(len(db.history(identity)), 4)


if __name__ == "__main__":
    unittest.main()
