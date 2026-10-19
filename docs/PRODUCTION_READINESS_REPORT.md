# Signal Daily — Phase 2 production readiness

Date: 2026-10-19. Development branch: `production-readiness`, based on published `main` commit `3b4ae381ba3d2db7d0834002dfa0f49aec83b27e`.

**NOT READY FOR CONTROLLED DEPLOYMENT**

Application hardening and local acceptance checks are complete. The remaining host, container, HTTPS, SMTP and off-host recovery checks below must be completed before a public pilot. No push, public deployment, real-news approval/publication, real-recipient email, or subscriber export occurred. All test servers were stopped.

## Completed improvements

- Added a production Waitress 3.0.2 WSGI entry point that shares the existing route/business logic without using the development HTTP parser. `run.py` refuses production mode; `production.py` requires it. Both supported entry points lock the database against a second application process.
- Enforced canonical production Host and HTTPS scheme checks, canonical-origin CSRF checks, explicit trust in one proxy IP, rejection of wildcard proxy trust, and removal of untrusted forwarding headers. Real Waitress tests cover trusted and untrusted peers.
- Added request limits: 140,000-byte bodies, 16 KiB headers, eight worker threads, 64 active connections/backlog entries, and 30-second inactive-channel cleanup. Unsupported methods fail; HEAD cannot confirm a subscription.
- Preserved secure HTTP response headers and production cookies (`Secure`, `HttpOnly`, `SameSite=Strict`). Login/subscription limits now persist in SQLite in production; IP identities are stored as keyed hashes, bounded to 10,000 entries with expiry cleanup.
- Added schema version 2 for persistent throttles, idempotent migrations, and rejection of unsupported newer schemas. Approval state, history, consent and delivery reservations remain intact.
- Added consistent online SQLite backup, validation and non-destructive restore tooling. Restore refuses existing files, stale SQLite sidecars, and locked targets; restores use a new path rather than overwriting the live database.
- Made production email explicitly opt-in (`EMAIL_DELIVERY_ENABLED` defaults false). Validated sender, TLS ports/mode and credential pairs before connection. Fixed SMTP QUIT failures incorrectly making accepted messages retryable; DATA disconnects remain `uncertain`. Added one-click unsubscribe headers while retaining GET confirmation / POST unsubscribe behavior.
- Disabled hosted Gemma generation. Authenticated JSON import always creates a draft; local Ollama remains loopback-only with no cloud fallback or downloaded weights.
- Reworked Docker/Compose for Waitress behind Caddy, with only proxy ports public, an editor IP/VPN allowlist, unprivileged application UID, read-only root, restricted capabilities, resource bounds, health probes and persistent SQLite/certificate volumes. **Configuration prepared; container/proxy execution unverified.**
- Added a guarded, synthetic container smoke tool, updated four-job CI dependencies, expanded the dependency/private-file audits, and wrote the [operator runbook](PRODUCTION_RUNBOOK.md).

## Validation results

| Check | Result and scope |
|---|---|
| Existing baseline | **56/56 passed** before changes on Windows Python 3.12. |
| Final regression suite | **77/77 passed**, zero failures/errors; 21 added tests. |
| Ruff lint / formatting | Passed; 22 Python files formatted/checked. |
| Python compilation | Passed for application modules, tools and tests. |
| JavaScript syntax | `node --check static/app.js` passed. |
| Bandit | Passed, no findings; tests, private data/backups and temporary checker installation excluded. |
| OSV dependency audit | Ten pinned packages checked, **zero advisories** returned: one production package plus nine checker packages. See `dependency-audit.json`; this does not audit the OS or container images. |
| Private-file / known-secret audit | No findings in Git candidates. Real configuration, databases, backups, local drafts and temporary artifacts remain ignored. This is not an exhaustive secret detector. |
| Live RSS | **18 relevant records**, zero feed errors in this run; fetched with the actual feed collector. These were saved to isolated verification inputs rather than inserted into the original database. |
| Installed local model | Actual Ollama `/api/tags` confirmed `gemma4:e4b`. No model installation/download. |
| Live generation CLI | `tools/local_generate.py --stories ... --output local-drafts/phase2-gemma-draft.json` generated five source-linked items in **26.75 seconds**. JSON validation passed. Semantic factual accuracy still requires human review. |
| Authenticated real-draft import | Imported generated real JSON through the actual production HTTP process into a separate temporary database. Unauthenticated import failed; imported edition remained **draft**, absent from public pages before and after restart. It was never approved. |
| Synthetic publication/archive | Actual HTTP import → draft → review → approved → published succeeded only for synthetic content. Premature publish failed. Homepage, archive, edition URL and sitemap passed. |
| Restart persistence | Terminated/restarted the actual WSGI process against the same isolated DB; synthetic publication persisted, real draft stayed private, previous session became invalid. |
| Synthetic smoke CLI | `tools/pilot_smoke.py` passed against a local process and again after restart. This validates the tool/application locally, **not Docker**. |
| SMTP/consent | Mock TLS SMTP through actual Waitress HTTP: confirmation, HEAD safety, active-only delivery, duplicate-send prevention, multipart messages and GET/POST unsubscribe passed. STARTTLS/implicit TLS modes, config rejection, QUIT/DATA outcomes also passed. No real SMTP connection or inbox acceptance verified. |
| Windows/Linux | Current code tested on Windows Python 3.12. Linux/WSL unavailable; Linux `flock`, container UID/volume permissions and Python 3.11 were not executed here. The previous release passed four CI jobs; this branch's updated matrix has **not run** because pushing is prohibited. |

Initial checks encountered Windows sandbox temporary-file permissions, then passed with an authorized workspace-local temporary directory. An intermediate 73-test run found two Windows backup flush errors (`fsync` on a read-only descriptor); changing to a writable descriptor resolved them. Final failures: **none**. Unexecuted environment checks remain blockers, not passes.

Sanitized evidence is retained in [production-test-evidence.txt](production-test-evidence.txt) and [production-validation.json](production-validation.json). Local commits separate persistence, SMTP safety, production serving, container preparation, and documentation/audit evidence. None were pushed.

## Original database, backup and restoration

The actual local database was opened read-only for fingerprinting/backup. It still contains **19 stories, one draft, zero subscribers, zero deliveries, one creation event and one operation**. It remains schema version 1, with the original real draft unmodified. Phase 2 did not migrate or publish against this database. Opening it later with the updated application will apply version 2 under the process lock.

A real SQLite backup was written to ignored `backups/phase2-before-production.db`, restored to a separate ignored verification database, checked with `PRAGMA integrity_check` and `foreign_key_check`, and compared by a full logical SQL dump. The original, backup/restoration and final original fingerprint matched:

```text
SHA-256 of logical SQL dump:
f1d7ee351c9a723c464267b8494a64dc872b0026adcb832cf58357c10cf319ca
```

Only the restored copy was migrated to schema 2, twice, without errors. Automated tests additionally exercised committed WAL contents, published synthetic state/history, missing/invalid source rejection, refusal to overwrite, active-process lock rejection, v1 migration, newer-schema rejection and cross-process lock release/reacquisition.

The backup is local and unencrypted by the tool. POSIX files request mode 0600; Windows ACLs and encrypted storage are operator responsibilities. No off-host backup, scheduled job, disaster restore, measured RTO, or recovery from a physical disk loss was verified. Restoring an old delivery ledger can duplicate newer accepted emails; keep email disabled until provider logs are reconciled. See the runbook for exact backup/restore commands and retention requirements.

## Security audit findings

| Finding | Resolution / remaining constraint |
|---|---|
| Development `http.server` is unsuitable for a public service | Production now uses Waitress with bounded parsing/connections behind Caddy; development mode is rejected by the production launcher. Do not use an alternate WSGI command that bypasses configuration validation and the instance lock. |
| Host/Origin trust and proxy ambiguity | Canonical host/scheme/origin enforced in production. Exactly one trusted proxy and one forwarding hop; no public backend port in Compose. Actual Caddy ingress still needs end-to-end testing. |
| Restart-reset brute-force throttles | SQLite-backed production counters survive application restarts. Hash keys depend on the session secret; secret rotation resets client identities. Distributed abuse can still require additional edge protection. |
| Concurrent application processes / unsafe SQLite restores | OS lock on supported entry points, single-instance deployment, local disk only, new-path restores. No distributed lock or multi-host support. |
| Accidental real email / incomplete TLS config | Production defaults to mail off; settings validated; mocks only used. Operator must explicitly enable and acceptance-test approved credentials and sender DNS. |
| Accepted SMTP message becoming retryable after QUIT failure | Fixed and regression-tested. Uncertain DATA/interrupted `sending` claims remain held for manual provider reconciliation. Exactly-once SMTP delivery is not guaranteed. |
| Editor exposure | Prepared Caddy IP/VPN restriction in addition to password, secure cookies, CSRF checks and throttling. No MFA, account recovery, separate roles or independent second approver. Actual allowlisting is a launch acceptance check. |
| Token/privacy leakage | Application token paths are redacted; production adapter has no access log; Caddy access logs are disabled. Avoid proxy/debug URL logging. DB/backups contain private addresses/tokens and require restricted encrypted storage. |
| Feed SSRF/DNS | Existing public-HTTPS and redirect/DNS checks retained. Operator-owned feed configuration is trusted input; DNS rebinding/egress policy remains an operational defense requirement. |
| Model accuracy | Source/shape/numeric validation retained, but cannot verify all semantics or prompt injection. Only the human editor may approve real content. |
| Synchronous work / availability | RSS and bounded mail batches run in request workers. Compose uses five-recipient batches; waits/timeouts can leave work active. No load/soak/DoS claim, background queue, automatic failover or availability SLA. |
| Supply chain and host | Python advisory check passed. Docker base/Caddy image digests, OS patches, Caddy validation and image vulnerability scans still need verification on the intended host. |

Published editions are immutable and there is no takedown UI. Define an emergency withdrawal/correction procedure before launch; restrict any direct database maintenance to a backed-up, stopped instance. Subscriber deletion/retention and bounce/complaint synchronization are manual. Add publisher identity, contact and privacy/retention information before collecting public addresses.

## SMTP readiness

The application is ready for a controlled SMTP **configuration rehearsal**, not verified live email delivery. Configuration handling, expiring double opt-in, active-only targeting, unsubscribe POST, TLS selection, bounded batches and delivery reservations passed mocks. No real credentials were supplied, no bulk mail was sent, and no subscriber data was published.

The runbook provides Amazon SES setup using region-specific SMTP credentials, TLS, verified domain/DKIM, SPF/DMARC, sandbox recipient constraints and bounce/complaint monitoring. After separate authorization, test only an operator-controlled mailbox with a synthetic staging edition. Verify real headers, inbox/spam placement and unsubscribe before enabling pilot subscription traffic. No automatic bounce/complaint webhook is implemented.

## Hosting architecture

```text
Internet :80/:443 → Caddy (TLS, limits, editor IP/VPN restriction)
                       ↓ private bridge; exact trusted proxy IP
                 Waitress → application routes → local persistent SQLite
                       ↓ outbound TLS SMTP, only when explicitly enabled
                 verified sender / opt-in recipients

Laptop RSS → loopback Ollama/Gemma → private JSON file
                                      ↓ authenticated HTTPS import
                                 draft → review → approval → publish
```

Use one persistent Linux VPS and one application instance. Do not expose port 8787/11434 or introduce a CDN/proxy chain without retesting trust. Compose persists data and Caddy certificate state. Detailed configuration follows official [Waitress arguments](https://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html), [Caddy limits](https://caddyserver.com/docs/caddyfile/directives/request_body), and [Caddy server options](https://caddyserver.com/docs/caddyfile/options). This is a prepared architecture, not a verified running deployment.

## Docker result and remaining blockers

**Docker NOT VERIFIED:** no Docker command was available on PATH or at the usual Docker Desktop CLI location. WSL reported it was not installed. No image build, container start, volume mount, Docker restart, image scan, Caddy binary validation or actual HTTPS handshake occurred. Local process restart and real SQLite restoration were verified independently; those do not establish Docker persistence.

Before a public pilot:

1. Obtain separate authorization to push the reviewed development commits and to deploy. Run the updated four-job CI matrix; the previous green matrix is evidence only for the earlier release.
2. Run the runbook's isolated Docker build/synthetic workflow/restart/migration/backup/restore rehearsal on the intended Linux environment. Confirm image/volume permissions, non-root execution, health checks and resource restrictions. Audit and pin image digests.
3. Choose the VPS/domain, configure DNS/firewall/operator CIDR and secrets, validate Caddy, and verify the actual HTTPS path, proxy identity and editor restrictions from separate networks after deployment authorization.
4. Configure encrypted off-host backups, retention and monitoring. Restore on a separate volume and measure recovery time. Retain a separate secrets backup.
5. Supply and approve SMTP/sender setup, DNS authentication, feedback monitoring and a single-mailbox acceptance test. Until then, keep subscriptions and all outgoing mail disabled; an online-only pilot can be considered separately after the hosting gates pass.
6. Add publisher/privacy/contact information and define correction/takedown/consent-retention procedures. Perform your own source review and approval of the first real edition.

## Exact first-launch / first-edition steps

Follow [PRODUCTION_RUNBOOK.md](PRODUCTION_RUNBOOK.md) in order: Docker verification → host configuration → authorized start → external HTTPS/security/restart checks → off-host recovery → approved SMTP rehearsal if email is desired → human editorial publication. It includes copyable commands and the actual UI labels.

For your first real edition specifically: run local Ollama; generate private JSON with `python tools/local_generate.py --output local-drafts/first-real-edition.json`; log in to the allowed HTTPS editor; choose **Import local draft → Import as unapproved draft**; open every original source; edit and **Save as draft**; expand **Preview saved edition**; **Submit for review → Approve reviewed edition → Publish + notify subscribers** and confirm only after your final check. With email disabled this publishes online only; with email enabled it immediately attempts the first batch. Check the homepage, archive and edition URL, then use **Send / retry subscriber delivery** only for eligible remaining/failed recipients. Your original local draft ID 1 and the new private JSON are available for review; neither was approved by Phase 2.

**NOT READY FOR CONTROLLED DEPLOYMENT**
