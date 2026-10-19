"""Check repository Markdown links/anchors and screenshot manifests without network access."""

import hashlib
import json
import re
import shutil
import struct
import subprocess  # nosec B404
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.targets.append(value)


def targets(text):
    text = re.sub(r"```[\s\S]*?```", "", text)
    found = [
        match[0] or match[1]
        for match in re.findall(
            r'!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+"[^"]*")?\s*\)', text
        )
    ]
    found.extend(re.findall(r"^\s*\[[^\]]+\]:\s*(\S+)", text, re.MULTILINE))
    parser = Links()
    parser.feed(text)
    return set(found + parser.targets)


def anchors(text):
    used = {}
    result = set()
    text = re.sub(r"```[\s\S]*?```", "", text)
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.MULTILINE):
        slug = unicodedata.normalize("NFC", heading).lower()
        slug = re.sub(r"[^\w\- ]", "", slug).replace(" ", "-")
        count = used.get(slug, 0)
        used[slug] = count + 1
        result.add(slug + (f"-{count}" if count else ""))
    return result


def check_link(source, target, root):
    parts = urlsplit(target)
    if parts.scheme in ("https", "http", "mailto", "data") or target.startswith("//"):
        return None
    destination = (source.parent / unquote(parts.path)).resolve() if parts.path else source
    if not destination.is_relative_to(root.resolve()):
        return "link leaves repository"
    if not destination.exists():
        return "missing local target"
    if parts.fragment and destination.suffix.lower() == ".md":
        if unquote(parts.fragment) not in anchors(destination.read_text(encoding="utf-8-sig")):
            return "missing Markdown heading anchor"
    return None


def audit():
    git = shutil.which("git")
    if not git:
        raise RuntimeError("Git is required for the repository documentation inventory")
    # Fixed developer-only command; no shell and no caller-supplied options.
    result = subprocess.run(
        [git, "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )  # nosec B603
    files = sorted({name for name in result.stdout.decode().split("\0") if name.endswith(".md")})
    failures = []
    local_links = 0
    for name in files:
        source = ROOT / name
        if not source.exists():
            continue  # Removed tracked paths can remain in an unstaged worktree diff.
        for target in targets(source.read_text(encoding="utf-8-sig")):
            if urlsplit(target).scheme in ("https", "http", "mailto", "data"):
                continue
            local_links += 1
            failure = check_link(source, target, ROOT)
            if failure:
                failures.append({"file": name, "target": target, "error": failure})
    manifest_path = ROOT / "docs/screenshots/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required = {
        "homepage-desktop.png",
        "homepage-mobile.png",
        "editor-dashboard.png",
        "newsletter-editor.png",
        "newsletter-preview.png",
        "published-edition.png",
    }
    if {item["file"] for item in manifest["images"]} != required:
        failures.append({"error": "screenshot manifest does not contain the six required images"})
    for item in manifest["images"]:
        path = manifest_path.parent / item["file"]
        if not path.exists():
            failures.append({"file": str(path.relative_to(ROOT)), "error": "screenshot missing"})
            continue
        raw = path.read_bytes()
        if raw[:8] != b"\x89PNG\r\n\x1a\n" or len(raw) < 24:
            failures.append({"file": item["file"], "error": "invalid PNG header"})
            continue
        width, height = struct.unpack(">II", raw[16:24])
        if (
            (width, height) != (item["width"], item["height"])
            or len(raw) != item["bytes"]
            or hashlib.sha256(raw).hexdigest() != item["sha256"]
        ):
            failures.append({"file": item["file"], "error": "screenshot metadata/hash mismatch"})
    report = {
        "markdown_files": len(files),
        "local_links_checked": local_links,
        "screenshots_checked": len(manifest["images"]),
        "findings": failures,
        "scope": "Local links/heading anchors and PNG manifest integrity; external URLs/rendering checked separately",
    }
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    raise SystemExit(bool(audit()["findings"]))
