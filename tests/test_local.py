"""Local startup must stay private and default to no real email."""

import os
import unittest
from unittest.mock import patch

import run
import server


class TestLocalStartup(unittest.TestCase):
    def test_local_startup_defaults_mail_off(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(run, "load_env"),
            patch.object(server, "main") as start,
        ):
            run.main()
            self.assertEqual(os.environ["EMAIL_DELIVERY_ENABLED"], "false")
            start.assert_called_once()

    def test_local_startup_rejects_public_bind(self):
        for host in ("0.0.0.0", "::", "192.168.1.8", "example.org"):
            with (
                self.subTest(host=host),
                patch.dict(os.environ, {"HOST": host}, clear=True),
                patch.object(run, "load_env"),
                patch.object(server, "main") as start,
            ):
                with self.assertRaisesRegex(ValueError, "loopback"):
                    run.main()
                start.assert_not_called()

    def test_local_startup_preserves_existing_secrets(self):
        values = {
            "HOST": "127.0.0.1",
            "ADMIN_PASSWORD": "existing-test-only",
            "SESSION_SECRET": "existing-test-only-secret",
        }
        with (
            patch.dict(os.environ, values, clear=True),
            patch.object(run, "load_env"),
            patch.object(server, "main"),
        ):
            run.main()
            self.assertEqual(os.environ["ADMIN_PASSWORD"], values["ADMIN_PASSWORD"])
            self.assertEqual(os.environ["SESSION_SECRET"], values["SESSION_SECRET"])
