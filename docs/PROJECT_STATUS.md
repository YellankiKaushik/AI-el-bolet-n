# Project status

Signal Daily works as a local, single-editor newsletter application. **The public newsletter service is not deployed.** GitHub source publication, laptop execution, public website hosting and real email delivery are separate outcomes.

The [final engineering report](FINAL_ENGINEERING_REPORT.md), [test results](FINAL_TEST_RESULTS.md) and [completion checklist](PROJECT_COMPLETION_CHECKLIST.md) are the current verification record, dated 20 October 2026. [Historical reports](HISTORY.md), including the earlier documentation and QA reports, retain their original dates, counts and environment limitations.

## Implemented and tested

| Area | Evidence / boundary |
|---|---|
| RSS/Atom and dedupe | Parser/transport/filter tests plus actual local RSS collection; feeds can fail or provide no relevant records |
| Local Gemma drafting | Real `gemma4:e4b` generation on the laptop, structured-output/provenance checks; no cloud fallback |
| Editor | Manual/import/generated drafts, editing, saved preview/evidence/history, stale-save and dirty-state controls |
| Approval | Draft → Review → Approved → Published; save/revision resets approval; published immutable |
| Reader site | Homepage, published edition pages, searchable/topic/paginated archive and sitemap; drafts hidden |
| Consent and mail logic | Registration/expiry/confirmation/unsubscribe, multipart templates, TLS settings, active-only/duplicate/uncertain delivery tests with mocked SMTP |
| Storage/recovery | SQLite migrations, WAL-aware backup, separate-path restore/integrity checks, process restart and instance locking |
| Laptop startup | Working Windows Python detection, loopback-only local entry and email disabled |
| Demo / docs | Isolated fictional workspaces, fresh responsive browser captures, beginner/configuration/troubleshooting guides and link/image audit |
| Quality | 97 automated tests and 75 fresh browser scenarios passed, plus two protocol checks; Windows/Linux Python matrix passed |
| Docker / Caddy | Actual Linux image build, nonroot/read-only/resource/log controls, workflow, restart, separate-volume restore/migration and internal proxy acceptance passed; app and patched proxy HIGH/CRITICAL scans passed |

## Implemented but not externally accepted

| Prepared component | Still required |
|---|---|
| HTTPS/proxy/cookie protections | Real approved domain, certificate, ingress, trusted-client and operator-IP checks from separate networks |
| SMTP support | Approved sender/provider credentials, DNS authentication and consented single-mailbox/inbox acceptance |
| Backup tool | Encrypted off-host storage, retention/scheduler/alerting and timed disaster recovery on the intended host |
| Browser responsiveness | Desktop/tablet/mobile/narrow-mobile emulation, Axe and keyboard checks passed; physical devices and real email-client rendering remain outside the verified scope |

Docker/Podman and WSL were unavailable locally. The authorized GitHub Linux runner executed the actual container and Caddy acceptance and strict image scans successfully. No suitable existing production host or encrypted off-host storage was found through scoped integration/configuration discovery. Public HTTPS and installed operations remain blocked. Live email stays disabled.

## Not implemented

- Multiple editor accounts/roles, MFA, account recovery or independent two-person approval.
- Subscriber list/import/export/deletion UI and automatic retention/purge controls.
- Automatic bounce/complaint webhook or provider suppression synchronization.
- Durable/background send queue, distributed scheduling, multi-host SQLite, failover or availability guarantees.
- Automatic remote JSON upload, scheduled approval/publication or an installed OS task.
- Published-edition edit/correction/takedown UI, autosave or unsaved-navigation warning.
- Guaranteed semantic fact verification, arbitrary full-article extraction or a cloud-model fallback.
- Successful REA runtime capture/private backend analysis.

## Planned work

Connect an existing suitable host and backup allocation, then execute the staging and external HTTPS/recovery acceptance in the [deployment report](FINAL_DEPLOYMENT_REPORT.md). Local application acceptance has already been automated and executed; no owner manual application QA is required. Correction/retention and mail-operation controls remain necessary before inviting public subscribers. Roadmap items are not completed functionality.

## Public pilot blockers

1. An accessible existing host with durable private storage and approved origin/editor-access policy. Deployment to a suitable existing target is authorized; new charges require separate approval.
2. Actual staging and public HTTPS/ingress/restart acceptance on that host.
3. Installed and verified encrypted off-host recovery, monitoring and disk/retention procedures.
4. Publisher identity/privacy/contact information, correction/takedown policy and consent/complaint operations.
5. Approved sender DNS and live mailbox acceptance if email is included; keep mail off otherwise.
6. Human source review and deliberate approval of each real edition.

Use [PRODUCTION_OPERATIONS.md](PRODUCTION_OPERATIONS.md) and [PRODUCTION_RUNBOOK.md](PRODUCTION_RUNBOOK.md) for controlled deployment. The remaining owner input is infrastructure/access, any separately approved spending and real-news editorial judgment. No public URL or actual SMTP delivery is claimed.
