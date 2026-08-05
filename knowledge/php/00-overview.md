---
id: php/00-overview
topic: php
slug: overview
title: "PHP Overview"
type: doc
order: 0
status: ready
tags: [php, overview]
related: [php/01-language-fundamentals, php/02-types, php/04-oop, php/23-modern-php, php/24-psr-standards]
when_to_use: "Read first when starting or reviewing any PHP work to orient yourself among the topic's docs."
---
# PHP Overview

## Purpose

This document is the map for the `php` topic. It orients an agent to how modern PHP
works and points to the specific doc for each concern. PHP in 2026 means **PHP 8.3+**
(8.4 is current, 8.1 is the practical floor): a strictly-typed, object-oriented language
with a mature ecosystem (Composer, PSR standards, PHPStan, Pest/PHPUnit). Treat pre-8.0
patterns — untyped code, manual `require`, `mysql_*` — as legacy to be replaced, not
copied.

## Why It Matters

PHP still runs a large fraction of the web, and most of its bad reputation comes from
code written for PHP 5. Modern PHP is a different language: union and intersection types,
enums, readonly properties, first-class callables, and fibers. An agent that writes
PHP as if it were 2012 produces insecure, untyped, hard-to-test code. Knowing which
version-appropriate feature to reach for — and which sibling doc governs it — is the
difference between idiomatic PHP and a liability.

## Core Principles

- **Target a supported version.** Only PHP 8.3 and 8.4 receive active support in 2026.
  Never write for or recommend an end-of-life version (8.2 and below are security-fix
  only or dead); check <https://www.php.net/supported-versions.php> before relying on a
  feature.
- **Types are not optional.** Declare `declare(strict_types=1);`, type every parameter,
  return, and property. See [types](02-types.md).
- **Composer and PSR-4 own the wiring.** No manual `include` chains, no global state.
  See [autoloading](06-autoloading.md) and [composer](07-composer.md).
- **Follow the PSRs.** They are the community's shared conventions; deviating from them
  costs interoperability. See [psr-standards](24-psr-standards.md).

## How the Docs Fit Together

- **Language core** — start here: [language-fundamentals](01-language-fundamentals.md),
  [types](02-types.md), [functions](03-functions.md), [oop](04-oop.md),
  [namespaces](05-namespaces.md).
- **Modern features** — [attributes](17-attributes.md), [generators](18-generators.md),
  [enums](19-enums.md), [modern-php](23-modern-php.md).
- **Structure & tooling** — [autoloading](06-autoloading.md), [composer](07-composer.md),
  [psr-standards](24-psr-standards.md), [tooling](28-tooling.md).
- **Errors** — [error-handling](08-error-handling.md), [exceptions](09-exceptions.md).
- **I/O & platform** — [files](10-files.md), [http](11-http.md), [database](12-database.md),
  [cli](16-cli.md).
- **Quality & delivery** — [security](13-security.md), [performance](14-performance.md),
  [testing](15-testing.md), [debugging](25-debugging.md), [production](27-production.md).
- **Design** — [dependency-injection](20-dependency-injection.md),
  [design-patterns](21-design-patterns.md), [clean-code](22-clean-code.md),
  [architecture](29-architecture.md), [engineering-principles](30-engineering-principles.md).
- **Consolidated rules** — [best-practices](26-best-practices.md),
  [production-checklist](98-production-checklist.md),
  [ai-review-checklist](99-ai-review-checklist.md),
  [common-antipatterns](100-common-antipatterns.md).

## Best Practices

- Begin every new PHP file with `<?php` and `declare(strict_types=1);`, never a closing
  `?>` in a pure-PHP file (a trailing newline after `?>` emits output and breaks headers).
- Manage every dependency through Composer; never vendor a library by hand.
- Run PHPStan/Psalm at a high level and a formatter (PHP-CS-Fixer or Pint) in CI so style
  and type errors never reach review.
- Prefer the newest stable syntax the target version supports because it is more explicit
  and static-analysis-friendly; the cost is a higher minimum-version requirement.

## Common Mistakes

- Copying PHP 5/7 idioms (untyped params, `array()` long syntax, manual autoloaders) into
  new code.
- Assuming a feature exists without checking the version — e.g. `readonly` classes need
  8.2, property hooks need 8.4.
- Mixing HTML and logic in one file instead of separating concerns.
- Skipping `strict_types`, so `"5"` silently becomes `5` and hides bugs.

## AI Review Checklist

- Is the code written for a supported PHP version (8.3/8.4), using no dead APIs?
- Does every file declare `strict_types=1` and use full type declarations?
- Are dependencies and autoloading handled by Composer/PSR-4, not manual includes?
- Does the change route to the right sibling doc's rules for its concern?

## Related

- `knowledge/php/01-language-fundamentals.md`
- `knowledge/php/02-types.md`
- `knowledge/php/04-oop.md`
- `knowledge/php/23-modern-php.md`
- `knowledge/php/24-psr-standards.md`
