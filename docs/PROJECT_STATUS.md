# Project status

Signal Daily works as a local, single-editor newsletter application. **The public newsletter service is not deployed.** GitHub source publication, laptop execution, public website hosting and real email delivery are separate outcomes.

The [documentation release report](GITHUB_DOCUMENTATION_REPORT.md) is the current source/CI verification record. [Historical reports](HISTORY.md) retain their original dates, test counts and environment limitations; they are not current status assertions.

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
| Demo / docs | Isolated fictional workspace, six real browser screenshots, beginner/manual/configuration/troubleshooting guides and link/image audit |
| Quality | Local automated suite and lint/security checks; exact final counts and hosted matrix outcome in the release report |

## Implemented but not externally accepted

| Prepared component | Still required |
|---|---|
| Waitress/Caddy/Compose architecture | Actual Docker image/volume/restart/migration test and Caddy configuration/runtime validation |
| HTTPS/proxy/cookie protections | Real approved domain, certificate, ingress, trusted-client and operator-IP checks from separate networks |
| SMTP support | Approved sender/provider credentials, DNS authentication and consented single-mailbox/inbox acceptance |
| Backup tool | Encrypted off-host storage, retention/scheduler/alerting and timed disaster recovery on the intended host |
| Browser responsiveness | Desktop/mobile emulation and screenshots passed; physical devices/email-client rendering/accessibility audits are broader work |

Docker/Linux hosting were unavailable on the development laptop; source presence is not container verification. CI can verify Linux application tests without proving deployment infrastructure. Live email is deliberately disabled locally.

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

Prioritize local manual acceptance with the fictional workspace, then fix reproducible usability failures. Add correction/retention and mail-operation controls before inviting public subscribers. Durable delivery workers and independent roles make sense only with clear requirements/evidence. Roadmap items are not promised dates or completed functionality.

## Public pilot blockers

1. Separate authorization for hosting and real email; source-push authorization does not deploy the service.
2. Maintained host/domain/firewall/operator access and verified container/HTTPS ingress.
3. Encrypted off-host recovery, monitoring and disk/retention procedures.
4. Publisher identity/privacy/contact information, correction/takedown policy and consent/complaint operations.
5. Approved sender DNS and live mailbox acceptance if email is included; keep mail off otherwise.
6. Human source review and deliberate approval of each real edition.

Use [PRODUCTION_RUNBOOK.md](PRODUCTION_RUNBOOK.md) for future controlled deployment preparation. The current recommended next task is **local manual acceptance testing**, not purchasing hosting or sending subscriber mail.
