# Historical engineering evidence

These documents are dated snapshots, preserved to show what was checked at each stage. Historical test counts, process IDs, missing features and unpushed/CI statements remain tied to their original revisions. For current behavior use the [complete project status](COMPLETE_PROJECT_STATUS.md) and [master report index](MASTER_REPORT_INDEX.md). The [publication summary](REPORT_PUBLICATION_SUMMARY.md) records privacy redactions and annotations; byte-for-byte originals remain private and Git history was not rewritten.

| Snapshot | What it records |
|---|---|
| [Implementation report](IMPLEMENTATION_REPORT.md) | Original local engineering changes and architecture decisions |
| [Test report](TEST_REPORT.md), [test output](test-evidence.txt) | Earlier 56-test audit, real versus mocked services and earlier environment failures |
| [Issue report](ISSUE_REPORT.md) | Resolved audit findings and limitations as of the original pass |
| [REA analysis](REA_ANALYSIS.md) | Passive public-page evidence, missing optional REA runtime and explicit boundaries |
| [Original publication report](GITHUB_PUBLICATION_REPORT.md) | Initial GitHub history, first successful four-job matrix and repository verification |
| [Production readiness report](PRODUCTION_READINESS_REPORT.md) | Later 77-test hardening, actual local backup/restore and unverified hosting prerequisites |
| [Local launch report](LOCAL_LAUNCH_REPORT.md) | Later 80-test laptop run, original-row preservation and privately saved unapproved real draft metadata |
| [Original browser captures](screenshots/archive/README.md) | Earlier synthetic browser evidence retained in its original low-resolution form |
| [Historical QA](FINAL_QA_REPORT.md), [browser report](BROWSER_TEST_REPORT.md), [bugs](BUG_REPORT.md), [coverage](TEST_COVERAGE_MATRIX.md), [release checklist](FINAL_RELEASE_CHECKLIST.md), [handoff](MANUAL_TESTING_HANDOFF.md), [commands](qa-evidence/commands.md) | 19–20 October audit: 91 tests and 75 browser scenarios, tested source `eda3ff6`; later QA evidence corrected at `50dd84d` |
| [Final engineering](FINAL_ENGINEERING_REPORT.md), [tests](FINAL_TEST_RESULTS.md), [security](FINAL_SECURITY_REPORT.md), [issues](FINAL_ISSUE_REGISTER.md), [deployment](FINAL_DEPLOYMENT_REPORT.md), [operations](PRODUCTION_OPERATIONS.md), [completion](PROJECT_COMPLETION_CHECKLIST.md) | 20 October: fresh 97 tests, 75 browser scenarios, nine actual Linux phases and both image scans at runtime source `aaf91a7`; final source/report tip `d7494f9` also passed all five CI jobs |

Personal machine paths and actual private generated title/subject have been redacted from current public copies. Process IDs apply only to their recorded sessions; never reuse them without verifying ownership. Private JSON/DB paths are not repository resources. Credentials, complete private drafts, databases, backups and subscriber datasets remain excluded. Public publisher headlines and synthetic fixtures remain distinguishable from private generated prose. Previously published Git snapshots can still contain the older paths/title metadata because this task does not rewrite history.

The production runbook is an operational document, not deployment evidence. New CI results belong to the exact tested commit. A green historical matrix does not certify later work, and a newer source release still does not prove a live website or SMTP inbox delivery.
