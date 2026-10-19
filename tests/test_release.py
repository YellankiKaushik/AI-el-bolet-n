"""Regression and release checks using isolated SQLite and external-service doubles."""

import concurrent.futures
from contextlib import closing
import io
import json
import os
import smtplib
import sqlite3
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock
from urllib.error import URLError
import db
import feeds
import llm
import mailer
import server
from validation import verify_issue, email_address, valid_url


def edition():
    return {
        "title": "AI research briefing",
        "subject": "Research today",
        "intro": "A sourced introduction.",
        "closing": "Check the original research.",
        "topic": "Research",
        "items": [
            {
                "headline": "AI paper released",
                "summary": "Researchers shared an AI paper.",
                "why": "Builders can inspect the method.",
                "url": "https://example.org/paper",
                "source": "Example Research",
            }
        ],
    }


def stories():
    return [
        {
            "id": 7,
            "title": "An AI paper",
            "description": "Researchers shared an AI paper.",
            "source": "Example Research",
            "url": "https://example.org/paper",
            "published_at": db.now(),
        }
    ]


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def model_reply(**changes):
    data = {
        "title": "AI research briefing",
        "subject": "Research today",
        "intro": "A sourced introduction.",
        "closing": "Check the original research.",
        "items": [
            {
                "story_id": 7,
                "headline": "AI paper released",
                "summary": "Researchers shared an AI paper.",
                "why": "Builders can inspect the method.",
            }
        ],
    }
    data.update(changes)
    return Response(json.dumps({"message": {"content": json.dumps(data)}}).encode())


class DatabaseCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.previous = db.DB_PATH
        db.DB_PATH = Path(self.tmp.name) / "test.sqlite3"
        db.init()

    def tearDown(self):
        db.DB_PATH = self.previous
        self.tmp.cleanup()

    def published(self):
        identity = db.create_issue(edition())
        db.review(identity)
        db.approve(identity)
        db.publish(identity)
        return identity

    def subscriber(self, status="active"):
        with db.connect() as conn:
            return conn.execute(
                "INSERT INTO subscribers(email,status,unsubscribe_token,created_at) VALUES(?,?,?,?)",
                ("reader@example.org", status, "test-unsubscribe-token-123456", db.now()),
            ).lastrowid


class TestPersistenceWorkflow(DatabaseCase):
    def test_review_is_mandatory(self):
        identity = db.create_issue(edition())
        with self.assertRaises(ValueError):
            db.approve(identity)
        with self.assertRaises(ValueError):
            db.publish(identity)
        db.review(identity)
        with self.assertRaises(ValueError):
            db.publish(identity)
        db.approve(identity)
        db.publish(identity)
        self.assertEqual(db.get_issue(issue_id=identity)["status"], "published")

    def test_blank_draft_cannot_enter_review(self):
        identity = db.create_issue({"title": "Blank", "subject": "Blank"})
        with self.assertRaises(ValueError):
            db.review(identity)

    def test_revision_and_edit_reset_approval(self):
        identity = db.create_issue(edition())
        db.review(identity)
        db.approve(identity)
        db.revise(identity)
        self.assertEqual(db.get_issue(issue_id=identity)["status"], "draft")
        db.review(identity)
        db.approve(identity)
        db.update_issue(identity, edition())
        self.assertEqual(db.get_issue(issue_id=identity)["status"], "draft")

    def test_stale_save_is_rejected(self):
        identity = db.create_issue(edition())
        saved = db.get_issue(issue_id=identity)
        db.update_issue(identity, saved)
        with self.assertRaisesRegex(ValueError, "changed"):
            db.update_issue(identity, saved)

    def test_history_records_transitions_and_snapshots(self):
        identity = self.published()
        self.assertEqual(
            [e["action"] for e in db.history(identity)],
            ["published", "approved", "review", "created"],
        )
        with db.connect() as conn:
            snap = json.loads(
                conn.execute("SELECT snapshot_json FROM issue_events ORDER BY id DESC").fetchone()[
                    0
                ]
            )
        self.assertEqual(snap["status"], "published")

    def test_persistence_and_idempotent_init(self):
        identity = self.published()
        db.init()
        db.init()
        self.assertEqual(db.get_issue(issue_id=identity)["topic"], "Research")
        with db.connect() as conn:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 2)
            self.assertIsNone(conn.execute("PRAGMA foreign_key_check").fetchone())

    def test_search_topic_and_private_drafts(self):
        self.published()
        db.create_issue({"title": "Secret draft", "subject": "Private"})
        self.assertEqual(len(db.get_issues(True, search="research", topic="Research")), 1)
        self.assertEqual(db.get_issues(True, search="Secret"), [])
        self.assertEqual(db.get_issues(True, search="' OR 1=1 --"), [])

    def test_url_deduplication_preserves_metadata(self):
        source = stories()[0]
        self.assertEqual(
            db.insert_stories([source, {**source, "url": source["url"] + "?utm_source=email#top"}]),
            1,
        )
        stored = db.get_stories()[0]
        self.assertEqual(stored["source"], source["source"])
        self.assertEqual(stored["published_at"], source["published_at"])
        self.assertEqual(stored["description"], source["description"])

    def test_delivery_reservation_is_atomic(self):
        identity = self.published()
        subscriber = self.subscriber()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            claims = list(pool.map(lambda _: db.claim_delivery(identity, subscriber), range(8)))
        self.assertEqual(sum(claims), 1)

    def test_failed_delivery_can_retry_sent_cannot(self):
        identity = self.published()
        subscriber = self.subscriber()
        self.assertTrue(db.claim_delivery(identity, subscriber))
        db.record_delivery(identity, subscriber, "failed", "SMTP refusal")
        self.assertTrue(db.claim_delivery(identity, subscriber))
        db.record_delivery(identity, subscriber, "sent")
        self.assertFalse(db.claim_delivery(identity, subscriber))
        self.assertEqual(db.delivery_targets(identity), [])

    def test_uncertain_and_interrupted_are_not_retried(self):
        identity = self.published()
        subscriber = self.subscriber()
        db.claim_delivery(identity, subscriber)
        self.assertEqual(db.delivery_targets(identity), [])
        db.record_delivery(identity, subscriber, "uncertain")
        self.assertFalse(db.claim_delivery(identity, subscriber))

    def test_consent_and_publication_checked_at_reservation(self):
        identity = db.create_issue(edition())
        subscriber = self.subscriber("pending")
        with self.assertRaises(ValueError):
            db.claim_delivery(identity, subscriber)
        db.review(identity)
        db.approve(identity)
        db.publish(identity)
        self.assertFalse(db.claim_delivery(identity, subscriber))
        with db.connect() as conn:
            conn.execute("UPDATE subscribers SET status='unsubscribed'")
        self.assertEqual(db.delivery_targets(identity), [])

    def test_safe_retry_delivery_and_uncertain_delivery(self):
        identity = self.published()
        self.subscriber()
        handler = object.__new__(server.Handler)
        with patch.object(mailer, "email_issue", side_effect=smtplib.SMTPRecipientsRefused({})):
            self.assertEqual(handler.deliver(identity)["failed"], 1)
        with patch.object(mailer, "email_issue") as sender:
            self.assertEqual(handler.deliver(identity)["sent"], 1)
            self.assertEqual(handler.deliver(identity)["sent"], 0)
            self.assertEqual(sender.call_count, 1)

    def test_old_schema_migration_preserves_rows(self):
        # Reproduce the original pre-migration schema independently.
        legacy = Path(self.tmp.name) / "legacy.db"
        db.DB_PATH = legacy
        with closing(sqlite3.connect(legacy)) as conn:
            conn.executescript("""CREATE TABLE issues(id INTEGER PRIMARY KEY,slug TEXT UNIQUE,title TEXT,subject TEXT,intro TEXT,closing TEXT,items_json TEXT,status TEXT CHECK(status IN ('draft','approved','published')),created_at TEXT,updated_at TEXT,published_at TEXT);
            CREATE TABLE subscribers(id INTEGER PRIMARY KEY,email TEXT UNIQUE,status TEXT,verify_hash TEXT,unsubscribe_token TEXT,created_at TEXT,confirmed_at TEXT);
            CREATE TABLE deliveries(id INTEGER PRIMARY KEY,issue_id INTEGER REFERENCES issues(id),subscriber_id INTEGER REFERENCES subscribers(id),status TEXT CHECK(status IN ('sent','failed')),error TEXT,created_at TEXT,UNIQUE(issue_id,subscriber_id));
            INSERT INTO issues VALUES(1,'legacy','Legacy','Subject','Intro','Bye','[]','draft','2026','2026',NULL);
            INSERT INTO subscribers VALUES(1,'reader@example.org','active',NULL,'token','2026','2026');
            INSERT INTO deliveries VALUES(1,1,1,'sent','','2026');""")
            conn.commit()
        db.init()
        self.assertEqual(db.get_issue(issue_id=1)["title"], "Legacy")
        with db.connect() as conn:
            self.assertEqual(conn.execute("SELECT status FROM deliveries").fetchone()[0], "sent")


class TestGeneration(unittest.TestCase):
    def test_actual_payload_and_provenance(self):
        with patch.object(llm, "urlopen", return_value=model_reply()) as request:
            result = llm.generate(stories())
        body = json.loads(request.call_args.args[0].data)
        self.assertEqual(body["model"], llm.OLLAMA_MODEL)
        self.assertFalse(body["stream"])
        self.assertEqual(result["items"][0]["url"], stories()[0]["url"])
        self.assertEqual(result["items"][0]["source_description"], stories()[0]["description"])

    def test_unknown_duplicate_and_noninteger_ids_rejected(self):
        for ids in ([8], [7, 7], ["7"], [True]):
            with self.subTest(ids=ids):
                items = [
                    {"story_id": x, "headline": "AI", "summary": "A paper", "why": "Read it"}
                    for x in ids
                ]
                with patch.object(llm, "urlopen", return_value=model_reply(items=items)):
                    with self.assertRaises(ValueError):
                        llm.generate(stories())

    def test_missing_subject_or_summary_rejected(self):
        for change in ({"subject": ""}, {"intro": ""}, {"items": []}, {"items": [{"story_id": 7}]}):
            with (
                self.subTest(change=change),
                patch.object(llm, "urlopen", return_value=model_reply(**change)),
            ):
                with self.assertRaises(ValueError):
                    llm.generate(stories())

    def test_detectable_unsupported_numeric_claim_rejected(self):
        items = [
            {
                "story_id": 7,
                "headline": "AI paper",
                "summary": "Achieved 99 percent accuracy.",
                "why": "Read it",
            }
        ]
        with patch.object(llm, "urlopen", return_value=model_reply(items=items)):
            with self.assertRaisesRegex(ValueError, "numbers"):
                llm.generate(stories())

    def test_network_timeout_malformed_and_size_failures(self):
        for error in (URLError("offline"), TimeoutError("timeout")):
            with patch.object(llm, "urlopen", side_effect=error):
                with self.assertRaisesRegex(RuntimeError, "no cloud fallback"):
                    llm.generate(stories())
        for payload in (b"not json", b"{}", b"x" * 1_000_001):
            with patch.object(llm, "urlopen", return_value=Response(payload)):
                with self.assertRaises(ValueError):
                    llm.generate(stories())

    def test_empty_inputs_and_concurrency_bound(self):
        with self.assertRaises(ValueError):
            llm.generate([])
        with llm.GENERATION_LOCK:
            with self.assertRaises(RuntimeError):
                llm.generate(stories())


class TestAdditionalGeneration(unittest.TestCase):
    def test_inline_model_citations_rejected(self):
        with patch.object(
            llm, "urlopen", return_value=model_reply(intro="Read https://invented.example/fake")
        ):
            with self.assertRaisesRegex(ValueError, "citations"):
                llm.generate(stories())


class TestDeliveryLedgerFailure(DatabaseCase):
    def test_successful_send_with_failed_ledger_write_is_not_retryable(self):
        identity = self.published()
        subscriber = self.subscriber()
        handler = object.__new__(server.Handler)
        with (
            patch.object(mailer, "email_issue"),
            patch.object(
                db, "record_delivery", side_effect=sqlite3.OperationalError("disk unavailable")
            ),
        ):
            with self.assertRaises(sqlite3.OperationalError):
                handler.deliver(identity)
        self.assertFalse(db.claim_delivery(identity, subscriber))
        self.assertEqual(db.delivery_targets(identity), [])


class TestFeeds(unittest.TestCase):
    def test_atom_prefers_article_over_self_link(self):
        raw = b'<feed><entry><title>AI research</title><link rel="self" href="https://example.org/api"/><link rel="alternate" href="https://example.org/paper"/><updated>2026-10-19T00:00:00Z</updated></entry></feed>'
        self.assertEqual(feeds.parse_feed(raw, "Research")[0]["url"], "https://example.org/paper")

    def test_entity_and_malformed_feed_rejected(self):
        for raw in (b"<!DOCTYPE rss><rss/>", b'<!ENTITY a "b"><rss/>', b"<bad", b"x" * 1_500_001):
            with self.subTest(raw=raw[:20]), self.assertRaises(Exception):
                feeds.parse_feed(raw, "Example")

    def test_recency_and_relevance(self):
        recent = stories()[0]
        self.assertTrue(feeds.relevant_recent(recent))
        self.assertFalse(
            feeds.relevant_recent(
                {
                    **recent,
                    "published_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                }
            )
        )
        self.assertFalse(feeds.relevant_recent({**recent, "published_at": "invalid"}))
        self.assertFalse(
            feeds.relevant_recent(
                {**recent, "title": "Football results", "description": "A match report"}
            )
        )

    def test_private_endpoints_rejected(self):
        for url in ("http://example.org/rss", "https://127.0.0.1/rss", "https://localhost/rss"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                feeds.public_endpoint(url)

    def test_retry_limit_and_partial_failure(self):
        raw = b"<rss><channel><item><title>New AI model</title><link>https://example.org/paper</link></item></channel></rss>"
        opener = MagicMock()
        opener.open.side_effect = [URLError("temporary"), Response(raw)]
        with (
            patch.object(feeds, "sources", return_value={"Example": "https://example.org/feed"}),
            patch.object(feeds, "public_endpoint"),
            patch.object(feeds, "build_opener", return_value=opener),
            patch.object(feeds.time, "sleep"),
        ):
            result, errors = feeds.fetch_all()
        self.assertEqual(len(result), 1)
        self.assertEqual(errors, [])
        self.assertEqual(opener.open.call_count, 2)

    def test_collection_limits(self):
        raw = (
            "<rss><channel>"
            + "".join(
                f"<item><title>AI model {i}</title><link>https://example.org/{i}</link></item>"
                for i in range(8)
            )
            + "</channel></rss>"
        ).encode()
        opener = MagicMock()
        opener.open.return_value = Response(raw)
        with (
            patch.dict(os.environ, {"RSS_LIMIT": "2"}),
            patch.object(feeds, "sources", return_value={"E": "https://example.org/f"}),
            patch.object(feeds, "public_endpoint"),
            patch.object(feeds, "build_opener", return_value=opener),
        ):
            result, errors = feeds.fetch_all()
        self.assertEqual(len(result), 2)


class TestSecurityAndMail(unittest.TestCase):
    def test_email_validation(self):
        self.assertEqual(email_address(" READER@Example.org "), "reader@example.org")
        for bad in (
            "a@b",
            "a..b@example.org",
            ".a@example.org",
            "x@-example.org",
            "x\r\nBcc:z@example.org",
            None,
        ):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                email_address(bad)

    def test_bad_urls_and_duplicate_sources_rejected(self):
        for url in (
            "javascript:alert(1)",
            "https://a:b@example.org/",
            "https://example.org\\evil",
            "https://example.org:bad",
            "https://exa mple.org",
        ):
            self.assertFalse(valid_url(url))
        draft = edition()
        draft["items"] *= 2
        with self.assertRaises(ValueError):
            verify_issue(draft)

    def test_session_tampering_expiry_and_logout_epoch(self):
        token = server.mk_session()
        self.assertTrue(server.session_ok("sd_session=" + token))
        self.assertFalse(server.session_ok("sd_session=" + token + "x"))
        with patch.object(server, "SESSION_EPOCH", server.SESSION_EPOCH + 1):
            self.assertFalse(server.session_ok("sd_session=" + token))
        with patch.object(server.time, "time", return_value=time.time() + 90000):
            self.assertFalse(server.session_ok("sd_session=" + token))

    def test_missing_and_placeholder_production_config(self):
        with patch.dict(
            os.environ, {"APP_ENV": "production", "ADMIN_PASSWORD": "", "SESSION_SECRET": ""}
        ):
            with self.assertRaises(ValueError):
                server.validate_config()
        with patch.dict(
            os.environ, {"APP_ENV": "development", "ADMIN_PASSWORD": "replace-with-a-password"}
        ):
            with self.assertRaises(ValueError):
                server.validate_config()

    def test_mail_multipart_and_header_sanitization(self):
        smtp = MagicMock()
        smtp.__enter__.return_value = smtp
        with (
            patch.dict(
                os.environ,
                {
                    "SMTP_HOST": "smtp.example.org",
                    "MAIL_FROM": "news@example.org",
                    "SMTP_PORT": "587",
                },
            ),
            patch.object(mailer.smtplib, "SMTP", return_value=smtp),
        ):
            mailer.send(
                "reader@example.org",
                "Subject\r\nBcc: bad",
                "Plain",
                "<p>HTML</p>",
                "https://example.org/unsubscribe/token",
            )
        message = smtp.send_message.call_args.args[0]
        self.assertEqual(message.get_content_type(), "multipart/alternative")
        self.assertIn("List-Unsubscribe", message)
        self.assertNotIn("\n", message["Subject"])
        smtp.starttls.assert_called_once()

    def test_missing_smtp_and_unpublished_issue_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                mailer.send("reader@example.org", "Hi", "Text")
        with self.assertRaises(ValueError):
            mailer.email_issue(edition(), {}, "https://example.org")

    def test_smtp_disconnect_is_uncertain(self):
        smtp = MagicMock()
        smtp.send_message.side_effect = smtplib.SMTPServerDisconnected("disconnect")
        with self.assertRaises(mailer.DeliveryUncertain):
            mailer.transmit(smtp, MagicMock())

    def test_html_escape_public_output(self):
        with patch.object(db, "get_issues", return_value=[]):
            page = server.simple_page("Title", "<script>alert(1)</script>", "<img src=x>")
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_token_paths_are_redacted_in_logs(self):
        handler = object.__new__(server.Handler)
        handler.client_address = ("127.0.0.1", 12)
        with patch("builtins.print") as printer:
            handler.log_message("GET %s", "/confirm/secret-token")
        self.assertNotIn("secret-token", printer.call_args.args[0])


class TestConfiguration(unittest.TestCase):
    def test_setup_creates_private_config_without_overwriting(self):
        from tools.setup_local import create_config

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath(".env.example").write_text(
                "ADMIN_PASSWORD=replace-with-a-strong-unique-password\nSESSION_SECRET=replace-with-a-long-random-secret\n"
            )
            create_config(root)
            original = root.joinpath(".env").read_text()
            self.assertNotIn("replace-with", original)
            with self.assertRaises(FileExistsError):
                create_config(root)
            self.assertEqual(root.joinpath(".env").read_text(), original)

    def test_env_load_preserves_caller_and_handles_bom_quotes(self):
        from config import load_env

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text(
                '\ufeffSIGNAL_TEST_VALUE="test with spaces"\nSIGNAL_TEST_KEEP=new\n',
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"SIGNAL_TEST_KEEP": "old"}, clear=True):
                load_env(path)
                self.assertEqual(os.environ["SIGNAL_TEST_VALUE"], "test with spaces")
                self.assertEqual(os.environ["SIGNAL_TEST_KEEP"], "old")

    def test_utf16_entity_bypass_rejected(self):
        xml = '<!DOCTYPE rss [<!ENTITY x "expanded">]><rss><channel><item><title>&x;</title></item></channel></rss>'
        with self.assertRaises(ValueError):
            feeds.parse_feed(xml.encode("utf-16-le"), "Untrusted")

    def test_newsletter_template_contains_alternatives_and_source_links(self):
        issue = edition()
        issue.update(status="published", slug="test-edition")
        with patch.object(mailer, "send") as sender:
            mailer.email_issue(
                issue,
                {"email": "reader@example.org", "unsubscribe_token": "test-token"},
                "https://news.example.org",
            )
        args = sender.call_args.args
        self.assertIn("Source: https://example.org/paper", args[2])
        self.assertIn('<meta name="viewport"', args[3])
        self.assertIn("https://news.example.org/unsubscribe/test-token", args[3])
        self.assertIn("Original source", args[3])


if __name__ == "__main__":
    unittest.main()
