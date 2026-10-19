# User guide

Signal Daily is a browser workbench for a human editor. AI prepares a draft; you decide what is accurate and when it should be published. This guide describes the current controls, including what is intentionally unavailable.

## Reader pages

Open [the homepage](http://localhost:8787). **Home** returns there; **Archive** lists published editions. **All editions** and the cards open the archive/individual editions. On narrow screens the redundant Home link is hidden; the wordmark still returns home.

The archive supports **Search editions**, **Topic**, **Search** and pagination. Searches match saved title/introduction text. Draft, review and approved editions remain private. A reader page includes the introduction, numbered stories, why-it-matters sections, source links and closing note. An empty archive is normal before your first publication.

![Fictional published edition showing the reader page](screenshots/published-edition.png)

*Synthetic demo data, captured from the real application on localhost. These are not real published news claims.*

## Enter the workbench

Open [the editor](http://localhost:8787/admin), enter `ADMIN_PASSWORD` from your private `.env`, and choose **Unlock workbench**. There is no username, signup or password recovery flow. Repeated failed attempts are throttled. **Log out** invalidates current sessions; a server restart also requires a new login.

The dashboard shows cached **NEWS SOURCES**, all **UNPUBLISHED** editions, **PUBLISHED** editions and active confirmed **SUBSCRIBERS**. Its tabs are **Editions**, **Source feed**, **Import local draft** and **Publishing setup**.

![Actual dashboard with fictional edition states](screenshots/editor-dashboard.png)

## Prepare your first edition

### Collect and select

In **Source feed**, click **Refresh news sources**. Results report additions and feed errors. Zero additions can mean deduplication found only already cached URLs. Records include publisher, date, description where available and **Original story** links. Invalid/out-of-window records can be excluded, so a reachable feed need not contribute articles.

Select relevant checkboxes and choose **Generate selected with Gemma**. The client uses up to eight selected records and returns one to six stories. On **Editions**, **Generate with Gemma** instead selects recent cached sources automatically. Ollama must be running locally with the configured installed tag. Generation can take time; wait for completion and avoid duplicate clicks. Errors never trigger a cloud fallback.

### Start or import without AI

**+ New blank edition** creates an incomplete draft for writing manually. **+ Add another story** adds fields; **Remove** removes that draft item. Complete content and sources are required before review.

For JSON, choose **Import local draft**, paste/upload a complete file, then **Import as unapproved draft**. Invalid JSON shows an error and does not create an edition. An incoming status cannot bypass the draft gate. A complete [fictional example](examples/synthetic-newsletter.json) is available for an isolated demo workspace.

The local CLI is another option:

```powershell
py -3 tools/local_generate.py --output local-drafts/edition-UNIQUE-NAME.json
```

Choose a new filename. The CLI creates the parent directory, refuses overwrites and does not publish or save into the app database. Import its file to edit it in the workbench.

### Edit and preview

Open an edition row. Edit **Issue title**, **Email subject**, **Topic**, **Opening / editorial introduction**, each story's **Headline**, **Summary (fact-checked)**, **Why it matters**, **Source name**, **Source URL**, and **Closing note**. “Fact-checked” is an instruction for you, not a claim that the AI verified the prose.

![Editable fictional draft with source fields](screenshots/newsletter-editor.png)

Select **Save as draft**. Expand **Preview saved edition**, **Collected source evidence** where available, and **Edition history**. Preview shows the saved revision; save first to see changes. The evidence is a feed excerpt and may be incomplete. Open the original links yourself and check attribution, dates, numbers and implications.

![Saved fictional draft preview](screenshots/newsletter-preview.png)

Unsaved edits disable approval/publication. Saving an edition in review/approved state resets it to draft. A stale save from another tab is rejected; reload the latest saved version and reconcile your changes. There is no autosave or unsaved-navigation protection.

## States, review and publication

| State | Available editorial decision |
|---|---|
| DRAFT | Edit/save, inspect saved preview, **Submit for review** |
| REVIEW | Check the saved revision, **Approve reviewed edition** or **Request revision** |
| APPROVED | **Request revision**, or deliberately publish after your final check |
| PUBLISHED | Read-only fields and **View published edition**; no edit/takedown UI |

Submitting for review saves the current content first. Incomplete fields/invalid sources block review. Any save or requested revision returns the edition to draft. Approval is recorded, but the same configured account can perform both review and approval; there are no independent editor roles.

With mail disabled, the final control is **Publish online only** and its confirmation states no messages will be sent. On a loopback-only laptop this publishes to localhost, not the internet. With working, explicitly enabled SMTP it becomes **Publish + notify subscribers** and attempts the first delivery batch immediately. Never approve/publish real news just to test a button—use the isolated demo.

After publication, check the homepage, **Archive** and **View published edition**. Published content is immutable; there is currently no correction/delete UI, so decide on your correction policy before releasing real content.

## Subscribers and optional email

Reader signup uses the email form, then a one-use confirmation link valid for 24 hours. Only active confirmed records are eligible for editions. Unsubscribe GET shows a confirmation page; a POST changes consent. The email's one-click unsubscribe also uses POST.

The dashboard shows the active subscriber count. **There is no subscriber list, bulk import/export, per-address management or deletion screen.** Consent/delivery behavior is implemented in the backend and tests. Retention, complaint handling and exceptional data maintenance require an operator with a backup; do not casually edit SQLite.

Email is disabled by default and the Windows launcher deliberately keeps it off. **Publishing setup** describes requirements but does not save configuration; edit `.env` privately and restart. `SMTP_HOST`, `MAIL_FROM`, valid TLS settings and any required credentials must be configured, and `EMAIL_DELIVERY_ENABLED=true` explicitly chosen outside the mail-off launcher. This task did not configure or test a real provider.

With email enabled, **Send / retry subscriber delivery** handles another bounded batch for a published edition. It is hidden when mail is disabled. Sent/in-flight/uncertain reservations are excluded. A transport disconnect can leave unknown acceptance; reconcile provider logs before changing a held claim. Never blindly retry it. [SMTP setup and operations](PRODUCTION_RUNBOOK.md#smtp-setup-and-consent-rehearsal).

## Safe local habits

- Keep the server and Ollama on loopback; no port forwarding or tunnel is required.
- Do not share `.env`, database files, backups, subscriber details or private drafts.
- Use [the manual testing guide](LOCAL_TESTING_GUIDE.md) and its separate fictional workspace for repeated publication checks.
- Back up before upgrades. A restart retains data but invalidates login sessions.
- If an error occurs, inspect the visible message, current saved state and [troubleshooting guide](TROUBLESHOOTING.md) before repeating a long action.
