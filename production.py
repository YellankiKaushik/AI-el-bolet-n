"""Production WSGI transport. Business routes are shared with the local editor."""

import io
import ipaddress
import os
import sys
from email.message import Message
from http import HTTPStatus
from urllib.parse import urlparse

from config import load_env

if __name__ == "__main__":
    load_env()
import db
import server
from instance import instance_lock


class WSGIRequest(server.Handler):
    """Adapt parsed WSGI requests; never invoke the development HTTP parser."""

    def __init__(self, environ):
        self.path = environ.get("PATH_INFO", "/")
        if environ.get("QUERY_STRING"):
            self.path += "?" + environ["QUERY_STRING"]
        self.client_address = (environ.get("REMOTE_ADDR", ""), 0)
        self.headers = Message()
        for name, value in environ.items():
            if name.startswith("HTTP_"):
                self.headers[name[5:].replace("_", "-")] = value
        for name in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            if name in environ:
                self.headers[name.replace("_", "-")] = environ[name]
        self.rfile = environ["wsgi.input"]
        self.wfile = io.BytesIO()
        self.response_headers = []

    def send_response(self, code, message=None):
        self.status = f"{code} {HTTPStatus(code).phrase}"

    def send_header(self, name, value):
        self.response_headers.append((name, str(value)))

    def end_headers(self):
        pass


def application(environ, start_response):
    request = WSGIRequest(environ)
    method = environ.get("REQUEST_METHOD", "GET")
    try:
        production = os.getenv("APP_ENV", "development") == "production"
        host = environ.get("HTTP_HOST", "").lower()
        expected = urlparse(server.PUBLIC_URL).netloc.lower()
        # Health checks use the canonical Host as well; no bypass for privileged paths.
        if production and host != expected:
            request.json_out(400, {"error": "Invalid host"})
        elif production and environ.get("wsgi.url_scheme") != "https":
            request.json_out(400, {"error": "HTTPS proxy required"})
        elif method not in ("GET", "POST", "HEAD"):
            request.send(405, "Method not allowed", "text/plain", {"Allow": "GET, HEAD, POST"})
        elif method == "HEAD" and request.path.startswith("/confirm/"):
            # Link scanners' HEAD requests must not confirm subscriptions.
            request.send(200, b"")
        elif method == "POST":
            request.do_POST()
        else:
            request.do_GET()
    except Exception as exc:
        print("WSGI request error:", type(exc).__name__, file=sys.stderr)
        request.wfile = io.BytesIO()
        request.response_headers = []
        request.json_out(500, {"error": "Request failed"})
    start_response(request.status, request.response_headers)
    return [b"" if method == "HEAD" else request.wfile.getvalue()]


def waitress_options():
    proxy = os.getenv("TRUSTED_PROXY", "127.0.0.1")
    ipaddress.ip_address(proxy)  # Reject '*', DNS names and ambiguous proxy chains.
    return {
        "host": os.getenv("HOST", "127.0.0.1"),
        "port": int(os.getenv("PORT", "8787")),
        "threads": 8,
        "connection_limit": 64,
        "backlog": 64,
        "channel_timeout": 30,
        "cleanup_interval": 5,
        "max_request_header_size": 16384,
        "max_request_body_size": 140000,
        "trusted_proxy": proxy,
        "trusted_proxy_count": 1,
        "trusted_proxy_headers": {"x-forwarded-for", "x-forwarded-proto"},
        "clear_untrusted_proxy_headers": True,
        "expose_tracebacks": False,
        "ident": "SignalDaily",
    }


def main():
    from waitress import serve

    if os.getenv("APP_ENV") != "production":
        raise ValueError("Set APP_ENV=production for the production entry point")
    server.validate_config()
    options = waitress_options()
    with instance_lock(db.DB_PATH):
        db.init()
        print("Signal Daily WSGI started; one instance, private proxy upstream", flush=True)
        serve(application, **options)


if __name__ == "__main__":
    main()
