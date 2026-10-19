# Test report

> Historical local-engineering audit, recorded before GitHub publication. See [the publication report](GITHUB_PUBLICATION_REPORT.md) for the later Git operations and verification.

Date: 2026-10-19, Asia/Calcutta. No real subscriber emails or external publication occurred. Full final test output: [test-evidence.txt](test-evidence.txt).

## Environment and execution history

- PATH `python.exe` was the inaccessible Windows Store alias; the attempted baseline command could not launch.
- `py --list-paths` reported no installed Pythons.
- Codex's bundled interpreter ran Python **3.12.14**. Its path is `%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
- First bundled-runtime run: four discovered tests errored in setup and HTTP class setup failed because sandbox temporary SQLite files could not open; cleanup also hit access errors. No application verdict was taken from this run.
- With `TMP`/`TEMP` pointing to the project `.tmp`: four core tests passed; the HTTP test failed on WinError 10013 (restricted loopback sockets).
- With authorized local networking: the unchanged baseline passed **5/5**.
- First expanded run: **40 tests, 39 passed, 1 error**. Root cause: the migration test fixture used SQLite's context manager without closing the connection, leaving the legacy file locked on Windows. Fixed using `contextlib.closing` and explicit commit.
- Next expanded run: **50/50 passed**.
- Configuration/XML/template coverage run: **54/54 passed** in 3.272 seconds.
- Final run after citation and delivery-ledger regressions: **56 passed, 0 failed, 0 errors, 0 skipped**. The exact timing is recorded at the end of `test-evidence.txt`.

PowerShell execution used the bundled interpreter, a writable project `.tmp` directory and authorized loopback networking:

```powershell
$Python = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$env:TMP = Join-Path (Get-Location) '.tmp'
$env:TEMP = $env:TMP
& $Python -m unittest discover -s tests -v
```

## Final suites

| Suite | Tests | Coverage |
|---|---:|---|
| `test_core.TestCore` | 4 | RSS/Atom parsing, dedupe, workflow, unsafe URL rejection, rejecting unknown model IDs. |
| `test_http.TestHTTP` | 11 | Full editor/subscriber flow, auth/authorization, CSRF, login throttling, logout replay, expiry/single-use links, generic duplicates, unsubscribe token stability, missing SMTP, public routes/search, ingest/generation workflow through HTTP. |
| `test_release.TestFeeds` | 6 | Atom alternate links, XML rejection, recency/relevance, private destinations, retry and collection limits. |
| `test_release.TestGeneration` | 6 | Actual provider request shape, provenance, unknown/duplicate/non-integer IDs, missing fields, numeric claims, network/timeout/JSON/size errors, concurrency bound. |
| `test_release.TestPersistenceWorkflow` | 14 | Mandatory review/approval, incomplete drafts, edit/revision resets, stale saves, history snapshots, persistence/init, search privacy/SQL values, canonical dedupe, atomic claims, delivery retries/uncertainty/consent, legacy migration. |
| `test_release.TestSecurityAndMail` | 9 | Email/URL checks, sessions, production defaults, multipart/TLS/header handling, missing SMTP, unpublished-email rejection, uncertain SMTP, escaping and token-log redaction. |
| Additional configuration/generation/ledger classes | 6 | Exclusive secret setup, BOM/env precedence, UTF-16 XML bypass, real newsletter template, inline citation rejection, ledger failure after accepted SMTP. |

## Complete local workflow evidence

The HTTP tests use the actual request handler, loopback HTTP, signed session cookies and temporary SQLite files. RSS transport/model responses/SMTP are external-service doubles where noted.

1. A test RSS collection response goes through `/api/admin/ingest` and real SQLite source storage.
2. `/api/admin/draft` calls the actual Ollama client with a fake HTTP response; source attribution survives persistence.
3. Publishing is rejected before approval; approval is rejected before review.
4. Explicit review → approval → publication succeeds, and the edition appears on public routes/archive.
5. A subscriber registers through HTTP and the confirmation transport is intercepted. Opening the real confirmation route activates the record; expired/reused links do not.
6. The delivery workflow dispatches only to active confirmed records, records results, retries safe failures and excludes duplicates. Template tests execute the actual multipart construction against a fake SMTP connection.
7. Unsubscribe GET preserves consent; POST changes it. A newly published future fixture edition sends nothing to the unsubscribed record.
8. Concurrency tests issue eight competing reservations across four threads and confirm exactly one succeeds.
9. An SMTP acceptance followed by failed ledger persistence leaves the reservation non-retryable. Ambiguous disconnects also remain excluded until reconciliation.

## Real and simulated integrations

| Boundary | Evidence | Mode |
|---|---|---|
| Four configured RSS endpoints | 19 relevant recent records, no feed errors | Real outbound HTTPS |
| Ollama model inventory | `gemma4:e4b`, `gemma4-lab:latest`; base metadata 8.0B | Real local `/api/tags` |
| Gemma generation | Two-story validated output, 52.84 seconds; final-validator real-model recheck passed in 14.17 seconds | Real local model, no cloud fallback |
| SQLite schema/state/persistence | Temporary databases plus actual local database with 19 fetched records and one unapproved Gemma draft; legacy migration, foreign keys, concurrency | Real SQLite |
| HTTP routes/cookies | Loopback test server, actual handler/client | Real HTTP |
| Subscription/delivery transport | Fake SMTP/client dispatch; zero real emails | Simulated external transport |
| OSV advisory check | 9 pinned developer packages, zero returned advisories | Real public OSV API |
| REA CLI | Exit 1: compiled runtime missing | Real availability probe; no captures |

Artifacts: `integration-evidence.json`, `dependency-audit.json`, `bandit-results.json`, `release-audit.json`, `final-startup-evidence.json`, `test-evidence.txt` and `screenshots/`.

## Other executed checks

| Command/check | Result |
|---|---|
| `python -m ruff check .` | PASS after unused-import cleanup and formatting. Initial style pass found 242 findings; eight were auto-fixed, and formatting resolved the remaining statement-layout findings. Later new-file formatting findings were corrected before release. |
| `python -m ruff format --check .` | PASS, all 16 Python files formatted. |
| `python -m compileall -q ...` | PASS for runtime modules, tools and tests. |
| `ast.parse(..., feature_version=(3,11))` | PASS for all 16 Python files; syntax compatibility only, not a Python 3.11 runtime test. |
| `node --check static/app.js` | PASS on Node 24.16.0. |
| `python -m bandit -q -r . --exclude ./.tmp,./tests,./.venv,./data` | PASS: zero remaining findings/errors after fixes and reviewed local suppressions. |
| `python tools/audit_dependencies.py` | PASS: zero OSV advisories for 9 exact pinned developer packages; application has zero third-party runtime packages. |
| `python tools/release_audit.py` | PASS: no known credential/private-file findings among Git push candidates. Not an exhaustive secret proof. |
| Git ignore checks | PASS for `.env`, environment variants, database, local model draft and fixture database. |
| `git diff --check` | PASS; final check also uses intent-to-add source entries so new files are included. |
| `python tools/setup_local.py` | PASS, created private ignored configuration without printing credentials. Regression test verifies no overwrite. |
| Local startup | PASS: final real `run.py` with the actual .env/database; homepage/archive/health 200, unauthorized admin 401, real unapproved draft hidden. `final-startup-evidence.json`. |

The initial Bandit pass found six issues: two low-confidence SQL-construction warnings, XML import/parse warnings, a catch/pass date parser and a URL-opening warning. SQL now uses fixed parameterized statements; the XML boundary gained strict encoding/DTD checks; date parsing no longer silently passes; Ollama enforces a loopback HTTP(S) endpoint. Local `nosec` comments cover guarded XML parsing, validated URL opening and the developer-only fixed Git subprocess. These are explicitly reviewed suppressions, not proof of absence of vulnerabilities.

## Browser checks

Codex browser tools exercised homepage/archive navigation, server-side search and empty results, protected editor login, blank-draft creation, dynamically labelled story fields, review, approval, unsaved-edit publication blocking and return-to-draft revision. A label-ID collision found during dynamic story testing was corrected and reverified. A cached script initially obscured that change; asset URLs now carry a modification version.

Mobile edition reading and the editor layout were also checked at actual width 434 with no overflow. Screenshots record synthetic local fixtures. Requested widths 390/768/1440 produced actual CSS widths **434/853/1600** because of browser-provider scaling. Document widths were **417/836/1583** respectively: no horizontal overflow. No captured browser console warnings/errors remained. These are responsive desktop/tablet/mobile layout smoke checks, not proof of an exact physical device viewport.

## Not executed / limits

- Real SMTP credentials, sender DNS, inbox acceptance, client-specific email rendering, bounces and complaints: no account/configuration, and no authorization to send real bulk mail.
- Docker build/compose: Docker absent from PATH.
- Hosted CI matrix and Python 3.11 execution: no remote push or second local interpreter. Workflow is defined; only local Python 3.12.14 execution is verified.
- Static type checking: no established annotated type contract/type-check configuration in the existing dynamic Python application; not claimed as passed. Syntax, lint and behavioral checks were executed instead.
- REA runtime captures: missing `dist`/dependencies; no setup/configuration installation performed.
- Reference signup submission/mobile behavior/private backend: intentionally outside passive public-page evidence.
- Public deployment, TLS, restores, penetration/load testing and OS scheduling: not configured. The collection CLI was executed once successfully against the actual local database. No production throughput or deliverability claim.
