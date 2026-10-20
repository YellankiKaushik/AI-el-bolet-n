# Signal Daily — browser test report

> Historical QA snapshot (19–20 October 2026), retained at its recorded revision and counts. The later [complete status](COMPLETE_PROJECT_STATUS.md) and [master report index](MASTER_REPORT_INDEX.md) supersede its current-status, push, Docker and manual-handoff statements. This annotation does not rerun or change the historical results.

19–20 October 2026. Actual headless Playwright Chromium 151.0.7922.34 on Windows.

**75 final browser scenarios passed, zero failed.** Two additional protocol checks passed and are explicitly labeled below; they are excluded from the browser count. Each scenario can contain several related interactions. Unittest assertions and screenshot-only captures are not counted as browser scenarios. Nine-view Axe diagnostics supplement these scenarios and are not counted a second time.

Only fictional data was approved/published, on the isolated port-8790 server. Source collection and actual local-model UI checks used a separate private database on 8792. Consent UI used a dedicated fake-SMTP application on 8791; no real mail connection occurred. Normal-app checks on 8787 were read-only apart from ephemeral authentication.

| Test ID | Page/Feature | Action Performed | Expected Result | Actual Result | Status | Evidence |
|---|---|---|---|---|---|---|
| B01 | Homepage | Navigate to empty demo homepage | HTTP 200, demo banner, branding and empty edition state | HTTP 200, demo banner, branding and empty edition state | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B02 | Navigation and assets | Follow Archive, Home and Subscribe navigation | Links navigate; CSS/JS succeed; no broken images | Links navigate; CSS/JS succeed; no broken images | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B03 | Subscription validation | Submit invalid email then a reserved example.org email | Native invalid email blocked; mail-off error displayed | Native invalid email blocked; mail-off error displayed | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B04 | Login failure | Open Editor login and submit incorrect password | Clear rejection and password input remains masked | Clear rejection and password input remains masked | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B05 | Login success | Enter isolated workspace password and unlock | Authenticated dashboard is visible | Authenticated dashboard is visible | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B06 | Dashboard tabs | Open Source feed, Publishing setup and Editions tabs | Empty source state, mail-off setup and edition controls render | Empty source state, mail-off setup and edition controls render | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B07 | Disabled generation | Click Generate with Gemma in isolated mail-off demo | Generation refusal is visible and no edition is created | Generation refusal is visible and no edition is created | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B08 | Blank edition | Create a blank edition and submit incomplete review | DRAFT created; review validation rejects incomplete intro | DRAFT created; review validation rejects incomplete intro | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B09 | Story controls | Add and remove a fictional story | Story count changes and returns to zero | Story count changes and returns to zero | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B10 | Invalid JSON import | Enter malformed JSON and import | Enter valid JSON error appears; no extra edition | Enter valid JSON error appears; no extra edition | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B11 | Missing required import fields | Import an empty JSON object | title is required error appears | title is required error appears | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B12 | Invalid source URL | Import a fixture containing javascript source URL | Import rejected with valid HTTP(S) URL error | Import rejected with valid HTTP(S) URL error | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B13 | File import | Upload the supplied fictional JSON and import | New edition opens in DRAFT state | New edition opens in DRAFT state | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B14 | Full edition editor | Edit title, subject, intro, closing, topic, headline, summary, why, source and URL; save | All submitted values persist; changed source clears old evidence | All submitted values persist; changed source clears old evidence | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B15 | Reopening saved draft | Return to editions and reopen edited title | Edited draft content persists | Edited draft content persists | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B16 | Saved preview | Expand saved preview and evidence disclosure | Correct order, text escaping, retained evidence and saved content | Correct order, text escaping, retained evidence and saved content | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B17 | Version conflict | Save the same draft in a second tab, then attempt a stale save | Stale browser sees reload error and does not overwrite newer content | Stale browser sees reload error and does not overwrite newer content | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B18 | Review transition | Submit complete saved fictional edition | REVIEW status and approval button appear | REVIEW status and approval button appear | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B18a | Stale approval regression | Change and re-review fictional content from another client, then click the old approval button | Old tab cannot approve unseen revision; reload shows latest review | Old tab cannot approve unseen revision; reload shows latest review | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B19 | Dirty approval guard | Edit reviewed content, then save | Approval is disabled while dirty; saving returns to DRAFT | Approval is disabled while dirty; saving returns to DRAFT | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B20 | Request revision | Submit again then request revision | REVIEW returns to DRAFT | REVIEW returns to DRAFT | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B21 | Approval transition | Submit and explicitly approve reviewed fictional edition | APPROVED state and mail-off publish button | APPROVED state and mail-off publish button | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B21a | Stale publication regression | Replace and approve a newer fictional revision, then use the old publish button | Old tab cannot publish unseen revision; current edition remains approved | Old tab cannot publish unseen revision; current edition remains approved | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B22 | Dirty publication guard | Edit an approved edition and save | Publish disables while dirty; save invalidates approval | Publish disables while dirty; save invalidates approval | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B23 | Publication cancellation | Review, approve, click publish and dismiss confirmation | Edition remains APPROVED after cancellation | Edition remains APPROVED after cancellation | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B24 | Fictional publication | Accept local-only publication confirmation | PUBLISHED; immutable fields; zero email deliveries | PUBLISHED; immutable fields; zero email deliveries | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B25 | Edition history | Expand Edition history | created, saved, review, approval, revision and publication events | created, saved, review, approval, revision and publication events | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B26 | Published permalink | Open View published edition link | Correct fictional article opens in new reader page | Correct fictional article opens in new reader page | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B27 | Homepage publication listing | Open homepage and click published edition card | Published title appears; link opens correct permalink | Published title appears; link opens correct permalink | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B28 | Archive text search | Search exact acceptance title through form | Correct published title returned | Correct published title returned | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B29 | Archive topic filter | Change topic to Tools then Research | Mismatch hides edition; matching topic restores it | Mismatch hides edition; matching topic restores it | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B30 | Empty search | Search nonexistent fictional text | Understandable empty state | Understandable empty state | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B31 | Private draft visibility | Search unpublished blank edition title | Private blank edition absent from archive | Private blank edition absent from archive | PASS | [JSON](qa-evidence/browser-main-results.json) |
| P01 | API state validation [protocol only] | Attempt direct approval/publication of blank draft; mutate publication; cross-origin and oversized request | Unsafe transitions, edits and requests rejected without tracebacks | Unsafe transitions, edits and requests rejected without tracebacks | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B32 | Missing route and query handling | Visit unknown route and archive with malformed page parameter | 404 useful page; invalid page query safely falls back | 404 useful page; invalid page query safely falls back | PASS | [JSON](qa-evidence/browser-main-results.json) |
| P02 | Pagination fixture preparation [protocol only] | Create and explicitly review/approve/publish 25 fictional editions via authenticated APIs | Sufficient separate synthetic records for actual UI pagination | Sufficient separate synthetic records for actual UI pagination | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B33 | Archive pagination | Click Next and Previous on populated archive | 24 cards first page, 2 second page, no overlap or private drafts | 24 cards first page, 2 second page, no overlap or private drafts | PASS | [JSON](qa-evidence/browser-main-results.json) |
| R1440 | Responsive layout 1440 | Render homepage, archive, reader and draft editor; inspect geometry | No page overflow or clipped editor controls at requested viewport | No page overflow or clipped editor controls at requested viewport | PASS | [JSON](qa-evidence/browser-main-results.json) |
| R768 | Responsive layout 768 | Render homepage, archive, reader and draft editor; inspect geometry | No page overflow or clipped editor controls at requested viewport | No page overflow or clipped editor controls at requested viewport | PASS | [JSON](qa-evidence/browser-main-results.json) |
| R390 | Responsive layout 390 | Render homepage, archive, reader and draft editor; inspect geometry | No page overflow or clipped editor controls at requested viewport | No page overflow or clipped editor controls at requested viewport | PASS | [JSON](qa-evidence/browser-main-results.json) |
| R320 | Responsive layout 320 | Render homepage, archive, reader and draft editor; inspect geometry | No page overflow or clipped editor controls at requested viewport | No page overflow or clipped editor controls at requested viewport | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B38 | Keyboard navigation | Press Tab from fresh homepage, use skip link, keyboard search submit | Visible focus, skip link and keyboard-operated search work | Visible focus, skip link and keyboard-operated search work | PASS | [JSON](qa-evidence/browser-main-results.json) |
| A/ | Accessibility / | Run Axe WCAG 2.1 A/AA including labels and contrast | No serious or critical accessibility violations | 24 checks passed; 0 violations | PASS | [JSON](qa-evidence/browser-main-results.json) |
| A/archive | Accessibility /archive | Run Axe WCAG 2.1 A/AA including labels and contrast | No serious or critical accessibility violations | 22 checks passed; 0 violations | PASS | [JSON](qa-evidence/browser-main-results.json) |
| A/issue/demo-a-quieter-kind-of-ai-briefing-6a44a9 | Accessibility /issue/demo-a-quieter-kind-of-ai-briefing-6a44a9 | Run Axe WCAG 2.1 A/AA including labels and contrast | No serious or critical accessibility violations | 23 checks passed; 0 violations | PASS | [JSON](qa-evidence/browser-main-results.json) |
| A/admin | Accessibility /admin | Run Axe WCAG 2.1 A/AA including labels and contrast | No serious or critical accessibility violations | 26 checks passed; 0 violations | PASS | [JSON](qa-evidence/browser-main-results.json) |
| Aimport | Accessibility import | Run Axe WCAG 2.1 A/AA including labels and contrast | No serious or critical accessibility violations | 24 checks passed; 0 violations | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B44 | Logout | Log out using dashboard control then request protected data | Login form returns and protected request returns 401 | Login form returns and protected request returns 401 | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B45 | Session tampering | Install a modified signed session cookie | Protected API returns 401 | Protected API returns 401 | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B46 | Browser exceptions | Inspect all observed uncaught page exceptions | Zero uncaught JavaScript exceptions | Zero uncaught JavaScript exceptions | PASS | [JSON](qa-evidence/browser-main-results.json) |
| B51 | Restart publication | Open saved permalink after process restart | Saved fictional publication remains readable | Saved fictional publication remains readable | PASS | [JSON](qa-evidence/browser-restart-results.json) |
| B52 | Restart sessions | Replay the old private browser state | Old authentication is rejected after restart | Old authentication is rejected after restart | PASS | [JSON](qa-evidence/browser-restart-results.json) |
| B53 | Restart login | Log in again and open persisted edition | Published editor and history survive restart | Published editor and history survive restart | PASS | [JSON](qa-evidence/browser-restart-results.json) |
| B54 | Post-restart private data | Open archive and search private blank title | Private editions remain hidden after restart | Private editions remain hidden after restart | PASS | [JSON](qa-evidence/browser-restart-results.json) |
| B55 | Browser exceptions | Inspect captured page exceptions | Zero uncaught JavaScript exceptions | Zero uncaught JavaScript exceptions | PASS | [JSON](qa-evidence/browser-restart-results.json) |
| M01 | Subscription form requests a double-opt-in message | Fill reserved fictional email and submit signup | Generic confirmation feedback; exactly one fake multipart message | Feedback displayed; captured message included text/plain and text/html | PASS | [JSON](qa-evidence/subscriber-browser.json) |
| M02 | Open real confirmation UI using token captured only by fake SMTP | Open confirmation URL captured by fake SMTP | Confirmation page says You’re on the list | Expected success heading visible | PASS | [JSON](qa-evidence/subscriber-browser.json) |
| M03 | Confirmation is single use | Navigate to the same confirmation URL again | Token is rejected as expired/already used | Expected invalid-link heading visible | PASS | [JSON](qa-evidence/subscriber-browser.json) |
| M04 | Duplicate confirmed subscription sends no second message | Resubmit the confirmed fictional address | Generic feedback; no second fake message | Feedback displayed and captured-message count remained one | PASS | [JSON](qa-evidence/subscriber-browser.json) |
| M05 | GET unsubscribe shows confirmation without mutating consent | Open the unsubscribe URL using GET | Page requests explicit unsubscribe confirmation | Leave the list? heading and confirmation control visible; GET non-mutation also covered by HTTP tests | PASS | [JSON](qa-evidence/subscriber-browser.json) |
| M06 | POST unsubscribe shows successful confirmation | Click Confirm unsubscribe | POST succeeds and removal message appears | You’re unsubscribed heading visible; final isolated DB held unsubscribed state | PASS | [JSON](qa-evidence/subscriber-browser.json) |
| M07 | Invalid confirmation token shows safe error | Open an invalid confirmation token URL | Understandable invalid-link page | Link expired or already used heading visible | PASS | [JSON](qa-evidence/subscriber-browser.json) |
| L01 | Log in to isolated live integration app and open Source feed | Log into separate integration app and click Source feed | Cached source controls render | Source-row count was greater than zero | PASS | [JSON](qa-evidence/live-browser.json) |
| L02 | Click Refresh news sources and observe real collector result | Click Refresh news sources and await actual response/toast | Actual collector reports usable sources and visible feedback | 19 found, 0 added, 0 feed errors; feedback displayed | PASS | [JSON](qa-evidence/live-browser.json) |
| L03 | Generate selection with no selected sources | Click selected generation without checking any source | Selection bounds error shown | Select between 1 and 8 stories toast visible | PASS | [JSON](qa-evidence/live-browser.json) |
| L04 | Select too many source checkboxes and generate | Check nine sources and click selected generation | Selection bounds error shown without model call | Expected bounds toast visible; checkboxes then cleared | PASS | [JSON](qa-evidence/live-browser.json) |
| L05 | Open Original story link in a real browser popup | Click Original story and inspect actual browser popup | Link opens its original publisher host | Popup completed DOM load at the same publisher hostname | PASS | [JSON](qa-evidence/live-browser.json) |
| L06 | Generate a real local Gemma draft through selected-source UI | Select one source and click Generate selected with Gemma | Busy control; actual generated private DRAFT opens | Button disabled during generation; validated one-story DRAFT opened after 11.954 seconds | PASS | [JSON](qa-evidence/live-browser.json) |
| L07 | Private generated draft is absent from public archive and JS has no exceptions | Navigate to public archive after actual generation | No unapproved model draft or JS exception leaks | Empty public archive and zero captured page exceptions | PASS | [JSON](qa-evidence/live-browser.json) |
| N01 | Normal app homepage and archive keep pre-existing drafts private | Visit normal app and click Archive | Existing unapproved editions remain private | Homepage inaugural state and empty archive observed | PASS | [JSON](qa-evidence/normal-extra-browser.json) |
| N02 | Normal app authenticates privately and shows preserved drafts and sources with mail off | Log into normal app privately, inspect data/source tab, then log out | Original counts and mail-off settings preserved | 2 private issues, 19 source rows, 0 published, mailer false; no real writes | PASS | [JSON](qa-evidence/normal-extra-browser.json) |
| K1440 | Login layout at 1440 pixels | Render unauthenticated login at 1440 CSS pixels | Masked labeled password control; no horizontal document overflow | Login control rendered and document width did not exceed viewport | PASS | [JSON](qa-evidence/normal-extra-browser.json) |
| K768 | Login layout at 768 pixels | Render unauthenticated login at 768 CSS pixels | Masked labeled password control; no horizontal document overflow | Login control rendered and document width did not exceed viewport | PASS | [JSON](qa-evidence/normal-extra-browser.json) |
| K390 | Login layout at 390 pixels | Render unauthenticated login at 390 CSS pixels | Masked labeled password control; no horizontal document overflow | Login control rendered and document width did not exceed viewport | PASS | [JSON](qa-evidence/normal-extra-browser.json) |
| K320 | Login layout at 320 pixels | Render unauthenticated login at 320 CSS pixels | Masked labeled password control; no horizontal document overflow | Login control rendered and document width did not exceed viewport | PASS | [JSON](qa-evidence/normal-extra-browser.json) |
| N03 | Browser login throttling displays understandable error | Submit repeated wrong passwords in actual demo login form | Eventually 429 with useful visible error | Observed 401 rejections then 429 and Too many sign-in attempts toast | PASS | [JSON](qa-evidence/normal-extra-browser.json) |
| N04 | Additional browser pages have zero JavaScript exceptions | Check captured exceptions across these actual pages | Zero uncaught page exceptions | Zero captured exceptions | PASS | [JSON](qa-evidence/normal-extra-browser.json) |

## Complete final journey mapping

| Required sequence | Evidence |
|---|---|
| Start app; open homepage; open login; log in | Fresh demo startup log retained privately; B01, B04, B05 |
| Import fictional JSON; verify draft; edit; save; reopen; preview | B13–B16 |
| Submit and verify review; approve and verify approved | B18–B21; additional invalidation/stale-version regressions B18a/B19/B20/B21a |
| Publish online only and verify published | B22–B24; B23 dismisses confirmation, B24 explicitly accepts it |
| Open reader; verify homepage; search archive | B26–B30 |
| Restart same isolated database; verify persisted publication and old-session rejection | B51–B53 |
| Verify private drafts remain hidden after restart | B54 |
| Confirm zero real mail and unchanged original database | [Recovery](qa-evidence/recovery-stability.json), [original-data comparison](qa-evidence/environment-final.json) |
| Check JavaScript exceptions | B46, B55, L07, N04: zero uncaught page exceptions |

## Screenshots and accessibility

- [Desktop homepage](qa-evidence/homepage-desktop.png), [mobile homepage](qa-evidence/homepage-mobile.png), [published home listing](qa-evidence/published-home-listing.png).
- [Saved preview](qa-evidence/saved-preview.png), [published editor](qa-evidence/published-editor.png), [reader desktop](qa-evidence/published-reader-desktop.png), [reader mobile](qa-evidence/published-reader-mobile.png), [archive search](qa-evidence/archive-search.png).
- [320px editor controls](qa-evidence/editor-320.png), [320px full reader](qa-evidence/reader-320-full.png), [mobile login](qa-evidence/login-mobile.png).
- [Image provenance/hashes](qa-evidence/screenshot-manifest.json), [final nine-view Axe survey](qa-evidence/axe-final-all.json).

Responsive checks visited homepage, archive, reader and editor at 1440×900, 768×1024, 390×844 and 320×844. Separate unauthenticated login checks covered the same sizes. Geometry assertions reject page-level horizontal overflow; the long-title fixture makes the reader regression deterministic. Screenshots were visually inspected, including desktop homepage, mobile reader and narrow editor controls. Browser emulation does not establish physical-device behavior.

The initial accessibility survey found contrast and an unlabeled upload control; final rendered checks found zero violations. Keyboard testing exercised Tab focus, Skip to content and Enter-to-submit search. Screen readers, every possible tab/arrow-key pattern and physical-device touch behavior remain human acceptance tasks.

Console resource errors caused intentionally by rejected login/import/state requests, mail-off subscription, and the 404 page are expected negative-test evidence. Final contexts recorded zero uncaught JavaScript page exceptions. No passing scenario was inferred merely from an HTTP-only assertion: P01/P02 are explicitly excluded from the browser count.

## Reproduction

The retained [browser harness](../tools/acceptance_browser.cjs) requires Playwright and Axe. It deliberately targets only the empty demo at `http://127.0.0.1:8790`. Do not run its publication workflow against the normal app.

From the project root, choose a **new** workspace name, start it in a separate terminal with a working Python:

```powershell
& '.\.tmp\fresh-venv\Scripts\python.exe' tools/demo.py --name acceptance-recheck --port 8790 --empty
```

In the audit tooling terminal:

```powershell
New-Item -ItemType Directory -Force .tmp/qa-20261019 | Out-Null
'acceptance-recheck' | Set-Content .tmp/qa-20261019/demo-name.txt
$env:NODE_PATH=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
$env:AXE_PLAYWRIGHT=(Resolve-Path '.tmp/qa-20261019/browser-deps/node_modules/@axe-core/playwright').Path
node tools/acceptance_browser.cjs
```

The development-only Axe package was installed with `npm install --prefix .tmp/qa-20261019/browser-deps --no-save --no-audit --no-fund @axe-core/playwright`. Fresh machines need working Python, Node, Playwright and its browser before reproducing this maintainer harness. The current audit already completed these steps. Raw browser state stays private in `.tmp/qa-20261019/state.json`; do not publish it. Restart the same demo and run `node tools/acceptance_browser.cjs --restart-check` for the persisted journey. Reproduction overwrites audit JSON/screenshots, so preserve this report's evidence first.
