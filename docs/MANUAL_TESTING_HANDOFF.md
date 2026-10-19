# Signal Daily — your manual testing handoff

Automated local acceptance completed on 20 October 2026, following tests begun on 19 October (Asia/Kolkata). The normal app was left running and its health endpoint returned HTTP 200 after temporary test servers were stopped. It is a background process, not a Windows service, so it may stop when the machine/app session ends.

## 1. Open your existing app

Open [http://localhost:8787](http://localhost:8787), then [Editor login](http://localhost:8787/admin). An empty public homepage is expected: your two existing drafts were preserved and neither was published. Your original 19 source records and `.env` are unchanged.

If the app is unavailable, open PowerShell in the project folder and run:

```powershell
Set-Location 'C:\Users\YellankiKaushik\Desktop\KAUSHIK\ALL Projects\AI Newsletter\signal-daily'
.\Start-Local.ps1
```

Keep that terminal open. The launcher finds a working Python and forces loopback-only operation and email off. Do not start another copy when the existing page already works. If PowerShell blocks the script, use the direct commands in [getting started](GETTING_STARTED.md#5-start-signal-daily); do not change Windows security policy.

## 2. Find your password privately

In that folder, open `.env` privately in Notepad or your editor. Find the value after `ADMIN_PASSWORD=`. Enter it in **Editor password**, then **Unlock workbench**. No username is required. Do not paste that value into chat, screenshots or GitHub. Do not change `.env` for these tests.

The dashboard tabs are **Editions**, **Source feed**, **Import local draft**, and **Publishing setup**. The counters show cached sources, all unpublished editions, published editions and confirmed subscribers. Open an edition row to inspect it. Your real drafts should remain unapproved while you practice.

## 3. Start a separate fictional practice app

Use a second PowerShell window in the same project folder. The `py -3` command is broken on this laptop; use the working existing interpreter below instead:

```powershell
$SignalPython=Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $SignalPython tools/demo.py --name user-acceptance-20261019 --port 8790 --empty
```

Keep this terminal open too. Open [http://127.0.0.1:8790/admin](http://127.0.0.1:8790/admin). Check that the page says **DEMO WORKSPACE**. This app has its own database and cannot send mail or generate real-news drafts. If `user-acceptance-20261019` already exists, it preserves its data; choose a new name such as `user-acceptance-2` for a fresh empty practice app.

Open `.tmp\user-acceptance-20261019\credentials.json` privately and use its `ADMIN_PASSWORD`. It is different from your normal password. If you chose another name, use that name's folder. The automated-audit databases remain preserved separately; there is no need to delete/reset them.

## 4. Import the fictional edition

In the demo, choose **Import local draft**. Under **Upload newsletter JSON**, select `docs\examples\synthetic-newsletter.json`. Select **Import as unapproved draft**. You should see a **Demo:** title and **DRAFT** status. All names, claims and example.org links in this fixture are fictional placeholders.

## 5. Edit and save

Change **Issue title** to `Demo: My acceptance briefing`. Change **Email subject**, **Topic**, **Opening / editorial introduction**, story **Headline**, **Summary (fact-checked)**, **Why it matters**, **Source name**, **Source URL**, and **Closing note** as desired. Keep valid `https://example.org/...` URLs and complete story fields for the fictional test.

Use **+ Add another story** and **Remove** if useful. Select **Save as draft**. Then **Back to all editions**, reopen the edition and verify your edits returned. There is no autosave or warning before navigating away: save before switching tabs/pages. If a second tab saved a newer version, copy your unsaved text privately, reload and reconcile instead of overwriting it.

## 6. Preview exactly what was saved

Expand **Preview saved edition**. Check the title, introduction, story order, summaries, why-it-matters text, source names/URLs and closing. Expand **Collected source evidence** where present. Preview shows the saved revision; typing without saving does not update it. Changing a source URL clears the old source evidence rather than attaching it to a different source.

## 7. Review and approve the fictional edition

Select **Submit for review**. You should see **REVIEW**. Missing introduction, closing, story details or invalid URLs prevent review and show an error. **Request revision** returns the edition to draft.

When this fictional saved version looks right, select **Approve reviewed edition**. You should see **APPROVED**. Unsaved edits disable approval/publication. Saving an approved edition returns it to **DRAFT**, so review and approve again after a change. An old tab cannot approve or publish a newer revision that another tab saved: reload when told the edition changed.

## 8. Publish only inside the fictional demo

Confirm the browser is still on **127.0.0.1:8790**, the demo banner is present, and the title is your **Demo:** fixture. Select **Publish online only**, read and accept its confirmation. The state becomes **PUBLISHED**, the fields become read-only and no email is sent.

Open **View published edition**. Also open the [demo homepage](http://127.0.0.1:8790) and [archive](http://127.0.0.1:8790/archive). Search `acceptance` and try the saved topic. Check that your fictional edition appears and unapproved drafts do not. Local publication is visible on your computer; it does not deploy a website.

## 9. Stop and restart the demo

Press Ctrl+C in its terminal. Run the same demo command with the **same name** again. Log in again, open the reader page and check that the publication survived. When finished, Ctrl+C stops that demo without deleting its data. The normal app is separate.

## 10. Try real sources and Gemma when ready

Use the **normal** app at [http://localhost:8787/admin](http://localhost:8787/admin). In **Source feed**, select **Refresh news sources**. Zero additions is normal when the stories are already cached. Select 1–8 relevant checkboxes, then **Generate selected with Gemma**. Wait while the button is disabled; an actual generation here will create a private draft, not approve it.

Ollama must be running with `gemma4:e4b`. The audit left its loopback service available. If it has stopped, open the installed Ollama application; use `ollama serve` only when another service is not already running. Do not expose port 11434 or select a cloud model. A cold model may take longer than the audit's observed 12–15 seconds. Feed failures or safe model-validation refusals should be read and investigated, not bypassed.

## Expected limitations and your judgment tasks

- Signup on the normal/demo app says subscriptions are unavailable while email is off. This is expected. The subscriber and SMTP logic passed simulated transport tests; no live provider or inbox was tested.
- Public hosting/HTTPS, Docker, sender DNS, real email clients, off-host backups and production operations remain unverified. Do not invite real subscribers yet.
- Real summaries require your review: open original articles, check dates, source identity, numbers, names, quotations and implications. The model sees RSS descriptions and can still make mistakes.
- Decide whether the writing, visual layout, mobile readability, keyboard experience and error messages meet your needs. Try your own browser/device and assistive technology where relevant.
- Published editions are immutable and there is no correction/takedown UI. Decide how you would handle a correction before deliberately publishing actual news.
- Source links in the fictional fixture are placeholders and need not lead to real articles. Real feed links were retained and one original-source link was opened during the live browser audit.

If you find a problem, record the workspace/URL, browser, exact clicks, expected result and error text. Use fictional content for screenshots; omit passwords, cookies, tokens, real subscriber addresses and private drafts. The full results are in [final QA report](FINAL_QA_REPORT.md).
