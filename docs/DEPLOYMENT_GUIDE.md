# Deployment guide

Date: 2026-10-19. Source readiness and a live production launch are separate. This application has not been deployed.

## Windows local installation

Use Python 3.11+ and SQLite (bundled with Python). No pip packages are needed to run the service. Work from the `signal-daily` folder. Git is needed for the release audit; Node is only needed for the JavaScript syntax check.

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
| HOST / PORT | Defaults `127.0.0.1:8787`. Container binds internally to all interfaces; compose exposes only host loopback. |
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

Use one persistent Python service/container behind an HTTPS reverse proxy on a host you control. Keep SQLite on a private durable disk with backups. Keep SMTP outbound only. Configure request/body/connection/time limits and IP-based throttling at the proxy. The app deliberately ignores untrusted forwarded client headers; behind a proxy its built-in limits may treat clients as one proxy address, so edge throttling is important.

The bounded standard-library HTTP server is suitable for local validation and a small controlled pilot, not a verified production server. Python's [http.server documentation](https://docs.python.org/3.12/library/http.server.html) advises against production use. Harden or replace the serving layer and perform representative load/security checks before launch. No production throughput or availability claim was tested.

The supplied Dockerfile uses an unprivileged service user. Compose binds host `127.0.0.1:8787` and mounts the `signal_data` volume at `/data`. Before any future deployment, configure `APP_ENV=production`, your HTTPS `PUBLIC_URL`, secrets, SMTP and a reverse proxy. Then, only after deployment authorization:

```powershell
docker compose up -d --build
```

Docker was absent from PATH during this audit, so image build and runtime are NOT VERIFIED. Do not use an ephemeral/serverless filesystem for this SQLite architecture. Multiple service processes would require shared sessions/rate limits and a delivery worker design; only one application instance is supported here.

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

Feed URL checks reject private resolved addresses/redirects. Because configuration is operator-controlled, this is defense in depth; enforce outbound network policy against DNS rebinding and local infrastructure in a public environment. No arbitrary reader-supplied URL is fetched.

## GitHub preparation

Run the README's test/lint/format/compile/security commands and `python tools/release_audit.py`. Check ignore rules for `.env*`, database/WAL files, local drafts and temporary tooling. Review all source candidates. The publication history and target remote are recorded in [GITHUB_PUBLICATION_REPORT.md](GITHUB_PUBLICATION_REPORT.md). Commit and push future changes only when authorized. Never add database files, drafts or actual secrets to the repository.
