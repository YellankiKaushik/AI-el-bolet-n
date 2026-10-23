# First real newsletter launch guide

23 October 2026. The draft/export workflow is ready. **No real edition has been automatically approved or published.** The production reader release remains gated in [release readiness](PORTFOLIO_RELEASE_READINESS.md); email is independent and stays off.

1. In the private Signal Daily folder run `./Start-Local.ps1`. It binds to loopback, enables local generation and forces email delivery off while preserving existing `.env`/data. Start the installed Ollama service if needed; keep it on `127.0.0.1:11434`. Open `http://localhost:8787/admin` with your existing local credentials.
2. Open **Source feed**, enter a topic, then **Refresh news sources**. The search covers configured trusted RSS/Atom feeds, not the unrestricted web. Review the match count and source dates, open primary URLs, and select the final stories. If results are insufficient, refine the topic or approved feeds; do not ask the model to invent missing news.
3. Choose **Generate selected with Gemma**. The installed `gemma4:e4b` creates a private unapproved draft. Fresh acceptance collected 47 records/29 topic matches and generated 3 items as DRAFT, with zero feed errors. The actual model text is retained only in an isolated private database; [public counts](portfolio-release-evidence/editor-results.json).
4. Check every factual claim, numerical detail, source URL/date and headline against the original sources. Edit introduction, topic, stories and closing. Save as draft, preview, then **Submit for review → Approve reviewed edition** only when you personally accept its contents. Edits reset approval. This guide and automated acceptance are not factual approval of your first real issue.
5. With email still disabled, choose **Publish online only**. This publishes only to the loopback editorial application; it does not update the portfolio. Note the published issue ID and current version. If needed, inspect metadata privately in Python after loading your local configuration:

   ```python
   from config import load_env
   load_env()
   import db
   print([(i['id'], i['version'], i['status'], i['title']) for i in db.get_issues()])
   ```

6. Export only that approved/published revision from the configured private database. From Signal Daily, substitute your real database path, ID and version:

   ```powershell
   python tools/publish_portfolio.py --database "PRIVATE_DATABASE" --issue ISSUE_ID --version PUBLISHED_VERSION --output "../portfolio/src/data/newsletters.json"
   ```

   The default database is `data/signal_daily.db`; honor a custom `DATABASE_PATH` in your private configuration. The command reads SQLite without modifying it, requires the exact published revision and approval snapshot, and exports only public allowlisted fields. Identical export is a no-op; stale/conflicting identity or revisions are rejected. It does not commit, push or email. Never copy the full database or private admin response into the portfolio.
7. In the portfolio use a feature branch, inspect `git diff -- src/data/newsletters.json`, build/type-check/audit and test the actual preview permalink. Verify only the deliberately approved edition, source attribution, dates and mobile rendering are present. Keep subscriber signup disabled. Resolve the current account-level CI restriction and all applicable release gates before a normal production merge; never release the local fictional acceptance fixture.
8. After the exact production deployment succeeds, open `https://kaaush.vercel.app/newsletter` and the edition permalink, verify the content and existing portfolio pages, and retain the source/deployment SHA. The static edition remains available while the laptop is offline. Creating a provider draft and sending any email are separate actions under the [email checklist](EMAIL_ACTIVATION_CHECKLIST.md).

Use the same authoritative database/catalog pairing. If an export leaves a `.json.lock` after a crash, first verify that no exporter is active; preserve evidence and remove only that destination lock before retrying. Do not overwrite an existing publication to conceal a correction. Create and review a new correction edition unless an explicit correction workflow is designed.
