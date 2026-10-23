import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import db
import feeds
from tools.publish_portfolio import export, public_edition
from tools.buttondown_draft import create_draft, draft_payload, send_test


class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = db.DB_PATH
        db.DB_PATH = Path(self.temp.name) / "test.db"
        db.init()
        self.issue = db.create_issue(
            {
                "title": "Fictional open models",
                "subject": "Fixture",
                "intro": "Fictional intro",
                "closing": "Fixture only",
                "items": [
                    {
                        "headline": "Fictional model",
                        "summary": "A fictional release",
                        "why": "A fixture",
                        "source": "Example",
                        "url": "https://example.org/source",
                    }
                ],
            }
        )

    def tearDown(self):
        db.DB_PATH = self.previous
        self.temp.cleanup()

    def publish(self):
        db.review(self.issue)
        db.approve(self.issue)
        db.publish(self.issue)
        return db.get_issue(issue_id=self.issue)["version"]

    def test_requires_approval_and_publication(self):
        with self.assertRaises(ValueError):
            public_edition(db.DB_PATH, self.issue, 1)
        db.review(self.issue)
        db.approve(self.issue)
        with self.assertRaises(ValueError):
            public_edition(db.DB_PATH, self.issue, 3)

    def test_export_public_allowlist_duplicate_and_stale(self):
        version = self.publish()
        destination = Path(self.temp.name) / "public.json"
        self.assertTrue(export(db.DB_PATH, self.issue, version, destination))
        self.assertFalse(export(db.DB_PATH, self.issue, version, destination))
        with self.assertRaises(ValueError):
            export(db.DB_PATH, self.issue, version - 1, destination)
        edition = json.loads(destination.read_text())[0]
        self.assertNotIn("subject", edition)
        self.assertNotIn("source_description", edition["items"][0])
        self.assertEqual(
            set(edition),
            {"id", "version", "slug", "publishedAt", "title", "topic", "intro", "closing", "items"},
        )

    def test_topic_rank_insufficient_and_validation(self):
        records = [
            {"title": "Open source models", "description": ""},
            {"title": "Unrelated hardware", "description": "models"},
            {"title": "Unrelated", "description": ""},
        ]
        self.assertEqual(feeds.rank_topic(records, "open-source models"), records[:2])
        self.assertEqual(feeds.rank_topic(records, "biochemistry"), [])
        with self.assertRaises(ValueError):
            feeds.rank_topic(records, ["invalid"])

    def test_provider_draft_no_send_and_duplicate_reservation(self):
        edition = public_edition(db.DB_PATH, self.issue, self.publish())
        ledger = Path(self.temp.name) / "provider.json"
        with patch(
            "tools.buttondown_draft.request", return_value={"id": "fixture", "status": "draft"}
        ) as provider:
            self.assertEqual(create_draft(edition, ledger), "fixture")
            with self.assertRaises(FileExistsError):
                create_draft(edition, ledger)
            self.assertEqual(provider.call_count, 1)
            self.assertEqual(provider.call_args.args[2]["status"], "draft")
        self.assertIn("https://kaaush.vercel.app/newsletter/", draft_payload(edition)["body"])

    def test_provider_ambiguous_failure_keeps_reservation(self):
        edition = public_edition(db.DB_PATH, self.issue, self.publish())
        ledger = Path(self.temp.name) / "uncertain.json"
        with patch("tools.buttondown_draft.request", side_effect=TimeoutError):
            with self.assertRaises(TimeoutError):
                create_draft(edition, ledger)
        self.assertTrue(ledger.exists())

    def test_single_mailbox_preview_requires_enablement(self):
        with patch.dict("os.environ", {"BUTTONDOWN_TEST_SEND_ENABLED": "false"}):
            with self.assertRaises(ValueError):
                send_test("fixture", Path(self.temp.name) / "test-send")
        with (
            patch.dict(
                "os.environ",
                {
                    "BUTTONDOWN_TEST_SEND_ENABLED": "true",
                    "BUTTONDOWN_TEST_EMAIL": "owner@example.org",
                },
            ),
            patch("tools.buttondown_draft.reconcile", return_value={"status": "draft"}),
            patch("tools.buttondown_draft.request", return_value={}) as provider,
        ):
            reservation = Path(self.temp.name) / "test-send"
            send_test("fixture", reservation)
            self.assertEqual(provider.call_args.args[2], {"recipients": ["owner@example.org"]})
            with self.assertRaises(FileExistsError):
                send_test("fixture", reservation)
