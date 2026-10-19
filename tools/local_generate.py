"""Create a newsletter JSON locally using your laptop's Ollama instance.
Usage: python tools/local_generate.py --output edition.json
Optional: python tools/local_generate.py --stories custom_stories.json --output edition.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import load_env

load_env()
import feeds
import llm


def main():
    parser = argparse.ArgumentParser(description="Create a source-grounded AI newsletter locally")
    parser.add_argument(
        "--stories",
        help="A JSON array of stories, each with title,url,description,source and optional id",
    )
    parser.add_argument("--output", default="newsletter-draft.json")
    args = parser.parse_args()
    if args.stories:
        stories = json.loads(Path(args.stories).read_text(encoding="utf-8-sig"))
    else:
        stories, errors = feeds.fetch_all()
        for err in errors:
            print("Feed warning:", err, file=sys.stderr)
    # Preserve full URLs for editorial fact checking.
    for index, story in enumerate(stories):
        story.setdefault("id", index + 1)
    if not stories:
        sys.exit("No stories available. Check your RSS feeds or supply --stories.")
    result = llm.generate(stories[:8])
    path = Path(args.output).resolve()
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Draft written to {path}. Import it into /admin and review before publishing.")


if __name__ == "__main__":
    main()
