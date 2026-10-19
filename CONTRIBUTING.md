# Contributing to Signal Daily

Keep local AI private, preserve human editorial control and make changes easy to verify. Read [README.md](README.md), [AGENTS.md](AGENTS.md), [architecture](docs/ARCHITECTURE.md) and [project status](docs/PROJECT_STATUS.md) before changing behavior.

## Development setup

Use Python 3.11/3.12 (the CI matrix), Git and optional Node for JavaScript checks. From a fresh clone:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe tools/setup_local.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
git switch -c describe-your-change
```

Virtual-environment activation is optional. Use the actual executable if `py` is not registered. No model/SMTP credentials are needed for automated tests. Ollama and an installed model are required only for an intentional real local generation check; keep its result unapproved. Never download weights, contact paid providers or send mail as a side effect of running the suite.

## Code organization

`server.py` shares public/editor business routes across local HTTP and production WSGI. `db.py` owns transactional state and migrations; `validation.py` validates at boundaries. `feeds.py`, `llm.py` and `mailer.py` own their external-service contracts. Plain browser assets are in `static/`. Tools and isolated tests live in their own directories. [Detailed inventory](docs/ARCHITECTURE.md).

Keep the current stack unless a change has a demonstrated need. Preserve source provenance, foreign keys and delivery reservations. Changes to an approved edition must reset it to draft. Never introduce automatic approval/publication of real content or retry an uncertain SMTP claim blindly. Do not load real `.env`/private data while importing test modules. Test transports should remain mocks or intentionally isolated local services.

## Required checks

Run the commands in [README testing](README.md#tests), including unit/HTTP tests, Ruff lint/format, compilation, Node syntax, Bandit, `tools/check_docs.py` and `tools/release_audit.py`. Run OSV when pinned package versions change. Treat every failure honestly; record unsupported environments rather than fabricating coverage. Tests should exercise behavior/invariants, including meaningful failure cases, without duplicating implementation details.

Use the [manual testing guide](docs/LOCAL_TESTING_GUIDE.md) for browser changes. Repeated approval/publication must use the fictional acceptance workspace. The [screenshot guide](docs/screenshots/README.md) describes reproducible real captures; never replace them with mockups or real private drafts. Playwright/Sharp/Mermaid tooling is optional and does not belong in production dependencies.

## Pull requests and commits

- Keep changes focused and use meaningful commits describing actual work.
- Explain the concrete problem, resulting behavior, checks run and material limitations. Include synthetic before/after evidence when it helps review.
- Update user/configuration/architecture docs when behavior changes; use the exact current UI labels.
- Preserve existing history and unrelated work. Do not force-push shared/published history.
- Never stage `.env`, databases/WAL, backups, private JSON drafts, subscriber details, model weights, logs or browser profiles. Review staged paths and diff in addition to running the candidate audit.
- Keep historical reports as dated evidence; add a pointer to current status instead of changing old results to look new.

The repository's CI checks Windows/Linux on Python 3.11/3.12. A local test count or green run for an older commit does not substitute for the new commit's matrix. Public hosting, real SMTP and model behavior require separate acceptance evidence.

## Security reporting

Do not put live credentials, subscriber data, token links or exploit payloads exposing a user into a public issue. Use GitHub private vulnerability reporting **if the repository advertises it**. No dedicated security email/channel is asserted by these docs; if none is available, request a private contact through a minimal public issue without sensitive details. Follow the maintainer's private instructions only after a suitable channel exists. Rotate any accidentally disclosed credentials promptly and preserve private evidence; do not post more secrets to explain the leak.

## Licensing and attribution

Preserve [LICENSE](LICENSE), [LICENSES/Signal-Daily-MIT.txt](LICENSES/Signal-Daily-MIT.txt) and [NOTICE](NOTICE). Their provenance is documented; do not relabel the whole tree with an unsupported blanket license grant. Use original project assets and properly licensed contributions. REA is an optional separate investigation tool; do not claim it is a runtime dependency or that private third-party systems were reverse engineered.
