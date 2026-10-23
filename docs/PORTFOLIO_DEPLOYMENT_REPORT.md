# Portfolio preview deployment report

23 October 2026. Target verified through Vercel project metadata and authenticated CLI: project `kaushik`, ID `prj_XgrIOPf3xzxQpsZ16fLZLafMd3sn`, team `team_UYEpjjRaObtrYF55SYu5rqUl`. Portfolio source is `YellankiKaushik/KAUSHIK`, baseline `fd0f0be68e9434854ffb702928c2fadd92ced17d`; feature branch `feat/signal-daily-newsletter` at `11969c2c5c513ba279652e777f64c02c90cdb4d2`.

Vercel connector deployment reads returned 403/404. Its mapped CLI fallback succeeded with the same project/team, without disabling protection or changing account permissions. Existing production deployment `dpl_6Cx1bVxuhwKC6dUUeECTo3m6bQPf` serves the `kaaush.vercel.app` / `kaaushik.vercel.app` aliases. No production promotion, alias reassignment, domain purchase or new host/database was performed.

An initial CLI preview was requested at https://kaushik-99yfdjpnq-kaushik-yellanki-project.vercel.app. Its observed initial state was BUILDING; this is not yet an accepted deployment. Final preview build/status/deep-link and protected-browser acceptance will be recorded after the exact committed source deployment completes. Preview protection stays enabled. The public catalog is empty and Buttondown signup unconfigured; no real news, subscribers or API secrets are shipped.

Production remains UNCHANGED. To release later, review the tested feature diff, verify all original sections, direct routes, private-content boundaries and the exact Vercel project/commit, then merge/promote only with approved public content. Do not interpret a local build or deployment request as live acceptance. The first real edition and subscriber delivery still need independent editorial/account authorization.

## Dependency and release boundary

The actual Vercel install audit reported **32 findings: 7 moderate, 23 high and 2 critical** in the inherited portfolio dependency tree. Dependencies/lockfile were not changed by the newsletter feature. This is an unresolved production-release blocker, not a passing security scan; avoid broad forced dependency upgrades without compatibility testing. The production portfolio remains unchanged.
