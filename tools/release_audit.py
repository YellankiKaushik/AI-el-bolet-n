"""Audit Git's push candidates without printing secret contents."""

import json
import re
import subprocess  # nosec B404
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b"),
)


def audit():
    git = shutil.which("git")
    if not git:
        raise RuntimeError("Install Git before running the release audit")
    # Developer-only command: resolved executable, fixed arguments, no shell or caller-supplied options.
    result = subprocess.run(  # nosec B603
        [git, "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    candidates = sorted(set(result.stdout.decode().rstrip("\x00").split("\x00")))
    failures = []
    for name in candidates:
        path = ROOT / name
        parts = Path(name).parts
        if (
            (path.name.startswith(".env") and path.name != ".env.example")
            or path.suffix in (".db", ".sqlite", ".sqlite3", ".key", ".pem")
            or any(p in (".tmp", "data", "backups", "local-drafts", "__pycache__") for p in parts)
        ):
            failures.append(
                {"file": name, "reason": "private or generated file in push candidates"}
            )
        if path.is_file() and path.suffix not in (".png", ".jpg"):
            data = path.read_bytes()
            if any(pattern.search(data) for pattern in PATTERNS):
                failures.append(
                    {"file": name, "reason": "possible credential pattern; inspect privately"}
                )
    required = [
        "server.py",
        "db.py",
        "feeds.py",
        "llm.py",
        "mailer.py",
        "validation.py",
        "config.py",
        "run.py",
        "production.py",
        "instance.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
    ]
    for name in required:
        if not (ROOT / name).is_file():
            failures.append({"file": name, "reason": "essential source missing"})
    evidence = {
        "candidate_count": len(candidates),
        "findings": failures,
        "scope": "Git candidates; known credential signatures and private file rules. Not an exhaustive secret detector.",
    }
    print(json.dumps(evidence, indent=2))
    return evidence


if __name__ == "__main__":
    evidence = audit()
    raise SystemExit(bool(evidence["findings"]))
