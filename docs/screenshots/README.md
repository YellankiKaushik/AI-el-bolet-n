# Screenshot provenance and reproduction

These are **actual browser screenshots** of Signal Daily. Playwright rendered the running application with a separate `.tmp/screenshots/demo.db`. All newsletters are handwritten fictional fixtures; none is presented as real news or as a real Gemma output. There are no real subscribers, private drafts, administrator credentials, cookies or tokens in the images. SMTP and generation are disabled in this demo.

The demo banner and **Demo:** edition titles identify the sample content. Some editor captures are intentionally scrolled to show the relevant feature. Images are captured directly, without compositing, text substitution, resizing or stretching. PNG compression is lossless. Desktop images use 1440 × 900 CSS/device pixels; mobile uses 390 × 844 CSS pixels at 2× density (780 × 1688 PNG) for sharp text.

| File | Actual view |
|---|---|
| [homepage-desktop.png](homepage-desktop.png) | Reader homepage / original project identity |
| [homepage-mobile.png](homepage-mobile.png) | Narrow responsive homepage |
| [editor-dashboard.png](editor-dashboard.png) | Authenticated fictional edition list and states |
| [newsletter-editor.png](newsletter-editor.png) | Unapproved fictional draft form |
| [newsletter-preview.png](newsletter-preview.png) | Saved preview and source evidence |
| [published-edition.png](published-edition.png) | Fictional published edition on localhost only |

[manifest.json](manifest.json) records dimensions, byte sizes, hashes, viewport, page route and capture state. Every final image was opened and visually reviewed. No captured JavaScript page errors or page-wide horizontal overflow occurred. These are emulated browser sizes, not physical-device testing or proof of SMTP email-client rendering.

## Reproduce with optional maintainer tools

Use a working Python, Node 24 and an installed browser. These Node dependencies are **optional screenshot tools**, not app/runtime requirements. The recorded capture used Playwright **1.62.1**, Sharp **0.35.5**, and the pre-existing Chrome installation.

Terminal 1, from the project root:

```powershell
py -3 tools/demo.py --name screenshots --port 8789
```

This is a fixed fictional workspace, separate from your real app. Its credentials remain private in `.tmp/screenshots/credentials.json`. Do not replace that file with the real `.env`. Reusing the name preserves demo edits; if the expected fixture titles have been changed, choose a fresh private workspace/copy only the fictional fixtures rather than resetting real data.

Terminal 2, from the same root:

```powershell
npm install --prefix .tmp/visuals --no-save playwright@1.62.1 sharp@0.35.5
$env:NODE_PATH=(Resolve-Path .tmp/visuals/node_modules).Path
$env:CHROMIUM_EXECUTABLE=Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'
node tools/capture_screenshots.cjs
```

Only set `CHROMIUM_EXECUTABLE` to an existing browser you installed from a trusted source. If using Playwright's own Chromium, install it and leave that override unset:

```powershell
node .tmp/visuals/node_modules/playwright/cli.js install chromium
Remove-Item Env:CHROMIUM_EXECUTABLE -ErrorAction SilentlyContinue
node tools/capture_screenshots.cjs
```

The script is bound to loopback port 8789 and the private `screenshots` credentials file. It signs in only to that fictional workspace, captures no login screen, validates horizontal geometry/page errors and writes the six documented PNGs plus manifest. Review each output before staging it. Run `py -3 tools/check_docs.py` and the normal release/private-value audits afterward.

Stop the demo with Ctrl+C. No browser profile or Node dependency cache should be committed. [Playwright screenshot API](https://playwright.dev/docs/screenshots) and [browser setup](https://playwright.dev/docs/browsers) explain the underlying renderer.

Older captures are preserved under [archive](archive/README.md) as historical evidence, not used as current product marketing. Unreferenced duplicate preview PNGs were removed from the root; their earlier bytes remain in Git history.
