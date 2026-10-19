# Production operations procedure

Prepared 2026-10-20 (Asia/Calcutta). **These are future host procedures, not installed operations.** The [hosting discovery evidence](engineering-evidence/hosting-discovery.json) identified no suitable existing authorized host or encrypted off-host storage. No production scheduler, external monitor, backup encryption/upload agent, retention job or production log rotation policy was installed by this document. Remote acceptance passed nine actual runtime phases and both strict application/proxy scans had zero HIGH/CRITICAL findings for source `aaf91a7b955323dc2928d6f9b5d9222037d8fb99`; the [final deployment report](FINAL_DEPLOYMENT_REPORT.md) links the actual CI evidence. That verification does not establish a live production service.

This procedure supplements the [production runbook](PRODUCTION_RUNBOOK.md) and [architecture](ARCHITECTURE.md). It does not authorize purchases, new paid resources, real email, automatic publication or changes to the laptop's private `.env`.

## Supported host and boundaries

Use one maintained Linux VPS/container host with Docker Engine and Compose v2, persistent local storage and an existing approved budget. Run exactly one [Waitress application process](../production.py) behind the [Caddy configuration](../deploy/Caddyfile). The [Compose file](../compose.yaml) publishes Caddy's 80/443 only, keeps port 8787 private, and persists `signal_data`, `caddy_data` and `caddy_config`. Its proxy service builds [deploy/Dockerfile.caddy](../deploy/Dockerfile.caddy), which replaces the stock binary with Caddy 2.11.7 built using Go 1.26.9 and `golang.org/x/net` 0.60.0. Never expose 11434, a SQLite file, a backup directory or Caddy's administration API. Do not use multiple replicas/writers, NFS/SMB or ephemeral local disks for SQLite.

Configure the real public hostname, exact trusted proxy address, operator IP/VPN `EDITOR_CIDR` and host-only strong credentials before launch. Preserve restricted host access and encrypted host storage. Keep `ENABLE_LOCAL_GENERATION=false` and explicitly set `EMAIL_DELIVERY_ENABLED=false`. Generate with private laptop Ollama, then import through authenticated HTTPS. Imported drafts still require review and explicit approval/publication; no operation in this procedure publishes an edition or sends mail.

Image digests, DNS, TLS, firewall, editor restrictions, persistent volumes and available capacity require host-specific evidence. Render/Railway were suggested only to permit discovery of an existing suitable account allocation; neither was confirmed connected. A connector suggestion does not establish budget or resource authorization.

## Build and validate before start

After selecting an existing authorized host and reviewing its private production configuration, build **both** service images before running Caddy validation. The proxy is a custom build, so validation must not assume a preexisting stock `caddy` image or local `signal-daily-proxy:release` tag:

```bash
docker compose config --quiet
docker compose build --pull
docker compose run --rm --no-deps proxy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
```

Use the same reviewed Compose files/project name for later service commands. These commands validate configuration/build artifacts; they do not start the public service or prove ACME, external ingress or host recovery. The final [remote container run](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39321202556) already exercised actual images, nine runtime phases and both strict scans. Rebuild/scan again when source or dependencies change, and retain the resulting image IDs/digests. Staging and production remain blocked until their existing host, origin, access configuration and backup storage are available.

## Health and incident response

The image runs [tools/healthcheck.py](../tools/healthcheck.py): it reads SQLite's schema/table and opens the private listening socket. It cannot prove that HTTPS ingress, an HTTP request, backups or external delivery work. The public `/health` route returns HTTP 200 with `{"status":"ok"}` when it can read the database and HTTP 503 on database failure.

After host selection, configure an external HTTPS health check every minute with a ten-second timeout; alert an approved operator channel after three consecutive failures. No channel is configured or contacted here. Also alert on fewer than 20% free bytes/inodes, unhealthy/restarting containers, certificate renewal failures and a verified off-host backup older than 26 hours. Alerts must exclude private URLs, credentials, recipient addresses and draft content.

Run these diagnostic commands from the approved host checkout; substitute its actual approved origin for `ORIGIN` first:

```bash
docker compose ps
docker compose exec -T newsletter python tools/healthcheck.py
curl --fail --silent --show-error --max-time 10 "$ORIGIN/health"
docker compose logs --tail=100 newsletter proxy
```

Do not use `docker compose config` without `--quiet`, because expanded environment output can reveal credentials. Treat logs as private operational data. A healthy container plus a failing HTTPS probe points to ingress/DNS/TLS; a failed private probe requires application/database/disk investigation. Preserve relevant redacted logs before restarting. Do not restart repeatedly to conceal a persistent fault.

## Restart and host boot

Compose already declares `restart: unless-stopped` for both services. After a future host deployment, verify the Docker service starts at boot and record the results of a controlled host reboot. That policy alone is not reboot evidence. A deliberately stopped container remains stopped until started.

```bash
docker compose restart newsletter
docker compose ps
docker compose exec -T newsletter python tools/healthcheck.py
```

Use the same compose files and project name used to create the service. A restart preserves named volumes and invalidates editor sessions by design. It does not load changed environment configuration; after a reviewed configuration change, recreate the application with `docker compose up -d --no-deps newsletter` and repeat the health checks. Do not delete instance lock files to bypass an active writer. Never use `docker compose down -v` on a retained environment.

Before an upgrade, take and verify a fresh off-host backup, retain the previous application image/release and stop competing maintenance. Schema versions newer than the chosen release are rejected; rolling back an image without considering database migration compatibility is unsafe. Restore to a new database path when recovery requires an older database.

## Bounded private logs

The Compose file declares the following bounded Docker logging policy for **both** services. It is source configuration, not evidence of an installed production service:

```yaml
services:
  newsletter:
    logging:
      driver: local
      options:
        max-size: "10m"
        max-file: "5"
  proxy:
    logging:
      driver: local
      options:
        max-size: "10m"
        max-file: "5"
```

Validate the selected compose files with `docker compose config --quiet` before creating services. Verify that the declared policy is active on the future host. Docker daemon/system logs need their own host retention limits. Do not enable unredacted Caddy access logs: confirmation/unsubscribe URLs contain secrets. Application diagnostic output is bounded/redacted, but that does not make logs public. The operational records held in SQLite have no automatic retention policy; Docker log rotation does not purge them.

## Daily encrypted off-host backups and retention

[tools/database_backup.py](../tools/database_backup.py) implements consistent online SQLite backup, integrity/foreign-key checks and restoration to a new path. It **does not encrypt, upload, schedule or prune backups**. A copy on the same named volume/VPS is not disaster recovery.

After an existing encrypted off-host destination and its approved host backup agent are identified, install a daily host job at **02:15 Asia/Calcutta**, plus a job before each upgrade. Configure the scheduler's timezone explicitly. Only one backup job may run at a time. No scheduler was created here.

Each job must perform this sequence:

1. Use a restrictive `umask 077` and a unique UTC timestamped filename in a private staging directory. For the default live filename, run the repository tool inside the application container:

   ```bash
   docker compose exec -T newsletter python tools/database_backup.py backup /data/signal_daily.db /data/backups/backup-UNIQUE-UTC-TIMESTAMP.db
   docker compose exec -T newsletter python tools/database_backup.py check /data/backups/backup-UNIQUE-UTC-TIMESTAMP.db
   ```

   Replace the timestamp and, if `DATABASE_FILE` selects a restored file, replace the source path with that exact current filename. The destination must not exist; this guard prevents overwrites. The tool includes committed WAL contents through SQLite's backup API. Never copy only a live SQLite main file.

2. Extract the verified snapshot to a private host staging path using the actual container ID returned by `docker compose ps -q newsletter` and `docker cp`. Use the host's **selected approved encryption/backup agent** to encrypt before transmitting and upload to its **selected existing off-host destination**. No provider path, bucket, encryption command or agent is configured in this repository; claiming this step succeeded requires its real result. Keep decryption keys in separate approved secret storage, outside both the backup artifact and Git.
3. Verify the encrypted object was received and is readable by the recovery identity. Retain a private manifest with timestamp, release/image digest, schema version, integrity result, ciphertext checksum, destination identifier and upload outcome. Never put subscriber data, tokens or credentials in the manifest. Mark success only after encryption and off-host verification; a successful local SQLite copy alone is insufficient.
4. Apply retention **only after a new verified off-host backup exists**: keep the newest 14 daily snapshots and one snapshot per calendar week for eight weeks. Keep the latest pre-upgrade snapshot until the upgrade and a subsequent recovery rehearsal have passed. Retain private local plaintext staging for no longer than 24 hours, removing it after successful encrypted upload; failed staging must remain protected and trigger an alert. Storage encryption and filesystem access controls protect staging; deletion is not a claim of secure erasure on SSDs.
5. Alert on job failure or a newest verified backup age exceeding 26 hours. Log only bounded status/manifest identifiers. Do not prune the last known good backup after a failed run. Schedule a recovery rehearsal at least monthly and after a material schema/backup change, using an isolated private environment with mail and generation off.

An initial operating target is RPO at most 24 hours and RTO at most one hour. Neither is measured or promised until the actual host and off-host restoration rehearsal exist. Secrets and the Caddy certificate/configuration volumes need their own encrypted backup/recovery coverage; a database snapshot does not contain `.env` or TLS configuration. Apply a deliberate privacy/retention policy to backups before collecting public subscriber data.

## Separate restoration procedure

Restoration is a controlled recovery operation, not a modification of the live database in place. Keep the original volume, database and sidecars intact.

1. Keep mail disabled. Stop the application with `docker compose stop newsletter`; preserve the selected backup manifest, current release, database filename and any `sending`/`uncertain` delivery state. Keep the proxy in a reviewed maintenance state or stop it so readers do not receive misleading success responses. Pause backup/pruning jobs while restoring.
2. Retrieve a selected encrypted snapshot from the approved off-host destination with the recovery identity. Verify its recorded checksum, decrypt into restricted private staging using the approved agent/key, and copy it into the private volume under a new backup filename. Do not overwrite the original database or a previous recovery attempt. The operator's actual storage/encryption integration must supply this step; no credential or provider workflow is invented here.
3. Use the backup tool in a one-off container with the same private volume and a **new** target filename:

   ```bash
   docker compose run --rm --no-deps newsletter python tools/database_backup.py check /data/backups/recovered-UNIQUE.db
   docker compose run --rm --no-deps newsletter python tools/database_backup.py restore /data/backups/recovered-UNIQUE.db /data/restored-UNIQUE.db
   docker compose run --rm --no-deps newsletter python tools/database_backup.py check /data/restored-UNIQUE.db
   ```

4. Prefer an isolated restore volume/private staging instance first. Confirm integrity, supported schema version, expected edition/history/subscriber/ledger counts and absence of unintended publication/mail. Record measured retrieval, decryption and restoration times. Do not expose the recovery staging instance publicly or reuse it as a second writer.
5. For an authorized recovery cutover, set the private host configuration's `DATABASE_FILE` to the new restored filename, keep `EMAIL_DELIVERY_ENABLED=false`, and recreate the application with `docker compose up -d --no-deps newsletter`. Check the private probe and external HTTPS health path; retain the original database for investigation. The restored release must support its schema, and normal startup may apply supported migrations.
6. Reconcile any mail provider acceptances newer than the backup before any separately authorized future mail enablement. A restored old ledger can otherwise resend accepted messages. `sending`/`uncertain` rows must not be blindly retried. Resume the daily backup job, verify a new encrypted off-host snapshot of the recovered state, and preserve the recovery evidence privately.

No step enables automatic publishing. Human review, approval and deliberate publication remain required for every real edition. Production readiness requires actual evidence of the selected host, HTTPS/editor boundary, persistent restart, encrypted off-host backup and successful separate restoration; this procedure alone proves none of those installations.
