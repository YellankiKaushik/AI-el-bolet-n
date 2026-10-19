"""Create private local configuration once. Never overwrite a user's existing .env."""

import os
import secrets
from pathlib import Path


def create_config(root):
    root = Path(root)
    content = (root / ".env.example").read_text(encoding="utf-8-sig")
    content = content.replace("replace-with-a-strong-unique-password", secrets.token_urlsafe(24))
    content = content.replace("replace-with-a-long-random-secret", secrets.token_urlsafe(48))
    descriptor = os.open(root / ".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)


if __name__ == "__main__":
    try:
        create_config(Path(__file__).resolve().parents[1])
    except FileExistsError:
        print("Existing .env preserved. Review its configuration locally.")
    else:
        print(
            "Created ignored .env with random editor credentials. Read it locally; keep it private."
        )
