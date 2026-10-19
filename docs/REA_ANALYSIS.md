# REA and reference analysis

> Historical snapshot: retain the recorded results and machine details as evidence. For current behavior, portable setup and verification, see [Project status](PROJECT_STATUS.md), [Getting started](GETTING_STARTED.md) and the [documentation release report](GITHUB_DOCUMENTATION_REPORT.md).

Inspected 2026-10-19. Passive public-page reading only. No signup submission, authentication, private API access, code extraction, protection bypass or brand/content copying.

## Local REA findings

The checked-out `rea-main/package.json` identifies `rea-agents` **6.7.0**. It requires Node `^22.19.0 || ^24.11.0 || >=26.0.0`, pins npm 11.16.0, and `.nvmrc` specifies 24.18.0. The machine's PATH Node was 24.16.0, satisfying the declared engine range but differing from the repository pin. `node_modules` and `dist` were absent.

REA supports native binaries, JavaScript/Electron, .NET and browser observation. Native deep analysis uses separately installed providers such as Ghidra, IDA or Hopper; these are not requirements for ordinary page observation. No Ghidra/Java executable was found by the PATH probe. Other installed locations were not exhaustively searched.

`docs/browser-observation.md` describes passive CDP target discovery, DOM/accessibility/script/resource inspection, observation windows, screenshots and evidence comparisons. Those tools can inspect a public frontend through an authorized Chrome-family debugging session. They do not reveal a private CMS or subscriber database. The browser must expose a loopback CDP endpoint; a private automation channel alone is insufficient.

`docs/installation.md` lists Codex integration through local MCP registration and bundled instructions. Setup changes agent configuration and requires approval under REA's own instructions. It was not run or configured during this task.

Executed runtime probe:

```text
node rea-main/scripts/rea.mjs --version
exit 1: REA's compiled runtime is missing. Run npm ci && npm run build:cached ...
```

**Actually exercised:** repository/documentation inspection and the CLI availability probe. **Not exercised:** REA page capture, screenshot comparison, static bundle analysis, native analysis or MCP registration. No dependencies were installed into REA, and no unrelated REA source was changed. Ordinary web reading and Codex browser QA are identified separately below.

## Public evidence and original feature mapping

| Evidence | Confirmed observation | Independently implemented here |
|---|---|---|
| [Homepage](https://www.therundown.ai/) | Prominent email signup, navigation to newsletters/news/guides/tools, recent edition cards and repeated signup opportunities. | Existing original Signal Daily hero, signup forms, recent editions and simple public navigation retained. |
| [Newsletter archive](https://www.therundown.ai/articles) | Public category navigation, newsletter search, pagination and edition listings with editorial metadata. | SQLite-backed search, topic filters, pagination, public edition links and date/topic metadata. |
| [Public edition](https://www.therundown.ai/articles/rogue-ai-agents-sit-for-their-first-interview) | Dated editorial page with introduction, sections, source links, significance/context explanations, closing and further discovery. | Original introduction, numbered stories, why-it-matters sections, primary links, closing and archive navigation. |

The public subscription controls were observed, but the form was not submitted. Confirmation behavior, provider implementation, subscriber storage, private authentication and editorial approval rules could not be inferred from that UI. Double opt-in and review/approval are our own requirements and implementation.

The public page reader supplied structured text, not responsive screenshots or actual interaction recordings of the reference. Its mobile breakpoints, dynamic loading/errors and signup network behavior remain **not verified**. Reference news claims were not independently fact-checked and were not used as application seed content.

## Signal Daily browser evidence

Codex's browser tools, independently of REA, exercised local homepage/archive navigation, search/no-result state, editor login, blank-draft creation, accessible story fields, review, approval, unsaved-edit publication blocking and revision. Screenshots under `screenshots/` show synthetic test fixtures, not real published news. Responsive checks reported no horizontal overflow at all tested sizes; provider scaling produced actual CSS viewport widths 434, 853 and 1600 for requested widths 390, 768 and 1440.

## Boundaries

No reference assets, logo, CSS, proprietary scripts or article paragraphs were copied into the implementation. The existing Signal Daily appearance remains independently authored. No claim is made that REA ran a successful capture or recovered any private implementation. Run official REA setup/build separately if a later investigation specifically needs its evidence workflow.
