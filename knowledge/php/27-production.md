---
id: php/27-production
topic: php
slug: production
title: "PHP Production"
type: doc
order: 27
status: ready
tags: [php, production]
related: [php/14-performance, php/13-security, php/08-error-handling, php/25-debugging, php/98-production-checklist]
when_to_use: "Read before deploying a PHP app or reviewing its runtime, config, and deployment setup."
---
# PHP Production

## Purpose

This document defines how to run PHP safely and fast in production: interpreter and OPcache
configuration, deployment strategy, secrets and config handling, health and observability,
and the runtime settings that differ from a developer laptop. The goal is a deployment that
is fast, does not leak information, and can be rolled back in seconds.

Production is where the settings that make development pleasant become liabilities.
Verbose errors, disabled caches, and mutable code paths must be flipped off deliberately.

## Why It Matters

PHP's defaults are tuned for developer convenience, not production. Ship with
`display_errors=On` and you hand attackers stack traces and absolute paths. Ship without a
warmed OPcache and every request recompiles source, wasting most of your CPU. Deploy by
`git pull` on a live server and a half-copied file serves a fatal error to real users. Each
of these is a common, avoidable outage. Getting the runtime and deployment right is what
separates a demo from a service.

## Core Principles

- **Configure the runtime for prod explicitly.** `display_errors=Off`, `log_errors=On`,
  `expose_php=Off`, and OPcache enabled with validation off. Do not rely on defaults.
- **Deploy atomically with instant rollback.** Build an immutable artifact, switch a symlink
  (or container image tag), and keep the previous release ready to swap back.
- **Config comes from the environment, secrets from a vault.** Never bake credentials into
  the image or commit `.env`. The same artifact must run in staging and prod.
- **Cache the framework, not just data.** Compile routes, config, and the container in a
  build step so the first request is not paying startup cost.
- **Make the app observable.** Structured logs, metrics, and a health endpoint are how you
  know it is up — and where it broke — before users tell you.

## Best Practices

- Enable OPcache with `opcache.validate_timestamps=0` in production and clear it on deploy;
  this stops PHP re-checking file mtimes on every request. Consider `opcache.preload` for
  hot classes and the JIT only if profiling shows a CPU-bound win.
- Run PHP-FPM sized to memory: set `pm.max_children` from (available RAM / avg process size),
  not an arbitrary number, or you will swap under load.
- Build a release artifact with `composer install --no-dev --optimize-autoloader` so dev
  tools and unoptimized autoloading never reach production.
- Run framework cache steps at build time (e.g. `config:cache`, `route:cache`,
  `event:cache`) and generate an authoritative classmap.
- Serve behind a reverse proxy/CDN; set `expose_php=Off` and remove the `X-Powered-By`
  header so the PHP version is not advertised to scanners.
- Expose a `/health` endpoint that checks real dependencies (DB, cache, queue) so load
  balancers drain unhealthy instances.
- Set resource limits deliberately: `memory_limit`, `max_execution_time`, upload sizes —
  tuned per workload, not left at defaults.

## Examples

**Good Example** — production runtime and build (illustrative config)

```ini
; php.ini (production) — errors logged, never shown; OPcache trusted, not re-validated
display_errors = Off
log_errors = On
expose_php = Off
opcache.enable = 1
opcache.validate_timestamps = 0   ; do not stat files each request; cleared on deploy
opcache.memory_consumption = 256
realpath_cache_size = 4096K
```

```bash
# Build an immutable release, then atomically switch — previous release stays for rollback
composer install --no-dev --optimize-autoloader --classmap-authoritative
php artisan config:cache && php artisan route:cache
ln -sfn /releases/2026-07-07 /var/www/current   # atomic symlink swap; instant rollback
```

**Bad Example** — deploy in place with dev settings live

```bash
# On the live server, mutating the running code path — users hit half-written files
cd /var/www/app && git pull            # non-atomic; a fatal error is served mid-pull
composer install                       # installs dev deps (phpunit, etc.) into prod
# php.ini still has display_errors=On → stack traces and paths leaked to every visitor
# OPcache validate_timestamps=1 → every request stats the filesystem, wasting CPU
```

## Common Mistakes

- `display_errors=On` in production, leaking stack traces, queries, and file paths.
- Deploying with `git pull`/`rsync` in place, so requests hit partially updated code.
- Installing dev dependencies in production or skipping `--optimize-autoloader`.
- OPcache disabled or `validate_timestamps=1`, forcing recompilation on every request.
- Secrets committed to the repo or baked into the image instead of injected at runtime.
- No health check, so the load balancer keeps routing to a dead instance.
- `pm.max_children` set blindly, causing memory exhaustion and swapping under load.

## Production Tips

- Warm OPcache and run migrations *before* the symlink switch, so the new release serves
  correctly from its first request.
- Ship logs as JSON to stdout and let the platform collect them; a trace id per request
  makes cross-service debugging tractable.
- Keep the previous two releases on disk so rollback is a symlink flip, not a rebuild.

## AI Review Checklist

- Is `display_errors` off, `log_errors` on, and `expose_php` off in the prod config?
- Is OPcache enabled with `validate_timestamps=0` and cleared on each deploy?
- Does the build run `composer install --no-dev --optimize-autoloader`?
- Is deployment atomic (symlink or image tag) with a ready rollback?
- Are secrets injected from the environment/vault, never committed or baked in?
- Is there a health endpoint that checks real dependencies?
- Are framework config/route/container caches generated at build time?

## Related

- `knowledge/php/14-performance.md`
- `knowledge/php/13-security.md`
- `knowledge/php/08-error-handling.md`
- `knowledge/php/25-debugging.md`
- `knowledge/php/98-production-checklist.md`
