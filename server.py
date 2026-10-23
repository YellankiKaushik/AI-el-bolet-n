"""Signal Daily: dependency-free newsletter service + local AI editorial dashboard."""

import base64
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime
from http.cookies import SimpleCookie, CookieError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import db
import feeds
import llm
import mailer
from validation import verify_issue, valid_url, email_address, TOPICS

ROOT = Path(__file__).resolve().parent
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8787"))
PUBLIC_URL = os.getenv("PUBLIC_URL", f"http://localhost:{PORT}").rstrip("/")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or secrets.token_urlsafe(12)
SESSION_KEY = os.getenv("SESSION_SECRET", "").encode() or secrets.token_bytes(32)
HTTPS = PUBLIC_URL.startswith("https://")
REQUEST_COUNTS = defaultdict(list)
LOCK = threading.Lock()
INGEST_LOCK = threading.Lock()
SESSION_EPOCH = secrets.randbits(64)

# Password hash is never disclosed through application routes.
PASSWORD_SALT = b"signal-daily-admin-v1"
PASSWORD_HASH = hashlib.pbkdf2_hmac("sha256", ADMIN_PASSWORD.encode(), PASSWORD_SALT, 260000)


def esc(s):
    return html.escape(str(s or ""), quote=True)


def mk_session():
    payload = f"{int(time.time()) + 86400}:{secrets.token_hex(10)}:{SESSION_EPOCH}"
    encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    sig = hmac.new(SESSION_KEY, encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{sig}"


def session_ok(cookie_header):
    try:
        cookies = SimpleCookie()
        cookies.load(cookie_header or "")
        token = cookies["sd_session"].value
        encoded, sig = token.rsplit(".", 1)
        check = hmac.new(SESSION_KEY, encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, check):
            return False
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode()
        expires, _, epoch = payload.split(":")
        return int(expires) > time.time() and int(epoch) == SESSION_EPOCH
    except (ValueError, KeyError, UnicodeError, CookieError):
        return False


def rate_limit(ip, limit=5, window=3600):
    if os.getenv("APP_ENV", "development") == "production":
        identity = hmac.new(SESSION_KEY, ip.encode(), hashlib.sha256).hexdigest()
        return db.rate_limited(identity, limit, window, int(time.time()))
    ts = time.monotonic()
    with LOCK:
        if len(REQUEST_COUNTS) > 10000:
            for key in list(REQUEST_COUNTS):
                if not REQUEST_COUNTS[key] or REQUEST_COUNTS[key][-1] < ts - 3600:
                    REQUEST_COUNTS.pop(key, None)
            if len(REQUEST_COUNTS) > 10000:
                return True
        items = [x for x in REQUEST_COUNTS[ip] if x > ts - window]
        if len(items) >= limit:
            REQUEST_COUNTS[ip] = items
            return True
        items.append(ts)
        REQUEST_COUNTS[ip] = items
    return False


def layout(title, content, admin=False):
    demo_banner = (
        '<aside class="demo-banner" role="note">DEMO WORKSPACE <span>Fictional editions · Email disabled · Separate database</span></aside>'
        if os.getenv("DEMO_MODE", "false").lower() == "true"
        else ""
    )
    nav = (
        '<a href="/">Home</a><a href="/archive">Archive</a><a class="nav-cta" href="/#subscribe">Subscribe <span>↗</span></a>'
        if not admin
        else '<a href="/">← View site</a><a href="/archive">Archive</a>'
    )
    asset_version = max(
        (ROOT / "static/app.js").stat().st_mtime_ns, (ROOT / "static/style.css").stat().st_mtime_ns
    )
    content = content.replace("<main", '<main id="main-content"', 1)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Signal Daily: independent AI news explained without the noise.">
<meta name="robots" content="{"noindex,nofollow" if admin else "index,follow"}"><meta property="og:title" content="{esc(title)} | Signal Daily"><title>{esc(title)} | Signal Daily</title><link rel="stylesheet" href="/static/style.css?v={asset_version}"></head>
<body class="{"admin-page" if admin else ""}"><a class="skip-link" href="#main-content">Skip to content</a><div class="topbar"><div class="topbar-inner"><a class="wordmark" href="/">SIGNAL<span class="logo-dot">●</span> DAILY</a><nav aria-label="Main navigation">{nav}</nav></div></div>
{demo_banner}{content}<footer class="footer"><div class="footer-inner"><div><strong>SIGNAL<span class="logo-dot">●</span> DAILY</strong><p>Independent AI reporting, distilled with care.</p></div><p>AI drafts. Human approves. Source links always.</p><span>© {datetime.now().year} Signal Daily · <a href="/admin">Editor login</a></span></div></footer>
<script src="/static/app.js?v={asset_version}" defer></script></body></html>'''


def signup_form(style=""):
    return f"""<form class="subscribe-form {esc(style)}" data-subscribe-form><label class="sr-only" for="email-{esc(style)}">Email address</label><input id="email-{esc(style)}" type="email" name="email" placeholder="you@company.com" required maxlength="254" autocomplete="email"><button type="submit">Get the briefing <span>↗</span></button><p class="form-message" role="status" aria-live="polite"></p></form>"""


def story_card(issue, featured=False):
    dt = issue.get("published_at") or issue.get("created_at", "")
    day = esc(dt[:10])
    summ = issue.get("intro", "")[:155]
    cls = "feature-card" if featured else "issue-card"
    return f'''<a class="{cls}" href="/issue/{quote(issue["slug"])}"><div class="eyebrow">{esc(issue.get("topic", "AI"))} <span>•</span> {day}</div>
<h3>{esc(issue["title"])}</h3><p>{esc(summ)}</p><span class="text-link">Read the issue <span>↗</span></span></a>'''


def home():
    issues = db.get_issues(published_only=True, limit=7)
    latest = issues[0] if issues else None
    feature = (
        story_card(latest, True)
        if latest
        else """<div class="feature-card empty"><div class="eyebrow">THE FIRST EDITION</div><h3>Something worth reading is coming.</h3><p>The editor is preparing the inaugural issue. Subscribe for the first dispatch.</p><span class="text-link">Made with a local AI model. Published by a human.</span></div>"""
    )
    others = (
        "".join(story_card(i) for i in issues[1:])
        or '<p class="muted">Published editions will appear here.</p>'
    )
    body = f"""<main><section class="hero wrap"><div class="hero-copy"><div class="edition-label"><span class="live-dot"></span> INDEPENDENT AI NEWSLETTER <span class="separator">/</span> HUMAN-EDITED</div>
<h1>Make sense of<br><em>what's next.</em></h1><p class="hero-subtitle">AI moves fast. We find the signal, explain what changed, and show you why it matters. An essential briefing for curious builders.</p>
{signup_form("hero-form")}<div class="assurance">Free to read <span>·</span> Original source links <span>·</span> Unsubscribe anytime</div></div>
<div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="orbit orbit-three"></div><div class="orbit-cross">✳</div><div class="art-label art-label-top">RESEARCH / TOOLS / MODELS</div><div class="art-label art-label-bottom">LESS NOISE<br>MORE SIGNAL.</div><span class="coordinate">SD—001</span></div></section>
<section class="ticker"><div class="ticker-inner"><span>THE EDITOR'S PROMISE</span><strong>Facts before hype.</strong><span>✳</span><strong>Context over clicks.</strong><span>✳</span><strong>Readers first.</strong></div></section>
<section class="wrap stories-section"><div class="section-heading"><div><div class="eyebrow">THE LATEST</div><h2>Fresh from the feed<span class="pink">.</span></h2></div><a class="text-link" href="/archive">All editions ↗</a></div><div class="featured-layout">{feature}<aside class="how-it-works"><div class="eyebrow">HOW IT WORKS</div><h3>A better way to stay ahead.</h3><div class="step"><b>01</b><div><strong>Curated inputs</strong><p>Trusted RSS headlines and primary sources—not invented news.</p></div></div><div class="step"><b>02</b><div><strong>Local AI draft</strong><p>Your own Gemma model summarizes and explains.</p></div></div><div class="step"><b>03</b><div><strong>Human review</strong><p>Every edition is checked and approved before publishing.</p></div></div></aside></div></section>
<section class="wrap archive-preview"><div class="section-heading"><div><div class="eyebrow">FROM THE ARCHIVE</div><h2>Previously on Signal<span class="pink">.</span></h2></div></div><div class="issues-grid">{others}</div></section>
<section id="subscribe" class="bottom-cta wrap"><div class="eyebrow">YOUR INBOX, UPGRADED</div><h2>Stay curious.<br><em>Stay informed.</em></h2><p>One sharp briefing. The stories that count. Nothing you don't need.</p>{signup_form("bottom-form")}</section></main>"""
    return layout("The AI briefing without the noise", body)


def archive(query=None):
    query = query or {}
    search = query.get("q", [""])[0][:120]
    topic = query.get("topic", [""])[0]
    try:
        page = min(10000, max(1, int(query.get("page", ["1"])[0])))
    except ValueError:
        page = 1
    issues = db.get_issues(
        published_only=True, limit=25, search=search, topic=topic, offset=(page - 1) * 24
    )
    more = len(issues) > 24
    issues = issues[:24]
    options = "".join(
        f'<option value="{esc(t)}" {"selected" if t == topic else ""}>{esc(t or "All topics")}</option>'
        for t in ("", *TOPICS)
    )
    links = ""
    for number, label in ((page - 1, "← Previous"), (page + 1, "Next →")):
        if number > 0 and (number < page or more):
            links += f'<a class="btn btn-outline" href="/archive?q={quote(search)}&amp;topic={quote(topic)}&amp;page={number}">{label}</a>'
    body = f'''<main class="wrap page-content"><div class="eyebrow">LIBRARY / ALL EDITIONS</div><h1 class="page-title">The archive<span class="pink">.</span></h1><p class="page-lead">Every edition, available to everyone. No paywall, no algorithm.</p><form class="search-line" method="get" action="/archive"><input name="q" type="search" value="{esc(search)}" placeholder="Search editions…" aria-label="Search editions"><select name="topic" aria-label="Topic">{options}</select><button class="btn btn-dark" type="submit">Search</button></form><div class="issues-grid" id="archive-grid">{"".join(story_card(i) for i in issues) or '<div class="empty-archive" role="status">No editions match. Try another search or topic.</div>'}</div><nav aria-label="Archive pages">{links}</nav></main>'''
    return layout("Archive", body)


def issue_page(issue):
    items = "".join(
        f'''<article class="issue-story"><div class="story-number">0{idx} / {esc(item["source"])}</div><h2>{esc(item["headline"])}</h2><p>{esc(item["summary"])}</p>
<div class="why-box"><span>WHY IT MATTERS</span><p>{esc(item.get("why", ""))}</p></div><a class="source-link" href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">Explore the original source ↗</a></article>'''
        for idx, item in enumerate(issue["items"], 1)
    )
    content = f"""<main class="wrap issue-layout"><article><a href="/archive" class="back-link">← All editions</a><div class="eyebrow">SIGNAL DAILY / {esc((issue["published_at"] or "")[:10])}</div><h1 class="issue-headline">{esc(issue["title"])}</h1><p class="issue-intro">{esc(issue["intro"])}</p><div class="issue-rule">THE STORIES <span>✳</span> ISSUE NO. {issue["id"]:03d}</div>{items}<div class="closing-note"><div class="eyebrow">THE TAKEAWAY</div><p>{esc(issue["closing"])}</p></div></article><aside class="issue-aside"><div class="sticky-signup"><div class="eyebrow">NEVER MISS THE SIGNAL</div><h3>Good news, delivered.</h3><p>Useful AI updates, published after human review.</p>{signup_form("side-form")}</div></aside></main>"""
    return layout(issue["title"], content)


def simple_page(title, headline, text):
    return layout(
        title,
        f'<main class="wrap message-page"><div class="eyebrow">SIGNAL DAILY</div><h1>{esc(headline)}</h1><p>{esc(text)}</p><a href="/" class="primary-link">Back to home ↗</a></main>',
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "SignalDaily/1.0"

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, fmt, *args):
        message = re.sub(r'/(confirm|unsubscribe)/[^ ?"\s]+', r"/\1/[REDACTED]", fmt % args)
        print(f"[{self.log_date_time_string()}] {self.address_string()} {message}", flush=True)

    def send(self, status, body, content_type="text/html; charset=utf-8", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
        )
        if self.path.startswith(("/api/", "/admin", "/confirm/", "/unsubscribe/")):
            self.send_header("Cache-Control", "no-store")
        if HTTPS:
            self.send_header("Strict-Transport-Security", "max-age=31536000")
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def json_out(self, status, obj, extra=None):
        self.send(
            status,
            json.dumps(obj, ensure_ascii=False).encode(),
            "application/json; charset=utf-8",
            extra,
        )

    def admin(self):
        return session_ok(self.headers.get("Cookie"))

    def require_admin(self):
        if not self.admin():
            self.json_out(401, {"error": "Sign in to the editor first"})
            return False
        return True

    def mutation_ok(self):
        # SameSite=Strict session cookies and a non-simple custom request header protect admin mutations.
        if self.headers.get("X-Signal-Request") != "1":
            self.json_out(403, {"error": "Missing required anti-CSRF request header"})
            return False
        origin = self.headers.get("Origin")
        if origin:
            expected = (
                PUBLIC_URL
                if os.getenv("APP_ENV", "development") == "production"
                else ("https://" if HTTPS else "http://") + self.headers.get("Host", "")
            )
            if origin != expected:
                self.json_out(403, {"error": "Cross-origin requests forbidden"})
                return False
        return True

    def incoming(self):
        if self.headers.get("Transfer-Encoding"):
            raise ValueError("Chunked bodies unsupported")
        if "application/json" not in self.headers.get("Content-Type", ""):
            raise ValueError("JSON content type required")
        length = int(self.headers.get("Content-Length", "0"))
        if length > 140_000 or length < 1:
            raise ValueError("Request body must be under 140 KB")
        raw = self.rfile.read(length)
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError("Request body must be a JSON object")
        return result

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return self.send(200, home())
        if path == "/archive":
            return self.send(200, archive(parse_qs(urlparse(self.path).query)))
        if path == "/robots.txt":
            return self.send(
                200,
                "User-agent: *\nDisallow: /admin\nDisallow: /api/\nDisallow: /confirm/\nDisallow: /unsubscribe/\nSitemap: "
                + PUBLIC_URL
                + "/sitemap.xml\n",
                "text/plain",
            )
        if path == "/sitemap.xml":
            urls = ["/", "/archive"] + [
                "/issue/" + quote(i["slug"]) for i in db.get_issues(True, 5000)
            ]
            xml = (
                '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + "".join("<url><loc>" + esc(PUBLIC_URL + u) + "</loc></url>" for u in urls)
                + "</urlset>"
            )
            return self.send(200, xml, "application/xml; charset=utf-8")
        if path.startswith("/issue/"):
            issue = db.get_issue(slug=path.split("/", 2)[2], published_only=True)
            return (
                self.send(200, issue_page(issue))
                if issue
                else self.send(
                    404,
                    simple_page(
                        "Missing", "Edition not found", "There is no published edition at this URL."
                    ),
                )
            )
        if path == "/admin":
            body = """<main class="wrap admin-shell"><div class="eyebrow">EDITORIAL CONTROL ROOM</div><h1 class="page-title">The workbench<span class="pink">.</span></h1><div id="editor-root"><p>Loading editor…</p></div></main>"""
            return self.send(200, layout("Editor dashboard", body, admin=True))
        if path.startswith("/static/"):
            name = path.removeprefix("/static/")
            if name not in ("style.css", "app.js"):
                return self.send(404, "Not found", "text/plain")
            data = (ROOT / "static" / name).read_bytes()
            ctype = (
                "text/css; charset=utf-8"
                if name.endswith(".css")
                else "text/javascript; charset=utf-8"
            )
            return self.send(200, data, ctype, {"Cache-Control": "public,max-age=300"})
        if path == "/health":
            try:
                with db.connect() as conn:
                    conn.execute("SELECT id FROM issues LIMIT 1").fetchone()
                return self.json_out(200, {"status": "ok"})
            except Exception:
                return self.json_out(503, {"status": "unavailable"})
        if path == "/api/admin/status":
            return self.json_out(
                200,
                {
                    "authenticated": self.admin(),
                    "local_model_note": "Generation works where Ollama is running, not automatically on a remote server.",
                },
            )
        history_match = re.fullmatch(r"/api/admin/issue/(\d+)/history", path)
        if history_match:
            if not self.require_admin():
                return
            return self.json_out(200, {"events": db.history(int(history_match.group(1)))})
        if path == "/api/admin/data":
            if not self.require_admin():
                return
            return self.json_out(
                200,
                {
                    "stats": db.stats(),
                    "issues": db.get_issues(limit=100),
                    "stories": db.get_stories(80),
                    "mailer": mailer.configured(),
                    "model": llm.OLLAMA_MODEL,
                },
            )
        if path.startswith("/confirm/"):
            token = path.split("/", 2)[2]
            h = hashlib.sha256(token.encode()).hexdigest()
            with db.connect() as conn:
                conn.execute("BEGIN IMMEDIATE")
                subscriber = conn.execute(
                    "SELECT id FROM subscribers WHERE verify_hash=? AND status='pending' AND verify_expires>?",
                    (h, int(time.time())),
                ).fetchone()
                if subscriber:
                    conn.execute(
                        "UPDATE subscribers SET status='active',verify_hash=NULL,confirmed_at=? WHERE id=?",
                        (db.now(), subscriber["id"]),
                    )
            return self.send(
                200,
                simple_page(
                    "Subscription confirmed",
                    "You’re on the list." if subscriber else "Link expired or already used.",
                    "Your next Signal Daily edition will arrive by email."
                    if subscriber
                    else "This confirmation link is no longer valid.",
                ),
            )
        if path.startswith("/unsubscribe/"):
            token = path.split("/", 2)[2]
            if not re.fullmatch(r"[A-Za-z0-9_-]{20,100}", token):
                return self.send(404, "Not found", "text/plain")
            body = f"""<main class="wrap message-page"><div class="eyebrow">PREFERENCES</div><h1>Leave the list?</h1><p>Click below to unsubscribe from future Signal Daily emails.</p><form method="post" action="/unsubscribe/{esc(token)}"><button class="primary-link" type="submit">Confirm unsubscribe</button></form></main>"""
            return self.send(200, layout("Unsubscribe", body))
        return self.send(
            404, simple_page("Not found", "This page has moved.", "Try the homepage or archive.")
        )

    def do_POST(self):
        global SESSION_EPOCH
        path = urlparse(self.path).path
        if path.startswith("/unsubscribe/"):
            token = path.split("/", 2)[2]
            if not re.fullmatch(r"[A-Za-z0-9_-]{20,100}", token):
                return self.send(404, "Not found", "text/plain")
            with db.connect() as conn:
                conn.execute(
                    "UPDATE subscribers SET status='unsubscribed',verify_hash=NULL WHERE unsubscribe_token=?",
                    (token,),
                )
            return self.send(
                200,
                simple_page(
                    "Unsubscribed",
                    "You’re unsubscribed.",
                    "No more newsletter emails will be sent to this address.",
                ),
            )
        if path.startswith("/api/"):
            if not self.mutation_ok():
                return
            try:
                data = self.incoming()
                if path == "/api/login":
                    if rate_limit("login:" + self.client_address[0], 10, 900):
                        return self.json_out(
                            429, {"error": "Too many sign-in attempts. Try again later."}
                        )
                    password = str(data.get("password", ""))
                    candidate = hashlib.pbkdf2_hmac(
                        "sha256", password.encode(), PASSWORD_SALT, 260000
                    )
                    if not hmac.compare_digest(PASSWORD_HASH, candidate):
                        return self.json_out(401, {"error": "Incorrect editor password"})
                    cookie = (
                        "sd_session="
                        + mk_session()
                        + "; HttpOnly; Path=/; Max-Age=86400; SameSite=Strict"
                        + ("; Secure" if HTTPS else "")
                    )
                    return self.json_out(200, {"ok": True}, {"Set-Cookie": cookie})
                if path == "/api/subscribe":
                    if rate_limit(self.client_address[0]):
                        return self.json_out(429, {"error": "Too many attempts. Try again later."})
                    if not mailer.configured():
                        return self.json_out(
                            503,
                            {
                                "error": "Subscriptions are not available yet. Email delivery is being configured."
                            },
                        )
                    email = email_address(data.get("email", ""))
                    token = secrets.token_urlsafe(32)
                    h = hashlib.sha256(token.encode()).hexdigest()
                    with db.connect() as conn:
                        conn.execute("BEGIN IMMEDIATE")
                        old = conn.execute(
                            "SELECT id,status FROM subscribers WHERE email=?", (email,)
                        ).fetchone()
                        if old and old["status"] == "active":
                            return self.json_out(
                                200,
                                {
                                    "message": "If this address is not already subscribed, a confirmation email has been sent."
                                },
                            )
                        if old:
                            conn.execute(
                                "UPDATE subscribers SET status=?,verify_hash=?,verify_expires=? WHERE id=?",
                                ("pending", h, int(time.time()) + 86400, old["id"]),
                            )
                        else:
                            conn.execute(
                                "INSERT INTO subscribers(email,status,verify_hash,unsubscribe_token,created_at,verify_expires) VALUES(?,?,?,?,?,?)",
                                (
                                    email,
                                    "pending",
                                    h,
                                    secrets.token_urlsafe(32),
                                    db.now(),
                                    int(time.time()) + 86400,
                                ),
                            )
                    try:
                        url = PUBLIC_URL + "/confirm/" + quote(token)
                        mailer.send(
                            email,
                            "Confirm your Signal Daily subscription",
                            "Confirm your subscription by opening: " + url,
                            '<p>Welcome to Signal Daily! Please confirm your subscription:</p><p><a href="'
                            + esc(url)
                            + '">Confirm subscription</a></p>',
                        )
                    except Exception:
                        db.log_operation("confirmation_failed", "SMTP failed; recipient redacted")
                    return self.json_out(
                        200,
                        {
                            "message": "If this address is not already subscribed, a confirmation email has been sent."
                        },
                    )
                if not self.require_admin():
                    return
                if path == "/api/logout":
                    with LOCK:
                        SESSION_EPOCH += 1
                    return self.json_out(
                        200,
                        {"ok": True},
                        {
                            "Set-Cookie": "sd_session=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict"
                            + ("; Secure" if HTTPS else "")
                        },
                    )
                if path == "/api/admin/ingest":
                    topic = data.get("topic", "")
                    feeds.rank_topic([], topic)
                    if not INGEST_LOCK.acquire(blocking=False):
                        raise RuntimeError("Collection is already running")
                    try:
                        incoming, errors = feeds.fetch_all()
                        count = db.insert_stories(incoming)
                        db.log_operation("ingestion", f"{count} added; {len(errors)} feed errors")
                    finally:
                        INGEST_LOCK.release()
                    matches = feeds.rank_topic(
                        [s for s in db.get_stories(200) if feeds.relevant_recent(s)], topic
                    )
                    return self.json_out(
                        200,
                        {
                            "ok": True,
                            "added": count,
                            "found": len(incoming),
                            "errors": errors,
                            "matching_ids": [s["id"] for s in matches],
                            "relevant": len(matches),
                        },
                    )
                if path == "/api/admin/draft":
                    default_generation = "false" if os.getenv("APP_ENV") == "production" else "true"
                    if os.getenv("ENABLE_LOCAL_GENERATION", default_generation).lower() != "true":
                        raise RuntimeError(
                            "Generate JSON on your laptop and import it into the editor"
                        )
                    selected = data.get("story_ids")
                    all_stories = [s for s in db.get_stories(200) if feeds.relevant_recent(s)]
                    topic = data.get("topic", "")
                    all_stories = feeds.rank_topic(all_stories, topic)
                    if isinstance(selected, list) and selected:
                        ids = set(int(x) for x in selected[:12])
                        all_stories = [s for s in all_stories if s["id"] in ids]
                    result = (
                        llm.generate(all_stories[:8], topic=topic)
                        if topic
                        else llm.generate(all_stories[:8])
                    )
                    validated = verify_issue(result)
                    issue_id = db.create_issue(validated)
                    return self.json_out(
                        200,
                        {
                            "ok": True,
                            "issue_id": issue_id,
                            "issue": db.get_issue(issue_id=issue_id),
                        },
                    )
                if path == "/api/admin/manual" or path == "/api/admin/import":
                    payload = verify_issue(data, complete=path == "/api/admin/import")
                    issue_id = db.create_issue(payload)
                    return self.json_out(200, {"ok": True, "issue_id": issue_id})
                match = re.fullmatch(
                    r"/api/admin/issue/(\d+)/(save|review|revise|approve|publish|send)", path
                )
                if match:
                    issue_id = int(match.group(1))
                    action = match.group(2)
                    if action == "save":
                        db.update_issue(
                            issue_id, {**verify_issue(data), "version": data.get("version")}
                        )
                        return self.json_out(200, {"ok": True})
                    if action == "review":
                        db.review(issue_id)
                        return self.json_out(200, {"ok": True})
                    if action == "revise":
                        db.revise(issue_id)
                        return self.json_out(200, {"ok": True})
                    if action == "approve":
                        db.approve(issue_id, data.get("version"))
                        return self.json_out(200, {"ok": True})
                    if action == "publish":
                        db.publish(issue_id, data.get("version"))
                        result = (
                            self.deliver(issue_id)
                            if mailer.configured()
                            else {
                                "sent": 0,
                                "failed": 0,
                                "note": "Published online. SMTP not configured; no emails were sent.",
                            }
                        )
                        return self.json_out(200, {"ok": True, **result})
                    if action == "send":
                        issue = db.get_issue(issue_id=issue_id)
                        if not issue or issue["status"] != "published":
                            raise ValueError("Publish the edition before sending emails")
                        if not mailer.configured():
                            raise ValueError("SMTP is not configured")
                        return self.json_out(200, {"ok": True, **self.deliver(issue_id)})
                return self.json_out(404, {"error": "Unknown API endpoint"})
            except (ValueError, TypeError, KeyError, UnicodeError) as exc:
                return self.json_out(400, {"error": str(exc)[:400]})
            except RuntimeError as exc:
                return self.json_out(503, {"error": str(exc)[:400]})
            except Exception as exc:
                print("Request error:", type(exc).__name__, file=sys.stderr)
                return self.json_out(
                    500, {"error": "Internal server error. Check the server logs."}
                )
        return self.send(404, "Not found", "text/plain")

    def deliver(self, issue_id):
        issue = db.get_issue(issue_id=issue_id)
        if not issue or issue["status"] != "published":
            raise ValueError("Publish the approved edition first")
        sent = 0
        failed = 0
        uncertain = 0
        limit = min(100, max(1, int(os.getenv("DELIVERY_BATCH_SIZE", "25"))))
        for subscriber in db.delivery_targets(issue_id, limit):
            if not db.claim_delivery(issue_id, subscriber["id"]):
                continue
            try:
                # Recheck consent immediately before dispatch; an in-flight SMTP message cannot be recalled.
                with db.connect() as conn:
                    active = conn.execute(
                        "SELECT 1 FROM subscribers WHERE id=? AND status='active'",
                        (subscriber["id"],),
                    ).fetchone()
                if not active:
                    db.record_delivery(
                        issue_id, subscriber["id"], "failed", "Consent withdrawn before send"
                    )
                    continue
                mailer.email_issue(issue, subscriber, PUBLIC_URL)
            except mailer.DeliveryUncertain:
                db.record_delivery(
                    issue_id,
                    subscriber["id"],
                    "uncertain",
                    "SMTP result uncertain; reconcile provider logs before retry",
                )
                uncertain += 1
            except Exception as exc:
                db.record_delivery(issue_id, subscriber["id"], "failed", type(exc).__name__)
                failed += 1
            else:
                # A failed ledger write after SMTP acceptance must retain 'sending', never become retryable.
                db.record_delivery(issue_id, subscriber["id"], "sent")
                sent += 1
        remaining = db.delivery_target_count(issue_id)
        db.log_operation(
            "delivery", f"issue={issue_id}; sent={sent}; failed={failed}; uncertain={uncertain}"
        )
        return {
            "sent": sent,
            "failed": failed,
            "uncertain": uncertain,
            "remaining": remaining,
            "note": "Retry failed/pending deliveries. Interrupted/uncertain sends require provider-log reconciliation.",
        }


def validate_config():
    if os.getenv("APP_ENV", "development") not in ("development", "production"):
        raise ValueError("APP_ENV must be development or production")
    if not valid_url(PUBLIC_URL):
        raise ValueError("PUBLIC_URL must be an HTTP(S) origin")
    p = urlparse(PUBLIC_URL)
    if p.path not in ("", "/") or p.query or p.fragment:
        raise ValueError("PUBLIC_URL must have no path, query or fragment")
    production = os.getenv("APP_ENV", "development") == "production"
    for key in ("ADMIN_PASSWORD", "SESSION_SECRET"):
        value = os.getenv(key, "")
        if value.startswith("replace-with-"):
            raise ValueError(f"Replace the {key} placeholder before starting")
        if production and len(value) < (16 if key == "ADMIN_PASSWORD" else 32):
            raise ValueError(f"Production {key} is missing or too short")
    if production and (not HTTPS or p.hostname in ("localhost", "127.0.0.1")):
        raise ValueError("Production requires an HTTPS public origin")
    if production and os.getenv("ENABLE_LOCAL_GENERATION", "false").lower() != "false":
        raise ValueError("Production must disable local generation; use authenticated JSON import")
    mailer.validate_config()


class BoundedHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, *args, **kwargs):
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(*args, **kwargs)

    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.slots.release()


def main():
    if os.getenv("APP_ENV", "development") == "production":
        raise RuntimeError("Use python production.py behind an HTTPS reverse proxy in production")
    validate_config()
    if "ADMIN_PASSWORD" not in os.environ:
        print(
            "IMPORTANT: No ADMIN_PASSWORD set. Temporary editor password (restart resets):",
            ADMIN_PASSWORD,
            flush=True,
        )
    print(
        f"Signal Daily listening on http://{HOST}:{PORT} (public base URL {PUBLIC_URL})", flush=True
    )
    print(f"Gemma / Ollama: {llm.OLLAMA_MODEL} at {llm.OLLAMA_URL}", flush=True)
    if not mailer.configured():
        print(
            "Email is not configured; public subscriptions disabled until SMTP_HOST + MAIL_FROM are set.",
            flush=True,
        )
    from instance import instance_lock

    with instance_lock(db.DB_PATH):
        db.init()
        BoundedHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
