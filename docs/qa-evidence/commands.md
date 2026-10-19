# Audit command record

Run from the `signal-daily` project root on Windows, 19–20 October 2026 (Asia/Kolkata). Paths below are exactly the project-relative commands used; PowerShell's call operator invokes Python. Full checker executable paths and durations are in [checks.json](checks.json).

| Command | Observed result |
|---|---|
| `git status --short`, `git branch --show-current`, `git rev-parse HEAD` | Initial clean `main` at `1f428c2a200e43f930371bd0164d6f2dc530df69` |
| `py -3 --version` | Failed: no registered Python; no app defect or machine change |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' --version` | Python 3.12.14 |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -m unittest discover -s tests -v` | Before: 88 passed; final: 91 passed; zero failed/skipped |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -m unittest discover -s tests -p test_http.py -v` | 12 targeted HTTP tests passed |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -m unittest discover -s tests -p test_release.py -v` | 43 targeted release/database tests passed |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -m ruff check .` | Passed |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -m ruff format --check .` | Passed, 28 files |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -m compileall -q db.py server.py production.py instance.py feeds.py llm.py mailer.py config.py validation.py run.py tools tests` | Passed |
| `node --check static/app.js` | Passed |
| `node --check tools/capture_screenshots.cjs` | Passed |
| `node --check tools/acceptance_browser.cjs` | Passed |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -m bandit -q -r . --exclude ./.tmp,./tests,./.venv,./data,./backups` | Passed |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' tools/check_docs.py` | Passed; includes final reports |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' tools/release_audit.py` | No private-file/known-signature findings among Git candidates |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' tools/audit_dependencies.py` | Actual OSV response; 10 pinned Python packages, zero advisories |
| `npm install --prefix .tmp/qa-20261019/browser-deps --no-save --no-audit --no-fund @axe-core/playwright` | Development-only install under ignored test directory |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -u tools/demo.py --name acceptance --port 8790 --empty` | Initial empty fictional workspace; preserved after test |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -u tools/demo.py --name acceptance-final-20261019 --port 8790 --empty` | Intermediate fresh workspace; preserved after overflow finding |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' -u tools/demo.py --name acceptance-verified-20261019 --port 8790 --empty` | Final passing fresh fictional workspace; later restarted with same command |
| `node tools/acceptance_browser.cjs` | Two initial failed runs preserved; final 48 browser and two protocol scenarios passed |
| `node tools/acceptance_browser.cjs --restart-check` | Five browser restart scenarios passed |
| `node .tmp/qa-20261019/mail_browser.cjs` | Seven browser scenarios passed with fake SMTP |
| `node .tmp/qa-20261019/live_browser.cjs` | Seven browser scenarios passed with actual feeds/local Gemma |
| `node .tmp/qa-20261019/normal_browser.cjs` | Eight normal-app/login-layout/throttle scenarios passed |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' .tmp/qa-20261019/live_integration.py` | Actual RSS + three-story Gemma draft, separate private DB |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' .tmp/qa-20261019/recovery.py` | Verified local backup/restore, rollback, zero demo deliveries and bounded concurrency |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' .tmp/qa-20261019/extra_recovery.py` | Final retry passed SQLite contention/release, post-restart dump equality and actual closed-loopback model error |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' .tmp/qa-20261019/preflight.py` | Consistent private original backup/baseline; later every original table/.env comparison matched |
| `& '.\.tmp\fresh-venv\Scripts\python.exe' .tmp/qa-20261019/final_security.py` | Exact private-secret scan and known signatures: no findings; no secrets printed |
| `.\Start-Local.ps1` (hidden child PowerShell) | Normal mail-disabled app started successfully on loopback |
| `Get-NetTCPConnection -State Listen` filtered to app/Ollama/test ports | Actual bindings were 127.0.0.1 only; after cleanup only 8787 and 11434 remain |
| `git diff --check` | Passed |
| `git switch -c qa/acceptance-20261019` | Local audit branch created |
| `git commit -m "Fix stale editorial actions, accessible forms and narrow reader layout"` | Local tested-source commit `eda3ff6`; no push |

Private `.tmp` scripts retain raw setup/state and are deliberately not committed; their sanitized JSON outputs are retained here. The main fictional browser regression harness is committed in `tools/acceptance_browser.cjs`. Background services were launched with `Start-Process -WindowStyle Hidden`, explicit loopback configuration and mail disabled (or FakeSMTP replacing the transport). No arbitrary public address or real recipient was contacted for mail.

The exploratory Axe probe first needed an explicit browser context and the contention probe needed transaction rollback before reopening a transaction. Those harness errors were corrected and rerun; they are not counted as application defects or original passes. The actual application findings are preserved in the bug report and before-fix artifacts.
