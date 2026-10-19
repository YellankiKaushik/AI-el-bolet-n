"""Fictional workspaces must never seed or reset a real newsletter database."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import db
from tools import demo


class TestDemoWorkspace(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.target = self.root / ".tmp/check/demo.db"
        self.database = patch.object(db, "DB_PATH", self.target)
        self.database.start()
        db.init()

    def tearDown(self):
        self.database.stop()
        self.temp.cleanup()

    def test_seed_and_restart_preserve_synthetic_edits(self):
        # The fixture is read from the real source tree; only the isolation root is temporary.
        import json

        fixture = Path(demo.ROOT / "docs/examples/synthetic-newsletter.json").read_text(
            encoding="utf-8"
        )
        destination = self.root / "docs/examples/synthetic-newsletter.json"
        destination.parent.mkdir(parents=True)
        destination.write_text(fixture, encoding="utf-8")
        with patch.object(demo, "ROOT", self.root):
            self.assertTrue(demo.seed_demo(self.target))
            self.assertEqual(len(db.get_issues()), 5)
            self.assertEqual(len(db.get_issues(published_only=True)), 3)
            draft = next(item for item in db.get_issues() if item["status"] == "draft")
            db.update_issue(draft["id"], {**json.loads(fixture), "title": "Edited synthetic draft"})
            self.assertFalse(demo.seed_demo(self.target))
            self.assertEqual(db.get_issue(issue_id=draft["id"])["title"], "Edited synthetic draft")
            self.assertEqual(db.stats()["subscribers"], 0)

    def test_rejects_real_path_and_mismatched_active_database(self):
        with patch.object(demo, "ROOT", self.root):
            with self.assertRaises(ValueError):
                demo.seed_demo(self.root / "data/signal_daily.db")
            with self.assertRaises(ValueError):
                demo.seed_demo(self.root / ".tmp/other/demo.db")

    def test_rejects_existing_subscriber_records(self):
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO subscribers(email,status,unsubscribe_token,created_at) VALUES('fixture@example.org','pending','synthetic-token',?)",
                (db.now(),),
            )
        with patch.object(demo, "ROOT", self.root), self.assertRaises(ValueError):
            demo.seed_demo(self.target)

    def test_workspace_rejects_traversal(self):
        with patch.object(demo, "ROOT", self.root):
            self.assertEqual(demo.workspace("acceptance"), self.root / ".tmp/acceptance")
            for name in ("../data", "", "nested/name", "name with spaces"):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    demo.workspace(name)
