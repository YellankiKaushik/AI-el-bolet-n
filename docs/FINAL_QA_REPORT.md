# Signal Daily — final QA report

Audit date: **19–20 October 2026, Asia/Kolkata**. **Local automated acceptance: PASS. Ready for human acceptance. Production: BLOCKED.**

This audit independently executed the current checkout. Previous reports and CI badges were context, not evidence of this run. No GitHub push, public deployment, real-news approval/publication, real SMTP connection, real-recipient email or original database reset occurred.

## Revision and environment

| Item | Observed value |
|---|---|
| Initial branch / revision | Clean `main`, `1f428c2a200e43f930371bd0164d6f2dc530df69` |
| Audit branch | `qa/acceptance-20261019` |
| Tested source revision | `eda3ff6efc809f6ddc6f6dfe8160381b0d25050a`; reports/evidence are a subsequent local commit |
| OS | Windows; loopback-only processes |
| Python used for full suites | 3.12.14, existing `.tmp/fresh-venv/Scripts/python.exe` |
| Other interpreter | Installed Python 3.11.9 exists; `py -3` reports no registered runtime. The supported PowerShell launcher successfully selected its working fallback. This is an environment limitation, already covered in the startup guide. |
| Node / browser | Node 24.16.0; Playwright headless Chromium **151.0.7922.34** |
| Actual model | `gemma4:e4b`; Ollama reports GGUF / Q4_K_M / `parameter_size: 8.0B` for this tag. No model was downloaded or replaced. |
| Normal app | `http://localhost:8787`, bound `127.0.0.1:8787`, mail disabled |
| Final fictional workspace | `.tmp/acceptance-verified-20261019/demo.db`, served at `127.0.0.1:8790` during the audit; stopped after tests |
| Live integration workspace | `.tmp/qa-20261019/live-integration.db`, temporary server at `127.0.0.1:8792`; stopped |
| Fake SMTP browser workspace | `.tmp/qa-20261019/mail-demo.db`, temporary server at `127.0.0.1:8791`; stopped |

Existing demo data and earlier failed-run databases were preserved under separate `.tmp` names. Screenshots contain fictional editions only. Browser cookies, credentials, model inputs/drafts and raw private backups remain ignored under `.tmp`; they are excluded from Git.

## Results

| Check | Current result | Evidence |
|---|---|---|
| Before changes | **88 passed, 0 failed, 0 skipped** | [Baseline output](qa-evidence/baseline-unittest.txt) |
| Final full suite | **91 passed, 0 failed, 0 skipped** | [Final output](qa-evidence/final-unittest.txt) |
| Actual browser scenarios | **75 passed, 0 failed**; excludes protocol-only actions | [Detailed report](BROWSER_TEST_REPORT.md) |
| Additional protocol checks | 2 passed: invalid requests/transitions and synthetic pagination setup | [Main results](qa-evidence/browser-main-results.json) |
| Final fictional user journey | PASS, including actual process restart and fresh login | [Restart results](qa-evidence/browser-restart-results.json) |
| Live source / model buttons | 7 scenarios passed, using actual RSS and Gemma | [Live browser evidence](qa-evidence/live-browser.json) |
| Subscriber UI | 7 passed with fake SMTP; real UI, HTTP, consent storage and multipart construction | [Simulated transport evidence](qa-evidence/subscriber-browser.json) |
| Recovery / stability | Backup/restore, overwrite refusal, rollback, SQLite write contention/recovery, restart persistence; 48/48 concurrent requests returned 200 with eight workers | [Recovery evidence](qa-evidence/recovery-stability.json) |
| Responsive rendering | Homepage, archive, reader, editor and login at 1440×900, 768×1024, 390×844, 320×844; no document overflow | [Browser cases](BROWSER_TEST_REPORT.md), [320px reader](qa-evidence/reader-320-full.png) |
| Accessibility | Zero Axe WCAG 2.1 A/AA violations in the final nine-view survey and final main-run checks; keyboard skip link and search verified | [Nine-view survey](qa-evidence/axe-final-all.json) |
| Code quality / security tools | Ruff lint/format, Python compilation, JS syntax, Bandit, local documentation links, private-file and exact-secret scans passed | [Commands/results](qa-evidence/checks.json), [Security evidence](qa-evidence/security-final.json) |
| Dependency audit | Live OSV query: 10 pinned Python packages, **0 advisories** | [OSV result](dependency-audit.json) |

The three added unittest cases cover stale approval, stale publication and HTTP propagation of both version checks. An existing backup regression now includes fictional consent and a simulated sent-delivery ledger. Browser regressions cover color contrast, upload labeling and a deterministic long title at 320 pixels.

Initial browser runs detected failures and were not counted as final passes. One stopped on low contrast; the next exposed narrow reader overflow. Both are preserved in [initial results](qa-evidence/browser-initial-results.json), [second results](qa-evidence/browser-second-results.json) and [initial accessibility output](qa-evidence/axe-initial-all.txt). All four defects were fixed and the final complete journey was rerun from a new empty fictional database. See [bug report](BUG_REPORT.md).

## Architecture and tested user story

The browser workbench sends same-origin JSON mutations to `server.py`, which validates access and content before `db.py` transactions. Source refresh calls bounded HTTPS RSS/Atom ingestion; drafting calls loopback Ollama and validates structured output/provenance. Imports start as drafts. Saves invalidate approval, stale saves fail, and publication requires review and explicit approval. Public readers and archive queries see published rows only. `mailer.py` sends only when email is deliberately enabled; consent and delivery reservations persist in SQLite. Separate production WSGI/proxy tests exercise prepared production code without proving a deployment.

The browser performed create/import → edit every content field → save/reopen → saved preview/evidence → review → revision → approve → cancel/confirm local publication → reader/home/archive → restart → persistence/privacy checks. It also exercised validation failures, story add/remove, file upload, all dashboard tabs, source selection bounds, throttling, session tampering, logout, keyboard search and pagination. Two simulated clients reproduced stale-version races before and after the fix.

## Live RSS and local model

| Source contacted | Parsed records | Relevant/recent accepted |
|---|---:|---:|
| Hugging Face | 30 | 3 |
| MIT Technology Review | 10 | 8 |
| arXiv AI | 0 | 0 |
| The Verge AI | 10 | 8 |

All four configured HTTPS endpoints responded without collector errors. The arXiv response produced no parsed entries; reachability does not establish that it supplied usable articles. **19 accepted stories**, zero duplicates during this fetch, 19 inserted in an isolated database; reinsertion added zero. The actual browser refresh found 19 and added zero, with no errors. Configured feed URLs, accepted source URLs and publisher-supplied dates are recorded in [live integration evidence](qa-evidence/live-integration.json). Missing dates were not invented.

Actual `gemma4:e4b` generated a three-story structured draft in **15.06 seconds** through the local client. A second actual generation through the browser source-selection button produced one story in **11.954 seconds**. Both remained private **DRAFT** rows in the isolated integration database. Source identity/URL attachment and available provenance passed validation. `/api/ps` confirmed the requested local model was loaded; the configured endpoint and listening service were loopback. There was no authorized or configured cloud fallback. A separate call to an actually unavailable loopback endpoint returned the safe no-cloud-fallback error.

**No semantic fact certification is made.** RSS descriptions are incomplete evidence; neither valid JSON nor HTTP 200 establishes that a generated summary/implication is accurate. The editor still must open sources, verify dates, numbers, attribution and every substantive claim.

## Original-data safety and recovery

A read-only SQLite connection and the SQLite backup API produced a consistent private baseline backup before testing. The original contained 19 stories, two issues, two history rows, two operation rows, no subscribers, no deliveries and no persistent rate-limit rows. After normal-app startup, browser authentication/read-only inspection and all tests, **every original table digest and the `.env` SHA-256 still matched**. Counts remained identical. The original database received no RSS writes, generated drafts or publications; both actual generation samples went into a separate private integration database.

[Baseline](qa-evidence/environment-baseline.json) and [final comparison](qa-evidence/environment-final.json) expose counts and comparison booleans, not original rows/secrets. The private consistent backup is `.tmp/qa-20261019/original-backup.db`. Do not distribute it. The final fictional database contains 27 issues: 26 published synthetic editions and one private blank draft; no subscribers/deliveries. Its restored copy matched the complete dump. The mock-mail database retained one unsubscribed fictional subscriber. Tests also cover versioned migrations, single-writer locking and delivery reservations across connections.

## Security boundaries and remaining limitations

Local automated security controls passed: protected APIs, session expiry/tamper/logout/restart, CSRF/custom header/origin checks, request limits, HTML escaping, token-log redaction, private model endpoint restrictions, production host/proxy/cookie checks, source XML/URL validation and delivery reservation/uncertain-state handling. Current Git candidates were scanned for known credential signatures, private paths and exact private configuration secrets without printing their values. These checks are scoped evidence, not an exhaustive penetration test or Git-history audit.

Unresolved application defects: **none identified in the completed local scope**. External/unverified areas remain:

- Public deployment, real domain/HTTPS/certificates/ingress and external-network behavior.
- Docker/Caddy runtime and persistent-volume deployment; Docker was unavailable.
- Actual SMTP provider connection, sender SPF/DKIM/DMARC, bounce/complaint handling and inbox placement. All mail checks used simulated transport.
- Encrypted off-host disaster recovery and production monitoring/retention/operations.
- Physical devices, other browser engines, full assistive-technology review and real email-client rendering. Chromium emulation is not physical-device acceptance.
- Human editorial/factual judgment, usability preference and final visual approval. Automated Axe cannot certify complete accessibility.
- Existing documented feature limits: no autosave/navigation-loss warning, multi-editor roles/MFA/recovery, published correction/takedown UI, background mail queue or automated provider reconciliation.

Current CI was not rerun or reverified on GitHub; this was a Windows local audit. Public deployment and real SMTP remain blocked pending separate authorization and acceptance.

## Handoff and final process state

The normal application was started through `Start-Local.ps1` and health-checked after the final test-server cleanup: HTTP 200, `{"status":"ok"}`. Normal app and Ollama listen only on `127.0.0.1` (8787 and 11434). Temporary ports 8790/8791/8792 are stopped. These are background processes, not installed Windows services; persistence across reboot/app exit is not guaranteed. Exact restart commands and private-password instructions are in [manual handoff](MANUAL_TESTING_HANDOFF.md).

See [final server evidence](qa-evidence/final-servers.json), [coverage matrix](TEST_COVERAGE_MATRIX.md), [release checklist](FINAL_RELEASE_CHECKLIST.md) and [screenshot manifest](qa-evidence/screenshot-manifest.json). The starting tree was clean. Source fixes and reports are local commits on the audit branch; no push/deployment was performed. Use `git log -2 --oneline` for the source and evidence commits.

**SIGNAL DAILY — READY FOR USER ACCEPTANCE TESTING**
