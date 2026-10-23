"""Fetch concise headlines and descriptions from configured RSS/Atom sources."""

import html
import os
import re
import time
import ipaddress
import socket
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import build_opener, HTTPRedirectHandler, Request

# parse_feed applies UTF-8, size and DTD guards before parsing.
from xml.etree import ElementTree as ET  # nosec B405
from email.utils import parsedate_to_datetime
from validation import canonical_url, valid_url

DEFAULT_FEEDS = {
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "MIT Technology Review": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "arXiv AI": "https://rss.arxiv.org/rss/cs.AI",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def clean(raw, limit=500):
    p = Text()
    p.feed(raw or "")
    text = html.unescape(" ".join(p.parts))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def local_name(tag):
    return tag.split("}", 1)[-1]


def field(node, field_names):
    if "link" in field_names:
        for child in node:
            if (
                local_name(child.tag) == "link"
                and child.attrib.get("rel", "alternate") == "alternate"
            ):
                return child.attrib.get("href") or "".join(child.itertext()).strip()
    for child in node:
        if local_name(child.tag) in field_names:
            if local_name(child.tag) == "link" and child.attrib.get("href"):
                return child.attrib["href"]
            return "".join(child.itertext()).strip()
    return ""


def parse_feed(xml_data, source):
    if (
        len(xml_data) > 1_500_000
        or b"<!DOCTYPE" in xml_data.upper()
        or b"<!ENTITY" in xml_data.upper()
    ):
        raise ValueError("Unsafe or oversized feed XML")
    # Reject alternate-encoding/NUL tricks before the stdlib XML parser sees any declarations.
    decoded = xml_data.decode("utf-8-sig")
    if "\x00" in decoded or "<!doctype" in decoded.lower() or "<!entity" in decoded.lower():
        raise ValueError("Only UTF-8 feeds without DTD/entity declarations are supported")
    # Bounded UTF-8 input; DTD/entities rejected above, including NUL/encoding tricks.
    root = ET.fromstring(decoded)  # nosec B314
    records = []
    for el in root.iter():
        if local_name(el.tag) not in ("item", "entry"):
            continue
        title = clean(field(el, {"title"}), 220)
        link = field(el, {"link"})
        desc = clean(field(el, {"description", "summary", "content"}), 640)
        date = field(el, {"pubDate", "published", "updated"})[:100]
        try:
            if "GMT" in date or "," in date:
                date = parsedate_to_datetime(date).isoformat()
        except (ValueError, TypeError, OverflowError):
            date = "invalid"  # Excluded by relevant_recent; never invent a publication date.
        if title and valid_url(link):
            records.append(
                {
                    "title": title,
                    "url": canonical_url(link),
                    "description": desc,
                    "published_at": date,
                    "source": source,
                }
            )
    return records[:30]


def sources():
    custom = os.getenv("RSS_FEEDS", "").strip()
    if not custom:
        return DEFAULT_FEEDS
    # Format: Label|https://feed,Another|https://feed
    feeds = {}
    for spec in custom.split(","):
        if "|" in spec:
            name, url = spec.split("|", 1)
            if urlparse(url.strip()).scheme == "https":
                feeds[name.strip()[:60]] = url.strip()
    return feeds


def public_endpoint(url):
    if not valid_url(url) or urlparse(url).scheme != "https":
        raise ValueError("Feed endpoints require public HTTPS URLs")
    p = urlparse(url)
    addresses = socket.getaddrinfo(p.hostname, p.port or 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(x[4][0]).is_global for x in addresses):
        raise ValueError("Private and loopback feed destinations are forbidden")
    return url


class PublicRedirect(HTTPRedirectHandler):
    max_redirections = 3

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_endpoint(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def relevant_recent(story):
    date = story.get("published_at", "")
    if date:
        try:
            stamp = datetime.fromisoformat(date.replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            current = datetime.now(timezone.utc)
            if stamp < current - timedelta(
                days=int(os.getenv("RSS_MAX_AGE_DAYS", "14"))
            ) or stamp > current + timedelta(days=1):
                return False
        except ValueError:
            # Unparseable dates are excluded from current-news generation.
            return False
    keywords = os.getenv(
        "RSS_KEYWORDS",
        "ai,artificial intelligence,machine learning,llm,model,agent,neural,robot,transformer",
    ).split(",")
    haystack = (story["title"] + " " + story["description"]).lower()
    return any(
        re.search(r"\b" + re.escape(word.strip().lower()) + r"\b", haystack)
        for word in keywords
        if word.strip()
    )


def fetch_all():
    results = []
    errors = []
    limit = min(200, max(1, int(os.getenv("RSS_LIMIT", "80"))))
    retries = min(2, max(0, int(os.getenv("RSS_RETRIES", "1"))))
    deadline = time.monotonic() + 90
    opener = build_opener(PublicRedirect())
    seen = set()
    for name, url in list(sources().items())[:10]:
        for attempt in range(retries + 1):
            try:
                if time.monotonic() > deadline:
                    raise TimeoutError("Collection time budget exhausted")
                public_endpoint(url)
                req = Request(
                    url,
                    headers={"User-Agent": "SignalDaily/1.0 (+RSS reader; editorial summaries)"},
                )
                with opener.open(req, timeout=min(12, max(1, deadline - time.monotonic()))) as resp:
                    data = resp.read(1_500_001)
                for story in parse_feed(data, name):
                    if story["url"] not in seen and relevant_recent(story) and len(results) < limit:
                        results.append(story)
                        seen.add(story["url"])
                break
            except Exception as err:
                if attempt < retries and isinstance(err, (OSError, TimeoutError)):
                    time.sleep(0.2 * (attempt + 1))
                    continue
                errors.append(f"{name}: {type(err).__name__} (check feed URL/network)")
                break
        if len(results) >= limit:
            break
    return results, errors


def rank_topic(stories, topic):
    """Rank only supplied feed evidence; this is not unrestricted web search."""
    if not isinstance(topic, str) or len(topic) > 200:
        raise ValueError("Topic must be text of at most 200 characters")
    ignored = {"the", "in", "of", "and", "for", "to", "latest", "developments", "ai"}
    terms = {
        word.rstrip("s")
        for word in re.findall(r"[a-z0-9]+", topic.lower())
        if len(word) > 2 and word not in ignored
    }
    if not topic.strip():
        return list(stories)
    if not terms:
        raise ValueError("Use a specific topic, such as open-source models")
    ranked = []
    for index, story in enumerate(stories):
        title = {word.rstrip("s") for word in re.findall(r"[a-z0-9]+", story["title"].lower())}
        body = {
            word.rstrip("s")
            for word in re.findall(r"[a-z0-9]+", story.get("description", "").lower())
        }
        score = len(terms & title) * 3 + len(terms & body)
        if score:
            ranked.append((score, index, story))
    return [story for _, _, story in sorted(ranked, key=lambda row: (-row[0], row[1]))]
