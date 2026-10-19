# Deployment guide

Date: 2026-10-19. Source readiness and a live production launch are separate. This application has not been deployed.

Phase 2's [production readiness report](PRODUCTION_READINESS_REPORT.md) and [controlled pilot runbook](PRODUCTION_RUNBOOK.md) contain the current launch gates, Docker rehearsal, backup/restore commands and first-edition instructions.

For portable laptop onboarding and the current release, use [Getting started](GETTING_STARTED.md), [Configuration](CONFIGURATION.md) and [Project status](PROJECT_STATUS.md). Historical audit counts remain in their dated reports.

## Windows local installation

Use Python 3.11+ and SQLite (bundled with Python). Local `run.py` needs no pip packages; `production.py` requires `requirements.txt`. Work from the `signal-daily` folder. Git is needed for the release audit; Node is only needed for the JavaScript syntax check.

```powershell
python tools/setup_local.py
python run.py
```

The setup command exclusively creates `.env` using cryptographically random local credentials; it preserves existing files. A fresh clone includes no `.env`; run the setup command locally. The original development workspace retains its ignored configuration. Read the administrator password locally in that file, without copying it into chats, screenshots or version control.

On this laptop the Store alias was inaccessible and `py --list-paths` was empty. The tested interpreter is:

```powershell
$Python = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $Python run.py
```

Visit `http://localhost:8787` and `/admin`. Close the terminal/server to stop it. The database is initialized automatically and relative database paths resolve under the project. Before upgrading an existing database, stop the app and take a SQLite-consistent backup. Migration version 1 retains existing rows; pending confirmation links from the legacy schema expire and need reissuing.

## Gemma

Run the already installed Ollama application/service. Inspect `/api/tags` or `ollama list` and set the exact `OLLAMA_MODEL`. This machine's tested base tag is `gemma4:e4b`; a custom `gemma4-lab:latest` also exists. Do not run a model-download command unless intentionally changing the local installation.

`OLLAMA_URL=http://127.0.0.1:11434` stays private and must resolve to loopback. `OLLAMA_TIMEOUT` defaults to 240 seconds and is capped at 600. One generation runs at a time; the request bounds context/output and response size. Failure never activates a cloud AI fallback.

Use fetched material, inspect the source evidence, edit, submit for review, approve and explicitly publish. All factual claims need editorial checking: numeric/source/shape validation is not semantic fact verification.

## Environment variables

| Variable | Purpose |
|---|---|
| APP_ENV | `development` locally; set `production` before a public launch. |
| HOST / PORT | Defaults `127.0.0.1:8787`. Production container binds internally; only Caddy publishes ports. |
| PUBLIC_URL | Bare origin, e.g. `https://news.example.org`; no path/query/fragment. Used for confirmation, unsubscribe, sitemap and edition links. |
| ADMIN_PASSWORD | Unique editor password. Production minimum 16 characters; generated local value exceeds this. |
| SESSION_SECRET | Random signing key, at least 32 characters in production. Rotate to invalidate sessions. |
| DATABASE_PATH | Persistent SQLite path. Keep database and backups private. |
| OLLAMA_URL / OLLAMA_MODEL / OLLAMA_TIMEOUT | Local model endpoint/tag/timeout. |
| RSS_FEEDS | Comma-separated `Label|https://feed` entries; defaults are built in. Only public HTTPS feed destinations and UTF-8 XML are supported. |
| RSS_LIMIT / RSS_MAX_AGE_DAYS / RSS_RETRIES | Defaults 80 records, 14 days, one retry. Hard caps prevent unbounded collection. |
| RSS_KEYWORDS | Comma-separated relevance terms; default AI/research vocabulary. |
| DELIVERY_BATCH_SIZE | Default 25; maximum 100 subscribers per action. |
| SMTP_HOST / SMTP_PORT | Provider endpoint; default port 587 with STARTTLS. |
| SMTP_USER / SMTP_PASSWORD | Provider credentials when required; never commit. |
| MAIL_FROM | Verified sender address or display-name mailbox. |
| SMTP_SSL | `true` for implicit TLS; port 465 also enables it. |
| EMAIL_DELIVERY_ENABLED | Explicit `true` required in production; setup defaults false. Gates confirmation and edition mail. |
| ENABLE_LOCAL_GENERATION | False on the host; local laptop generation remains enabled in development. |
| TRUSTED_PROXY | Exact reverse proxy IP; wildcard trust is rejected. Compose uses `172.30.0.2`. |
| PUBLIC_HOST / EDITOR_CIDR | Compose public DNS name and operator IP/VPN range. Default editor range denies remote access. |
| DATABASE_FILE | Optional restored database filename inside Compose's persistent `/data`. |

Environment values supplied by the process take precedence over `.env`. Restart after changes. Placeholder credentials are rejected; production also requires a non-local HTTPS public origin and strong credentials. Local setup does not configure SMTP or hosting.

## Email acceptance and consent

Obtain an SMTP account that permits opt-in newsletter mail, verify the sender/domain, and configure SPF/DKIM/DMARC with that provider. Put credentials only in the private host environment. Test a single mailbox that you control after approving the exact content and configuration. This was not performed during engineering; all test SMTP transports were mocked.

A subscription receives a generic response and a 24-hour one-time confirmation link. SMTP failures are logged without recipient/password details. Check operational logs if a user gets no confirmation. Pending/expired links can be reissued by subscribing again. Only confirmed active subscribers are eligible for editions. Unsubscribe requires confirmation POST; an SMTP message already in flight cannot be recalled.

Delivery reservations are unique per edition/subscriber:

- `sent`: excluded from future sends.
- `failed`: safely retryable through the editor.
- `sending`: process may still be working, or may have stopped after SMTP acceptance.
- `uncertain`: SMTP disconnected while acceptance was ambiguous.

For `sending`/`uncertain`, first stop competing delivery work and inspect provider logs against the edition, recipient and recorded time. Back up the database. Only after proving non-delivery should an operator change that specific ledger row to `failed`; if accepted, record `sent`. No automatic stale-claim retry is provided because it could duplicate mail. There is no claim of exactly-once SMTP delivery.

## Public hosting architecture

Use the current [production runbook](PRODUCTION_RUNBOOK.md): one Waitress process behind Caddy, a private upstream port, HTTPS, editor IP/VPN restrictions and persistent local SQLite storage. Waitress trusts exactly the configured proxy's forwarding headers; production throttles use a SQLite ledger keyed by hashed client identity. Both entry points hold an OS process lock. The development `http.server` entry point refuses production mode. No throughput or availability claim was tested.

The Dockerfile runs as an unprivileged user. Compose adds a read-only application root, capability restrictions, bounded resources, persistent data/certificate volumes and health checks. Docker and Linux are NOT VERIFIED on this machine. Complete the isolated container rehearsal and validate Caddy before separate deployment authorization. Only one application instance is supported; do not use ephemeral storage or multiple writers.

## Keep laptop AI private

The public host cannot reach the laptop through its own `localhost`. Generate locally, then import through authenticated HTTPS:

```powershell
New-Item -ItemType Directory -Force local-drafts
python tools/local_generate.py --output local-drafts/edition.json
```

In the hosted editor choose Import local draft, upload/paste JSON, review, approve and publish. No incoming laptop connection, public Ollama port or insecure tunnel is needed. Automatic authenticated upload/worker polling is deferred; manual authenticated import is the implemented transport.

## Collection schedule, backups and logs

Schedule only `python tools/collect_news.py`; set Task Scheduler's executable, script path and project working directory. No schedule was created automatically. This command cannot approve, publish or send.

Back up SQLite using its backup API or stop the service before copying a WAL database. Include WAL state in a live backup; never copy only the main file during active writes. Encrypt/restrict backups, test restoration and monitor disk space. Host ACLs and backup retention are operator responsibilities. Story/event/operation history currently has no automated retention policy.

Use `python tools/database_backup.py backup SOURCE NEW_BACKUP`, `restore BACKUP NEW_DATABASE`, and `check DATABASE`. Restore refuses overwrites; the runbook explains selecting the restored path while retaining the old database. Phase 2 verified a real backup and separate restoration of the original local database. Migration version 2 adds persistent throttle records without changing editions or consent.

Feed URL checks reject private resolved addresses/redirects. Because configuration is operator-controlled, this is defense in depth; enforce outbound network policy against DNS rebinding and local infrastructure in a public environment. No arbitrary reader-supplied URL is fetched.

## GitHub preparation

Run the README's test/lint/format/compile/security commands and `python tools/release_audit.py`. Check ignore rules for `.env*`, database/WAL files, local drafts and temporary tooling. Review all source candidates. The publication history and target remote are recorded in [GITHUB_PUBLICATION_REPORT.md](GITHUB_PUBLICATION_REPORT.md). Commit and push future changes only when authorized. Never add database files, drafts or actual secrets to the repository.
