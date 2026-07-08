---
id: php/07-composer
topic: php
slug: composer
title: "Composer"
type: doc
order: 7
status: ready
tags: [php, composer]
related: [php/06-autoloading, php/24-psr-standards, php/28-tooling, php/27-production]
when_to_use: "Read before adding a dependency, editing composer.json, or setting up an install in CI/CD."
---
# Composer

## Purpose

This document defines how to use **Composer**, PHP's dependency manager, to declare,
install, and lock third-party packages and to configure project [autoloading](06-autoloading.md).
Composer resolves a dependency graph from `composer.json`, records exact resolved
versions in `composer.lock`, and installs them into `vendor/`. This doc is written so an
agent produces reproducible, secure installs rather than "latest and hope".

## Why It Matters

Dependencies are the largest slice of most PHP applications' code, and Composer is how
that code enters the build. An unpinned or unaudited dependency is a supply-chain risk
and a reproducibility hazard: two installs of the same commit can pull different code if
the lock file is ignored. A subtle version-constraint mistake can silently upgrade a
package across a breaking change and take down production. Treating `composer.lock` and
constraints with the same rigor as source code is what makes builds deterministic.

## Core Principles

- **The lock file is the source of truth for what runs.** `composer.json` states intent
  (constraints); `composer.lock` records the exact resolved versions and hashes. Both
  are committed; `vendor/` is not.
- **Constrain with intent.** Use caret (`^1.2`) to allow compatible updates within a
  major version; that is the sane default under semantic versioning. Pin exactly only
  when you must, and never use `*` or an unbounded `>=`.
- **`install` reproduces; `update` changes.** `composer install` builds exactly what the
  lock file says. `composer update` re-resolves and rewrites the lock. CI must run
  `install`, never `update`.
- **Separate runtime from tooling.** Production dependencies go in `require`; test,
  static-analysis, and formatting tools go in `require-dev` and are excluded from prod.
- **Audit continuously.** A dependency with a known CVE is a live vulnerability;
  `composer audit` must be part of the pipeline.

## Best Practices

- Add packages with `composer require vendor/pkg` (and `--dev` for tooling) so Composer
  picks a correct constraint and updates the lock atomically.
- Commit `composer.json` and `composer.lock` together in the same change. A lock file
  that drifts from `composer.json` is a review red flag.
- In CI and production, install with
  `composer install --no-dev --prefer-dist --no-interaction --optimize-autoloader`.
  `--no-dev` keeps test tooling out of the artifact; `-o` builds the fast classmap.
- Pin the PHP version and required extensions in the `config.platform` and `require`
  keys (`"php": "^8.3"`, `"ext-json": "*"`) so resolution matches the runtime.
- Run `composer audit` in CI and fail the build on known advisories. Run
  `composer outdated --direct` periodically to plan upgrades deliberately.
- Set `"config": { "sort-packages": true }` and keep scripts (lint, test, analyse) under
  the `scripts` key so contributors have one entry point.

## Examples

**Good Example** — reproducible, scoped, pinned to the runtime

```json
{
    "require": {
        "php": "^8.3",
        "ext-mbstring": "*",
        "guzzlehttp/guzzle": "^7.8"     // caret: compatible 7.x updates only
    },
    "require-dev": {
        "phpunit/phpunit": "^11.0",     // test tooling, excluded from prod
        "phpstan/phpstan": "^2.0"
    },
    "config": { "sort-packages": true, "optimize-autoloader": true }
}
```

```bash
# CI/production: deterministic, no dev tooling, fast autoload.
composer install --no-dev --prefer-dist --no-interaction --optimize-autoloader
composer audit                 # fail the pipeline if a dependency has a known CVE
```

**Bad Example** — non-reproducible and unsafe

```json
{
    "require": {
        "guzzlehttp/guzzle": "*",        // any version: a breaking major can slip in
        "phpunit/phpunit": ">=9"         // test tool leaked into runtime require
    }
}
```

```bash
composer update            # in CI: re-resolves every build -> non-reproducible
# vendor/ committed to git and lock file ignored -> nobody knows what actually runs
```

## Common Mistakes

- Running `composer update` in CI/deploy instead of `install`, making builds
  non-deterministic.
- Ignoring or not committing `composer.lock`, so environments diverge.
- Using `*` or unbounded `>=` constraints that admit breaking upgrades.
- Placing test/dev tooling in `require`, bloating and widening the production surface.
- Committing `vendor/` to version control instead of installing it in the pipeline.
- Never running `composer audit`, shipping known-vulnerable packages.
- Editing `composer.json` by hand and forgetting to update the lock file.

## Production Tips

- Cache Composer's global cache (`~/.composer/cache` or `COMPOSER_CACHE_DIR`) in CI to
  cut install time; the lock file guarantees correctness regardless of cache state.
- Build dependencies in a dedicated Docker layer keyed on `composer.json` +
  `composer.lock` so image rebuilds skip reinstalling unchanged deps.
- Set `COMPOSER_ALLOW_SUPERUSER=1` only inside containers, and avoid running plugins
  from untrusted packages (`--no-plugins` / `allow-plugins` allowlist).

## AI Review Checklist

- Are `composer.json` and `composer.lock` both committed and mutually consistent?
- Do constraints use bounded ranges (`^`) rather than `*` or open `>=`?
- Does CI/deploy run `composer install --no-dev`, never `composer update`?
- Are test/lint/analysis tools in `require-dev`, not `require`?
- Is `vendor/` excluded from version control?
- Does the pipeline run `composer audit` and fail on advisories?
- Are the PHP version and required extensions declared in `require`?

## Related

- `knowledge/php/06-autoloading.md`
- `knowledge/php/24-psr-standards.md`
- `knowledge/php/28-tooling.md`
- `knowledge/php/27-production.md`
