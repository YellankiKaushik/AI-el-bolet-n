# Implementation report

> Historical local-engineering audit, recorded before GitHub publication. See [the publication report](GITHUB_PUBLICATION_REPORT.md) for the later Git operations and verification.

Audit date: 2026-10-19 (Asia/Calcutta). Scope: `signal-daily`; sibling `rea-main` was inspected without source changes.

## Initial condition

The workspace contained two extracted directories and no Git repository. Signal Daily already had a dependency-free Python HTTP application, SQLite, public pages and CSS, a JavaScript editor, RSS/Atom parsing, a basic Ollama client, SMTP, a local JSON generator, Docker files and five tests. There was no existing `.env` or runtime database in the initial application listing. The original model default was `gemma3:4b`, which did not match the installed model inventory.

The five baseline tests passed after using the bundled Python and enabling loopback networking. The Windows Store Python alias was inaccessible; the Python launcher reported no registered installations. Restricted-agent temporary directories and socket permissions initially prevented meaningful test execution. These were environment failures, separately recorded in TEST_REPORT.md.

## Implemented and repaired

- Preserved the original green/pink editorial visual design, homepage, public edition pages and responsive layout.
- Added server-side archive title/introduction search, topic filters and pagination. Search works without JavaScript, and empty results are explicit.
- Added social title metadata, robots.txt, a published-only sitemap, skip navigation, focus outlines, reduced-motion support, labels for dynamic fields and versioned static assets.
- Centralized bounded validation for email addresses, HTTP(S) source URLs and draft fields. Imports must be complete; manually started drafts may be incomplete until review.
- Added the explicit `draft → review → approved → published` gate. Only authenticated administrators can mutate editions. Revisions and saves reset approval. Published editions are immutable.
- Added draft previews, collected-source evidence, topic editing and edition history. The editor blocks approval/publication after unsaved edits and sends the loaded version on saves.
- Added transactional SQLite schema migration version 1, preserving original edition/subscriber/delivery records. Added `issue_events`, operational logs, topic/version fields, confirmation expiry and delivery reservations. Legacy pending tokens with no expiry become invalid and must be reissued.
- Configured actual installed `gemma4:e4b`. Generation has one in-flight request per service, finite context/output/response bounds, timeout handling, a reusable prompt and JSON output schema. Loopback-only connection avoids exposing or depending on the laptop from a remote host.
- Generation rejects unknown or duplicate story IDs, missing structured fields, inline model-generated URLs and unsupported numerical claims in story headlines/summaries. The application attaches source URLs and provenance from the selected input records.
- RSS collection supports bounded retries, a collection deadline, relevance/recency filtering, URL normalization and deduplication, primary-source metadata and partial-failure reporting. Public HTTPS validation covers initial feed URLs and redirect targets. UTF-8, size, DTD/entity and NUL checks precede XML parsing.
- Added a one-shot ingestion CLI for scheduler use. It cannot publish or email.
- Added login throttling, bounded request workers, socket/body limits, production configuration checks, expiring HMAC sessions, logout invalidation, no-store token pages and token-log redaction. Subscriber responses are generic; addresses remain private.
- Double opt-in uses hashed one-time 24-hour confirmation tokens. Repeat subscriptions preserve existing unsubscribe links. Unsubscribe GET asks for confirmation; POST changes consent.
- SMTP has HTML/plain-text alternatives, TLS, source links and unsubscribe headers. SQLite atomically reserves each edition/subscriber delivery across concurrent requests; safe failures are retryable, sent/in-flight/uncertain sends are excluded. A ledger failure after SMTP acceptance remains non-retryable until reconciled.
- Expanded unit/integration coverage to 56 tests, added lint/format/security/dependency checks and Windows/Linux CI configuration.
- Created a private ignored `.env` with random credentials using an exclusive-create setup script. No existing secret was overwritten or printed.
- Initialized local Git branch `main`; no remote repository, commit, push, deployment or real bulk send was performed.

## Architecture decisions

Retained Python standard library + SQLite because the existing architecture supported the requested local workflow without a migration to a new service. Shared validation lives in `validation.py`; `.env` ownership lives in `config.py`; database transitions and delivery reservations live in `db.py`. SQL values are parameterized. Review/publication transitions use SQLite write transactions.

The public host stays online independently of the laptop. The laptop generates source-grounded JSON locally; an editor imports it over the hosted HTTPS administrator session. This preserves a private model endpoint and explicit editorial control. No paid cloud AI path exists.

SMTP does not provide an exactly-once distributed transaction with SQLite. The implementation favors preventing duplicate delivery: ambiguous sends require manual provider-log reconciliation. Small synchronous batches are retained; a durable delivery queue is a future scaling change.

## Real integrations and storage

Ollama `/api/tags` returned `gemma4:e4b` and `gemma4-lab:latest`; the base tag's reported total parameter size was 8.0B. Four live configured feeds yielded 19 relevant recent records, no feed errors. The first actual local generation produced two validated stories in 52.84 seconds. `integration-evidence.json` records the final-validator recheck as well.

Database initialization, legacy migration, foreign keys, persistence, concurrency, workflow transitions, subscriptions and delivery ledger behavior were tested on real temporary SQLite files. Browser checks used an isolated fixture database. No user edition or subscriber was published or mailed. The generated real-model draft remains ignored under `local-drafts/`. The safe collection CLI was also executed against the actual local database: 19 source records and one real Gemma edition are stored for review, with status `draft`, zero published editions and zero active subscribers.

## Significant files

Modified: `db.py`, `server.py`, `feeds.py`, `llm.py`, `mailer.py`, `run.py`, `static/app.js`, `static/style.css`, `tools/local_generate.py`, original tests, `.env.example`, `.gitignore`, `.dockerignore`, README and CI workflow.

Created: `validation.py`, `config.py`, `tools/collect_news.py`, `tools/setup_local.py`, `tools/release_audit.py`, `tools/audit_dependencies.py`, `tests/test_release.py`, `pyproject.toml`, `requirements-dev.txt`, `.gitattributes`, the six engineering reports and verification artifacts/screenshots.

Existing preview PNGs and `docs/REA-CODEX-WORKFLOW.md` were preserved. No `rea-main` file was edited.

## Deferred and production-dependent work

Live SMTP credentials and sender DNS, a deployed HTTPS host, backup/restore drills, mail-client acceptance testing, load testing, bounce/complaint handling and production edge hardening remain prerequisites for launch. REA captures were not run because its compiled runtime/dependencies are absent. No OS scheduler was installed. There is no automatic cloud upload, distributed queue, multi-editor role system, account recovery, analytics or scheduled publication. See the full issue table for these limits.
