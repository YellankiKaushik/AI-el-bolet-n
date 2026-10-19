# Historical engineering evidence

These documents are dated snapshots, preserved to show what was actually checked at each stage. Their old test counts, machine paths, process IDs, missing features and unpushed/CI statements are not rewritten to look current. For current behavior use [PROJECT_STATUS.md](PROJECT_STATUS.md), the [documentation release report](GITHUB_DOCUMENTATION_REPORT.md) and the portable beginner guides.

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

Machine-specific paths/PIDs in the local report apply only to that recorded session. Do not reuse stale process IDs, assume another user's runtime path exists, or treat private JSON/DB paths as repository contents. The real configuration, draft files and databases were excluded from Git. Historical prose may mention a local draft title/source metadata; it does not include a complete private newsletter file or subscriber dataset.

The production runbook is an operational document, not deployment evidence. New CI results belong to the exact tested commit. A green historical matrix does not certify later work, and a newer source release still does not prove a live website or SMTP inbox delivery.
