# SIGNAL DAILY — LOCAL LAUNCH REPORT

> Public copy sanitized on 20 October 2026: personal machine paths and private generated title/subject are `[REDACTED]`. The original is preserved privately; historical test counts and findings are unchanged. See the [publication summary](REPORT_PUBLICATION_SUMMARY.md).

> Historical snapshot: retain the recorded results and machine details as evidence. For current behavior, portable setup and verification, see [Project status](PROJECT_STATUS.md), [Getting started](GETTING_STARTED.md) and the [documentation release report](GITHUB_DOCUMENTATION_REPORT.md).

Date: 2026-10-19. **Local application: READY. Newsletter draft: READY FOR REVIEW.**

Signal Daily is running on this Windows laptop, with the real editor left open on draft #2. It is restricted to loopback, live email is disabled, and no real news was approved or published. No deployment, service purchase, VPS configuration or GitHub push occurred. Production readiness is a separate, deferred objective; its blockers do not prevent this local workflow.

## 1. Environment detected

| Item | Verified value |
|---|---|
| Git branch | `production-readiness`; existing Phase 2 commits retained |
| Project directory | `[REDACTED]` |
| OS | Windows 11, build 26300 |
| Working Python | Python **3.12.14**, `[REDACTED]\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` |
| Other Python commands | `python` points at the Windows Store alias; `py` exists but has no working registered runtime on this laptop |
| Existing configuration | Ignored `.env` present, administrator password/session secret present, no SMTP password configured; file hash unchanged |
| Ollama | Running at `http://127.0.0.1:11434`, bound only to `127.0.0.1` |
| Installed model tags | `gemma4:e4b` and `gemma4-lab:latest` |
| Model used | **`gemma4:e4b`**, actual generation verified; nothing installed/downloaded |
| Real database | `data/signal_daily.db`, resolved under the project directory |
| Startup entry points | `run.py` for local development; `production.py` for the separately deferred production architecture; new `Start-Local.ps1` for laptop use |

The source structure remains Python application modules (`server.py`, `db.py`, `feeds.py`, `llm.py`, `mailer.py`, `validation.py`), browser assets in `static/`, operator tools in `tools/`, regression tests in `tests/`, and reports in `docs/`. Private configuration, databases, backups, local drafts and temporary verification artifacts remain ignored. The sibling REA directory was not modified.

## 2. Startup commands and current process

The app is already running:

- Homepage: [http://localhost:8787](http://localhost:8787)
- Editorial dashboard: [http://localhost:8787/admin](http://localhost:8787/admin)
- Health: [http://localhost:8787/health](http://localhost:8787/health)

The verified listener is `127.0.0.1:8787`. The current Python process ID was **28180** at verification; process IDs can change. The startup wrapper runs hidden in the background for this session. It is not an installed Windows service or startup task and will not survive a reboot automatically. No firewall changes were made.

When the app is stopped, open PowerShell in the project directory and run:

```powershell
Set-Location -LiteralPath '[REDACTED]'
.\Start-Local.ps1
```

The launcher probes Python 3.11+, avoids the Store alias, falls back to the already installed Codex Python, preserves existing `.env`/credentials/data, and forces development mode, loopback, port 8787, local generation enabled and email disabled. It was actually used to start this app. For a future foreground launch, leave that terminal open; Ctrl+C stops it. Do not start a second copy while the current app is running; the database instance lock rejects concurrent starts.

If local script execution policy prevents the `.ps1` from running, do not change Windows security settings. Use the known executable directly:

```powershell
$env:HOST='127.0.0.1'
$env:PORT='8787'
$env:APP_ENV='development'
$env:PUBLIC_URL='http://localhost:8787'
$env:EMAIL_DELIVERY_ENABLED='false'
$env:ENABLE_LOCAL_GENERATION='true'
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" run.py
```

To stop the current background run, first verify that PID 28180 is still the Python listener on 8787 using `Get-NetTCPConnection -LocalPort 8787 -State Listen` and `Get-Process -Id 28180`; only then use `Stop-Process -Id 28180`. Do not use that old PID after restarting. Normal future foreground launches can simply use Ctrl+C.

## 3. Website and browser verification

| Check | Actual result |
|---|---|
| Homepage, archive, dashboard shell | HTTP **200** at the requested localhost addresses |
| CSS / JavaScript | HTTP **200**, correct content types; changed JavaScript actually served |
| Health | HTTP **200**, SQLite available |
| Administrator login | Browser login with existing credentials succeeded; password never printed; protected API also verified |
| Unauthenticated editor data | HTTP **401** |
| Missing page / static file / static traversal attempt | HTTP **404**, no private file content exposed |
| Real draft's newsletter URL | HTTP **404**, correctly private while unapproved |
| Synthetic newsletter reading page | HTTP **200**, verified only on isolated port 8788/database |
| Public archive search | Synthetic edition indexed; unmatched search showed a readable empty state |
| Responsive rendering | Homepage/editor/reading page/archive inspected; measured mobile, tablet and desktop document widths **417 / 836 / 1405 CSS px**. Mobile/tablet checks had no page-wide horizontal overflow; tabs can scroll within their tab bar. Temporary viewport overrides were reset. |
| Browser diagnostics | Zero captured JavaScript errors/warnings in the checked real and synthetic tabs |

The real homepage/archive are intentionally empty of editions: no real newsletter has been published. This is correct behavior, not missing data. The private editor shows both real drafts.

## 4–6. RSS, Gemma and draft generation

Fresh RSS collection ran through **Source feed → Refresh news sources** in the actual browser. The recorded result was **0 new stories added; 0 feed errors** at 09:09:34 UTC. Existing URLs were already cached, so deduplication retained all **19 stories** without deleting or replacing them.

Five source stories were selected in the dashboard and **Generate selected with Gemma** called the installed local model. The request produced a complete newsletter and saved it directly as **draft #2**. No manual fake model output or cloud fallback was used.

| Draft detail | Value |
|---|---|
| Title | **[REDACTED]** |
| Email subject | [REDACTED] |
| Generated | **2026-10-19 09:10:40 UTC / 14:40:40 IST** |
| Story count | **5** |
| Source coverage | Hugging Face: 2; MIT Technology Review: 1; The Verge AI: 2 |
| Source publication dates | **2026-10-13 through 2026-10-17** |
| Model | `gemma4:e4b`, local Ollama |
| State | **DRAFT**, version 1; creation event only; no review/approval/publication event |
| Dashboard location | `/admin` → **Editions** → **[REDACTED]** → **EDITION #2 / DRAFT** |
| Database location | `data/signal_daily.db`, issue ID 2 |
| Private JSON copy | `local-drafts/local-review-2026-10-19.json` |

The draft contains a title, subject, short introduction, five headlines/summaries/why-it-matters sections, original source links and a closing note. Complete JSON validation passed. Every source URL and source title/name matches the collected database record; all five links returned **HTTP 200** with HTTPS certificate validation and safe redirect handling.

Source links for your editorial check:

1. [Beam model announcement, 16 October](https://huggingface.co/blog/reflection-beam)
2. [Muse Spark Open, 15 October](https://huggingface.co/blog/meta-muse-spark-open)
3. [Open model benefits and risks, 13 October](https://www.technologyreview.com/2026/10/13/1146366/open-models-have-real-benefits-do-they-outweigh-the-risks/)
4. [Meta terms update, 17 October](https://www.theverge.com/tech/1013409/meta-removes-language-that-may-have-allowed-it-to-scrape-news-sites)
5. [Website restrictions on AI agents, 16 October](https://www.theverge.com/ai-artificial-intelligence/1013195/ai-agents-blocked-web)

Reachability and schema/source checks are not editorial verification. The model used source headlines/descriptions, which can be incomplete; two selected Hugging Face feed records contain only headline evidence. Check original authorship, open-weight versus open-source licensing, numeric claims and the summaries' implications yourself. No source claims were approved on your behalf.

## 7. Editorial workflow results

A second server on **127.0.0.1:8788** used only `.tmp/phase3-ui.db` and explicitly disabled SMTP/local generation. Browser automation used clearly labeled synthetic content; it never pointed publication actions at port 8787.

Verified through the actual UI:

1. Invalid JSON showed **Enter valid JSON**, without saving a draft.
2. A synthetic import claiming `status=published` still became **DRAFT**.
3. Opening, editing and **Save as draft** persisted changed content.
4. **Preview saved edition** showed the saved text and source link.
5. Draft/review states did not offer publication; server regression tests also rejected premature publication.
6. **Submit for review → Approve reviewed edition** exposed the publication control.
7. An unsaved change disabled publication; saving reset the approved edition to **DRAFT** and required another review/approval.
8. Only the synthetic revision was published; the mail-off confirmation stated no messages would be sent. The resulting reading page and archive were verified, published fields were immutable and unavailable email retry controls were hidden.

The isolated server was stopped and its tab closed. Its SQLite fixture remains ignored for local evidence. No synthetic edition, subscription or delivery was inserted into the real database.

## 8. Database preservation

A consistent, validated SQLite backup was created **before startup** at `backups/phase3-before-local-launch.db`. Its logical state matched the Phase 2 fingerprint. Startup applied the existing version 2 throttle migration; all pre-existing rows were compared by ID and full row contents and remain identical, including draft #1 and its history.

| Records | Before | After | Explanation |
|---|---:|---:|---|
| Stories | 19 | 19 | All original rows preserved; fresh collection deduplicated |
| Issues | 1 | 2 | One newly requested real-news draft added |
| Published issues | 0 | 0 | No real publication |
| Subscribers | 0 | 0 | No real registration or deletion |
| Deliveries | 0 | 0 | No real email |
| Issue events | 1 | 2 | Creation events only |
| Operations | 1 | 2 | Fresh RSS ingestion log added |
| Schema | 1 | 2 | Additive persistent-throttle migration |

`PRAGMA integrity_check` and foreign-key validation passed. `.env` remained byte-for-byte unchanged. No model files were modified. The final verifier initially compared different SQLite row representations incorrectly; correcting that verification script resolved the false failure. Rechecked integrity and full-row preservation both passed; no database repair/reset was needed.

## 9. Email simulations

Live SMTP remains **disabled** in the running app, confirmed by its authenticated status response. No external SMTP connection or real email was made. The 80-test suite exercises registration, expiring/one-use confirmation tokens, multipart HTML/plain-text templates, TLS mode/config validation, active-subscriber targeting, duplicate reservations, ambiguous sends, unsubscribe GET safety and confirmation POST. These use **isolated databases and mocks**, including the full flow through real Waitress HTTP with mocked TLS SMTP. They do not prove real inbox delivery.

## 10. Automated test results

| Check | Result |
|---|---|
| Before-change suite | **77 passed, 0 failed** |
| Final suite | **80 passed, 0 failed/errors** |
| New regressions | Mail-off local default, rejection of public binds, preservation of existing credentials |
| Ruff lint | Passed |
| Ruff formatting | Passed |
| Python compilation | Passed |
| `node --check static/app.js` | Passed |
| Bandit | Passed, no findings |
| Private-file/known-secret audit | Passed, no findings |

All seven verification commands returned exit code 0. Tests used the working Python 3.12.14, workspace-local temporary files and the previously installed pinned development checkers. No CI push was made. Evidence: [local-launch-test-evidence.txt](local-launch-test-evidence.txt) and [local-launch-validation.json](local-launch-validation.json).

## 11. Issues found and fixed

- **Windows startup:** Store Python alias/empty `py` registration made ordinary startup unreliable. Added and actually used `Start-Local.ps1` with interpreter probing/fallback, explicit loopback settings and email disabled.
- **Unsafe local bind possibility:** `run.py` now rejects non-loopback hosts and defaults email off. Existing secrets are preserved; production startup remains separate.
- **Incorrect selected dashboard tab:** Generated/imported drafts opened while the source/import tab remained highlighted. Editor navigation now selects **Editions**; verified with the actual synthetic import and real draft opening.
- **Misleading state count:** The counter included all unpublished states but said **IN REVIEW**. It now says **UNPUBLISHED**.
- **Mail-off publishing confusion:** The UI promised subscriber mail and displayed an unusable retry action when mail was disabled. It now shows **Publish online only**, a no-email confirmation and no unavailable retry button. This does not expose the local server to the internet; “online” means readable through this running website.

No layout rewrite was necessary. Readability, mobile wrapping, form feedback and source links passed the browser checks.

## 12. Remaining limitations

There are **no blocking technical issues for local editorial review**. Human fact-checking and approval remain mandatory. Email delivery/subscriptions are intentionally unavailable, and public hosting/HTTPS/Docker/live SMTP remain deferred. Keep the app and Ollama on loopback; do not use tunnels, public binds or port forwarding.

The laptop must stay awake with the app and Ollama running. The app uses a development server and one local SQLite instance, not a Windows service or production host. Restarts invalidate editor sessions. Backups remain local and should be copied to your own protected backup storage; no backup scheduler was installed. Published editions are immutable and there is no takedown UI. Browser preview shows the saved revision, so save before previewing; unsaved changes can be lost when navigating away.

## 13. Exactly how to use it now

1. Open [http://localhost:8787/admin](http://localhost:8787/admin). The current app is already running. If login is requested, read **ADMIN_PASSWORD** privately in the existing `.env` file and enter it; do not share it. The app does not have a separate username.
2. Under **Editions**, select **[REDACTED]**. Confirm **EDITION #2 / DRAFT** and five stories. Your older **AI Model Updates** draft is also preserved.
3. Expand **Preview saved edition** and each collected-source evidence section. Open all five original links and check every claim, attribution, number and implication.
4. Make your changes and select **Save as draft**, then reopen the saved preview. Check the title/subject and all five stories. No publication is necessary to read the private preview.
5. Only after your own editorial decision, select **Submit for review**, recheck, then **Approve reviewed edition**. Phase 3 deliberately did neither to real content.
6. If you personally want the edition readable on this laptop's homepage/archive, select **Publish online only** and confirm. Email remains disabled. This changes the edition to immutable published state; it does not deploy it publicly. You can leave it a draft indefinitely.
7. For future drafts: **Source feed → Refresh news sources → select relevant stories → Generate selected with Gemma**. Keep Ollama running locally. Alternatively generate a private JSON file with `tools/local_generate.py` and use **Import local draft**.

**SIGNAL DAILY — LOCAL NEWSLETTER READY FOR EDITORIAL REVIEW**
