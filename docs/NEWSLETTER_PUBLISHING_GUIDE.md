# Explicit publication to the portfolio

23 October 2026. Publication is deliberate: edit → review → approve → publish locally with email disabled → export → inspect JSON diff → feature commit → Vercel preview → approved production release. Local publication alone does not update the portfolio.

```powershell
python tools/publish_portfolio.py --database PRIVATE_DATABASE --issue ID --version CURRENT_PUBLISHED_VERSION --output PORTFOLIO/src/data/newsletters.json
```

The adapter reads SQLite with `mode=ro`, checks current published state/version and matching approval history, then exports a public allowlist only. It omits email subject, authentication/session configuration, subscriber rows, private drafts and internal source descriptions. Public fields are ID, version, slug, publication date, topic, title, introduction, closing and source-backed story text/URLs/dates. Stable identity is scoped to the authoritative Signal Daily database; do not mix unrelated databases into one catalog.

An exclusive destination lock and atomic replacement avoid overlapping writers. Identical repeat exports are no-ops; stale versions, conflicting IDs/slugs and unapproved states fail. The command never commits, pushes, sends mail or changes the private edition. A crashed writer may leave a lock: verify no exporter is active before manually removing only that destination lock. Never overwrite a publication to conceal a correction; create/review a new edition or design an explicit correction workflow.

In the portfolio checkout review `git diff -- src/data/newsletters.json`, commit on a feature branch, push, build and test a Vercel preview. Do not merge the feature branch or promote a preview containing fictional test content. Existing Vercel Git integration may deploy the production branch automatically. Keep local Ollama private. The committed catalog remains empty until the first real edition receives explicit editorial authorization.
