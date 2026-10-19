# REA + Codex: reference investigation and original implementation

## Reference and scope

Reference product: [The Rundown AI](https://www.therundown.ai/) (public homepage, archive, edition pages and signup).

Build *Signal Daily* as an original product. Study **visible behavior and information architecture**, not the original publisher's protected content or visual trade dress. We have no access to the publisher's private CMS, subscriber database, email infrastructure or proprietary code. Do not claim those have been reverse engineered.

### What to observe and record

| Feature | Reference behavior to investigate | Implemented here |
|---|---|---|
| Landing page | Lead statement, public signup form, featured newsletters | `server.py:home()` |
| Archive | List of editions and accessible detail pages | `server.py:archive()` |
| Reading page | Date, headline, editorial sections, source links | `server.py:issue_page()` |
| Registration | Email form and confirmation | `/api/subscribe`, `/confirm/<token>` |
| Workflow | The public site does not expose its internal workflow | Our own draft/approve/publish state machine |
| Publishing | Public articles + mailing list | SQLite + SMTP (no private-system inference) |

## Connect REA in your already-installed Codex

Run the *official* REA setup from a terminal (not inside this application):

```bash
npx rea-agents setup
```

Review its installation changes, select Codex if offered, then restart Codex. The downloaded ZIP of REA itself is not your newsletter project.

## Codex prompt: evidence-first passive inspection

> Use the installed REA tools to **passively inspect** the publicly accessible homepage, archive and an edition page of `https://www.therundown.ai/`. Analyze navigation, observable request/response flows, public signup UI states and layout structure. Do not log in, automate form submissions, enumerate subscribers, bypass access controls or fetch private endpoints. Produce an evidence log identifying what you directly observed versus what is only an inference. Compare the observed *functional patterns* against `Signal Daily` in this working directory and suggest improvements. Keep our unique branding, visual design and independently authored text. Do not replicate the reference site's assets or articles.

If REA does not expose a suitable website tool in your installed version, use ordinary browser devtools/manual public-page inspection and label the evidence accordingly. **No actual REA capture was performed as part of this packaged deliverable**; do not report that the reference backend was decompiled.

## Codex prompt: develop and deploy Signal Daily

> Open this Signal Daily folder. Read README.md and docs/REA-CODEX-WORKFLOW.md. Run the tests. Verify the application starts locally. Confirm my actual Ollama model tag with `ollama list`, update `.env`, and generate an edition from real RSS sources. Review UI rendering, approval transitions, double-opt-in registration, unsubscribe, and SMTP send idempotency. Do not publish any edition or email real subscribers before I approve the content. For public deployment, use a persistent Docker or VPS host with HTTPS, persistent `/data`, environment-based secrets and a verified email sender. My local Ollama should remain private: generate draft JSON on my laptop with `tools/local_generate.py`, then import it into the hosted `/admin` dashboard. Do not claim public deployment until you have a verified production URL and completed an end-to-end email test.

## Operational constraints

- REA analyzes public **client-observable** behavior. It cannot reveal the publisher's undisclosed backend implementation.
- Copy *ideas and functional patterns*, not names, logos, distinctive page assets, exact CSS, or articles.
- Reading RSS feed descriptions does not verify all factual claims. Review primary links before publication.
- Local Ollama is not automatically reachable from a cloud deployment; never expose an unauthenticated Ollama port to the public Internet.
