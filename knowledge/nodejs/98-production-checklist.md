---
id: nodejs/98-production-checklist
topic: nodejs
slug: production-checklist
title: "Node.js Production Checklist"
type: doc
order: 98
status: ready
tags: [nodejs, production-checklist]
related: [nodejs/26-deployment, nodejs/27-monitoring, nodejs/18-security, nodejs/16-error-handling, nodejs/17-logging]
when_to_use: "Read before shipping a Node.js service to production or signing off a release."
---
# Node.js Production Checklist

## Purpose

This is the go/no-go checklist for putting a Node.js service into production. Every item
is a concrete, verifiable yes/no an agent or reviewer can confirm against the code and
deployment config. If an item cannot be checked, treat it as failing.

## Why It Matters

Most Node.js production incidents are not exotic — they are a missing timeout, an
unhandled rejection, an unbounded body, or a process that never learned to shut down
cleanly. Each item below maps to a known class of outage. Passing the list does not
guarantee success, but every unchecked box is a documented way the service falls over
under real traffic.

## Runtime & Build

**Rules:** [Runtime](01-nodejs-runtime.md) · [Package Management](04-package-management.md)

- [ ] Node.js version is a current **LTS**, pinned via `engines` and `.nvmrc`/Dockerfile.
- [ ] `NODE_ENV=production` is set (enables framework/prod optimizations and disables dev paths).
- [ ] Dependencies installed with `npm ci` (or `pnpm i --frozen-lockfile`) from a committed lockfile.
- [ ] `--max-old-space-size` is set to match the container memory limit (leave headroom).
- [ ] No devDependencies, source maps, or test files shipped in the runtime image.
- [ ] Container runs as a **non-root** user with a read-only filesystem where possible.

## Configuration & Secrets

**Rules:** [Configuration](15-configuration.md) · [Environment](14-environment.md)

- [ ] All configuration is read from the environment and **validated once at startup**; the
      process fails fast if a required var is missing or malformed.
- [ ] No secrets, tokens, or connection strings are committed to the repo or baked into the image.
- [ ] Secrets are injected from a secrets manager / orchestrator, not a `.env` file in the image.
- [ ] The same build artifact runs in every environment, differing only by injected config.

## Resilience & Lifecycle

**Rules:** [Process](10-process.md) · [Error Handling](16-error-handling.md)

- [ ] `SIGTERM`/`SIGINT` trigger **graceful shutdown**: stop accepting, drain in-flight, close DB pools, then exit.
- [ ] `unhandledRejection` and `uncaughtException` are logged and the process **exits** (supervisor restarts it).
- [ ] Every outbound HTTP/DB/cache call has a **timeout** and propagates an `AbortSignal`.
- [ ] Server-level request timeout and `keepAliveTimeout`/`headersTimeout` are configured.
- [ ] Retries use **exponential backoff + jitter** and are capped; non-idempotent calls are not blindly retried.
- [ ] A supervisor (Kubernetes, systemd, PM2) restarts the process on exit.

## Limits & Backpressure

**Rules:** [Streams](06-streams.md) · [Performance](19-performance.md)

- [ ] Request body size is capped; oversized payloads are rejected at the boundary.
- [ ] DB and HTTP connection **pools are bounded** and sized to the workload.
- [ ] Concurrency / queue depth for background work is bounded (no unbounded `Promise.all` over unbounded input).
- [ ] Streams use `pipeline()` and respect backpressure — no manual `.pipe()` without error handling.
- [ ] CPU-heavy work (crypto, big JSON, compression) is off the main thread or rate-limited.

## Observability

**Rules:** [Logging](17-logging.md) · [Monitoring](27-monitoring.md)

- [ ] Logs are **structured JSON** to stdout, with a correlation/request id; no secrets or PII logged.
- [ ] Log level is configurable via env and defaults to `info` in production.
- [ ] Metrics exported (RED: rate, errors, duration) plus **event-loop lag** and memory/heap.
- [ ] Distributed tracing is wired for inbound and outbound calls (OpenTelemetry).
- [ ] Errors are reported to an aggregator (e.g. Sentry) with stack traces and context.

## Health & Deployment

**Rules:** [Deployment](26-deployment.md) · [Cluster](13-cluster.md)

- [ ] `/healthz` (liveness) and `/readyz` (readiness) endpoints exist and reflect real dependency state.
- [ ] Readiness returns **not-ready** during startup and during shutdown drain.
- [ ] Deployment is zero-downtime (rolling/blue-green) and honors the drain period.
- [ ] Resource **requests and limits** (CPU/memory) are set on the container.
- [ ] Horizontal scaling is safe: no in-memory session/state assumed to be shared.

## Security

**Rules:** [Security](18-security.md)

- [ ] `npm audit` / dependency scanning runs in CI and blocks on known-critical CVEs.
- [ ] Security headers set (via `helmet` or equivalent); CORS is explicitly configured, not wildcard-with-credentials.
- [ ] All input is schema-validated; no user input flows into shell, SQL, or file paths unsanitized.
- [ ] Rate limiting protects authentication and expensive endpoints.
- [ ] TLS terminates in front of the app; internal traffic policy is documented.

## Testing & Release

**Rules:** [Testing](21-testing.md)

- [ ] CI runs lint, type-check, and the full test suite on every change; the pipeline is green.
- [ ] Failure paths (timeout, dependency down, bad input) are covered by tests, not just happy paths.
- [ ] A rollback path exists and has been exercised; migrations are backward-compatible.
- [ ] Load/smoke test run against a production-like environment before first release.

## AI Review Checklist

- [ ] Does startup fail fast on missing/invalid config rather than crashing later under load?
- [ ] Is there a wired graceful-shutdown handler that drains before exit?
- [ ] Do all outbound calls have timeouts and bounded retries with backoff?
- [ ] Are logs structured, secret-free, and correlated by request id?
- [ ] Do liveness and readiness probes reflect actual dependency health?
- [ ] Are all resources (pools, body size, concurrency) explicitly bounded?

## Related

- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/27-monitoring.md`
- `knowledge/nodejs/18-security.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/17-logging.md`
