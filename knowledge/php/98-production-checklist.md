---
id: php/98-production-checklist
topic: php
slug: production-checklist
title: "PHP Production Checklist"
type: checklist
order: 98
status: ready
tags: [php, production-checklist, upload_max_filesize, post_max_size, opcache.memory_consumption, X-Powered-By, psalm, phpstan]
related: [php/27-production, php/13-security, php/14-performance, php/28-tooling, php/25-debugging]
when_to_use: "Read before promoting a PHP application to production or cutting a release."
---
# PHP Production Checklist

## Purpose

A concrete, verifiable checklist to run before shipping a PHP application to production.
Every item is a yes/no you can confirm by inspecting config, code, or the pipeline. It
complements [production](27-production.md) (the reasoning) with a gate you can enforce.

## Why It Matters

Most PHP outages and breaches trace to configuration left at development defaults:
`display_errors=On` leaking stack traces, OPcache disabled, `.env` committed, no resource
limits. These are invisible in `localhost` and catastrophic under real traffic. A checklist
turns "we think it's ready" into a signed-off, repeatable release gate.

## Runtime & Configuration

**Rules:** [Production](27-production.md) · [Composer](07-composer.md)

- [ ] PHP is a supported, patched version (8.3+ in 2026); EOL versions are removed.
- [ ] `display_errors=Off` and `display_startup_errors=Off` in the production `php.ini`.
- [ ] `log_errors=On` with `error_reporting=E_ALL`, writing to a collected log, not stdout.
- [ ] `expose_php=Off` so the `X-Powered-By` version header is not advertised.
- [ ] `memory_limit`, `max_execution_time`, and `post_max_size`/`upload_max_filesize` are
      set to sane bounds for the workload.
- [ ] `zend.assertions=-1` (assertions compiled out) in production.

## Performance

**Rules:** [Performance](14-performance.md)

- [ ] OPcache is enabled with `opcache.validate_timestamps=0` on immutable deploys.
- [ ] `opcache.memory_consumption` and `opcache.max_accelerated_files` fit the codebase.
- [ ] Preloading (`opcache.preload`) or the framework's cache warmers run at deploy time.
- [ ] Composer autoloader is dumped with `--optimize --classmap-authoritative --no-dev`.
- [ ] Realpath cache (`realpath_cache_size`) is tuned; no per-request filesystem storms.
- [ ] N+1 queries are eliminated; slow-query logging is on and reviewed.

## Security

**Rules:** [Security](13-security.md)

- [ ] No secrets in the repo; `.env` is gitignored and injected from a secrets manager.
- [ ] All database access uses parameterized/prepared statements — no string interpolation.
- [ ] Output is escaped for its context (HTML/attribute/JS/URL); templates auto-escape.
- [ ] CSRF protection is enabled on state-changing routes; sessions are `HttpOnly`,
      `Secure`, `SameSite`.
- [ ] Dependencies pass `composer audit` with no known-exploitable advisories.
- [ ] File uploads are validated by type/size and stored outside the web root.
- [ ] Security headers (HSTS, CSP, `X-Content-Type-Options`) are sent.

## Reliability & Observability

**Rules:** [Error Handling](08-error-handling.md) · [Debugging](25-debugging.md)

- [ ] Uncaught exceptions and fatal errors are captured to an error tracker (e.g. Sentry).
- [ ] Structured logs (PSR-3) include a request/correlation id; no PII or secrets logged.
- [ ] A liveness/readiness health endpoint exists and checks critical dependencies.
- [ ] Timeouts and retries are set on every outbound HTTP/DB call; no unbounded waits.
- [ ] Long-running work runs in queues/workers, not in the request lifecycle.

## Data & Deployment

**Rules:** [Database](12-database.md) · [Production](27-production.md)

- [ ] Database migrations run automatically and are reversible or forward-only by policy.
- [ ] `composer install --no-dev` runs in the release image; dev tools are absent in prod.
- [ ] Deploys are atomic (symlink/immutable image swap) with a tested rollback path.
- [ ] Backups run on a schedule and a restore has been tested, not just assumed.
- [ ] Scheduled tasks (cron) and workers are supervised and restart on failure.

## Verification

**Rules:** [Testing](15-testing.md) · [Tooling](28-tooling.md)

- [ ] The full test suite and `phpstan`/`psalm` pass in CI on the release commit.
- [ ] A smoke test hits critical paths against the built artifact before traffic cutover.
- [ ] Feature flags gate incomplete work; no half-finished code ships enabled.

## AI Review Checklist

- Is `display_errors` off and are errors logged, not rendered, in production config?
- Is OPcache enabled and is the Composer autoloader optimized for the release?
- Are all secrets externalized and is `composer audit` clean?
- Are exceptions captured to a tracker and logs structured with a correlation id?
- Do outbound calls have timeouts, and is heavy work moved to queues?
- Are migrations, backups, and rollback all tested rather than assumed?

## Related

- `knowledge/php/27-production.md`
- `knowledge/php/13-security.md`
- `knowledge/php/14-performance.md`
- `knowledge/php/28-tooling.md`
- `knowledge/php/25-debugging.md`
