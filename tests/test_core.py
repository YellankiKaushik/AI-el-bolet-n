import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db
import feeds
import llm
import server


class TestCore(unittest.TestCase):
    def setUp(self):
        self.previous = db.DB_PATH
        self.temp = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temp.name) / "test.db"
        db.init()

    def tearDown(self):
        db.DB_PATH = self.previous
        self.temp.cleanup()

    def test_rss_and_atom_ingestion(self):
        rss = b"""<rss><channel><item><title>New Tool</title><link>https://example.org/tool</link><description><![CDATA[<p>Useful &amp; promising</p>]]></description><pubDate>Wed, 14 Oct 2026 10:00:00 GMT</pubDate></item></channel></rss>"""
        atom = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Study</title><link href="https://example.org/study"/><summary>Research</summary></entry></feed>"""
        one = feeds.parse_feed(rss, "Example")
        two = feeds.parse_feed(atom, "Science")
        self.assertEqual(one[0]["description"], "Useful & promising")
        self.assertEqual(two[0]["url"], "https://example.org/study")
        self.assertEqual(db.insert_stories(one + two), 2)
        self.assertEqual(db.insert_stories(one + two), 0)

    def test_editor_state_machine(self):
        item = {
            "headline": "Model benchmark",
            "summary": "A release was announced.",
            "why": "Developers can compare it.",
            "url": "https://example.org/source",
            "source": "Example",
        }
        issue_id = db.create_issue(
            server.verify_issue(
                {
                    "title": "My edition",
                    "subject": "My subject",
                    "intro": "Hello",
                    "closing": "Bye",
                    "items": [item],
                }
            )
        )
        with self.assertRaises(ValueError):
            db.publish(issue_id)
        db.review(issue_id)
        db.approve(issue_id)
        self.assertEqual(db.get_issue(issue_id=issue_id)["status"], "approved")
        db.update_issue(
            issue_id, server.verify_issue({"title": "Revised", "subject": "A", "items": [item]})
        )
        self.assertEqual(db.get_issue(issue_id=issue_id)["status"], "draft")
        db.update_issue(
            issue_id, {**db.get_issue(issue_id=issue_id), "intro": "Hello", "closing": "Bye"}
        )
        db.review(issue_id)
        db.approve(issue_id)
        db.publish(issue_id)
        self.assertIsNotNone(db.get_issue(issue_id=issue_id, published_only=True))
        with self.assertRaises(ValueError):
            db.update_issue(issue_id, server.verify_issue({"title": "Bad", "subject": "Bad"}))

    def test_refuses_bad_url(self):
        with self.assertRaises(ValueError):
            server.verify_issue(
                {"title": "A", "subject": "A", "items": [{"url": "javascript:alert(1)"}]}
            )

    def test_grounded_model_rejects_unknown_ids(self):
        input_stories = [
            {
                "id": 9,
                "title": "Some research",
                "description": "Research launched",
                "url": "https://example.com/r",
                "source": "A",
            }
        ]
        model_json = {
            "title": "Today",
            "subject": "A",
            "intro": "Intro",
            "closing": "Bye",
            "items": [
                {"story_id": 999, "headline": "Unknown", "summary": "Bad"},
                {
                    "story_id": 9,
                    "headline": "New paper",
                    "summary": "Research launched",
                    "why": "Worth studying",
                },
            ],
        }
        reply = {"message": {"content": json.dumps(model_json)}}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *x):
                return None

            def read(self, *x):
                return json.dumps(reply).encode()

        with patch.object(llm, "urlopen", return_value=FakeResponse()):
            with self.assertRaisesRegex(ValueError, "unknown"):
                llm.generate(input_stories)


if __name__ == "__main__":
    unittest.main()
