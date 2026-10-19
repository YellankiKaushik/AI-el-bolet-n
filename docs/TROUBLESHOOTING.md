# Troubleshooting

Start with the exact URL, selected Python, current branch and visible error. Keep your database and configuration intact. Never fix a startup problem by deleting drafts, publishing real content, disabling tests, exposing Ollama or posting secrets.

## Python not found

**Symptoms:** Store opens, `python` is not recognized, or `py` reports no installed runtime.

Run `py -3 --version` and `python --version`. Install Python from [the official Windows page](https://www.python.org/downloads/windows/) if neither works, then open a new PowerShell window. An existing `py.exe` does not prove a runtime is registered. `Start-Local.ps1` probes candidates and can use `SIGNAL_DAILY_PYTHON` set to an actual executable. Use `.\.venv\Scripts\python.exe` directly for a virtual environment; activation is optional. The original laptop's pre-existing Codex fallback is documented in [getting started](GETTING_STARTED.md), not required for ordinary installations.

## Port 8787 already occupied

**Symptoms:** bind/address-in-use error, or a second instance reports the database is in use.

```powershell
Get-NetTCPConnection -LocalPort 8787 -State Listen
```

Inspect the returned owning process before doing anything. If the existing Signal Daily page works, use that server. Stop the known server with Ctrl+C in its terminal; do not kill unrelated Python processes. A lock file's existence alone does not mean the lock is held; OS locks release after process death. Never delete a lock file to bypass a live process. For separate tests, use `tools/demo.py --name acceptance --port 8790 --empty`.

## PowerShell blocks the launcher

Use the direct-interpreter commands in [getting started](GETTING_STARTED.md#5-start-signal-daily). Do not weaken execution policy, firewall rules or endpoint protection. Run from the root containing `run.py`. The launcher creates `.env` only if missing and forces mail off; it never prints existing administrator credentials.

## Ollama not running

**Symptoms:** local generation reports a failed Ollama request or connection refused.

Open the installed Ollama application. Check `Invoke-RestMethod http://127.0.0.1:11434/api/tags`. If no service is listening, `ollama serve` can run it in another terminal; if it already responds, don't launch a duplicate. Keep `OLLAMA_URL=http://127.0.0.1:11434`. Never solve this by opening port 11434 to the internet or adding a cloud fallback.

## Gemma model not found

Run `ollama list` or inspect `/api/tags`; use the exact local identifier in `.env`, then restart Signal Daily. The tested tag is `gemma4:e4b`, but availability can differ. Only deliberately download weights if needed using the official catalog; do not choose a `:cloud` tag for this local workflow. The app does not auto-install a model. [Model setup](GETTING_STARTED.md#4-start-ollama-and-select-a-local-model).

## Newsletter generation timeout or invalid output

One request runs at a time. Wait for it to finish; **Another generation is running** is a guard, not a second job. Check Ollama status/memory, select fewer useful source records and increase `OLLAMA_TIMEOUT` deliberately if necessary (5–600 seconds, default 240). A cold model can be slower than a warm one. No hardware speed is guaranteed.

A JSON/source/numeric validation error means the response was rejected safely. Preserve previous drafts; try different source descriptions or regenerate after the active request finishes. Do not remove validation or approve malformed output. The JSON CLI now refuses an existing output file—choose a new filename. It creates missing parent folders itself.

Generation is intentionally disabled inside `tools/demo.py` and production mode. Use the real laptop app for unapproved real generation, or the local JSON tool with source inputs, then import. Demo publication tests should use the checked-in fictional fixture.

## RSS errors or zero new records

Zero additions with no errors often means deduplication. Check **Source feed**, source dates, keyword filters and your clock. Feeds may fail temporarily, rate-limit readers, publish no relevant current records or use unsupported XML. Inspect source-specific error types, check internet/DNS, and correct trusted `RSS_FEEDS` URLs if required. Partial successes remain usable; the collector does not fabricate replacements. Only public HTTPS destinations, bounded UTF-8 XML and configured relevance/age windows are supported.

## Administrator login problems

Open the correct app/port and privately check its credentials file: normal app uses `.env`; demo uses its separate `.tmp/NAME/credentials.json`. No username is required. Process environment overrides `.env`. Restart after intended config changes; restarts invalidate old sessions. Wrong attempts are limited to ten per client IP per 15 minutes—wait rather than keep guessing. Production also requires the allowed editor IP/VPN and correct proxy/HTTPS setup.

If another local demo used the same hostname on a different port, browser cookies can replace each other; simply log in again to the desired app. Each server's session epoch prevents that cookie granting cross-server access. Use the documented `127.0.0.1` demo versus `localhost` normal URLs to avoid unnecessary cookie collisions.

If no stable admin password was configured, raw local startup generates a temporary value in logs. Prefer setup-created `.env` and never share the logs. For an intentionally changed credential, manage it privately and restart; no recovery email/UI exists.

## Empty newsletter archive

This is expected when all editions are draft/review/approved. Only **PUBLISHED** editions appear publicly. Check the editor state, archive text/topic filters and correct localhost port. Do not publish real content to prove the site works; import the [synthetic fixture](examples/synthetic-newsletter.json) into the separate acceptance workspace and follow [manual tests](LOCAL_TESTING_GUIDE.md).

## Draft save or preview problems

Preview shows the saved version. Save first; unsaved edits intentionally disable approval/publication. A stale version indicates another tab saved changes—copy unsaved text privately, reload and reconcile. Required fields and valid source URLs must be complete before review. A save/reset is intentional; do not bypass the review gate. Published fields are immutable and there is no delete/takedown UI.

## Database issues

Confirm the resolved `DATABASE_PATH`, free disk space and filesystem permissions. Relative paths resolve under the project, not an arbitrary terminal directory. Stop duplicate processes and use local durable storage. Don't delete `.db`, `-wal`, `-shm` or lock files to “reset” errors.

```powershell
py -3 tools/database_backup.py check data/signal_daily.db
```

Take a consistent backup before upgrades/repair; do not copy only a live WAL database's main file. If integrity/schema checks fail, stop writes and use [the verified new-path restoration procedure](PRODUCTION_RUNBOOK.md#backups-restoration-and-daily-operations). Unsupported newer schemas require the matching newer application; do not downgrade them. Windows needs connections closed before cleanup/moves; bundled tests use explicit ownership. Restore to a separate path/volume and keep mail off until any delivery-log rollback is reconciled.

## Emails not sending

This is the default safe state. `Start-Local.ps1` and the demo explicitly disable live email; **Publishing setup** is informational, not a settings editor. Existing code/test coverage does not prove real provider/inbox delivery. No SMTP account is required to use private drafts or publish locally.

Before any deliberate live test, separately approve a verified provider/sender, TLS port, credentials, DKIM/SPF/DMARC and a mailbox you control. Follow the [SMTP runbook](PRODUCTION_RUNBOOK.md#smtp-setup-and-consent-rehearsal), not a repeated send button. Check active consent and the ledger: sent/sending/uncertain deliveries are intentionally excluded. QUIT errors after known acceptance must not be retried; ambiguous acceptance needs provider-log reconciliation. There is no automated bounce/complaint synchronization.

## Docker unavailable

Docker is optional for laptop use. Continue with Python and Ollama. The Dockerfile/Compose architecture is prepared, but container build/runtime/volume/TLS acceptance was not verified on the development laptop. Follow the isolated rehearsal in [PRODUCTION_RUNBOOK.md](PRODUCTION_RUNBOOK.md) on a Docker-capable machine before considering a future host. Do not report a successful deployment just because Compose files exist.

## GitHub Actions failures

Open the failing matrix job and its first failed step. Run the same command locally with dependencies from both requirements files. Common causes: missing Waitress/checkers, formatting, a real regression, broken doc links or platform-specific open-file handling. Use the exact commit's run; an older green badge is not evidence for a new change. Check all four Windows/Linux Python jobs before calling CI verified.

For restricted agent environments, temporary-file or loopback permissions can block the suite before application logic runs. Use a writable temporary directory and required authorized networking, then rerun; document the environmental failure. Do not disable assertions or claim the failed attempt passed.

## Screenshot capture fails

Use the isolated `screenshots` demo, not your normal editor. Playwright/Sharp and a browser are optional maintainer dependencies; see [screenshot reproduction](screenshots/README.md). Missing Chromium can be resolved with Playwright's official browser installer or an existing `CHROMIUM_EXECUTABLE`. Never capture credentials/login fields, real subscribers or unapproved real news. Verify output images and manifest rather than assuming a script invocation succeeded.

## Reporting a problem

Include commit, OS/Python, the specific action, sanitized error and expected/actual behavior. Use only synthetic screenshots. Keep private files and token-bearing URLs out of issues. [Contribution/security instructions](../CONTRIBUTING.md).
