"""Private CLI outputs should create their directory and never overwrite drafts."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestLocalGenerateFiles(unittest.TestCase):
    def test_creates_parent_directory_for_new_private_output(self):
        from tools import local_generate

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "stories.json"
            source.write_text('[{"title":"Synthetic AI note"}]', encoding="utf-8")
            target = root / "nested/draft.json"
            result = {"title": "Synthetic draft", "items": []}
            with (
                patch.object(local_generate.llm, "generate", return_value=result),
                patch.object(
                    local_generate.sys,
                    "argv",
                    ["local_generate.py", "--stories", str(source), "--output", str(target)],
                ),
            ):
                local_generate.main()
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), result)

    def test_refuses_to_overwrite_before_using_model(self):
        from tools import local_generate

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "draft.json"
            target.write_text("keep this draft", encoding="utf-8")
            with (
                patch.object(local_generate.llm, "generate") as generate,
                patch.object(
                    local_generate.sys, "argv", ["local_generate.py", "--output", str(target)]
                ),
                self.assertRaises(SystemExit),
            ):
                local_generate.main()
            self.assertEqual(target.read_text(encoding="utf-8"), "keep this draft")
            generate.assert_not_called()
