# Agent instructions for Codex

This directory is **Signal Daily**, a standalone Python newsletter product. It is not the source directory for `morluto/rea`.

## User goal
- Use a **locally installed** Gemma 4B-class model through Ollama to draft AI newsletters from current RSS/Atom source descriptions.
- The editor must **review and explicitly approve** each edition before publication.
- Make published editions accessible on a website, collect verified email subscribers, and notify them when editions publish.
- Take inspiration from public capabilities of The Rundown AI; retain independent visual design and original text.

## Operational rules
1. Read README.md and `docs/REA-CODEX-WORKFLOW.md` first.
2. Run `python -m unittest discover -s tests -v` before and after changes.
3. Keep real credentials in `.env`; never commit them or log SMTP passwords.
4. Do not remove the `draft â†’ approved â†’ published` gate or introduce automatic publishing without explicit user approval.
5. Do not infer unpublished facts from a local LLM. Keep source references and prompt grounding.
6. If running the website on a remote server, leave local Ollama private and use the JSON import workflow (`tools/local_generate.py`).
7. Use REA only for authorized/passive observation of a target's publicly visible behavior; distinguish evidence from inference. Do not assert private backend analysis that has not happened.
8. Do not deploy or send to real subscribers until the user has approved the content and deployment configuration.

## Useful entry points
- `run.py` reads `.env` then starts `server.py`.
- `server.py` serves HTML/CSS/JS plus JSON APIs.
- `db.py` has SQLite schema, approval logic and idempotent delivery rows.
- `feeds.py` parses RSS/Atom.
- `llm.py` calls local Ollama `/api/chat`.
- `mailer.py` handles SMTP confirmation and issues.
- `static/` holds public site and editor UI.

## Acceptance criteria
- Public site and archive render correctly on desktop/mobile.
- Source ingestion reports failing feeds without fabricating articles.
- New drafts can be edited and cannot publish until approved.
- Editing an approved issue resets it to draft.
- Newsletter emails go only to active, opt-in subscribers, at most once per issue unless previous delivery failed.
- Unsubscribe page requires confirmation POST.
- HTTPS, secrets, SMTP, persistent storage, backups, and sender authentication are configured before public launch.
