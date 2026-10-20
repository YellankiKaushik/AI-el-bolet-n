# Signal Daily — master report index

Inventory date: **20 October 2026, Asia/Calcutta**. Start with [Complete project status](COMPLETE_PROJECT_STATUS.md) for the consolidated assessment and [Report publication summary](REPORT_PUBLICATION_SUMMARY.md) for this documentation release. This index navigates the full baseline document set; it does not claim a new application, browser, model or deployment test execution.

**Current boundary: local/source acceptance is supported by retained evidence; public staging and production are BLOCKED; no public website is deployed; real email is DISABLED.** Human factual review and explicit approval remain necessary for real editions. The latest mission does not assign manual application retesting to the owner.

## Inventory, copies and revisions

The [machine-readable inventory](reports/inventory.json) records **39 unique canonical Markdown files already tracked on GitHub** at discovery. The physical discovery count was **91 Markdown copies**: 39 canonical files, 25 copies in a fresh-source working tree, 25 in a remote-verification working tree, one release README copy and one parent-workspace readiness-report duplicate. The **52 working/external copies are excluded** from canonical report totals. This index, `COMPLETE_PROJECT_STATUS.md` and `REPORT_PUBLICATION_SUMMARY.md` add three canonical documents, giving **42 canonical Markdown files for this publication**. The tables below contain the 39 baseline files exactly once; the three new entry points are identified here instead of adding a circular self-table.

Generated dependency documentation, private `.tmp` contents, credentials, databases, backups and drafts are outside the public report inventory. Supporting JSON, text logs and screenshots are evidence artifacts, not additional Markdown reports. The inventory separately records 374 discovered supporting-artifact copies and 156 supporting artifacts already published at the baseline; six selected prior-run evidence JSON files are retained under `reports/evidence`. The unrelated sibling REA source tree is not Signal Daily's report set. The parent readiness report is a local duplicate of the tracked historical report from its `Date:` line onward, not a missing independent report.

Revision labels used below:

- **R — runtime-change revision:** `aaf91a7b955323dc2928d6f9b5d9222037d8fb99`. The final engineering reports associate fresh local acceptance with this source; its actual remote container and image checks passed.
- **D — published report baseline:** `d7494f9a6d8f27d2bb0a76342e7925193b96cb0c`. It directly follows R with reports/evidence and documentation changes. Public `main`, local `main` and `origin/main` matched D at discovery. D also passed its own retained release/container/image CI, documented below. D is not the future SHA of this new index.
- **Q — historical QA source:** `eda3ff6efc809f6ddc6f6dfe8160381b0d25050a`. Its reports/evidence followed in `9a7156f` and selected corrections in `50dd84d`.
- **Doc source** identifies a document's recorded Git provenance, not an assertion that its content was runtime-tested at that SHA. Where a tested source SHA was not recorded, the table says so. Undated guides use their Git source date, explicitly distinguished from a document date.

All 39 baseline Markdown paths occur in current main and reachable history. No deleted/history-only Markdown path or branch-exclusive report was found. Local `production-readiness` at `1f428c2` and `qa/acceptance-20261019` at `ce55b39`, plus all locally reachable commits, were ancestors of public main at D. Historical statements about unpushed changes describe their original snapshots; they are not the current publication state.

Status labels describe the cited record: **CURRENT** points to the latest assessment; **HISTORICAL** preserves an earlier execution; **REFERENCE** is guidance rather than a test result; **PROCEDURE** is an operational instruction rather than installed infrastructure. A report's PASS applies only to its recorded scope. The publication privacy pass sanitized nine public files; unsanitized originals were retained privately. Historical counts, dates and failure outcomes are preserved, with private machine details removed from public copies.

## A. Project Implementation

| Report | Engineering Phase | Date | Code Revision | Status | Main Findings | Unresolved Issues | Link |
|---|---|---|---|---|---|---|---|
| README.md | Product entry point | Undated; Git updated 20 Oct 2026 | Doc D; runtime R | CURRENT | Product, setup and current 97-test/75-browser summary | Public host and mail acceptance absent | [Open](../README.md) |
| FINAL_ENGINEERING_REPORT.md | Final autonomous engineering | 20 Oct 2026 | Runtime R; report D | CURRENT | 97 automated tests, fresh 75 browser cases, nine runtime phases and both image gates passed | Infrastructure BLOCKED; mail DISABLED | [Open](FINAL_ENGINEERING_REPORT.md) |
| PROJECT_STATUS.md | Product readiness | Record dated 20 Oct 2026 | Doc D; runtime R | CURRENT | Separates implemented/local features from public operations | No public host, off-host recovery or live SMTP acceptance | [Open](PROJECT_STATUS.md) |
| IMPLEMENTATION_REPORT.md | Initial implementation audit | 19 Oct 2026 | Tested SHA not recorded; introduced `2115029`, doc `c18d2b5` | HISTORICAL | Original architecture and 56-test engineering improvements | Historical limits superseded by later reports | [Open](IMPLEMENTATION_REPORT.md) |
| ARCHITECTURE.md | Technical reference | Undated; Git 19 Oct 2026 | Doc `c18d2b5`; tested SHA not recorded | REFERENCE | Single-writer SQLite, local model, workflow and hosted boundary | Older runtime-verification wording needs later evidence context | [Open](ARCHITECTURE.md) |
| USER_GUIDE.md | Product operation | Undated; Git 19 Oct 2026 | Doc `47f6907`; tested SHA not recorded | REFERENCE | Reader/editor actions and deliberate approval/publication | Human factual decisions and provider operations remain external | [Open](USER_GUIDE.md) |
| REA-CODEX-WORKFLOW.md | Reference-investigation boundaries | Undated; Git 19 Oct 2026 | Doc `2115029`; tested SHA not recorded | REFERENCE | Passive observation, independent implementation and private Ollama | Does not establish private reference-backend access | [Open](REA-CODEX-WORKFLOW.md) |
| REA_ANALYSIS.md | Initial reference research | Inspected 19 Oct 2026 | Tested SHA not recorded; doc `c18d2b5` | HISTORICAL | Public observable behavior; optional REA runtime boundary | No authenticated/private backend investigation claimed | [Open](REA_ANALYSIS.md) |
| CONTRIBUTING.md | Contributor guidance | Undated; Git 19 Oct 2026 | Doc `c18d2b5`; tested SHA not recorded | REFERENCE | Isolated changes, checks and private-data rules | Not acceptance or deployment evidence | [Open](../CONTRIBUTING.md) |
| AGENTS.md | Engineering instructions | Undated; Git 19 Oct 2026 | Introduced `2d7dee1`; doc `0d7d8d6`; tested SHA not recorded | REFERENCE | Review gate, local model privacy and project working rules | Scope/authorization must also follow current user instructions | [Open](../AGENTS.md) |

## B. Local AI and News Collection

| Report | Engineering Phase | Date | Code Revision | Status | Main Findings | Unresolved Issues | Link |
|---|---|---|---|---|---|---|---|
| LOCAL_LAUNCH_REPORT.md | Phase 3 laptop launch | 19 Oct 2026 | Tested SHA not recorded; report `97ce5a8`, doc `c18d2b5` | HISTORICAL | 77-test baseline to 80 final tests; actual local generation and private draft review | Session-specific process details are historical; no real publication/mail | [Open](LOCAL_LAUNCH_REPORT.md) |
| CONFIGURATION.md | Local/host settings reference | Undated; Git 19 Oct 2026 | Doc `b902238`; tested SHA not recorded | REFERENCE | Environment settings, local model and mail-off defaults | No actual host/provider configuration established | [Open](CONFIGURATION.md) |
| GETTING_STARTED.md | Windows onboarding | Undated; Git 19 Oct 2026 | Doc `b902238`; tested SHA not recorded | REFERENCE | Setup, launch, private credentials and model selection | Needs the reader's actual local runtime/model | [Open](GETTING_STARTED.md) |
| TROUBLESHOOTING.md | Local operation support | Undated; Git 19 Oct 2026 | Doc `b902238`; tested SHA not recorded | REFERENCE | Startup, model, source and workflow diagnostics | Guidance does not certify every host or model response | [Open](TROUBLESHOOTING.md) |

Current live-feed/model execution is described in [final test results](FINAL_TEST_RESULTS.md#live-integrations-and-error-boundaries) and retained [live integration evidence](engineering-evidence/live-integration.json). The historical QA collected 19 accepted records; the fresh final mission collected 20. Equal model tags or similar collection counts do not make separate executions the same run. Source/JSON validation does not certify factual accuracy.

## C. Application Testing

| Report | Engineering Phase | Date | Code Revision | Status | Main Findings | Unresolved Issues | Link |
|---|---|---|---|---|---|---|---|
| FINAL_TEST_RESULTS.md | Fresh final acceptance | 20 Oct 2026 | Runtime R; report D; later exact D CI retained | CURRENT | 97 automated tests, fresh 75 browser scenarios, two protocol checks; nine image phases | Public HTTPS/reboot/off-host recovery and actual SMTP not certified | [Open](FINAL_TEST_RESULTS.md) |
| FINAL_QA_REPORT.md | Earlier master QA | 19–20 Oct 2026 | Q; report `9a7156f`, corrected `50dd84d` | HISTORICAL | 88-test baseline to 91 final tests; earlier 75-browser execution | Older no-Docker/no-push/manual-handoff statements superseded | [Open](FINAL_QA_REPORT.md) |
| BROWSER_TEST_REPORT.md | Earlier browser acceptance | 19–20 Oct 2026 | Q-era audit; report corrected `50dd84d` | HISTORICAL | 75 actual Chromium scenarios and two separately counted protocol checks | Chromium/emulation scope; not the fresh final run | [Open](BROWSER_TEST_REPORT.md) |
| TEST_COVERAGE_MATRIX.md | Earlier feature coverage | 19–20 Oct 2026 | Q-era audit; doc `9a7156f` | HISTORICAL | Feature mapping for 91 tests and 75 browser scenarios | Not a line-coverage measurement or current test total | [Open](TEST_COVERAGE_MATRIX.md) |
| TEST_REPORT.md | Initial engineering tests | 19 Oct 2026 | Tested SHA not recorded; introduced `1aa6938`, doc `c18d2b5` | HISTORICAL | Original 56-test audit and real-versus-mocked boundaries | Later suites supersede its counts | [Open](TEST_REPORT.md) |
| LOCAL_TESTING_GUIDE.md | Optional manual walkthrough | Undated; Git 19 Oct 2026 | Doc `47f6907`; tested SHA not recorded | REFERENCE | Reproducible reader/editor checks using isolated content | Not a new owner testing requirement for the latest mission | [Open](LOCAL_TESTING_GUIDE.md) |
| MANUAL_TESTING_HANDOFF.md | Earlier QA handoff | Completed 20 Oct 2026 | Q-era audit; doc `9a7156f` | HISTORICAL | Prior local-server handoff and optional manual acceptance | Session/process assertions are historical; latest owner retest not required | [Open](MANUAL_TESTING_HANDOFF.md) |
| qa-evidence/commands.md | Earlier QA command provenance | 19–20 Oct 2026 | Q-era audit; doc `9a7156f` | HISTORICAL | Actual commands/results for baseline 88 to final 91 | Paths normalized for privacy; not fresh final commands | [Open](qa-evidence/commands.md) |
| screenshots/README.md | Documentation-gallery provenance | Undated; Git 19 Oct 2026 | Doc `2d100ba`; tested SHA not recorded | REFERENCE | Six synthetic screenshots, manifest and reproduction | Marketing gallery is separate from acceptance screenshots | [Open](screenshots/README.md) |
| screenshots/archive/README.md | Original browser-capture provenance | Undated; Git 19 Oct 2026 | Doc `2d100ba`; tested SHA not recorded | HISTORICAL | Preserves earlier low-resolution fictional captures | Superseded for the current gallery | [Open](screenshots/archive/README.md) |

The earlier **91/75** record lives under `qa-evidence`; the fresh **97/75** record lives under `engineering-evidence`. They are different executions. This publication review inspects retained evidence and exact-commit CI; it does not rebrand prior browser/model execution as a new local test.

## D. Security

| Report | Engineering Phase | Date | Code Revision | Status | Main Findings | Unresolved Issues | Link |
|---|---|---|---|---|---|---|---|
| FINAL_SECURITY_REPORT.md | Final targeted security assessment | 20 Oct 2026 | Runtime R; report D; exact D image gates retained | CURRENT; PARTIAL | Local AI privacy repairs, strict image gates, scoped authorization/storage/secret checks | Public infrastructure, trusted local daemon, RSS rebinding and single-account limits | [Open](FINAL_SECURITY_REPORT.md) |

The [exact-baseline history audit](reports/evidence/final-source-history-audit.json) records targeted pattern/private-path checks and private credential comparisons performed in memory without recording values. Zero findings is scoped evidence, not proof that no arbitrary secret or vulnerability ever existed. The final application and rebuilt proxy had zero HIGH/CRITICAL findings in their recorded strict scans; public ingress remains unverified.

## E. Database and Recovery

| Report | Engineering Phase | Date | Code Revision | Status | Main Findings | Unresolved Issues | Link |
|---|---|---|---|---|---|---|---|
| PRODUCTION_OPERATIONS.md | Future host and recovery procedures | 20 Oct 2026 | Runtime R; doc D | PROCEDURE; infrastructure BLOCKED | Single-instance health/restart/log policy; daily encrypted off-host backup and new-path restoration procedure | No host, encryption/upload destination, scheduler or monitor installed | [Open](PRODUCTION_OPERATIONS.md) |

Database evidence is distributed across the [Phase 2 readiness report](PRODUCTION_READINESS_REPORT.md), [current test results](FINAL_TEST_RESULTS.md), [local recovery record](engineering-evidence/recovery-stability.json), [original-state comparison](engineering-evidence/environment-final.json) and [actual D container recovery/migration evidence](reports/evidence/final-source-container.json). These supporting artifacts establish their recorded local/isolated behavior, not encrypted off-host production recovery. There is no missing standalone database report to invent.

## F. Deployment and Infrastructure

| Report | Engineering Phase | Date | Code Revision | Status | Main Findings | Unresolved Issues | Link |
|---|---|---|---|---|---|---|---|
| FINAL_DEPLOYMENT_REPORT.md | Final deployment assessment | 20 Oct 2026 | Runtime R; report D | CURRENT; BLOCKED | Actual Linux/runtime/scans passed; no suitable existing authorized host/storage allocation | Public staging/production NOT DEPLOYED; mail DISABLED | [Open](FINAL_DEPLOYMENT_REPORT.md) |
| PRODUCTION_READINESS_REPORT.md | Phase 2 production hardening | 19 Oct 2026 | Based on `3b4ae38`; exact tested final SHA not recorded; report `798475a`, doc `c18d2b5` | HISTORICAL | 56-test baseline to 77 final tests; local restore; prepared Waitress/Caddy | Historical Docker/CI gaps later resolved remotely; real hosting still blocked | [Open](PRODUCTION_READINESS_REPORT.md) |
| PRODUCTION_RUNBOOK.md | Controlled pilot procedure | Undated; Git 19 Oct 2026 | Introduced `798475a`; doc `c18d2b5`; tested SHA not recorded | PROCEDURE | Host, TLS, editor restriction, recovery and optional mail instructions | Read later operations for custom-proxy build-before-validation and current evidence | [Open](PRODUCTION_RUNBOOK.md) |
| DEPLOYMENT_GUIDE.md | Original deployment/setup guide | 19 Oct 2026 | Introduced `21e8179`; doc `c18d2b5`; tested SHA not recorded | REFERENCE | Local installation and supported persistent hosted architecture | Older runtime-verification language is contextualized by final reports | [Open](DEPLOYMENT_GUIDE.md) |

Actual remote Docker execution is verified; a public deployment is not. The retained [D container record](reports/evidence/final-source-container.json) passes nine phases and explicitly states `public_https=NOT_TESTED`. The [D application scan](reports/evidence/final-source-image-scan.json) and [D rebuilt-proxy scan](reports/evidence/final-source-proxy-scan.json) each record zero HIGH/CRITICAL findings. No host or SMTP resource was activated by this publication task.

## G. GitHub and Release Engineering

| Report | Engineering Phase | Date | Code Revision | Status | Main Findings | Unresolved Issues | Link |
|---|---|---|---|---|---|---|---|
| GITHUB_PUBLICATION_REPORT.md | Original public source release | 19 Oct 2026 snapshot | Tested/published `0d7d8d6`; report `3b4ae38`, doc `c18d2b5` | HISTORICAL | 56 tests and four successful matrix jobs; existing history preserved | Does not describe later main tips or a running website | [Open](GITHUB_PUBLICATION_REPORT.md) |
| GITHUB_DOCUMENTATION_REPORT.md | Prior documentation/demo release | 19 Oct 2026 | Tested implementation `56d76d8`; final report `1f428c2` | HISTORICAL | Baseline 80 to final 88 tests; screenshots, fresh clone and four-job CI | Earlier release counts are not current acceptance totals | [Open](GITHUB_DOCUMENTATION_REPORT.md) |
| GITHUB_PUSH_CHECKLIST.md | Initial pre-publication audit | 19 Oct 2026 | Tested SHA not recorded; introduced `1aa6938`, doc `c18d2b5` | HISTORICAL | 56-test source-readiness checklist before the original push | Later publication reports supersede its unpushed state | [Open](GITHUB_PUSH_CHECKLIST.md) |
| HISTORY.md | Earlier historical-evidence navigation | Undated; Git 19 Oct 2026 | Doc `c18d2b5`; tested SHA not recorded | REFERENCE; historical index | Earlier implementation/publication/readiness/local-launch snapshots | This master index adds the later QA/final engineering sets | [Open](HISTORY.md) |

The [exact D CI record](reports/evidence/final-source-ci.json) retains successful release run `39322205820` and container run `39322205921`. Its source is D, distinct from the original R runs cited by the final engineering reports. The [baseline release audit](reports/evidence/final-source-release-audit.json) records five successful jobs, nine container phases, both zero-finding strict scans, synchronized source and no public URL. These artifacts describe the recorded baseline, not the future publication commit of this index. The [publication summary](REPORT_PUBLICATION_SUMMARY.md) records this documentation release separately.

## H. Outstanding Issues

| Report | Engineering Phase | Date | Code Revision | Status | Main Findings | Unresolved Issues | Link |
|---|---|---|---|---|---|---|---|
| FINAL_ISSUE_REGISTER.md | Final confirmed-defect register | 20 Oct 2026 | Runtime R; report D | CURRENT | Seven mission defects fixed: two privacy, three tooling, two image/dependency | External launch prerequisites and documented feature limits remain | [Open](FINAL_ISSUE_REGISTER.md) |
| PROJECT_COMPLETION_CHECKLIST.md | Final layered readiness | 20 Oct 2026 | Runtime R; report D | CURRENT; deployment BLOCKED | Source/local/automated readiness separated from public infrastructure | Existing host/storage, HTTPS/operations and optional mail acceptance | [Open](PROJECT_COMPLETION_CHECKLIST.md) |
| BUG_REPORT.md | Earlier application defects | 19–20 Oct 2026 | Q; report `9a7156f` | HISTORICAL | Four earlier defects fixed; 91-test local suite | Does not include the later seven-defect mission | [Open](BUG_REPORT.md) |
| ISSUE_REPORT.md | Original audit findings | 19 Oct 2026 | Tested SHA not recorded; introduced `2115029`, doc `c18d2b5` | HISTORICAL | 21 resolved original audit items, including feature/test gaps | Not 21 security vulnerabilities; later limitations must be read separately | [Open](ISSUE_REPORT.md) |
| FINAL_RELEASE_CHECKLIST.md | Earlier QA release gates | 19–20 Oct 2026 | Q-era audit; doc `9a7156f` | HISTORICAL | 91 tests, earlier 75 browser cases and historical acceptance boundaries | Later automated mission supersedes owner manual-QA requirement | [Open](FINAL_RELEASE_CHECKLIST.md) |

The remaining engineering blockers are suitable existing hosting/storage access, approved origin/editor CIDR and private credentials, actual public HTTPS/reboot/operations acceptance, and optional separately authorized SMTP/sender/inbox acceptance. Source factual/editorial judgment remains with the owner. These are distinct from already executed local and remote automated acceptance; no real-news publication, real mail or deployment is claimed by any new index entry.
