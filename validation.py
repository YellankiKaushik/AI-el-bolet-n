"""Shared validation at model, import, database and publication boundaries."""

import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TOPICS = ("AI", "Research", "Tools", "Industry")


def valid_url(value):
    try:
        p = urlsplit(value)
        return (
            p.scheme in ("http", "https")
            and bool(p.hostname)
            and not p.username
            and not p.password
            and p.port != 0
            and not re.search(r"[\s\\\x00-\x1f\x7f]", value)
        )
    except (ValueError, TypeError):
        return False


def canonical_url(value):
    if not valid_url(value):
        raise ValueError("A valid HTTP(S) source URL is required")
    p = urlsplit(value)
    query = [
        (k, v)
        for k, v in parse_qsl(p.query, keep_blank_values=True)
        if not k.lower().startswith("utm_") and k.lower() not in ("fbclid", "gclid")
    ]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or "/", urlencode(query), ""))


def text(data, key, limit, required=False):
    value = data.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"{key} must be text")
    value = value.strip()
    if len(value) > limit:
        raise ValueError(f"{key} exceeds {limit} characters")
    if required and not value:
        raise ValueError(f"{key} is required")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ValueError(f"{key} contains control characters")
    return value


def verify_issue(data, complete=False):
    if not isinstance(data, dict):
        raise ValueError("Edition must be a JSON object")
    result = {
        key: text(data, key, limit, required=key in ("title", "subject") or complete)
        for key, limit in (("title", 180), ("subject", 200), ("intro", 2500), ("closing", 1200))
    }
    topic = data.get("topic", "AI")
    if topic not in TOPICS:
        raise ValueError("Choose a supported topic")
    result["topic"] = topic
    raw = data.get("items", [])
    if not isinstance(raw, list) or len(raw) > 12 or (complete and not raw):
        raise ValueError("Edition requires 1 to 12 stories before review")
    items = []
    seen = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Each story must be an object")
        out = {
            key: text(item, key, limit, complete)
            for key, limit in (("headline", 200), ("summary", 1200), ("why", 600), ("source", 100))
        }
        url = text(item, "url", 1400, True)
        if not valid_url(url):
            raise ValueError("Stories require valid HTTP(S) source URLs")
        if canonical_url(url) in seen:
            raise ValueError("Duplicate source URL in edition")
        seen.add(canonical_url(url))
        out["url"] = url
        for key, limit in (
            ("source_title", 240),
            ("source_description", 1200),
            ("published_at", 100),
        ):
            out[key] = text(item, key, limit)
        items.append(out)
    result["items"] = items
    return result


def email_address(value):
    if not isinstance(value, str):
        raise ValueError("Enter a valid email address")
    value = value.strip().lower()
    if len(value) > 254 or not re.fullmatch(
        r"[a-z0-9!#$%&'*+/=?^_`{|}~.-]+@[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,63}", value
    ):
        raise ValueError("Enter a valid email address")
    local, domain = value.rsplit("@", 1)
    if len(local) > 64 or local.startswith(".") or local.endswith(".") or ".." in value:
        raise ValueError("Enter a valid email address")
    if any(
        not label or len(label) > 63 or label.startswith("-") or label.endswith("-")
        for label in domain.split(".")
    ):
        raise ValueError("Enter a valid email address")
    return value
