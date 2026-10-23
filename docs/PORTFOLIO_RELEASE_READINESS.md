# Portfolio release readiness

23 October 2026. **PREVIEW VERIFIED; PRODUCTION NOT PROMOTED; EMAIL DISABLED.** This release-preparation report supersedes the dependency/release snapshot in the initial portfolio integration reports. It does not declare FULLY RELEASED.

Portfolio feature commit: `7909c58e409bf316d57d2c2d17c85f6ea144979f`, branch `feat/signal-daily-newsletter`, repository `YellankiKaushik/KAUSHIK`. Production main remains `fd0f0be68e9434854ffb702928c2fadd92ced17d`. No forced push, merge, alias change, paid resource, domain purchase or subscriber send occurred.

| Gate | Actual result |
|---|---|
| Dependency remediation | 20 of 32 affected package entries cleared: both critical, 16 high, 2 moderate |
| Full dependency audit | 12 remain: 0 critical, 7 high, 5 moderate; openly recorded |
| Production dependency audit | 2 moderate; 0 high/critical; runtime audit gate passes |
| Clean install / build / TypeScript | PASS; Vite 7.3.7; no existing unit-test script in portfolio |
| Local real browser | Existing 12 scenarios + expanded 39 checks PASS |
| Exact protected preview | READY; expanded 39 checks PASS; all 23 pre-existing detail routes |
| Public production observation | 35 checks PASS for old site; newsletter route still 404 |
| Portfolio preservation | All 9 original section text hashes and all 23 route headings match production |
| Privacy / signup | Empty catalog; signup disabled; 2 actual deployed JS/CSS assets checked with no known private values/signatures detected |
| Topic/RSS/local Gemma | 47 records, 29 matches, no feed errors; 3 items saved as private DRAFT |
| Approval/export | Unapproved export rejected; approved fictional export and browser rendering passed; fixture removed before commit |
| Portfolio GitHub CI | FAILED / ACCOUNT BLOCKED, runner ID 0, zero executed steps |
| Production promotion | BLOCKED pending portfolio release verification; no bypass |
| Live email | NOT TESTED; provider account/authorized inbox acceptance outstanding |

The remaining high entries derive from one unpatched build-only brace parser. No public request-to-parser path was found in the compiled reader or unchanged API. Remaining Router moderate findings and tooling parser findings are classified in the [dependency report](DEPENDENCY_REMEDIATION_REPORT.md), including each package/advisory and installed version. These exposure findings do not turn a nonzero full audit into a clean scan.

Verified preview: [kaushik-aky7tp2xe](https://kaushik-aky7tp2xe-kaushik-yellanki-project.vercel.app), deployment `dpl_E85SZC6rUtkAZCaNKsr7MxScSHN9`, Vercel project `kaushik` / `prj_XgrIOPf3xzxQpsZ16fLZLafMd3sn`, team `team_UYEpjjRaObtrYF55SYu5rqUl`. Private deployment metadata confirms the exact feature SHA. Protection stayed enabled; a short-lived development token was attached only to this origin. The Vercel connector returned 404; its mapped authenticated CLI fallback verified the project, created the preview and inspected the deployment. [Deployment evidence](portfolio-release-evidence/deployment.json).

## Owner action to restore release verification

The [exact-commit Actions run](https://github.com/YellankiKaushik/KAUSHIK/actions/runs/39947448227) failed before starting any step. Its annotation reports a recent-payment or spending-limit restriction. Repository Actions are enabled; this is not a disabled workflow setting or a frontend assertion failure. The branch endpoint reports main unprotected, but protection/rules endpoints returned 403, so their full policy could not be verified. No security rule or billing setting was changed.

1. As the repository owner, open GitHub account **Settings → Billing and licensing** (the annotation calls it Billing & plans). Inspect the account notice/payment history and **Budgets & alerts** for an exhausted Actions allowance or blocking budget. The annotation alone does not distinguish these causes.
2. If the included private-repository allowance is exhausted, wait for its reset if keeping zero spend. Do not raise a limit or disable a budget stop without an explicit owner spending decision. For a payment/account hold, resolve it directly with GitHub billing/support; no payment details belong in this repository.
3. Once GitHub confirms availability, open the run above and rerun it. It must actually execute install, build, TypeScript and the production-dependency audit. Any newly failing assertion needs correction before promotion. Do not record the old runnerless failure as a success.
4. Review applicable repository rules using owner access, the remaining documented tooling/Router risk and the exact preview commit. Independent local/Vercel checks are supplementary evidence, not a falsely successful GitHub result.

Official references: [Actions billing and included allowance](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [blocking budgets](https://docs.github.com/en/billing/how-tos/set-up-budgets).

## Production release procedure after gates pass

The existing user mission authorizes a normal merge after gates pass. No new domain/VPS is needed. Confirm the feature tip is still the tested commit or revalidate its changes; keep the public catalog empty unless an owner-approved edition is intentionally included, leave `VITE_BUTTONDOWN_USERNAME` unset and email delivery off. Pull main with fast-forward-only, merge the feature branch using normal Git history, and push main without force. Confirm the existing Vercel Git integration creates a production deployment for that exact merge SHA in project `kaushik`; do not promote an unrelated preview build. Then verify `https://kaaush.vercel.app/`, `/newsletter`, all existing sections/deep links, mobile/keyboard behavior and public-content boundaries. Record the actual production deployment/commit before calling the reader release live. A failed deployment/check leaves the prior production version in place; investigate before retrying.

An empty reader archive can be released independently of real newsletter content and email. The first real edition requires [human factual review and explicit approval](FIRST_NEWSLETTER_LAUNCH_GUIDE.md). Email requires the separate [activation checklist](EMAIL_ACTIVATION_CHECKLIST.md).

Evidence: [local browser](portfolio-release-evidence/browser-local.json), [existing acceptance suite](portfolio-release-evidence/browser-existing.json), [preview browser](portfolio-release-evidence/browser-preview.json), [public production](portfolio-release-evidence/browser-production.json), [runner restriction](portfolio-release-evidence/portfolio-ci.json), [editor verification](portfolio-release-evidence/editor-results.json), [privacy checks](portfolio-release-evidence/deployed-privacy.json). Exact final reporting commit/its CI outcome are reported separately; these results identify their actual tested source.
