"""Local AI privacy regressions, with synthetic input and loopback HTTP only."""

import io
import json
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import llm


STORIES = [
    {
        "id": 1,
        "title": "Synthetic AI report",
        "description": "A synthetic AI report.",
        "source": "Fictional source",
        "url": "https://example.org/synthetic",
    }
]
CONTENT = {
    "title": "Synthetic",
    "subject": "Synthetic",
    "intro": "Fictional test.",
    "closing": "Test only.",
    "items": [
        {
            "story_id": 1,
            "headline": "Synthetic AI report",
            "summary": "A synthetic AI report.",
            "why": "Test only.",
        }
    ],
}
RESPONSE = json.dumps({"message": {"content": json.dumps(CONTENT)}}).encode()


@contextmanager
def http_listener(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def model_handler(calls):
    class ModelHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            calls.append(
                (self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            )
            self.send_response(200)
            self.end_headers()
            self.wfile.write(RESPONSE)

        def do_GET(self):
            calls.append((self.path, None))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(RESPONSE)

        def log_message(self, *args):
            pass

    return ModelHandler


class TestLocalAIPrivacy(unittest.TestCase):
    def test_cloud_tags_are_rejected_before_transport(self):
        for model in ("gemma4:cloud", "gpt-oss:120b-cloud", "Gemma4:CLOUD", "cloud/test:latest"):
            with (
                self.subTest(model=model),
                patch.object(llm, "OLLAMA_MODEL", model),
                patch.object(llm, "urlopen") as request,
                self.assertRaisesRegex(ValueError, "cloud"),
            ):
                llm.generate(STORIES)
            request.assert_not_called()

    def test_local_model_tag_and_source_provenance_are_preserved(self):
        with (
            patch.object(llm, "OLLAMA_MODEL", "gemma4:e4b"),
            patch.object(llm, "urlopen", return_value=io.BytesIO(RESPONSE)) as request,
        ):
            result = llm.generate(STORIES)
        self.assertEqual(json.loads(request.call_args.args[0].data)["model"], "gemma4:e4b")
        self.assertEqual(result["items"][0]["url"], STORIES[0]["url"])
        self.assertEqual(result["items"][0]["source_description"], STORIES[0]["description"])

    def test_remote_endpoint_is_rejected_before_transport(self):
        with (
            patch.object(llm, "OLLAMA_URL", "https://example.org"),
            patch.object(llm, "urlopen") as request,
            self.assertRaisesRegex(ValueError, "loopback"),
        ):
            llm.generate(STORIES)
        request.assert_not_called()

    def test_loopback_redirect_does_not_contact_redirect_target(self):
        calls = []
        with http_listener(model_handler(calls)) as target:

            class Redirect(BaseHTTPRequestHandler):
                def do_POST(self):
                    self.rfile.read(int(self.headers["Content-Length"]))
                    self.send_response(302)
                    self.send_header("Location", target + "/redirected-model")
                    self.end_headers()

                def log_message(self, *args):
                    pass

            with (
                http_listener(Redirect) as origin,
                patch.object(llm, "OLLAMA_URL", origin),
                self.assertRaisesRegex(RuntimeError, "no cloud fallback"),
            ):
                llm.generate(STORIES)
        self.assertEqual(calls, [])

    def test_system_proxy_cannot_receive_local_model_prompts(self):
        direct_calls, proxy_calls = [], []
        with (
            http_listener(model_handler(direct_calls)) as direct,
            http_listener(model_handler(proxy_calls)) as proxy,
            patch.object(llm, "OLLAMA_URL", direct),
            patch("urllib.request.getproxies", return_value={"http": proxy}),
            patch("urllib.request.proxy_bypass", return_value=False),
        ):
            llm.generate(STORIES)
        self.assertEqual(proxy_calls, [])
        self.assertEqual(len(direct_calls), 1)
        self.assertEqual(direct_calls[0][0], "/api/chat")
        self.assertIn("Synthetic AI report", direct_calls[0][1]["messages"][1]["content"])


if __name__ == "__main__":
    unittest.main()
