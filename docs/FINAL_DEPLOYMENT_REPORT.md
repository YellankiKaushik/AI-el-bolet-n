# Final deployment report

Date: 2026-10-20 (Asia/Calcutta). Remote Linux container acceptance, both strict image scans and the four-job release matrix passed for source `aaf91a7b955323dc2928d6f9b5d9222037d8fb99`. Public deployment remains blocked by the missing existing hosting and backup allocation.

| Item | Actual status |
|---|---|
| Public staging | **BLOCKED — no suitable existing authorized allocation identified** |
| Public production | **BLOCKED — no suitable existing authorized allocation identified** |
| Actual public URL | **NOT DEPLOYED** |
| Real email delivery | **DISABLED — no real mail sent** |
| Automatic publication | **DISABLED — explicit editorial gate retained** |
| Remote Linux Docker | **PASS — nine actual runtime phases** |
| Application and proxy image scans | **PASS — zero HIGH/CRITICAL findings in each strict scan** |
| Release CI matrix | **PASS — all four Windows/Linux Python 3.11/3.12 jobs** |
| Encrypted off-host backups | **NOT CONFIGURED — no destination identified** |
| Production monitoring/schedulers | **NOT INSTALLED — procedures documented** |

The GitHub repository and its Actions runners host source and disposable verification jobs. They are not a public staging or production newsletter service. A localhost address, successful image build, synthetic publication or prepared Compose file is not a deployed public URL.

## Hosting discovery and concrete blocker

The [sanitized discovery record](engineering-evidence/hosting-discovery.json) contains the actual read-only searches:

- Replit searches for `Signal Daily` and `newsletter`: zero editable matching apps in each result.
- Vercel searches for `signal` and the repository URL: zero matching projects in each result.
- Railway and Render were discoverable but not installed at discovery. Suggestions were issued; **no installation/connection or existing resource allocation was confirmed**.
- Project configuration and relevant process environment key names identified no host access, selected public domain or off-host backup destination. Credential values were not recorded in the discovery evidence.
- Docker did not resolve on the development Windows command path. Docker **does run on the GitHub Linux verification runner**; this is not an overall Docker-unavailability claim.

These searches are scoped observations, not proof that the owner has no resources anywhere. No new account, paid service, domain, server, disk or bucket was created. No resources were purchased or provisioned. The connected tools did not establish a suitable existing authorized target with durable storage, public HTTPS, editor restrictions, automatic restart and encrypted off-host recovery.

Vercel/static hosting was not used as a substitute for the application's supported persistent architecture. No private data was moved into an unrelated connected service to manufacture a deployment result.

## Supported deployment configuration

The prepared [Compose configuration](../compose.yaml), [production transport](../production.py) and [Caddy configuration](../deploy/Caddyfile) support:

- One long-running non-root Waitress application process and exactly one writer to a persistent local SQLite volume. No ephemeral disk, NFS/SMB or multiple application replicas.
- Caddy as the sole published 80/443 ingress, private application port 8787, exact trusted proxy address and persistent certificate/configuration volumes. The [custom proxy image](../deploy/Dockerfile.caddy) replaces the stock binary with Caddy 2.11.7 built using Go 1.26.9 and `golang.org/x/net` 0.60.0.
- Strong host-only administrator/session secrets and an exact operator IP/VPN `EDITOR_CIDR`, with the editor password still required.
- `EMAIL_DELIVERY_ENABLED=false` and `ENABLE_LOCAL_GENERATION=false` on the public host. Laptop Ollama stays on loopback; drafts move through authenticated JSON import.
- Preserved draft → review → approved → published transitions. Every real edition still needs editorial judgment and deliberate publication.

This configuration is prepared, not installed on a public host. Real hostname/DNS, origin, access policy, private volume, secret injection and budget must belong to the selected existing allocation. Keep the private upstream and Ollama unreachable from the internet.

## Actual remote container and image scan evidence

The final [Linux container run 39321202556](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39321202556) completed successfully for source `aaf91a7b955323dc2928d6f9b5d9222037d8fb99`. [Stored GitHub evidence](engineering-evidence/github-aaf91a7.json) records the successful runtime step and both image scan steps. The actual runtime acceptance passed all nine phases:

1. Actual Dockerfile build on Linux.
2. Production Compose validation with synthetic configuration.
3. Non-root startup, private health probe, read-only root, resource limits and no external application network.
4. Authenticated import, approval-bypass rejection, review, approval, synthetic publication and public archive.
5. Persistence of the mounted-volume edition across an actual container restart.
6. Online backup, integrity, restoration into a separate volume, unsafe-restore rejection and preservation of consent/delivery state.
7. Actual image migration of a v1 SQLite volume to v2 without business-state loss.
8. Validation of the unmodified production Caddyfile in the actual custom Caddy image.
9. Actual Caddy proxy assertions for canonical metadata, public archive, four editor CIDR denials and the request-body limit on an isolated Docker network.

Both strict scans passed: the actual application image and the actual custom Caddy proxy image each had **zero HIGH/CRITICAL vulnerabilities** under the run's scanner/database. The Caddy binary rebuild uses the patched Go HTTP/TLS toolchain and `x/net` dependency instead of the vulnerable stock binary. This is the recorded scan result for these built images, not a guarantee against future vulnerabilities. The [release run 39321202509](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39321202509) also passed all four Windows/Linux Python 3.11/3.12 jobs at the same source commit.

The [first container-run record](engineering-evidence/container-first-failure.json) and [second container-run record](engineering-evidence/container-second-failure.json) retain earlier acceptance-driver failures for traceability. The final successful run supersedes their incomplete runtime status. These runner checks do not prove public ACME TLS, external ingress, production host reboot, production editor reachability or encrypted off-host restoration. Build the application and custom proxy with `docker compose build` before running proxy configuration validation on a selected host; see the [operations sequence](PRODUCTION_OPERATIONS.md#build-and-validate-before-start).

## Operations and recovery

[Production operations](PRODUCTION_OPERATIONS.md) documents private/external health checks, restart/boot verification, bounded Docker logs, daily encrypted off-host backup and retention, and restoration to a new database path. It explicitly distinguishes procedures from installed infrastructure.

The existing [backup tool](../tools/database_backup.py) verifies a SQLite-consistent snapshot and supports a separate restoration path. It does not encrypt, upload, schedule or prune backups. [Recovery evidence](engineering-evidence/recovery-stability.json) verifies isolated local backup/restore, rollback, concurrency and restart behavior; it is not evidence of an encrypted off-host production backup. No external monitor, operator alert channel, daily host job, off-host encryption/upload agent or retention job has been installed.

Mail remains disabled. Mock SMTP exercises consent/delivery behavior without contacting real recipients. No live SMTP credentials, sender DNS, spam/inbox placement or provider acceptance were certified. Nothing in this report asks the owner to test the application manually.

## Preserved data and owner decisions

The [environment comparison](engineering-evidence/environment-final.json) records the original private `.env` unchanged and equality of the original business tables. No unapproved real-news edition was published, no real subscriber mail was sent, and no laptop Ollama endpoint was exposed. Synthetic publication and mail tests use isolated test data/transports.

The remaining owner input concerns resources and editorial authority:

- Connect an existing suitable hosting account/allocation and approved encrypted backup storage, with no new charges. Render/Railway suggestions can enable existing-account discovery; a suggestion itself is not a connection or allocation.
- Supply the approved public origin/DNS target, editor IP/VPN range and host/backup access through the appropriate private credential mechanism. Do not put secrets in this repository or public evidence.
- Make the factual/editorial decision for real-news content before its explicit publication. Real email configuration and any actual recipient sends remain separately gated.

Engineering must then perform and record deployment, external HTTPS/editor checks, persistent restart/reboot, encrypted off-host recovery and monitoring installation on that selected host. Those are engineering tasks; they are not delegated application acceptance tests for the owner.

**Deployment verdict: STAGING BLOCKED / PRODUCTION BLOCKED / PUBLIC URL NOT DEPLOYED.** Source/runtime verification cannot replace the missing existing hosting and backup allocation.
