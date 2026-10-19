# Local manual testing, step by step

Use this guide to see whether the application works in your browser. A pass means the expected visible result actually happened; clicking a button alone is not a pass. Record the date, test number, result and exact error text. Never record a password, cookie, token, subscriber address or private draft in a public issue.

## Two workspaces, two purposes

| Workspace | URL | Data / credentials | Allowed tests |
|---|---|---|---|
| Your normal app | `http://localhost:8787` | Existing `data/signal_daily.db` and private `.env` | Reading, RSS collection and saving unapproved drafts; no automatic approval/publication |
| Fresh acceptance demo | `http://127.0.0.1:8790` | Separate `.tmp/acceptance/demo.db` and `credentials.json` | Repeatable fictional import/edit/review/approval/publication |

Start the normal app with [GETTING_STARTED.md](GETTING_STARTED.md). In another PowerShell window, from the project root:

```powershell
py -3 tools/demo.py --name acceptance --port 8790 --empty
```

The acceptance app displays **DEMO WORKSPACE**. Read its random password privately in `.tmp/acceptance/credentials.json`; it is not your real `.env` password. It ignores `.env`, refuses the real app's port, never seeds the real database, and disables SMTP/model generation. Leave its terminal open. Restarting reuses its data; to repeat from empty, choose a new unused name such as `acceptance2`, rather than deleting a database.

For tests 7–15, import only [synthetic-newsletter.json](examples/synthetic-newsletter.json). Its title starts with **Demo:** and its introduction explicitly says fictional. Keep the 8790 address visible before any approval/publication action. The seed demo command `py -3 tools/demo.py` is a different convenient tour workspace on 8789; this guide uses the empty 8790 workspace to test creation.

## 1. Start the application

**Objective:** Verify a running local server. **Prerequisites / URL:** Python/Git setup complete; `http://localhost:8787/health`.

**Action / input:** Run `.\Start-Local.ps1` from the root; open the health URL. If the app is already running, use it instead of starting another copy.

**Expected / pass:** Startup states a loopback listener, and health returns `{"status":"ok"}` with no traceback. **Fail:** connection refused, non-loopback binding, lock/port error or unhealthy response.

**Failure / recovery:** A Store alias, another instance or wrong working directory is common. Follow [startup troubleshooting](TROUBLESHOOTING.md); don't delete the database or weaken firewall/security policy.

## 2. Open the homepage

**Objective:** Verify reader HTML and assets. **Prerequisites / URL:** Test 1 passed; `http://localhost:8787/`.

**Action / input:** Open the URL, scroll, and select the wordmark/Home link.

**Expected / pass:** Signal Daily styling, introduction and navigation render without broken assets. No published edition yet is a valid empty state. **Fail:** blank page, missing styles, browser error or leaked private draft.

**Failure / recovery:** Check server URL/logs and reload. Try `http://127.0.0.1:8787` to diagnose local hostname issues; keep the configured public origin consistent for mutations.

## 3. Open the administrator dashboard

**Objective:** Verify protected editor entry. **Prerequisites / URL:** Server running; `http://localhost:8787/admin`.

**Action / input:** Choose **Editor login** or open the URL.

**Expected / pass:** **The workbench** and an **Editor password** form appear, or your authenticated dashboard appears. **Fail:** private edition data visible without authentication, endless loading or a backend error.

**Failure / recovery:** Check JavaScript/static responses and refresh; use [login troubleshooting](TROUBLESHOOTING.md#administrator-login-problems). Don't publish screenshots of credentials.

## 4. Log in

**Objective:** Verify authentication and error feedback. **Prerequisites / URL:** Test 3; use the existing private password at `http://localhost:8787/admin`.

**Action / input:** Optionally try `intentionally-wrong-for-test` once, expect rejection, then privately enter the actual `ADMIN_PASSWORD` and select **Unlock workbench**.

**Expected / pass:** Wrong input shows a readable error; correct input shows tabs/stats/editions. **Fail:** wrong input grants access or correct input repeatedly fails.

**Failure / recovery:** Check the correct `.env`/server process and unintended environment overrides. After throttling, wait 15 minutes; do not keep guessing or print the password into an issue.

## 5. Collect fresh news

**Objective:** Verify real RSS collection safely. **Prerequisites / URL:** Normal app login and internet; `http://localhost:8787/admin` → **Source feed**.

**Action / input:** Select **Refresh news sources** once; wait for its result.

**Expected / pass:** A result reports new additions/errors, and cached records show source links. Zero new records with no errors can be successful deduplication. **Fail:** an unexplained exception, invented replacements, or all feeds failing without a visible error.

**Failure / recovery:** Check connectivity/feed URLs, age/relevance filters and clock. Partial failures can coexist with usable records. Do not repeatedly click during collection.

## 6. Generate a real Gemma draft

**Objective:** Verify actual local AI drafting without approval. **Prerequisites / URL:** Test 5, Ollama running and exact installed tag; normal app **Source feed**.

**Action / input:** Select 1–8 useful records and choose **Generate selected with Gemma**. Wait for completion; do not approve/publish the result.

**Expected / pass:** A new **DRAFT** opens with title, subject, introduction, 1–6 complete source-linked items and closing. It stays out of the public archive. **Fail:** unknown sources, invalid JSON, empty required fields or publication without review.

**Failure / recovery:** Read the error; check `/api/tags`, memory, timeout and source content. A validator refusal is a safe failure. Preserve existing drafts, choose other source inputs and retry only after the prior request has ended.

## 7. Open a synthetic draft in the acceptance workspace

**Objective:** Practice safely on fictional content. **Prerequisites / URL:** Demo running at `http://127.0.0.1:8790/admin`; log in using its own credentials file.

**Action / input:** Choose **Import local draft**, upload the repository's `docs/examples/synthetic-newsletter.json`, then **Import as unapproved draft**.

**Expected / pass:** **EDITION #... / DRAFT**, a **Demo:** title and fictional intro; **Editions** tab selected. No approval/publication action has occurred. **Fail:** real data appears, import bypasses draft, or the wrong app/port is open.

**Failure / recovery:** Stop before further actions if it is port 8787. Return to the demo and import the exact JSON fixture, not a Markdown page or your real generated file.

## 8. Edit the synthetic newsletter

**Objective:** Verify editable controls. **Prerequisites / URL:** Test 7's synthetic draft at `http://127.0.0.1:8790/admin`.

**Action / input:** Change **Issue title** to `Demo: My acceptance briefing`; change the intro to `Fictional acceptance test. No real reporting.` Keep complete stories/source URLs.

**Expected / pass:** Fields retain the typed values. Approval/publication controls remain unavailable/disabled for dirty content. **Fail:** text disappears, unrelated data changes or dirty content can be published.

**Failure / recovery:** Check the selected edition and connection. Do not navigate away before saving; there is no autosave or navigation warning.

## 9. Save changes

**Objective:** Verify persistence of the edited revision. **Prerequisites / URL:** Test 8; same demo editor.

**Action / input:** Select **Save as draft**, then **Back to all editions** and reopen **Demo: My acceptance briefing**.

**Expected / pass:** Saved title/intro return and state is **DRAFT**. **Fail:** lost content, silent stale-version overwrite or approval retained after a save.

**Failure / recovery:** A second tab may have changed the version. Copy your unsaved text privately, reload the latest revision and reconcile; don't delete/reset the database.

## 10. Preview the saved edition

**Objective:** Verify reader-like preview and evidence. **Prerequisites / URL:** Test 9; same demo editor.

**Action / input:** Expand **Preview saved edition** and **Collected source evidence**.

**Expected / pass:** The saved title/intro, stories, why-it-matters and source references appear. Example.org links are synthetic placeholders, not actual news. **Fail:** preview silently shows unsaved changes, script markup executes, or required sections are missing.

**Failure / recovery:** Save first, reload and reopen. The preview deliberately shows the saved version. Check that the fixture contains provenance fields for evidence disclosures.

## 11. Submit for review

**Objective:** Verify the review gate. **Prerequisites / URL:** Complete synthetic draft only, port 8790.

**Action / input:** Select **Submit for review**. For a separate error check, clear a required field and confirm review is blocked, then restore/save it before continuing.

**Expected / pass:** State becomes **REVIEW**, with **Approve reviewed edition** / **Request revision**; incomplete content cannot pass. **Fail:** direct draft-to-publication path or missing review event.

**Failure / recovery:** Restore required title/subject/intro/closing/story/source fields. Inspect **Edition history** and the visible validation message; don't bypass the gate in SQLite.

## 12. Approve the synthetic revision

**Objective:** Verify explicit approval and edit invalidation. **Prerequisites / URL:** Only the fictional reviewed edition at `http://127.0.0.1:8790/admin`.

**Action / input:** Select **Approve reviewed edition**. Optionally change a field: publishing should disable; **Save as draft** must reset it to draft. Restore/review/approve again if testing that reset.

**Expected / pass:** **APPROVED** and **Publish online only** appear only for the saved reviewed revision. **Fail:** unsaved changes can publish or saving retains approval.

**Failure / recovery:** Check saved version/history and repeat review after saving. Never substitute a real news draft for this test.

## 13. Publish locally, synthetic content only

**Objective:** Verify deliberate publication without email. **Prerequisites / URL:** Approved **Demo:** edition, demo banner, port 8790 and email disabled.

**Action / input:** Select **Publish online only** and read/accept its confirmation for this fictional test.

**Expected / pass:** **PUBLISHED**, immutable fields, **View published edition**, and zero mail sent. **Fail:** a real edition is selected, mail is attempted or draft/review content bypasses approval.

**Failure / recovery:** Cancel if any prerequisite is wrong. If a long request times out, inspect its current state before retrying. Do not repeatedly publish or modify delivery reservations.

## 14. Verify the local reader page

**Objective:** Verify visibility after publication. **Prerequisites / URL:** Test 13; `http://127.0.0.1:8790/` and the **View published edition** link.

**Action / input:** Open that link and the demo homepage; compare title, intro, stories, why-it-matters and closing.

**Expected / pass:** The fictional edition is readable and indexed on the demo homepage; private/unpublished editions stay hidden. **Fail:** missing page, wrong content, unpublished leakage or a broken layout.

**Failure / recovery:** Check the correct demo port, published status and original slug. This is localhost publication, not a public deployment.

## 15. Search the archive

**Objective:** Verify filtering and empty states. **Prerequisites / URL:** Test 13; `http://127.0.0.1:8790/archive`.

**Action / input:** Search `acceptance`, then `no-such-synthetic-edition`, using **Search**. Try a different **Topic**, then reset to **All topics**.

**Expected / pass:** Matching title appears; unmatched input shows **No editions match. Try another search or topic.** **Fail:** draft leakage, a server exception or filters ignoring saved title/topic.

**Failure / recovery:** Search uses title/intro, not every story paragraph. Confirm the saved title contains `acceptance`, the edition is published and the topic filter is reset.

## 16. Check mobile layout

**Objective:** Verify readable responsive presentation. **Prerequisites / URL:** Demo homepage/archive/editor/edition, port 8790.

**Action / input:** Use the browser's responsive/device toolbar around 390 × 844 CSS pixels, or a narrow browser window. Scroll through forms and reader content.

**Expected / pass:** Text wraps, controls remain usable and the document does not scroll sideways. Tabs may scroll inside their tab bar. **Fail:** clipped controls, overlapping content or page-wide overflow.

**Failure / recovery:** Reset unusual browser zoom and retest; record actual viewport/zoom and a synthetic-only screenshot. Restore normal viewport settings afterward. No physical mobile device is implied by desktop emulation.

## 17. Restart the acceptance app

**Objective:** Verify clean stop/start. **Prerequisites / URL:** Saved fictional edition; acceptance server terminal, port 8790.

**Action / input:** Ctrl+C, then rerun `py -3 tools/demo.py --name acceptance --port 8790 --empty` from the same root.

**Expected / pass:** Same port starts, no second instance/lock error, and a fresh login is needed. **Fail:** duplicate listener, unexpected new DB or lost app state.

**Failure / recovery:** Verify the original process stopped and the same name/path is used. Don't bypass a live lock by deleting its file; OS locks release when the owning process ends.

## 18. Verify persisted data

**Objective:** Confirm restart did not reset editions. **Prerequisites / URL:** Test 17; demo `/admin`, `/archive` and published edition.

**Action / input:** Log in, open **Demo: My acceptance briefing**, read **Edition history**, then open the archive.

**Expected / pass:** Saved content, publication state/history and reader page remain. **Fail:** reset edits, missing rows or changed real app data.

**Failure / recovery:** Check `.tmp/acceptance/demo.db` versus a differently named workspace. Back up before any restoration. Use the [backup tool/runbook](PRODUCTION_RUNBOOK.md#backups-restoration-and-daily-operations), not manual live file copies.

## 19. Run automated tests

**Objective:** Verify regression coverage. **Prerequisites / URL:** Terminal at repository root; no browser URL required. Install `requirements.txt` and `requirements-dev.txt` into your development interpreter.

**Action / input:** Run `py -3 -m unittest discover -s tests -v`, then README's lint/format/compile/JS/security/docs checks.

**Expected / pass:** All discovered tests pass and check commands exit 0; exact counts can grow. External email/model transports are mocked in the suite. **Fail:** any failure/error, hidden skip, nonzero checker or claims based only on an old count.

**Failure / recovery:** Read the first traceback, ensure the selected Python has dependencies, and check temporary-directory/loopback permissions. Don't disable tests to get a green result. CI's Windows/Linux jobs are additional evidence.

## 20. Check error feedback and recover

**Objective:** Verify invalid inputs don't create unsafe state. **Prerequisites / URL:** Isolated demo `/admin` and `http://127.0.0.1:8790/not-a-real-page`.

**Action / input:** In **Import local draft**, paste `{invalid json` and submit; then try a complete fixture with an invalid source URL. Open the missing page. Check a disabled-mail signup only in this demo with `reader@example.org`.

**Expected / pass:** Readable JSON/validation/404/email-disabled messages, no new invalid edition/subscriber, no mail and no exposed stack trace/secret. **Fail:** silent success, private data leak, accepted unsafe URL or outgoing mail.

**Failure / recovery:** Restore the valid fixture, inspect current saved state, and capture only sanitized error text. For Ollama/RSS failures use tests 5–6 on the normal app while leaving output unapproved. The demo intentionally rejects generation and email; that is not a setup defect.

## When any test fails

Stop dependent actions. Preserve the database/unsaved text privately, record the URL/port, exact action, expected versus actual result and application version. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md), rerun the specific test after a fix, then run the automated suite. Keep all approval/publication repetitions inside the fictional workspace. Never send a full `.env`, database, private draft or token-bearing link to GitHub.
