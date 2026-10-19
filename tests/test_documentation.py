"""Documentation checks should catch real missing files and bad heading references."""

import tempfile
import unittest
from pathlib import Path
from tools.check_docs import check_link, targets


class TestDocumentationLinks(unittest.TestCase):
    def test_valid_and_missing_relative_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "README.md"
            source.write_text("# Start\n", encoding="utf-8")
            page = root / "guide.md"
            page.write_text("# Guide\n## Save the draft\n", encoding="utf-8")
            self.assertIsNone(check_link(source, "guide.md#save-the-draft", root))
            self.assertEqual(
                check_link(source, "guide.md#missing", root), "missing Markdown heading anchor"
            )
            self.assertEqual(check_link(source, "no-guide.md", root), "missing local target")
            self.assertEqual(check_link(source, "../outside.md", root), "link leaves repository")

    def test_collects_markdown_and_html_images_but_not_code_examples(self):
        text = '[Guide](guide.md) ![Alt](image.png) <img src="mobile.png" alt="Demo">\n```text\n[example](not-a-real-link.md)\n```'
        self.assertEqual(targets(text), {"guide.md", "image.png", "mobile.png"})
