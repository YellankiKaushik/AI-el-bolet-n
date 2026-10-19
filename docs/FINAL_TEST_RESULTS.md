# Signal Daily — final test results

20 October 2026. **97 passed / 0 failed / 0 skipped** automated tests; **75 passed / 0 failed / 0 skipped** actual browser scenarios, plus two explicitly protocol-only checks. These are this mission's fresh results, not copied acceptance claims.

## Environment and suite

Windows local Python 3.12.14 in the existing `.tmp/fresh-venv`; Node 24.16.0; actual Playwright Chromium 151.0.7922.34; local Ollama `gemma4:e4b`. GitHub separately exercised Windows/Ubuntu with Python 3.11/3.12 and the actual Linux container runtime.

| Check | Result | Evidence |
|---|---|---|
| Before changes | 91 passed, zero failed/skipped | [Baseline log](engineering-evidence/baseline-unittest.txt) |
| After integration/fixes | 97 passed, zero failed/skipped | [Final log](engineering-evidence/final-unittest.txt) |
| Added regressions | Five local AI privacy tests + one actual Docker metadata regression | `tests/test_final_security.py`, `tests/test_container_acceptance.py` |
| Ruff lint/format, compile, JS, Bandit, docs/private-file audits | PASS | [Exact checker commands/results](engineering-evidence/checks.json) |
| Pinned Python dependency audit | Actual OSV query: 10 packages, zero advisories | [Audit](dependency-audit.json) |
| Actual app and Caddy image HIGH/CRITICAL scan | PASS, zero findings at recorded scan time; unfixed advisories remain enabled in gate | [Summary](engineering-evidence/image-scan-summary.json) |
| Actual Linux runtime phases | 9/9 passed with cleanup; no public HTTPS claimed | [Image acceptance](engineering-evidence/container-final.json) |
| Original data/config | Every table digest and `.env` hash unchanged | [Comparison](engineering-evidence/environment-final.json) |
| Recovery/stability | Backup/restore, overwrite/lock/rollback/restart, 48 requests/eight workers all 200 | [Evidence](engineering-evidence/recovery-stability.json) |

All mail transport was simulated; actual subscriber emails sent: zero. The browser suite used fictional data on 8790, fake-SMTP data on 8791 and separate private live RSS/model data on 8792. Normal app checks on 8787 were authentication/read-only only. Credentials/cookies/raw drafts/backups remain private under ignored `.tmp`.

## Fresh browser interactions

| Test ID | Page/feature | Actual action | Status | Evidence |
|---|---|---|---|---|
| B01 | Homepage | Navigate to empty demo homepage | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B02 | Navigation and assets | Follow Archive, Home and Subscribe navigation | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B03 | Subscription validation | Submit invalid email then a reserved example.org email | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B04 | Login failure | Open Editor login and submit incorrect password | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B05 | Login success | Enter isolated workspace password and unlock | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B06 | Dashboard tabs | Open Source feed, Publishing setup and Editions tabs | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B07 | Disabled generation | Click Generate with Gemma in isolated mail-off demo | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B08 | Blank edition | Create a blank edition and submit incomplete review | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B09 | Story controls | Add and remove a fictional story | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B10 | Invalid JSON import | Enter malformed JSON and import | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B11 | Missing required import fields | Import an empty JSON object | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B12 | Invalid source URL | Import a fixture containing javascript source URL | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B13 | File import | Upload the supplied fictional JSON and import | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B14 | Full edition editor | Edit title, subject, intro, closing, topic, headline, summary, why, source and URL; save | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B15 | Reopening saved draft | Return to editions and reopen edited title | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B16 | Saved preview | Expand saved preview and evidence disclosure | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B17 | Version conflict | Save the same draft in a second tab, then attempt a stale save | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B18 | Review transition | Submit complete saved fictional edition | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B18a | Stale approval regression | Change and re-review fictional content from another client, then click the old approval button | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B19 | Dirty approval guard | Edit reviewed content, then save | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B20 | Request revision | Submit again then request revision | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B21 | Approval transition | Submit and explicitly approve reviewed fictional edition | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B21a | Stale publication regression | Replace and approve a newer fictional revision, then use the old publish button | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B22 | Dirty publication guard | Edit an approved edition and save | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B23 | Publication cancellation | Review, approve, click publish and dismiss confirmation | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B24 | Fictional publication | Accept local-only publication confirmation | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B25 | Edition history | Expand Edition history | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B26 | Published permalink | Open View published edition link | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B27 | Homepage publication listing | Open homepage and click published edition card | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B28 | Archive text search | Search exact acceptance title through form | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B29 | Archive topic filter | Change topic to Tools then Research | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B30 | Empty search | Search nonexistent fictional text | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B31 | Private draft visibility | Search unpublished blank edition title | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| P01 | API state validation (protocol only) | Attempt direct approval/publication of blank draft; mutate publication; cross-origin and oversized request | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B32 | Missing route and query handling | Visit unknown route and archive with malformed page parameter | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| P02 | Pagination fixture preparation (protocol only) | Create and explicitly review/approve/publish 25 fictional editions via authenticated APIs | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B33 | Archive pagination | Click Next and Previous on populated archive | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| R1440 | Responsive layout 1440 | Render homepage, archive, reader and draft editor; inspect geometry | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| R768 | Responsive layout 768 | Render homepage, archive, reader and draft editor; inspect geometry | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| R390 | Responsive layout 390 | Render homepage, archive, reader and draft editor; inspect geometry | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| R320 | Responsive layout 320 | Render homepage, archive, reader and draft editor; inspect geometry | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B38 | Keyboard navigation | Press Tab from fresh homepage, use skip link, keyboard search submit | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| A/ | Accessibility / | Run Axe WCAG 2.1 A/AA including labels and contrast | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| A/archive | Accessibility /archive | Run Axe WCAG 2.1 A/AA including labels and contrast | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| A/issue/demo-a-quieter-kind-of-ai-briefing-810fab | Accessibility /issue/demo-a-quieter-kind-of-ai-briefing-810fab | Run Axe WCAG 2.1 A/AA including labels and contrast | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| A/admin | Accessibility /admin | Run Axe WCAG 2.1 A/AA including labels and contrast | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| Aimport | Accessibility import | Run Axe WCAG 2.1 A/AA including labels and contrast | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B44 | Logout | Log out using dashboard control then request protected data | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B45 | Session tampering | Install a modified signed session cookie | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B46 | Browser exceptions | Inspect all observed uncaught page exceptions | PASS | [JSON](engineering-evidence/browser-main-results.json) |
| B51 | Restart publication | Open saved permalink after process restart | PASS | [JSON](engineering-evidence/browser-restart-results.json) |
| B52 | Restart sessions | Replay the old private browser state | PASS | [JSON](engineering-evidence/browser-restart-results.json) |
| B53 | Restart login | Log in again and open persisted edition | PASS | [JSON](engineering-evidence/browser-restart-results.json) |
| B54 | Post-restart private data | Open archive and search private blank title | PASS | [JSON](engineering-evidence/browser-restart-results.json) |
| B55 | Browser exceptions | Inspect captured page exceptions | PASS | [JSON](engineering-evidence/browser-restart-results.json) |
| M01 | Subscription form requests a double-opt-in message | Subscription form requests a double-opt-in message | PASS | [JSON](engineering-evidence/subscriber-browser.json) |
| M02 | Open real confirmation UI using token captured only by fake SMTP | Open real confirmation UI using token captured only by fake SMTP | PASS | [JSON](engineering-evidence/subscriber-browser.json) |
| M03 | Confirmation is single use | Confirmation is single use | PASS | [JSON](engineering-evidence/subscriber-browser.json) |
| M04 | Duplicate confirmed subscription sends no second message | Duplicate confirmed subscription sends no second message | PASS | [JSON](engineering-evidence/subscriber-browser.json) |
| M05 | GET unsubscribe shows confirmation without mutating consent | GET unsubscribe shows confirmation without mutating consent | PASS | [JSON](engineering-evidence/subscriber-browser.json) |
| M06 | POST unsubscribe shows successful confirmation | POST unsubscribe shows successful confirmation | PASS | [JSON](engineering-evidence/subscriber-browser.json) |
| M07 | Invalid confirmation token shows safe error | Invalid confirmation token shows safe error | PASS | [JSON](engineering-evidence/subscriber-browser.json) |
| L01 | Log in to isolated live integration app and open Source feed | Log in to isolated live integration app and open Source feed | PASS | [JSON](engineering-evidence/live-browser.json) |
| L02 | Click Refresh news sources and observe real collector result | Click Refresh news sources and observe real collector result | PASS | [JSON](engineering-evidence/live-browser.json) |
| L03 | Generate selection with no selected sources | Generate selection with no selected sources | PASS | [JSON](engineering-evidence/live-browser.json) |
| L04 | Select too many source checkboxes and generate | Select too many source checkboxes and generate | PASS | [JSON](engineering-evidence/live-browser.json) |
| L05 | Open Original story link in a real browser popup | Open Original story link in a real browser popup | PASS | [JSON](engineering-evidence/live-browser.json) |
| L06 | Generate a real local Gemma draft through selected-source UI | Generate a real local Gemma draft through selected-source UI | PASS | [JSON](engineering-evidence/live-browser.json) |
| L07 | Private generated draft is absent from public archive and JS has no exceptions | Private generated draft is absent from public archive and JS has no exceptions | PASS | [JSON](engineering-evidence/live-browser.json) |
| N01 | Normal app homepage and archive keep pre-existing drafts private | Normal app homepage and archive keep pre-existing drafts private | PASS | [JSON](engineering-evidence/normal-extra-browser.json) |
| N02 | Normal app authenticates privately and shows preserved drafts and sources with mail off | Normal app authenticates privately and shows preserved drafts and sources with mail off | PASS | [JSON](engineering-evidence/normal-extra-browser.json) |
| K1440 | Login layout at 1440 pixels | Login layout at 1440 pixels | PASS | [JSON](engineering-evidence/normal-extra-browser.json) |
| K768 | Login layout at 768 pixels | Login layout at 768 pixels | PASS | [JSON](engineering-evidence/normal-extra-browser.json) |
| K390 | Login layout at 390 pixels | Login layout at 390 pixels | PASS | [JSON](engineering-evidence/normal-extra-browser.json) |
| K320 | Login layout at 320 pixels | Login layout at 320 pixels | PASS | [JSON](engineering-evidence/normal-extra-browser.json) |
| N03 | Browser login throttling displays understandable error | Browser login throttling displays understandable error | PASS | [JSON](engineering-evidence/normal-extra-browser.json) |
| N04 | Additional browser pages have zero JavaScript exceptions | Additional browser pages have zero JavaScript exceptions | PASS | [JSON](engineering-evidence/normal-extra-browser.json) |

No screenshot-only capture or unittest was counted as an actual browser scenario. P01/P02 are excluded from the 75. Main 48 browser cases + five restart + seven fake-SMTP + seven actual RSS/Gemma + eight normal/login cases = 75. Final contexts recorded zero uncaught page exceptions; expected console HTTP errors from negative scenarios remain labeled in the retained JSON.

Desktop 1440×900, tablet 768×1024, mobile 390×844 and narrow mobile 320×844 were checked across public/editor/login views. Actual Axe A/AA, accessible upload labels, Tab/skip-link and keyboard search assertions passed. The final screenshot manifest retains real fictional-only captures/hashes; this is browser emulation, not physical-device or full assistive-technology certification.

## Live integrations and error boundaries

- Configured RSS feeds: all four HTTP 200; 20 accepted records in the live collection, no errors, repeated insert zero. [Explicit statuses](engineering-evidence/rss-response-status.json) and [source URLs/dates](engineering-evidence/live-integration.json).
- Actual hardened local Gemma: 3 stories / 15.39s through client and 1 / 3.748s through browser. Known source attribution validated; both drafts remained private/unapproved. No semantic fact certification is made.
- Actual closed-loopback model endpoint failed safely without cloud fallback. Malformed model output, timeout, numeric/source validation and SMTP failures/uncertain sends were deliberately simulated in unit/integration tests.
- Consent, confirmation expiry/single use, stable unsubscribe, eligibility, atomic reservations, failure/retry, duplicate prevention and uncertain state passed tests with fake SMTP. Actual provider/DNS/inbox/email-client acceptance is **not verified**.

## Exact commands and CI

From the project root, tests used `& '.\.tmp\fresh-venv\Scripts\python.exe' -m unittest discover -s tests -v`. Checker arguments/executable paths are in [checks.json](engineering-evidence/checks.json). Browser command was `node tools/acceptance_browser.cjs` with `SIGNAL_ACCEPTANCE_RUN_DIR=.tmp/final-engineering-20261020`, `SIGNAL_ACCEPTANCE_OUTPUT=docs/engineering-evidence`, bundled Playwright via `NODE_PATH`, and the private development Axe package path. After a same-workspace process restart, `node tools/acceptance_browser.cjs --restart-check` verified persisted publication/session rejection.

Actual Docker command on the Linux runner was `python tools/container_acceptance.py`, followed by strict Trivy HIGH/CRITICAL scans of both service images. The four release matrix jobs ran the full suite, lint/format/compile/JS/Bandit/private/docs checks; Ubuntu3.12 additionally queried OSV. Temporary acceptance containers/volumes/networks were cleaned up; no host ports or real SMTP were used.

- [Signal Daily release checks](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39321202509): success (exact source `aaf91a7b955323dc2928d6f9b5d9222037d8fb99`).
- [Linux container acceptance](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39321202556): success (exact source `aaf91a7b955323dc2928d6f9b5d9222037d8fb99`).

Public staging, public HTTPS, host reboot, off-host encrypted recovery and actual SMTP were not skipped tests disguised as passes: they are explicitly **BLOCKED/NOT VERIFIED** because no suitable existing host/storage/provider was accessible. No owner manual application test is required to validate the completed local scope.
