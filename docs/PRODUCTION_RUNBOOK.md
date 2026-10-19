# Controlled pilot runbook

These are operator instructions for a future authorized launch. No public deployment was performed. Read `PRODUCTION_READINESS_REPORT.md` first. Do not expose `run.py`, the Waitress port, SQLite files, or Ollama to the internet.

## Architecture and prerequisites

Use one maintained Linux VPS with local persistent storage, Docker Engine and Compose v2. Run one application container and Caddy. Caddy alone publishes TCP 80/443 and obtains/renews the public TLS certificate. Waitress listens on the Docker bridge, trusts exactly Caddy's `172.30.0.2` address, and accepts only the configured HTTPS host. The application's port is not published. Docker's private bridge still permits outbound RSS/SMTP; the name is not a promise of an isolated network. No CDN/load balancer is included.

The named `signal_data` volume holds SQLite, WAL files, the instance lock and optional local backups. Caddy's certificate/config volumes must also persist. Never use ephemeral/serverless disks, NFS/SMB for SQLite, multiple application replicas, multiple VPS writers, or `docker compose down -v` on production. Choose a different private subnet in both Compose and `TRUSTED_PROXY` if `172.30.0.0/24` conflicts with your host/VPN.

Restrict SSH to the operator, permit public TCP 80/443 only, and deny public 8787/11434. Caddy restricts `/admin`, `/api/admin/*`, `/api/login`, and `/api/logout` to `EDITOR_CIDR`; its default loopback-only range denies remote editors. Set the exact operator public IP or VPN CIDR. The password remains required. Do not put another proxy/CDN in front without redesigning and retesting both IP allowlisting and proxy trust. Keep the host patched, encrypted at rest, and monitored for disk/volume exhaustion.

Use Python 3.11+ for laptop tools. Production requires `python -m pip install -r requirements.txt`; development checks additionally require `requirements-dev.txt`. On Windows use a working Python executable or registered `py`, not the Microsoft Store placeholder. The original development laptop used Codex's bundled Python 3.12 at `%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

## Verify Docker before considering deployment

Docker was unavailable during Phase 2. Run these commands on a Docker-capable test machine. The following Bash example creates a separate test volume, has no published ports, has no internet access, and publishes synthetic content only. Do not use the production volume. On Windows PowerShell, use `$env:ADMIN_PASSWORD` / `$env:SESSION_SECRET` for environment assignments and run each Docker command on one line instead of Bash continuations.

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m unittest discover -s tests -v
docker version
docker compose version
docker build --pull -t signal-daily:pilot-check .
docker volume create signal_daily_verification
export ADMIN_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(24))')"
export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(40))')"
docker run -d --name sd-pilot-verification --network none --read-only \
  --tmpfs /tmp:size=32m --cap-drop ALL --security-opt no-new-privileges \
  -e ADMIN_PASSWORD -e SESSION_SECRET -e APP_ENV=production \
  -e HOST=127.0.0.1 -e PORT=8787 -e PUBLIC_URL=https://pilot.example.org \
  -e TRUSTED_PROXY=127.0.0.1 -e ENABLE_LOCAL_GENERATION=false \
  -e EMAIL_DELIVERY_ENABLED=false -e DATABASE_PATH=/data/verification.db \
  -v signal_daily_verification:/data signal-daily:pilot-check
docker exec sd-pilot-verification python tools/pilot_smoke.py
docker restart sd-pilot-verification
docker exec sd-pilot-verification python tools/pilot_smoke.py --verify-existing
docker exec sd-pilot-verification python tools/database_backup.py backup /data/verification.db /data/verification-backup.db
docker exec sd-pilot-verification python tools/database_backup.py restore /data/verification-backup.db /data/verification-restored.db
docker exec sd-pilot-verification python tools/database_backup.py check /data/verification-restored.db
docker stop sd-pilot-verification
```

Test migration on that stopped, disposable container's volume (never run this schema manipulation against production):

```bash
docker run --rm --network none -v signal_daily_verification:/data --entrypoint python signal-daily:pilot-check -c "import sqlite3; c=sqlite3.connect('/data/verification.db'); c.execute('DROP TABLE rate_limits'); c.execute('PRAGMA user_version=1'); c.commit(); c.close()"
docker start sd-pilot-verification
docker exec sd-pilot-verification python tools/pilot_smoke.py --verify-existing
docker exec sd-pilot-verification python -c "import sqlite3; c=sqlite3.connect('/data/verification.db'); assert c.execute('PRAGMA user_version').fetchone()[0]==2; c.close(); print('migration verified')"
docker rm -f sd-pilot-verification
docker volume rm signal_daily_verification
```

The smoke tool refuses ordinary production configuration. Save actual build/test output; a Dockerfile review or a successful local Python test is not a successful image test. Review image vulnerability scans and pin both base and Caddy image digests before launch; the supplied tags are not immutable.

## Configure the future host

After separate authorization to push and deploy, obtain the reviewed development commits on the VPS. Run `python tools/setup_local.py` once in a private checkout, then edit `.env` locally. Do not paste secrets into tickets or commit them. Keep `.env` readable only by the operator; use `chmod 600 .env` on Linux or explicit user-only Windows ACLs. Docker environment access is privileged: anyone controlling Docker can read secrets and the database.

Set these values deliberately:

```dotenv
APP_ENV=production
PUBLIC_HOST=newsletter.your-domain.example
PUBLIC_URL=https://newsletter.your-domain.example
EDITOR_CIDR=YOUR_OPERATOR_PUBLIC_IP/32
ADMIN_PASSWORD=YOUR_UNIQUE_RANDOM_PASSWORD_AT_LEAST_16_CHARACTERS
SESSION_SECRET=YOUR_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
ENABLE_LOCAL_GENERATION=false
EMAIL_DELIVERY_ENABLED=false
DELIVERY_BATCH_SIZE=5
```

Replace every example value. Compose overrides internal bind address, database path, proxy trust and generation settings. Keep the generated credentials or generate stronger replacements with `secrets.token_urlsafe`; the labels above are explanations, not valid secrets. Leave SMTP disabled during the first hosting verification. `DATABASE_FILE` optionally selects a restored filename inside `/data`; default is `signal_daily.db`.

Configure DNS A/AAAA records for this VPS; remove unusable AAAA records. Ensure inbound ACME challenges and 80/443 work. Keep Caddy's admin API private. Validate without starting a public service first:

```bash
docker compose config --quiet
docker compose run --rm --no-deps proxy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker compose build --pull
```

`docker compose config` without `--quiet` can print expanded secrets. The proxy validation container need not publish ports; Caddy certificate issuance and the full ingress path are still unverified until an authorized launch. Once authorized, `docker compose up -d` starts the service. Confirm all of the following before inviting readers:

1. `docker compose ps` reports a healthy application; HTTPS `/health` returns 200. Readiness checks SQLite access; it does not certify SMTP, backups, DNS, disk capacity or factual accuracy.
2. HTTP redirects to HTTPS and the public certificate chain is valid from a separate network. Check HSTS, CSP, frame protection and MIME protections.
3. Public scans cannot reach 8787/11434, data files or Caddy's admin port. Wrong-host requests fail. Oversized bodies/headers fail. Spoofed forwarding headers do not override real client identity.
4. `/admin` and login/API routes fail from outside `EDITOR_CIDR`. From the allowed address, login works; the session cookie is `Secure; HttpOnly; SameSite=Strict`. Cross-origin mutations fail. Password attempts are throttled after ten per client IP per fifteen minutes.
5. Restart the application and VPS; published synthetic test content remains and old editor sessions require login again. Use a separate staging volume/domain for public synthetic tests, then remove that staging service.
6. Complete an off-host backup/restore rehearsal and verify alerting and available disk space. Record the host, tested image digests and results privately.

## Local Gemma and first real edition

Ollama runs only on your laptop's loopback interface. Keep `OLLAMA_URL=http://127.0.0.1:11434` and the installed `OLLAMA_MODEL=gemma4:e4b`. Do not bind Ollama to `0.0.0.0`, open 11434, add an internet tunnel, or configure the hosted application to call the laptop. The application refuses non-loopback model endpoints and production disables its generation route.

For a local-only review of your existing draft, run `python run.py` from the project folder with the existing development `.env`. This starts a schema migration, so keep the Phase 2 backup first. Open `http://localhost:8787/admin`, log in with the password in your local `.env`, and open draft ID 1. Phase 2 did not approve or publish it. Old news can be stale: regenerate rather than publishing outdated reporting.

For a fresh edition, while Ollama is running on the laptop:

```bash
python tools/collect_news.py
python tools/local_generate.py --output local-drafts/first-real-edition.json
```

Create `local-drafts` first if it does not exist. RSS collection writes to the configured local database. The generation CLI writes a private file and never publishes. An additional Phase 2 draft exists only on this laptop at `local-drafts/phase2-gemma-draft.json`; it also needs source checking and may become stale.

1. Open the approved host's HTTPS `/admin` from the allowed operator address. Log in; select **Import local draft**, select/paste the local file, then **Import as unapproved draft**. Import always saves a draft, regardless of a supplied status.
2. Open the saved draft. Check every original source link, publication date, number, attribution and implication. The model saw source headlines/descriptions, not necessarily full articles. Remove unsupported claims and make the subject, introduction and closing your own.
3. Select **Save as draft**. Saving resets approval. Expand **Preview saved edition** and read the rendered edition, including sources and mobile layout. Confirm no private data or placeholder/test text remains.
4. Select **Submit for review**, perform the final editorial check, then **Approve reviewed edition**. Review and approval are separate recorded state changes. The product uses one editor account, not independent two-person approval.
5. Keep `EMAIL_DELIVERY_ENABLED=false` for an online-only first edition. If mail is enabled, **Publish** also immediately attempts the first subscriber delivery batch. Do not enable it until sender setup and recipient consent checks are complete.
6. When you personally approve the content, select **Publish + notify subscribers** and accept the confirmation. Confirm the edition appears on the homepage, `/archive` and its public `/issue/<slug>` page. Published content is immutable; correct mistakes in a clearly labeled follow-up. There is currently no public takedown/edit UI.
7. With approved email configuration, inspect sent/failed/uncertain/remaining counts. **Send / retry subscriber delivery** processes another bounded batch. Never replay `sending`/`uncertain` reservations until provider logs establish whether the message was accepted. SMTP acceptance does not prove inbox delivery.

## SMTP setup and consent rehearsal

Amazon SES is one suitable provider for a small opt-in pilot. Nothing was provisioned or sent through SES during Phase 2. In your chosen AWS region, verify your sending domain, publish SES's DKIM DNS records, configure SPF/custom MAIL FROM and DMARC alignment, and generate region-specific **SMTP credentials** (not AWS console credentials or ordinary access keys). SES requires TLS; use STARTTLS on 587 or implicit TLS on 465. While in the sandbox, recipients must be verified or use the SES mailbox simulator. Request production access before inviting arbitrary subscribers. See [SES SMTP setup](https://docs.aws.amazon.com/ses/latest/dg/send-email-smtp.html), [TLS connection modes](https://docs.aws.amazon.com/ses/latest/dg/smtp-connect.html), [sandbox restrictions](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html), and [DMARC](https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dmarc.html).

Keep `EMAIL_DELIVERY_ENABLED=false` while entering:

```dotenv
SMTP_HOST=email-smtp.YOUR_REGION.amazonaws.com
SMTP_PORT=587
SMTP_SSL=false
SMTP_USER=YOUR_SES_SMTP_USERNAME
SMTP_PASSWORD=YOUR_SES_SMTP_PASSWORD
MAIL_FROM=Signal Daily <newsletter@YOUR_VERIFIED_DOMAIN>
```

After your separate approval of live SMTP testing, enable delivery and recreate the application to load configuration. Initially subscribe only your own verified test address. Follow its confirmation link within 24 hours; verify replay/expiry does not grant another subscription. Check HTML and plain text, source links, sender authentication results and spam placement. Publish only a synthetic staging edition for the mail rehearsal. Verify at-most-once reservations, then open unsubscribe (GET must do nothing) and confirm unsubscribe by POST. One-click email unsubscribe also uses POST. Do not import subscribers or send bulk mail as a test.

Enable SES account-level bounce/complaint suppression and notifications before inviting readers. The application has no automatic bounce/complaint webhook or suppression synchronization: the operator must monitor provider feedback and suppress affected addresses promptly. Keep the pilot small and pause delivery on complaints, repeated failures, or unknown SMTP acceptance. See [SES sending and feedback](https://docs.aws.amazon.com/ses/latest/dg/send-email-concepts-process.html) and [reputation monitoring](https://docs.aws.amazon.com/ses/latest/dg/monitor-sender-reputation.html). Add the publisher's real identity, contact and privacy/retention information before collecting public subscriber addresses.

## Backups, restoration and daily operations

Use the SQLite backup API tool, never copy only the live `.db` file while WAL writes may exist. Backups include subscriber addresses and unsubscribe tokens; encrypt off-host storage, restrict access, set retention, and test restoration. Files are created with mode 0600 on POSIX; Windows deployments need explicit filesystem ACLs. Backup destinations must be new paths; accidental overwrites fail.

Example after deployment, substituting a unique timestamp:

```bash
docker compose exec newsletter python tools/database_backup.py backup /data/signal_daily.db /data/backups/backup-YYYYMMDD-HHMM.db
docker compose exec newsletter python tools/database_backup.py check /data/backups/backup-YYYYMMDD-HHMM.db
```

Export that verified backup to encrypted off-host storage using the operator's approved backup agent or `docker cp` from the application container, then encrypt/upload it. A backup stored only on the same VPS/volume is not disaster recovery. Establish a daily backup and another before upgrades; an initial pilot target is RPO <=24 hours and a measured RTO <=1 hour, not a verified guarantee. Alert on backup failures, stale backups, disk usage and HTTPS `/health` failures. No scheduler or alert service was installed by Phase 2.

Restore without overwriting production:

1. Stop the application (`docker compose stop newsletter`) and pause outbound mail. Keep Caddy running a maintenance response or stop it as well. Record all `sending`/`uncertain` claims and provider evidence before changing the database.
2. Attach the same data volume with a one-off container: `docker compose run --rm --no-deps newsletter python tools/database_backup.py restore /data/backups/backup-YYYYMMDD-HHMM.db /data/restored-YYYYMMDD.db`. This command runs the backup tool, not the HTTP server; it refuses existing targets and locks the new database path.
3. Run `check` against the restored file. Set `DATABASE_FILE=restored-YYYYMMDD.db` in `.env`; keep the original database and its sidecars untouched for recovery. Set `EMAIL_DELIVERY_ENABLED=false`.
4. Recreate just the application with `docker compose up -d --no-deps newsletter`. Startup migrates under its instance lock. Check `/health`, issue history, archive, consent and ledger counts. Reconcile SMTP logs for deliveries newer than the backup **before** re-enabling mail; restoring an old ledger can otherwise duplicate sends.
5. Rehearse this against an isolated restore volume regularly and time it. Restore the matching application release as well; schema versions newer than supported are rejected. Keep `.env`/SMTP credentials in a separate encrypted secrets backup; database backups do not include them.

There is no automatic failover, repair, purge, database encryption, replica, background send worker or guaranteed exactly-once SMTP delivery. Delivery is synchronous and capped at five recipients per batch in Compose; a timeout can leave work in progress. Check current state before retrying a timed-out publish/send request. The instance lock uses local OS locks and is released after process death; do not delete a lock file to bypass a live process. Restarts deliberately invalidate editor sessions. Runtime access logs omit token-bearing URLs; do not enable unredacted proxy/debug request logging.

Reference configuration: [Waitress proxy settings](https://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html), [Caddy request limits](https://caddyserver.com/docs/caddyfile/directives/request_body), [Caddy server timeouts](https://caddyserver.com/docs/caddyfile/options), [Caddy address matchers](https://caddyserver.com/docs/caddyfile/matchers).
