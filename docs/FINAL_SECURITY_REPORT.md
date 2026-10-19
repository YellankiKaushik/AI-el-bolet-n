# Signal Daily — final security report

Assessment date: **20 October 2026**, Asia/Calcutta. **Targeted assessment: PARTIAL. Seven confirmed mission defects are fixed and verified.** Two local AI privacy defects have five passing regression tests. The Debian application-image advisory issue was resolved by an actually tested/scanned Alpine replacement; the stock Caddy dependency findings were resolved by a rebuilt proxy. Final actual Linux acceptance passed all nine runtime phases, and both strict application/proxy scans returned zero High/Critical findings. Public infrastructure acceptance remains blocked. This assessment is not a full penetration test or a guarantee that all vulnerabilities are absent.

## Scope and evidence

Reviewed `server.py`, `production.py`, `db.py`, `validation.py`, `feeds.py`, `llm.py`, `mailer.py`, local configuration/backup tools, browser rendering, Docker/Compose/Caddy configuration and release audit behavior. Tests used fictional editions, isolated SQLite files, loopback listeners and mocked SMTP. Real RSS and installed `gemma4:e4b` inference were separately verified; real generated content stayed an unapproved private draft.

| Evidence | Observed result |
|---|---|
| [Targeted security review](engineering-evidence/security-review.json) | Two repaired privacy defects; five security regressions passed, zero failed/skipped |
| [Full local suite](engineering-evidence/final-unittest.txt) | 97 tests passed, zero failures/errors/skips; includes the five new privacy tests and Docker metadata regression |
| [Quality/security commands](engineering-evidence/checks.json) | Ruff lint/format, compilation, JavaScript syntax, Bandit, documentation/private-file audits and pinned-package audit exited successfully |
| [Dependency audit](dependency-audit.json) | Ten pinned Python packages checked against OSV; zero advisories returned in this run |
| [Fresh browser results](engineering-evidence/browser-main-results.json), [restart](engineering-evidence/browser-restart-results.json), [subscriber mocks](engineering-evidence/subscriber-browser.json) | 75 fresh browser acceptance checks passed across the combined runs; actual SMTP connections: zero |
| [Current-candidate secret comparison](engineering-evidence/security-final.json) | 245 candidates checked at the final scan; known credential findings empty; exact private-secret comparison recorded true |
| [Historical scan](engineering-evidence/history-scan.json) | 43 locally reachable commits and 204 historical blobs; zero known credential/private-path findings. Its earlier current-candidate snapshot contained 192 files |
| [Final all-ref history and candidate scan](engineering-evidence/history-final-scan.json) | 50 reachable commits, 224 unique blobs and 244 current candidates; zero findings. Two nonempty local credential values compared in memory, without recording values |
| [Original-state comparison](engineering-evidence/environment-final.json) | Original `.env` unchanged; all original database tables unchanged; original backup integrity `ok` |
| [Actual Debian container runtime](engineering-evidence/container-runtime-debian.json) | All nine runtime acceptance phases passed, including real Caddy proxy route/CIDR/request-limit assertions; public HTTPS not tested |
| [Original Debian image scan](engineering-evidence/image-scan-debian-before.json) | Trivy 0.70.0 found 44 High OS-package findings/eight unique advisories; Python-package findings zero. Original strict image gate failed |
| [Actual Alpine runtime](engineering-evidence/container-runtime-alpine.json), [Alpine image scan](engineering-evidence/image-scan-alpine.json) | All nine runtime phases passed; application image has zero High/Critical findings. SEC-03 verified fixed |
| [Original proxy scan](engineering-evidence/proxy-scan-before.json) | Four High binary-dependency entries/three unique advisories in stock Caddy 2.11.7; retained as before-repair evidence |
| [Final actual container/scan workflow](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39321202556) | Source `aaf91a7b955323dc2928d6f9b5d9222037d8fb99`; job `118295414338` succeeded, all nine runtime phases passed, strict application/proxy scans each returned zero High/Critical findings |
| [Final runtime metadata](engineering-evidence/container-final.json), [strict scan summary](engineering-evidence/image-scan-summary.json) | Retained application/proxy image IDs, Python base digest, actual Go/x/net build versions, nine checks and both scan results |
| [Final source release matrix](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39321202509) | All four Windows/Linux Python 3.11/3.12 jobs succeeded for that exact source |

Candidate and history counts describe their recorded scan snapshots. New evidence/documents can increase later candidate counts. The earlier historical scan did not compare private secret values; the final all-ref history scan and current-candidate scan did. These checks do not prove that an arbitrary secret never existed in unreachable objects, remote-only history, binary archives or unrecognized formats.

## Confirmed defects and repairs

### SEC-01 — cloud model tag accepted by local-only drafting client

**Severity: High for the documented local-only privacy guarantee. Status: fixed.** The client accepted `gemma4:cloud` and generated the corresponding model request despite a loopback URL. The reproduction mocked transport and did not invoke a cloud model. Ollama's [primary documentation](https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx) documents that a signed-in local daemon can route cloud models remotely; checking the HTTP destination alone therefore did not establish local inference.

`llm.py` now rejects cloud-token model names before transport. Tests cover `:cloud`, `-cloud`, case variants and cloud namespaces. The installed `gemma4:e4b` tag, structured output and source provenance remain functional; actual fresh local inference produced three validated stories in 15.39 seconds. See [live integration evidence](engineering-evidence/live-integration.json).

### SEC-02 — system proxies and redirects could reroute local inference

**Severity: Medium; requires proxy configuration or a redirecting local responder. Status: fixed.** A fictional loopback Ollama responder returned HTTP 302 to a second listener; the original client followed it and accepted its JSON. Separately, the original default urllib transport sent the fictional prompt and absolute Ollama target URL to a configured loopback proxy when proxy bypass was disabled. No external destination received a prompt.

The client now creates an opener with `ProxyHandler({})` and a redirect handler that rejects redirects. Real loopback regression tests verify that neither the configured proxy nor the redirect target receives a request. A separate test rejects non-loopback model endpoints before transport. Existing response-size, timeout, JSON, source-ID, duplicate-source, inline-citation and detectable unsupported-number checks remain in place.

### SEC-03 — known High advisories in the built runtime base image

**Severity: High, image supply chain. Status: verified fixed for the tested replacement artifact.** The actual application image built from `python:3.12-slim` identified Debian 13.7 packages with **44 High findings across eight unique advisories**: `CVE-2025-69720`, `CVE-2026-16742`, `CVE-2026-54369`, `CVE-2026-76642`, `CVE-2026-78408`, `CVE-2026-78409`, `CVE-2026-78410` and `CVE-2026-9538`. Multiple affected binary packages account for the larger finding count; these are not 44 independent application defects. The scan reported zero Python-package findings and no fixed versions for these recorded OS findings. This was a package-advisory scan, not proof of a reachable exploitation path.

The strict CI image gate failed rather than suppressing those advisories or excluding unfixed results. The Dockerfile now uses official `python:3.12.15-alpine3.24`, retains unprivileged UID/GID 10001, and keeps the same application/data/health behavior. Commit `a72af6848011461c2a9bd6c49183c5e26233fdb9` passed all nine actual runtime phases and its application image scan returned **zero High/Critical findings**. This runtime/scan evidence resolves SEC-03. The separate proxy scan introduced during that run found SEC-04 and prevented a complete pipeline pass.

### SEC-04 — known High advisories embedded in the stock Caddy binary

**Severity: High, proxy supply chain. Status: verified fixed for the tested rebuilt proxy.** The actual stock `caddy:2.11.7-alpine` proxy scan found **four High entries across three advisories**: `CVE-2026-78667`, `CVE-2026-78669` and `CVE-2026-97031`. The binary embedded Go standard library `1.26.8` and `golang.org/x/net v0.59.0`. The scan identifies fixed versions `1.26.9` and `v0.60.0`, respectively. The duplicated HTTP/2 advisory appears in both the standard library and x/net and is counted once when counting unique advisories.

Primary Go reports confirm the affected/fixed ranges for [HTTP/2 resource exhaustion](https://pkg.go.dev/vuln/GO-2026-6611), [HTTP Range handling](https://pkg.go.dev/vuln/GO-2026-6609) and [TLS ECH handling](https://pkg.go.dev/vuln/GO-2026-6607). The [official Go release history](https://go.dev/doc/devel/release#go1.26.9) records the 1.26.9 security update. These are dependency findings; a live exploit or production exposure was not tested.

`deploy/Dockerfile.caddy` now uses the official Caddy builder with `GOTOOLCHAIN=go1.26.9`, rebuilds the same Caddy `v2.11.7` release with `golang.org/x/net@v0.60.0`, and copies that binary into the digest-pinned official runtime image. Caddy's [official xcaddy documentation](https://github.com/caddyserver/xcaddy) supports version-selected builds and dependency replacement; the [official Docker builder template](https://github.com/caddyserver/caddy-docker/blob/master/Dockerfile.builder.tmpl) documents its builder environment. Compose, runtime acceptance and the strict scan now use this built proxy. Commit `aaf91a7b955323dc2928d6f9b5d9222037d8fb99` passed all nine actual runtime phases and strict application/proxy scans in [run `39321202556`](https://github.com/YellankiKaushik/AI-el-bolet-n/actions/runs/39321202556). The actual built proxy reports Go1.26.9 and the x/net v0.60.0 replacement. Both final scan artifacts contain zero findings within the configured High/Critical scope. No finding was suppressed and no severity gate was lowered. This resolves SEC-04 for the recorded artifact; future image/dependency changes require fresh scans.

## Control review

| Control | Verified behavior and boundary |
|---|---|
| Authentication and authorization | Password verification uses PBKDF2 and constant-time comparison. Private edition/history/data/mutation endpoints require signed sessions. Public archive/edition routes select published records. No new confirmed authorization defect was identified |
| Sessions | Signed expiry, tamper rejection, restart invalidation and logout epoch invalidation are tested. Production cookies use `Secure`, `HttpOnly`, `SameSite=Strict`, bounded lifetime and no-store responses. One configured editor account exists; no MFA or separate reviewer role |
| CSRF and production routing | API mutations require a non-simple custom header and reject mismatched supplied Origin. Production uses canonical Host/HTTPS checks and one explicit trusted proxy. Real Waitress tests cover untrusted forwarding peers; actual public ingress is still unverified |
| Brute force and request limits | Production rate limits persist as keyed identities in SQLite. Waitress bounds body/header size, workers, connections and channel timeout; unsupported methods fail. No sustained load/DoS or distributed-abuse claim is made |
| Editorial state | Review → approval → publication remains mandatory. Edits invalidate approval; published editions are immutable. Stale browser approval/publication decisions include the displayed version. Authenticated JSON imports create drafts regardless of supplied status |
| Content, SQL and files | HTML output and browser templates escape supplied text. URL/content/email validators and bounded XML/JSON handling reject tested unsafe forms. SQL values are parameterized; static files use an explicit allowlist. No new confirmed SQL injection, stored-XSS or path-traversal defect was found within this review |
| RSS outbound requests | Configured feeds require HTTPS and public DNS results; redirects receive the same destination check. XML length, UTF-8, DTD/entity and response bounds are enforced. DNS resolution is repeated during connection, so DNS rebinding remains a documented residual |
| Local AI | Only loopback endpoints and non-cloud tags are accepted; system proxies and redirects are disabled. The daemon is a trusted component: renamed/aliased remote models or a malicious local daemon are outside what tag screening can prove. Daemon cloud disablement and host egress policy strengthen that boundary |
| SMTP and consent | Email disabled for public launch until provider/sender/inbox acceptance. TLS modes, header handling, expiring confirmation, POST unsubscribe, active-only eligibility and persistent delivery reservations are tested with mocks. No real SMTP acceptance, sender DNS or inbox delivery was established |
| Private storage and secrets | Original private state remained unchanged. Setup/backup outputs request restrictive creation permissions and preserve existing files. Host filesystem ACLs, encrypted off-host storage, rotation and production secrets require acceptance on the actual host |
| Container and proxy | Final Alpine application and rebuilt Caddy proxy passed all nine actual Linux runtime phases, including nonroot/read-only startup, resource limits, no public app/Ollama ports, persistence, restoration/migration and real Caddy route/CIDR/size checks. Both final strict scans returned zero High/Critical findings. Public HTTPS and production infrastructure are separate unverified gates |

## Container verification boundary

The retained [release evidence at `de5623c`](engineering-evidence/github-de5623c.json) records four successful Windows/Linux Python release-check jobs and an earlier failed Linux container acceptance job. Its null-IPAM allocator defect was repaired in `6db28bd65fd278cca2b22cb0194e116dd0a93b29`. The [subsequent runtime report](engineering-evidence/container-runtime-debian.json) completed **all nine actual phases**, including real Caddy canonical metadata/public archive, four editor CIDR denials and request-body limits on an isolated Docker network. No cleanup errors were recorded. This establishes actual Linux runtime/proxy testing, with `public_https=NOT_TESTED`.

Earlier [BuildKit metadata](engineering-evidence/container-first-failure.json) and [explicit subnet](engineering-evidence/container-second-failure.json) tooling defects were repaired with evidence preserved. All three tooling repairs are implemented and actual runtime acceptance passed. The later Alpine artifact resolved SEC-03, then the added Caddy scan identified SEC-04. The final rebuilt proxy resolved SEC-04 with all nine runtime phases and both strict image scans passing. The [issue register](FINAL_ISSUE_REGISTER.md) records all seven verified fixes. Previous failed scans remain retained; a later passing artifact does not make an earlier failed attempt a pass.

Final container acceptance was executed on a disposable Linux CI runner with synthetic volumes/content and no published host ports. It did not create a persistent public deployment or verify a public certificate. Source/test workflow success and zero findings in a scoped package scan do not establish absence of all vulnerabilities, production ingress safety, off-host recovery or operational monitoring.

## Remaining launch requirements

No suitable existing persistent host or encrypted off-host backup destination was identified in the [bounded hosting discovery](engineering-evidence/hosting-discovery.json). Public HTTPS, intended operator-IP access restrictions, deployed secret/storage permissions, encrypted off-host recovery, monitoring, rollback and production-host patch/configuration acceptance therefore remain unverified. The tested application/proxy images passed their separate acceptance. No public website URL or staging success is claimed.

RSS DNS rebinding, trusted local daemon/model aliases, the single editor account, synchronous work and the absence of production operational acceptance remain explicit limits. They do not erase the passing targeted checks, and those checks do not remove these limits.

The user is **not asked to manually retest the application**. Unavoidable owner actions are limited to connecting suitable existing hosting/backup accounts or authorizing new costs if desired, supplying host/operator access and private production credentials, authorizing a controlled SMTP test mailbox/sender if email is wanted, providing required publisher/contact/privacy information, and reviewing source facts before explicitly approving any real edition. Mail remains disabled until its separate acceptance gates pass.
