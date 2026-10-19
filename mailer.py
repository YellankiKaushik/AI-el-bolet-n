"""Transactional SMTP for verification and subscriber delivery."""

import html
import os
import smtplib
import ssl
from contextlib import contextmanager
from email.message import EmailMessage
from email.utils import parseaddr
from urllib.parse import quote
from validation import verify_issue, email_address


class DeliveryUncertain(RuntimeError):
    """Transport failed during DATA; retrying could duplicate an accepted email."""


@contextmanager
def smtp_session(client):
    try:
        yield client
    finally:
        # Failure during QUIT must not turn a known accepted DATA into a retryable failure.
        try:
            client.quit()
        except (OSError, smtplib.SMTPException):
            try:
                client.close()
            except (OSError, smtplib.SMTPException):
                pass


def transmit(smtp, message):
    try:
        smtp.send_message(message)
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused, smtplib.SMTPDataError):
        raise
    except (OSError, smtplib.SMTPServerDisconnected) as exc:
        raise DeliveryUncertain("SMTP acceptance is unknown") from exc


def configured():
    default = "false" if os.getenv("APP_ENV") == "production" else "true"
    return os.getenv("EMAIL_DELIVERY_ENABLED", default).lower() == "true" and bool(
        os.getenv("SMTP_HOST") and os.getenv("MAIL_FROM")
    )


def validate_config():
    for key in ("EMAIL_DELIVERY_ENABLED", "SMTP_SSL"):
        if key in os.environ and os.environ[key].lower() not in ("true", "false"):
            raise ValueError(f"{key} must be true or false")
    default = "false" if os.getenv("APP_ENV") == "production" else "true"
    enabled = os.getenv("EMAIL_DELIVERY_ENABLED", default).lower() == "true"
    if not enabled:
        return
    if not os.getenv("SMTP_HOST") and not os.getenv("MAIL_FROM"):
        if os.getenv("APP_ENV") == "production":
            raise ValueError("Enabled production email requires SMTP_HOST and MAIL_FROM")
        return
    if not os.getenv("SMTP_HOST") or not os.getenv("MAIL_FROM"):
        raise ValueError("SMTP_HOST and MAIL_FROM must be configured together")
    host = os.environ["SMTP_HOST"]
    if any(char.isspace() for char in host) or "://" in host:
        raise ValueError("SMTP_HOST must be a hostname")
    sender = os.environ["MAIL_FROM"]
    if "\r" in sender or "\n" in sender:
        raise ValueError("Invalid MAIL_FROM")
    email_address(parseaddr(sender)[1])
    if bool(os.getenv("SMTP_USER")) != bool(os.getenv("SMTP_PASSWORD")):
        raise ValueError("SMTP_USER and SMTP_PASSWORD must be configured together")
    port = int(os.getenv("SMTP_PORT", "587"))
    implicit = os.getenv("SMTP_SSL", "false").lower() == "true" or port in (465, 2465)
    if port not in (465, 587, 2465, 2587):
        raise ValueError("Use a supported TLS SMTP port: 465, 587, 2465 or 2587")
    if implicit and port in (587, 2587):
        raise ValueError("STARTTLS ports require SMTP_SSL=false")


def send(to, subject, text, html_part="", unsubscribe_url=""):
    validate_config()
    if not configured():
        raise RuntimeError("Email is not configured: SMTP_HOST and MAIL_FROM are required")
    email_address(to)
    msg = EmailMessage()
    msg["From"] = os.getenv("MAIL_FROM")
    msg["To"] = to
    msg["Subject"] = subject.replace("\r", " ").replace("\n", " ")[:200]
    if unsubscribe_url:
        msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.set_content(text)
    if html_part:
        msg.add_alternative(html_part, subtype="html")
    host = os.environ["SMTP_HOST"]
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD", "")
    timeout = 20
    if os.getenv("SMTP_SSL", "false").lower() == "true" or port in (465, 2465):
        with smtp_session(
            smtplib.SMTP_SSL(host, port, timeout=timeout, context=ssl.create_default_context())
        ) as s:
            if username:
                s.login(username, password)
            transmit(s, msg)
    else:
        with smtp_session(smtplib.SMTP(host, port, timeout=timeout)) as s:
            s.ehlo()
            s.starttls(context=ssl.create_default_context())
            s.ehlo()
            if username:
                s.login(username, password)
            transmit(s, msg)


def email_issue(issue, subscriber, base_url):
    if issue.get("status") != "published":
        raise ValueError("Only approved, published editions may be emailed")
    verify_issue(issue, complete=True)
    unsub = base_url.rstrip("/") + "/unsubscribe/" + quote(subscriber["unsubscribe_token"])
    link = base_url.rstrip("/") + "/issue/" + quote(issue["slug"])
    lines = [issue["title"], "", issue["intro"], ""]
    segments = [f"<h1>{html.escape(issue['title'])}</h1>", f"<p>{html.escape(issue['intro'])}</p>"]
    for idx, item in enumerate(issue["items"], 1):
        lines += [
            f"{idx}. {item['headline']}",
            item["summary"],
            "Why it matters: " + item.get("why", ""),
            "Source: " + item["url"],
            "",
        ]
        source_url = html.escape(item["url"], quote=True)
        segments += [
            f"<h2>{idx}. {html.escape(item['headline'])}</h2>",
            f"<p>{html.escape(item['summary'])}</p>",
            f"<p><strong>Why it matters:</strong> {html.escape(item.get('why', ''))}</p>",
            f'<a href="{source_url}">Original source</a>',
        ]
    lines += [issue.get("closing", ""), "Read online: " + link, "Unsubscribe: " + unsub]
    segments += [
        f"<p>{html.escape(issue.get('closing', ''))}</p>",
        f'<p><a href="{html.escape(link, quote=True)}">Read online</a></p>',
        f'<p><a href="{html.escape(unsub, quote=True)}">Unsubscribe</a></p>',
    ]
    html_doc = (
        '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;padding:20px;line-height:1.65;color:#18272b">'
        + "".join(segments)
        + "</body></html>"
    )
    send(subscriber["email"], issue["subject"], "\n".join(lines), html_doc, unsub)
