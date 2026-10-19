# GitHub push checklist

> Historical local-engineering audit, recorded before GitHub publication. See [the publication report](GITHUB_PUBLICATION_REPORT.md) for the later Git operations and verification.

Audit date: 2026-10-19. **Source readiness: READY**, contingent on the final evidence files retaining their passing results. **Production deployment readiness: BLOCKED** for the reasons below. No remote repository was created or pushed.

| Requirement | Status | Evidence |
|---|---|---|
| Essential source/configuration present | PASS | Runtime modules, static assets, tools, example config, tests, README and reports exist; release audit checks essentials. |
| Local Git initialized | PASS | `git init -b main` in signal-daily; no parent workspace repository. |
| Secrets/private data excluded | PASS | `.env*` except `.env.example`, database/WAL files, data/, local-drafts/, .tmp/ and tooling ignored. `git check-ignore` verified key paths. |
| Known credential signatures in push candidates | PASS | `release-audit.json`: zero findings. Scope is known patterns/private file rules, not an exhaustive guarantee. |
| Actual local credentials handled privately | PASS | setup_local.py created `.env` using exclusive create and random secrets; values were not printed or staged. |
| No runtime dependency lock missing | PASS | Zero third-party runtime packages; Python 3.11+ standard library and bundled SQLite. |
| Developer dependencies reproducible | PASS | Exact pins in requirements-dev.txt; installation executed in ignored temporary checker directory. |
| Dependency advisory audit | PASS | Nine developer pins queried against OSV, zero returned advisories; dependency-audit.json. |
| Unit/integration tests | PASS | 56/56 passed, no skips/errors; test-evidence.txt. |
| Approval/authorization gates | PASS | HTTP rejects unauthenticated mutation, draft publication and approval before review; state-machine tests cover revisions. |
| Subscriber confirmation/unsubscribe | PASS | Expiry, one-time use, duplicates, stable unsubscribe link, POST confirmation and exclusion from future editions tested. |
| Delivery idempotency | PASS | Atomic concurrent claims, failed retry, sent/in-flight/uncertain exclusion and ledger-write failure tests. |
| Persistent storage and upgrade | PASS | Real SQLite persistence, idempotent init, original-schema migration preserving rows, foreign-key check. |
| Local Gemma | PASS | Actual gemma4:e4b inventory and two successful real generation runs; integration-evidence.json. |
| Live RSS | PASS | Four feeds, 19 relevant recent records, no errors during the recorded run. |
| Local startup/public routes | PASS | Real run.py preview and HTTP route/health tests. |
| Browser desktop/tablet/mobile smoke | PASS | Original design, search, editor workflow, no overflow, screenshots; actual CSS widths documented. |
| Python lint/format/syntax | PASS | Ruff check/format, compileall and Python 3.11 grammar validation. |
| JavaScript syntax | PASS | `node --check static/app.js`. |
| Security scanner | PASS | Bandit final zero findings/errors with documented reviewed suppressions. |
| New-file whitespace/diff audit | PASS | Final `git diff --check` after intent-to-add includes new source files. |
| README and required six reports | PASS | IMPLEMENTATION_REPORT, TEST_REPORT, ISSUE_REPORT, REA_ANALYSIS, DEPLOYMENT_GUIDE, GITHUB_PUSH_CHECKLIST. |
| REA source remains unrelated/untouched | PASS | Read-only repository/docs inspection and failed availability probe; no REA file edits. |
| Working REA runtime/capture | NOT VERIFIED | Missing dist/node_modules; explicitly not claimed. Not an app runtime dependency. |
| Docker build | NOT VERIFIED | Docker absent from PATH; does not block Python source readiness. |
| Hosted CI / Python 3.11 execution | NOT VERIFIED | Workflow defined but not remotely executed; local runtime was 3.12.14. |
| Static type checking | NOT VERIFIED | Existing Python has no established annotated contract; not represented as a passing check. |
| Real SMTP/mailbox acceptance | NOT VERIFIED | No credentials, sender DNS or approved real send. Production dependency. |
| Production host/HTTPS/backups/serving hardening | NOT VERIFIED | No deployment performed. Production dependency. |
| Initial commit and remote push | NOT VERIFIED | Intentionally not committed/pushed; source is available for review first. |

No known unresolved Critical/High source issue or failing required local check remains. Open operational and verification limits are all listed in ISSUE_REPORT.md. A scanner pass is not a claim of penetration-test coverage.

## Before a later authorized push

1. Review `git diff` and the reports; confirm `.env`, databases, local model drafts and test tooling remain excluded.
2. Run the README release checks again if source or dependencies change.
3. Set your Git identity if necessary; create the initial local commit after review.
4. Create/choose a remote and push only after explicit authorization. Do not add `rea-main` as application source.

## Before production launch

Resolve SMTP/sender DNS and a consented mailbox test, HTTPS hosting, private persistent backups/restore, serving-layer/edge hardening, load checks and operational mail handling. Keep Ollama on the laptop and import drafts through authenticated HTTPS. Code readiness does not satisfy these deployment requirements.
