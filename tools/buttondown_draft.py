"""Optional private Buttondown draft adapter. No subscriber-delivery operation."""

import json
import os
import re
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import URLError


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise URLError("Provider redirects are forbidden")


def draft_payload(edition, origin="https://kaaush.vercel.app"):
    if origin != "https://kaaush.vercel.app" or not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*", edition["slug"]
    ):
        raise ValueError("Use the verified portfolio origin and public slug")
    # Text is rendered as escaped HTML, never treated as provider instructions.
    from html import escape

    url = origin + "/newsletter/" + edition["slug"]
    body = f'<p><a href="{url}">Read this edition on the portfolio</a></p><p>{escape(edition["intro"])}</p>'
    for item in edition["items"]:
        body += f"<h2>{escape(item['headline'])}</h2><p>{escape(item['summary'])}</p><p>{escape(item['why'])}</p><p>Source: {escape(item['source'])}</p>"
    body += f"<p>{escape(edition['closing'])}</p>"
    return {
        "subject": edition["title"],
        "body": body,
        "status": "draft",
        "canonical_url": url,
        "archival_mode": "disabled",
    }


def request(method, path, payload=None):
    token = os.getenv("BUTTONDOWN_API_KEY", "")
    if not token:
        raise ValueError("Connect a private BUTTONDOWN_API_KEY; no request was made")
    req = Request(
        "https://api.buttondown.com/v1/" + path,
        data=json.dumps(payload).encode() if payload else None,
        headers={"Authorization": "Token " + token, "Content-Type": "application/json"},
        method=method,
    )
    with build_opener(NoRedirect()).open(req, timeout=30) as response:
        return json.load(response)


def create_draft(edition, ledger):
    """Exclusive durable reservation; ambiguous failures require reconciliation, never retry blindly."""
    from pathlib import Path

    ledger = Path(ledger)
    payload = draft_payload(edition)
    descriptor = os.open(ledger, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "edition_id": edition["id"],
                "version": edition["version"],
                "state": "reserved; reconcile before retry",
            },
            handle,
        )
        handle.flush()
        os.fsync(handle.fileno())
    result = request("POST", "emails", payload)
    if result.get("status") != "draft" or not re.fullmatch(r"[a-zA-Z0-9_-]+", result.get("id", "")):
        raise ValueError("Unexpected provider state; preserve ledger and reconcile")
    with ledger.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "edition_id": edition["id"],
                "version": edition["version"],
                "provider_id": result["id"],
                "state": "draft",
            },
            handle,
        )
    return result["id"]


def reconcile(provider_id):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", provider_id):
        raise ValueError("Invalid provider ID")
    return request("GET", "emails/" + provider_id)


def send_test(provider_id, reservation):
    """One explicit draft preview to the owner's configured mailbox, never a subscriber send."""
    from validation import email_address

    mailbox = os.getenv("BUTTONDOWN_TEST_EMAIL", "")
    if os.getenv("BUTTONDOWN_TEST_SEND_ENABLED") != "true":
        raise ValueError("Explicitly configure an authorized owner mailbox and enable test sends")
    mailbox = email_address(mailbox)
    if reconcile(provider_id).get("status") != "draft":
        raise ValueError("Test sends require an existing provider draft")
    descriptor = os.open(reservation, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    return request("POST", "emails/" + provider_id + "/send-draft", {"recipients": [mailbox]})
