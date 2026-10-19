"""Synthetic integration check for an isolated, network-disabled verification container.

Never points at a real deployment. See docs/PRODUCTION_RUNBOOK.md for its test-only setup.
"""

import argparse
import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    if (
        os.getenv("PUBLIC_URL") != "https://pilot.example.org"
        or os.getenv("EMAIL_DELIVERY_ENABLED") != "false"
        or Path(os.getenv("DATABASE_PATH", "")).name != "verification.db"
        or os.getenv("HOST") != "127.0.0.1"
    ):
        raise SystemExit("Refusing: this check requires the isolated verification configuration")
    cookie = ""

    def call(path, data=None):
        headers = {
            "Host": "pilot.example.org",
            "X-Forwarded-Proto": "https",
            "X-Signal-Request": "1",
            "Content-Type": "application/json",
            "Cookie": cookie,
        }
        request = Request(
            "http://127.0.0.1:8787" + path,
            headers=headers,
            data=json.dumps(data).encode() if data is not None else None,
        )
        try:
            # Fixed loopback URL, restricted to the disposable verification configuration.
            response = urlopen(request, timeout=5)  # nosec B310
        except HTTPError as exc:
            response = exc
        with response:
            return response.code, response.read(), response.headers

    for attempt in range(30):
        try:
            if call("/health")[0] == 200:
                break
        except URLError:
            pass
        time.sleep(0.2)
    else:
        raise RuntimeError("Verification server did not become ready")
    status, _, headers = call("/api/login", {"password": os.environ["ADMIN_PASSWORD"]})
    if status != 200:
        raise RuntimeError("Verification authentication failed")
    cookie = headers["Set-Cookie"].split(";", 1)[0]
    status, body, _ = call("/api/admin/data")
    data = json.loads(body)
    if status != 200 or data["stats"]["subscribers"]:
        raise RuntimeError("Verification database must have no active subscribers")
    if not args.verify_existing:
        if data["issues"]:
            raise RuntimeError("Start with a fresh verification volume")
        payload = {
            "title": "SYNTHETIC container check",
            "subject": "SYNTHETIC only",
            "intro": "Fictional verification content.",
            "closing": "Test complete.",
            "items": [
                {
                    "headline": "Synthetic AI check",
                    "summary": "A fictional event.",
                    "why": "Verifies persistence.",
                    "url": "https://example.org/synthetic",
                    "source": "Test fixture",
                }
            ],
            "status": "published",
        }
        status, body, _ = call("/api/admin/import", payload)
        if status != 200:
            raise RuntimeError("Synthetic import failed")
        identity = json.loads(body)["issue_id"]
        if call(f"/api/admin/issue/{identity}/publish", {})[0] != 400:
            raise RuntimeError("Approval bypass detected")
        for action in ("review", "approve", "publish"):
            if call(f"/api/admin/issue/{identity}/{action}", {})[0] != 200:
                raise RuntimeError("Synthetic editorial transition failed")
    _, body, _ = call("/api/admin/data")
    issues = json.loads(body)["issues"]
    if (
        len(issues) != 1
        or issues[0]["title"] != "SYNTHETIC container check"
        or issues[0]["status"] != "published"
    ):
        raise RuntimeError("Synthetic publication was not persisted")
    for path in ("/", "/archive", "/issue/" + issues[0]["slug"]):
        status, body, _ = call(path)
        if status != 200 or b"SYNTHETIC" not in body:
            raise RuntimeError("Public archive verification failed")
    print("Synthetic workflow and persisted public archive verified; no real content or recipients")


if __name__ == "__main__":
    main()
