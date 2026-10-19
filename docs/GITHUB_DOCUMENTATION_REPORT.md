# GitHub documentation release report

Release date: 2026-10-19. Repository: [YellankiKaushik/AI-el-bolet-n](https://github.com/YellankiKaushik/AI-el-bolet-n).

This report records the documentation/screenshot release. The newsletter service remains local and **not publicly deployed**. The final publication/CI section is updated after actual remote verification; pending stages are never represented as passed.

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
| `homepage-mobile.png` | 780 × 1688 (390 × 844 CSS, 2×) | 45,896 |
| `editor-dashboard.png` | 1440 × 900 | 18,227 |
| `newsletter-editor.png` | 1440 × 900 | 18,362 |
| `newsletter-preview.png` | 1440 × 900 | 19,878 |
| `published-edition.png` | 1440 × 900 | 20,062 |

Total: **170,050 bytes**. PNGs were losslessly compressed without resizing, stretching, compositing or replacing page text. Final files were opened and visually inspected; dashboard framing was corrected to show its edition list. No captured page errors or horizontal overflow. [Manifest and reproduction](screenshots/README.md).

## Small engineering changes

- Added `tools/demo.py` with strict private-path/port safeguards, separate credentials, mail/generation off, fictional seeding only into an empty isolated database, and restart preservation.
- Added a visible demo banner without altering real-workspace content or editorial behavior.
- Added optional `tools/capture_screenshots.cjs`; Playwright/Sharp are maintainer tools, not runtime dependencies.
- Fixed `tools/local_generate.py` to create missing output directories and refuse accidental overwrites before calling the model. Importing it for tests no longer reads the real `.env`.
- Added `tools/check_docs.py` to check local Markdown links/anchors and six PNG dimensions/bytes/hashes. Added meaningful regressions for demo isolation, output preservation and broken-link detection; CI now checks documentation and screenshot-tool syntax.

## Validation and private-data preservation

Independent final local suite: **88 passed, zero failures/errors**, up from the 80-test baseline. Ruff lint/format, Python compilation, both JavaScript syntax checks, Bandit, documentation/candidate audits and OSV all returned exit code 0. OSV checked ten pinned Python packages with zero advisories; optional screenshot/parser Node tools are not production dependencies and are outside that Python advisory scan.

The link audit passed for all repository-local Markdown targets/heading anchors and all six PNG manifest dimensions/bytes/hashes. Five Mermaid diagrams parsed and rendered to SVG with Mermaid 12.2.0; all four README badge endpoints returned HTTP 200 SVGs. Actual GitHub rendering/remote image verification is recorded after publication below.

An intermediate Bandit run flagged a constructed SQL query in the new demo guard, despite its fixed table-name list. It was replaced with a fixed SQL statement, and the complete checks were rerun successfully; the finding was not suppressed or ignored. No automated-test failure was hidden. The first link audit caught the not-yet-created release report; creating this report resolved all three references.

Candidate files and all 27 pre-release reachable commits were scanned against known credential signatures, forbidden private paths and both actual configured secret values held only in memory: no findings. Final post-commit/history scans are recorded with publication verification. Screenshots were independently visually inspected; the scan is not exhaustive secret detection or penetration testing.

Actual `gemma4:e4b` generated three validated items from explicitly fictional source notes in **26.11 seconds**, using loopback Ollama and the actual JSON CLI. Output stayed in ignored temporary storage; nothing was approved/published to the real database. Original SQLite/configuration fingerprints matched before/after: **19 stories, two drafts, zero subscribers/deliveries**.

No public deployment, real email, paid provider, model installation or Ollama exposure occurred. Synthetic seed publication applies only to the isolated demo. Public-facing documentation distinguishes backend subscriber consent/delivery functionality from the absent subscriber-management UI and unverified live SMTP acceptance.

## Publication and CI verification

**Pending actual publication at this report's preparation stage.** Local validation, safe branch integration, normal push, fetched-head equality, remote README/images/docs and exact-commit CI must all be verified before the release is called complete.

## Remaining limitations and next work

Public hosting, real Docker/TLS ingress, sender DNS/mailbox acceptance and off-host recovery remain external acceptance tasks. There is no multi-editor/MFA/recovery, correction/takedown UI, subscriber-management UI, background queue or bounce/complaint automation. Local screenshots do not prove physical-device or email-client rendering. No full penetration/load audit is claimed.

Recommended next task: **local manual acceptance testing** using the fictional workspace and [20-step guide](LOCAL_TESTING_GUIDE.md). Keep real news unapproved until its human editor checks sources and chooses publication.
