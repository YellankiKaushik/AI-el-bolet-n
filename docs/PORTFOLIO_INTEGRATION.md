# Portfolio integration and cross-repository plan

23 October 2026. Existing portfolio: https://kaaush.vercel.app/. Confirmed Vercel project `kaushik`, ID `prj_XgrIOPf3xzxQpsZ16fLZLafMd3sn`, team `team_UYEpjjRaObtrYF55SYu5rqUl`. Git access succeeded even though the GitHub connector returned 404. The actual source is React18/Vite7/TypeScript/Tailwind/React Router. Baseline portfolio SHA `fd0f0be68e9434854ffb702928c2fadd92ced17d`; integration feature SHA `11969c2c5c513ba279652e777f64c02c90cdb4d2`, branch `feat/signal-daily-newsletter` in `YellankiKaushik/KAUSHIK`.

Plan executed: inspect both projects; add configured-feed topic ranking and manual source selection; retain the local review gate; export only published, approved snapshots; add static portfolio routes and a homepage section; prepare hosted Buttondown signup/private draft API; build/test; validate an isolated Vercel preview before any production release.

The laptop keeps Python, SQLite, credentials and drafts. Only allowlisted public JSON enters `src/data/newsletters.json`. The static site serves published editions without the laptop. No database or Python server is deployed to Vercel. All existing routes, portfolio data and homepage sections remain. Two existing optional-property type errors were repaired without changing content. The catalog is empty in the committed preview: no real news or fictional acceptance fixture is published there.

Production is unchanged. See [workflow](TOPIC_NEWSLETTER_WORKFLOW.md), [publishing](NEWSLETTER_PUBLISHING_GUIDE.md), [provider](EMAIL_PROVIDER_INTEGRATION.md), [tests](PORTFOLIO_TEST_REPORT.md) and [deployment](PORTFOLIO_DEPLOYMENT_REPORT.md).
