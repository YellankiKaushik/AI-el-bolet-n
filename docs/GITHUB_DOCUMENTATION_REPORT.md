# GitHub documentation release report

Release date: 2026-10-19. Repository: [YellankiKaushik/AI-el-bolet-n](https://github.com/YellankiKaushik/AI-el-bolet-n).

This report records the documentation/screenshot release. The newsletter service remains local and **not publicly deployed**. The publication section records independently verified GitHub source hosting and exact-commit CI results.

## Starting point

- `main` / `origin/main`: `3b4ae381ba3d2db7d0834002dfa0f49aec83b27e` after fetching.
- `production-readiness`: `97ce5a8`, eight legitimate local hardening/local-launch commits ahead, no remote-only commits and a clean starting worktree.
- Independent baseline: **80 tests passed**, zero failures/errors.
- Old README had a blurred, weakly framed hero, no useful product gallery, mixed historical/current counts, and insufficient beginner/manual/configuration guidance.
- Existing `docs/screenshots/desktop.jpg` was opened and inspected. Older images used scaled browser-provider captures; the repository also held two unreferenced duplicate root preview PNGs.

## Implemented changes

The README now leads with the product purpose, local/human-review model, verified-feature overview, actual screenshot gallery, workflow diagram, stack, Windows setup, first-edition tutorial, test commands, deployment boundaries, security/privacy, directory tree, honest roadmap, contributing and accurate existing-license notices. Badges link to the actual workflow, supported Python combinations, existing license notices and local Ollama.

Added portable guides:

- [GETTING_STARTED.md](GETTING_STARTED.md)
- [USER_GUIDE.md](USER_GUIDE.md)
- [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md), with 20 objective/prerequisite/URL/action/input/expected/pass-fail/recovery scenarios
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CONFIGURATION.md](CONFIGURATION.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [PROJECT_STATUS.md](PROJECT_STATUS.md)
- [HISTORY.md](HISTORY.md), separating dated evidence from current instructions

Historical reports retain their results and now point to current guides. The operational runbook uses the current mail-off publication label. Old JPEGs were moved unchanged under `screenshots/archive`; unreferenced duplicate root previews were removed, with all bytes/history still recoverable in Git.

## Real screenshots

All six PNGs came from actual Playwright rendering with installed Chrome. Only `.tmp/screenshots/demo.db`, handwritten fictional fixtures and private temporary demo credentials were used. No real subscriber, private-news draft, credential, cookie or token was captured. SMTP and model generation were disabled in that demo. The demo banner and **Demo:** titles identify sample content. Editor/preview captures are intentionally scrolled to the feature.

| File under `docs/screenshots/` | PNG dimensions | Bytes |
|---|---:|---:|
| `homepage-desktop.png` | 1440 × 900 | 47,625 |
| `homepage-mobile.png` | 780 × 1688 (390 × 844 CSS, 2×) | 45,907 |
| `editor-dashboard.png` | 1440 × 900 | 18,227 |
| `newsletter-editor.png` | 1440 × 900 | 18,362 |
| `newsletter-preview.png` | 1440 × 900 | 19,878 |
| `published-edition.png` | 1440 × 900 | 20,062 |

Total: **170,061 bytes**. PNGs were losslessly compressed without resizing, stretching, compositing or replacing page text. Final files were opened and visually inspected; dashboard framing was corrected to show its edition list. No captured page errors or horizontal overflow. [Manifest and reproduction](screenshots/README.md).

## Small engineering changes

- Added `tools/demo.py` with strict private-path/port safeguards, separate credentials, mail/generation off, fictional seeding only into an empty isolated database, and restart preservation.
- Added a visible demo banner without altering real-workspace content or editorial behavior.
- Added optional `tools/capture_screenshots.cjs`; Playwright/Sharp are maintainer tools, not runtime dependencies.
- Fixed `tools/local_generate.py` to create missing output directories and refuse accidental overwrites before calling the model. Importing it for tests no longer reads the real `.env`.
- Added `tools/check_docs.py` to check local Markdown links/anchors and six PNG dimensions/bytes/hashes. Added meaningful regressions for demo isolation, output preservation and broken-link detection; CI now checks documentation and screenshot-tool syntax.

## Validation and private-data preservation

Independent final local suite: **88 passed, zero failures/errors**, up from the 80-test baseline. Ruff lint/format, Python compilation, both JavaScript syntax checks, Bandit, documentation/candidate audits and OSV all returned exit code 0. OSV checked ten pinned Python packages with zero advisories; optional screenshot/parser Node tools are not production dependencies and are outside that Python advisory scan.

The link audit passed for all repository-local Markdown targets/heading anchors and all six PNG manifest dimensions/bytes/hashes. Five Mermaid diagrams parsed and rendered to SVG with Mermaid 12.2.0; all four README badge endpoints returned HTTP 200 SVGs. Actual GitHub rendering/remote image verification is recorded after publication below.

An intermediate Bandit run flagged a constructed SQL query in the new demo guard, despite its fixed table-name list. It was replaced with a fixed SQL statement, and the complete checks were rerun successfully; the finding was not suppressed or ignored. Fresh Windows execution also exposed early-rejection HTTP client reset races; the tests now send only the rejected body declaration or exact header boundary. GitHub Windows CI exposed an 8.3 temporary-path spelling mismatch in the new demo assertion; comparing canonical paths fixed it. One CI job failed and its peer was cancelled by matrix fail-fast before this fix. Local edit indentation/formatting checks also failed during correction and were repaired before committing. All final checks passed; these intermediate failures were not ignored. The first link audit caught the not-yet-created release report; creating this report resolved all three references.

Candidate files and all 27 pre-release reachable commits were scanned against known credential signatures, forbidden private paths and both actual configured secret values held only in memory: no findings. Final post-commit/history scans are recorded with publication verification. Screenshots were independently visually inspected; the scan is not exhaustive secret detection or penetration testing.

Actual `gemma4:e4b` generated three validated items from explicitly fictional source notes in **26.11 seconds**, using loopback Ollama and the actual JSON CLI. Output stayed in ignored temporary storage; nothing was approved/published to the real database. Original SQLite/configuration fingerprints matched before/after: **19 stories, two drafts, zero subscribers/deliveries**.

No public deployment, real email, paid provider, model installation or Ollama exposure occurred. Synthetic seed publication applies only to the isolated demo. Public-facing documentation distinguishes backend subscriber consent/delivery functionality from the absent subscriber-management UI and unverified live SMTP acceptance.

## Publication and CI verification

**GitHub source publication verified.** Normal, non-forced pushes preserved the original published history. `main` was fast-forwarded from the validated `production-readiness` history; no merge conflict or discarded work. The original baseline remains an ancestor.

Verified implementation commit: `56d76d8b7d49a0a26dfcbe8d04ad3582dc0be83f`. Fetched `origin/main` and an independent clone of the public GitHub repository matched this commit and its complete 93-file Git tree. All six cloned PNGs matched manifest SHA-256 and byte size. Checkout line-ending differences are excluded by comparing Git objects.

Actual GitHub README rendering was inspected in Chrome: HTTP 200, correct heading/subtitle, all six product images and four badges loaded, guide links targeted the uploaded files, no rich-display error, and the GitHub Mermaid iframe rendered SVG. All new guides exist in the independently cloned tree. Five diagrams also parsed/rendered locally.

GitHub Actions **PASS: four of four jobs**, Windows and Ubuntu with Python 3.11/3.12, on the exact implementation commit: [run 39239865526](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39239865526). The final evidence-only commit triggers a separate run, checked before handoff; this snapshot intentionally identifies the commit/run it actually measured rather than claiming to contain its own future hash.

Fresh Windows onboarding used an independent source clone and a newly created virtual environment with both pinned requirement files. Setup created private configuration and preserved it on repeated setup; actual HTTP pages/authentication, mail-off state, synthetic import/review/approval/publication, restart persistence and session invalidation passed. The final fresh suite passed **88/88**, zero failures/errors, and its documentation audit passed. No real credentials or original database were used.

The scoped privacy audit at this implementation commit checked **39 reachable commits, 137 unique blobs and 93 candidate files**, including both actual local secret values compared only in memory: zero findings. Original database/configuration fingerprints still matched, with 19 stories, two unapproved drafts, zero subscribers/deliveries. This does not claim exhaustive secret discovery or a penetration test.

Machine-readable evidence: [documentation-release-validation.json](documentation-release-validation.json).

### Commits and repository accounting

Twenty previously unpushed commits were published, including eight preserved Phase 2/3 commits and twelve documentation/demo/test commits. This report/evidence follow-up is the twenty-first new commit relative to the starting remote baseline. No empty commits or rewritten history.

```text
1145770 feat(persistence): add verified SQLite recovery and instance locks
51a6a26 fix(email): validate SMTP and preserve accepted delivery outcomes
0aef33d feat(server): add bounded WSGI transport and production safeguards
dd782a2 feat(deploy): prepare private Caddy ingress and persistent containers
798475a docs(operations): record readiness evidence and controlled launch runbook
65be516 feat(local): add safe Windows launcher and loopback startup checks
b221bee fix(editor): clarify navigation and disabled-email publishing
97ce5a8 docs(local): record verified laptop launch and review-ready draft
c43ce9d feat(demo): add isolated fictional workspace for safe acceptance
18f5a0d fix(cli): preserve draft files and create output directories
2d100ba docs(visuals): add six verified browser screenshots and provenance
1a34f80 docs(readme): redesign project landing page around verified capabilities
b902238 docs(onboarding): add complete Windows setup and recovery guides
47f6907 docs(usage): explain editorial workflow and twenty manual tests
c18d2b5 docs(maintenance): map architecture status and historical evidence
e345f5a ci(docs): verify local links anchors and screenshot integrity
f5c670b docs(release): record validated documentation and visual changes
da02137 test(http): avoid Windows reset race when checking upload limits
f2c13fc test(http): send only the rejected header boundary on Windows
56d76d8 test(demo): compare canonical paths on Windows runners
```

Final follow-up: `docs(release): record verified GitHub publication and CI evidence`. The release changes **76 Git diff entries: 70 added/modified files, four exact renames and two removed duplicate previews** relative to the starting remote baseline. These figures include the preserved Phase 2/3 work and this evidence follow-up.


## Remaining limitations and next work

Public hosting, real Docker/TLS ingress, sender DNS/mailbox acceptance and off-host recovery remain external acceptance tasks. There is no multi-editor/MFA/recovery, correction/takedown UI, subscriber-management UI, background queue or bounce/complaint automation. Local screenshots do not prove physical-device or email-client rendering. No full penetration/load audit is claimed.

Recommended next task: **local manual acceptance testing** using the fictional workspace and [20-step guide](LOCAL_TESTING_GUIDE.md). Keep real news unapproved until its human editor checks sources and chooses publication.
