# Portfolio dependency remediation report

23 October 2026. The exact feature lockfile was audited before changes: **32 affected package entries (2 critical, 23 high, 7 moderate)**. Compatible remediation cleared **20 entries: both critical, 16 high and 2 moderate**. Final full-tree audit: **12 entries (0 critical, 7 high, 5 moderate)**. Final `npm audit --omit=dev`: **2 moderate, 0 high/critical**. Counts are affected packages, not distinct vulnerabilities. The audit remains nonzero; it has not been suppressed.

Removed unused `@huggingface/transformers` after searching source/API/config imports. Its declared production tree contained ONNX → protobufjs (untrusted schema/code generation/recursion), ONNX Node → tar (archive extraction/parsing) and sharp (native image decoding). None was used by the portfolio application. Removal clears these packages rather than forcing Transformers 4 or claiming their APIs were tested. Removed unused `lovable-tagger`. Moved `tailwindcss-animate` to devDependencies because only the Tailwind build configuration imports it; no runtime/API import exists.

Ran `npm audit fix --ignore-scripts` **without `--force`**. Supported updates retain existing top-level major versions, including Vite 7.3.7, PostCSS 8.5.31, Router DOM 6.30.6, TypeScript ESLint 8.72.0, Browserslist 4.29.4, source-map-js 1.2.2, js-yaml 4.3.2, nanoid 3.3.20 and humanfs/node 0.16.8. Regenerated lockfile was verified with `npm ci`. Existing pages, API, Vercel rewrites and portfolio data were not rewritten. Build, TypeScript, 12 existing browser checks and 39 expanded local browser checks passed.

## Findings that remain

**Seven high build-only entries:** braces, chokidar, micromatch, fast-glob, globby, gh-pages and tailwindcss. They share [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm), whose upstream advisory lists no patched version. The traced call is fast-glob → micromatch.braces → braces. Tailwind glob patterns are fixed repository paths such as `./src/**/*.{ts,tsx}`; gh-pages is a developer deployment command. The static reader and portfolio-chat function do not execute these tools or accept public glob patterns. No public exploit path was found. The advisory is still present; do not expose build tooling or execute untrusted repository configuration with credentials. Migrating Tailwind 3 to 4 solely to remove this graph requires a separate CSS compatibility review.

**Three moderate build-only entries:** postcss-selector-parser, postcss-nested and @tailwindcss/typography, through [GHSA-rj75-hqrm-r3gf](https://github.com/advisories/GHSA-rj75-hqrm-r3gf). Existing 6.x consumers are constrained below the patched 7.x parser. They process repository CSS, not public request bodies. No unreviewed cross-major override was introduced.

**Two moderate runtime entries:** react-router/react-router-dom, from [untrusted navigation targets](https://github.com/remix-run/react-router/security/advisories/GHSA-wrjc-x8rr-h8h6) and [SSR error hydration](https://github.com/advisories/GHSA-337j-9hxr-rhxg). This portfolio uses BrowserRouter client rendering without SSR error deserialization. Its navigation targets use fixed internal paths/repository data; exported newsletter slugs are validated. No attacker-controlled redirect input was identified. The complete supported fix requires Router 7; retaining Router 6 avoids an unnecessary routing migration while explicitly recording residual risk.

The workflow adds `npm audit --omit=dev --audit-level=high`. This runtime gate passed independently; it does not imply the full-tree audit is clean. GitHub's account restriction still prevents the portfolio runner from starting. Production promotion remains on hold rather than bypassing that verification gate. No billing, visibility or runner setting was changed.

## Package-by-package classification

Full advisory titles, ranges, identities, installed paths/versions and development flags are retained in [the sanitized review](portfolio-release-evidence/dependency-review.json). Each indirect entry inherits the listed upstream advisories; this avoids counting a dependency chain as multiple independent CVEs.

| Package | Before | Initial scope | Current versions | Result |
|---|---|---|---|---|
| `@huggingface/transformers` | 3.7.2; high | declared production/peer | removed | cleared |
| `@humanfs/node` | 0.16.7; moderate | dev only | 0.16.8 | cleared |
| `@protobufjs/utf8` | 1.1.0; moderate | declared production/peer | removed | cleared |
| `@remix-run/router` | 1.23.2; moderate | declared production/peer | 1.23.4 | cleared |
| `@tailwindcss/typography` | 0.5.15; moderate | dev only | 0.5.20 | remaining moderate |
| `@typescript-eslint/eslint-plugin` | 8.11.0; high | dev only | 8.72.0 | cleared |
| `@typescript-eslint/parser` | 8.11.0; high | dev only | 8.72.0 | cleared |
| `@typescript-eslint/type-utils` | 8.11.0; high | dev only | 8.72.0 | cleared |
| `@typescript-eslint/typescript-estree` | 8.11.0; high | dev only | 8.72.0 | cleared |
| `@typescript-eslint/utils` | 8.11.0; high | dev only | 8.72.0 | cleared |
| `brace-expansion` | 1.1.13, 2.0.3; high | declared production/peer | 1.1.21, 2.1.7, 5.0.12 | cleared |
| `braces` | 3.0.3; high | declared production/peer | 3.0.3 | remaining high |
| `browserslist` | 4.24.2; high | dev only | 4.29.4 | cleared |
| `chokidar` | 3.6.0; high | declared production/peer | 3.6.0 | remaining high |
| `fast-glob` | 3.3.2; high | declared production/peer | 3.3.3 | remaining high |
| `gh-pages` | 6.3.0; high | dev only | 6.3.0 | remaining high |
| `globby` | 11.1.0; high | dev only | 11.1.0 | remaining high |
| `js-yaml` | 4.1.1; high | dev only | 4.3.2 | cleared |
| `lovable-tagger` | 1.1.13; high | dev only | removed | cleared |
| `micromatch` | 4.0.8; high | declared production/peer | 4.0.8 | remaining high |
| `nanoid` | 3.3.11; high | declared production/peer | 3.3.20 | cleared |
| `postcss` | 8.5.6; high | declared production/peer | 8.5.31 | cleared |
| `postcss-selector-parser` | 6.0.10, 6.1.2; moderate | declared production/peer | 6.0.10, 6.1.5 | remaining moderate |
| `protobufjs` | 7.5.4; critical | declared production/peer | removed | cleared |
| `react-router` | 6.30.3; moderate | declared production/peer | 6.30.6 | remaining moderate |
| `react-router-dom` | 6.30.3; moderate | declared production/peer | 6.30.6 | remaining moderate |
| `sharp` | 0.34.3; high | declared production/peer | removed | cleared |
| `source-map-js` | 1.2.1; high | declared production/peer | 1.2.2 | cleared |
| `tailwindcss` | 3.4.17; high | declared production/peer | 3.4.19 | remaining high |
| `tar` | 7.5.13; critical | declared production/peer | removed | cleared |
| `typescript-eslint` | 8.11.0; high | dev only | 8.72.0 | cleared |
| `vite` | 7.3.1; high | dev only | 7.3.7 | cleared |
