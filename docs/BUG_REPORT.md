# Signal Daily — defect report

> Historical QA snapshot (19–20 October 2026), retained at its recorded revision and counts. The later [complete status](COMPLETE_PROJECT_STATUS.md) and [master report index](MASTER_REPORT_INDEX.md) supersede its current-status, push, Docker and manual-handoff statements. This annotation does not rerun or change the historical results.

19–20 October 2026. **Four reproducible application defects found; four fixed; zero unresolved local defects identified.** Multiple contrast failures share one stylesheet root cause and are counted as one defect. Stale approval/publication share one missing-version-check defect. Harness/environment problems are not counted as application defects.

| ID | Severity | Issue | Root Cause | Fix | Regression Test | Final Status |
|---|---|---|---|---|---|---|
| SD-QA-001 | High | An old reviewed tab approved a newer, unseen reviewed revision; the same stale-tab risk affected publication after another revision was approved | Approval/publication buttons sent no edition version and transitions checked state without the UI's version | Browser supplies its displayed version; API passes it to the database; version comparison occurs inside the same immediate transaction before mutation | New `test_stale_approval_rejects_a_new_unseen_reviewed_revision`, `test_stale_publication_rejects_a_new_unseen_approved_revision`, HTTP propagation test; real-browser B18a/B21a | FIXED / PASS |
| SD-QA-002 | Medium | Muted public/editor text and accent text failed WCAG AA contrast | Several low-contrast hardcoded text colors on tinted/light backgrounds | Darkened only affected text colors, retaining the layout and palette | Final Axe public/editor/import checks plus nine-view survey; initial actual contrast ratios retained | FIXED / PASS |
| SD-QA-003 | Medium | JSON file upload had no accessible name | `input#import-file` lacked a label | Added visible `Upload newsletter JSON` label associated by `for` | B13 now locates/upload via its accessible label; final Axe import scan | FIXED / PASS |
| SD-QA-004 | Medium | A long edition title caused reader overflow on a 320px viewport (observed document width 322px) | Grid children retained automatic minimum content width; edition text had no emergency wrapping | Permit reader grid children to shrink and wrap long content with `overflow-wrap:anywhere` | Deterministic long-number title in retained browser harness; R320 and full narrow reader screenshot | FIXED / PASS |

## Reproduction and evidence

**SD-QA-001:** Import a fictional edition, review it, and open that review in tab A. From client B, save a different subject and review again. Click Approve in A. Before the fix, the newly displayed approved edition had a different subject from the one A reviewed. [Recorded before-fix values](qa-evidence/stale-approval-before.json). For publication, keep an approved version in A while B saves/reviews/approves a new revision; the old publish click had the same omission. After the fix, both old buttons receive `Edition changed. Reload before continuing.`, with no state/history change or SMTP dispatch. [Passing browser cases](qa-evidence/browser-main-results.json). Programmatic database callers can retain the existing no-version transition API; browser actions now bind the deliberate decision to the displayed revision, matching the existing optimistic-save approach.

**SD-QA-002:** Run Axe WCAG A/AA on homepage and editor tabs. Initial examples: assurance text 3.02:1 (required 4.5), step labels 3:1 (required 4.5), tinted-panel descriptions 3.96:1 (required 4.5), and large CTA accent 2.7:1 (required 3). [Initial survey](qa-evidence/axe-initial-all.txt), [final survey](qa-evidence/axe-final-all.json). No stylesheet redesign was needed.

**SD-QA-003:** Open Import local draft and inspect/scan the upload input. Initial Axe `label` violation had critical impact under the tool's rule; application severity is Medium because mouse upload worked while assistive access was impaired. The final input has an explicit visible label and passes accessible-name upload interaction.

**SD-QA-004:** Publish a fictional edition containing a long unbroken title token, open its permalink at 320px and compare `document.documentElement.scrollWidth` with `innerWidth`. Before: 322 versus 320. [Before screenshot](qa-evidence/narrow-overflow-before.png). After: no document overflow at all four requested sizes; [final full narrow reader](qa-evidence/reader-320-full.png).

## Environmental findings and existing limits

- `py -3` has no registered interpreter on this machine; the supported `Start-Local.ps1` fallback worked. The handoff supplies the verified explicit interpreter for demos. No machine registration or `.env` was altered.
- Ollama was stopped at the start; its installed model was present. A loopback-only service was started and actual generation passed.
- No application change was made for Docker absence, public HTTPS or real SMTP: they need external infrastructure/credentials/authorization and remain production blockers.
- No autosave/navigation-loss warning, roles/MFA/recovery, correction/takedown UI or background mail worker exists. These are previously documented product limits, not newly claimed implementations.
- Two exploratory harness invocations needed correction (explicit Playwright context for Axe and rollback of the failed lock-test transaction); they were rerun successfully. They do not count as application defects or passing original attempts.

Source fix commit: `eda3ff6efc809f6ddc6f6dfe8160381b0d25050a`, local branch `qa/acceptance-20261019`. No tests were disabled or assertions weakened. Full final suite: 91 passed, 0 failed, 0 skipped.
