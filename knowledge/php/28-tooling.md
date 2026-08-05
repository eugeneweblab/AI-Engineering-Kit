---
id: php/28-tooling
topic: php
slug: tooling
title: "PHP Tooling"
type: doc
order: 28
status: ready
tags: [php, tooling, require-dev, composer.lock]
related: [php/07-composer, php/15-testing, php/24-psr-standards, php/25-debugging, php/26-best-practices]
when_to_use: "Read before setting up a PHP project's quality gate, CI, or local dev toolchain."
---
# PHP Tooling

## Purpose

This document defines the standard PHP toolchain an agent should assume and configure:
dependency management, static analysis, code style, testing, and how they run together in
CI. The point is a single command that catches type errors, style drift, and broken tests
before code merges — so review is about design, not mechanics.

Tooling is the automated part of your quality bar. If a rule can be checked by a machine,
a machine should check it on every commit, not a human on every review.

## Why It Matters

PHP has no compiler to catch type mismatches, dead code paths, or undefined variables before
runtime. Static analyzers (PHPStan, Psalm) fill that gap, catching bugs that would otherwise
surface as production fatals. A formatter ends style debates permanently. A pinned toolchain
means every developer and the CI runner get identical results, so "works on my machine" stops
being an argument. The cost is a few config files; the return is defects caught in seconds
instead of incidents caught in production.

## Core Principles

- **Pin every tool with Composer.** Put PHPStan, PHP-CS-Fixer, PHPUnit, etc. in
  `require-dev` with version constraints so CI and every laptop run the exact same versions.
- **Static analysis is non-optional.** Run PHPStan (or Psalm) at a defined level and only
  ratchet it upward. It finds null-safety and type bugs no test happened to cover.
- **Style is enforced, never argued.** A formatter reformats to the PSR-12/PER ruleset
  automatically; reviewers should never comment on brace placement.
- **One command, same everywhere.** `composer check` (or a Makefile target) runs lint,
  analysis, and tests identically locally and in CI. No hidden steps.
- **Fail the build on any gate.** A red analyzer or a failing test blocks merge — a warning
  that does not block is a warning everyone ignores.

## Best Practices

- Manage dependencies with Composer; commit `composer.lock` so installs are reproducible,
  and use `require-dev` for all tooling so it is excluded from prod builds.
- Adopt **PHPStan** at a starting level (e.g. level 5) and raise it one level per cleanup
  PR toward level 9/max; a baseline file quarantines legacy findings without blocking new code.
- Format with **PHP-CS-Fixer** or **PHP_CodeSniffer** pinned to a PSR-12/PER ruleset; run
  `--dry-run`/`--diff` in CI to fail on unformatted code and `--fix` locally.
- Write tests with **PHPUnit** (or Pest); wire them into CI with coverage reporting, and
  gate merges on green. See the testing doc for depth.
- Add **Rector** for automated, safe refactors and PHP version upgrades — it applies typed
  transformations across the codebase that would be error-prone by hand.
- Run the whole gate on pre-commit (via a hook) and again in CI, so nothing merges unchecked.
- Keep tool config in the repo root (`phpstan.neon`, `.php-cs-fixer.php`, `phpunit.xml`) so
  the setup is discoverable and versioned.

## Examples

**Good Example** — pinned dev tools and one aggregate command

```jsonc
// composer.json — tools pinned in require-dev, one script runs the whole gate
{
  "require-dev": {
    "phpstan/phpstan": "^2.0",
    "friendsofphp/php-cs-fixer": "^3.0",
    "phpunit/phpunit": "^11.0",
    "rector/rector": "^2.0"
  },
  "scripts": {
    // CI and every developer run the identical gate; any failure exits non-zero.
    "check": [
      "php-cs-fixer fix --dry-run --diff", // style: fail if not formatted
      "phpstan analyse --level=8",          // types/null-safety: fail on new issues
      "phpunit"                              // behavior: fail on red tests
    ]
  }
}
```

**Bad Example** — unpinned, manual, unenforced

```bash
# Tools installed globally at whatever version each machine happens to have —
# CI passes, a teammate's laptop fails, nobody can reproduce.
composer global require phpstan/phpstan   # not pinned, not in the repo
phpstan analyse                            # no level set → analyzes at the loosest default
# Style "checked" by asking in review; tests run "when someone remembers".
# Nothing blocks merge, so broken code lands and is discovered in production.
```

## Common Mistakes

- Installing tools globally instead of pinning them in `require-dev`, so versions drift.
- Not committing `composer.lock`, making builds non-reproducible.
- Running PHPStan at no explicit level (the loosest), missing most type bugs.
- Treating analyzer/style output as advisory warnings that do not fail the build.
- Formatting by hand or in review instead of with an automated fixer.
- No baseline strategy on a legacy repo, so the analyzer is switched off entirely.

## Production Tips

- Cache Composer and analyzer result caches in CI to keep the gate under a minute; a slow
  gate is one people bypass.
- Use a PHPStan baseline to adopt strict analysis on a legacy codebase incrementally —
  new code is held to the high bar while old findings are tracked, not ignored.

## AI Review Checklist

- Are all tools pinned in `require-dev` with `composer.lock` committed?
- Does static analysis run at an explicit, non-trivial level and fail the build on issues?
- Is code style enforced by a formatter in CI, not by reviewers?
- Do tests run in CI and gate merges?
- Is there a single command that runs lint, analysis, and tests identically everywhere?
- Is tool configuration committed at the repo root and version-controlled?

## Related

- `knowledge/php/07-composer.md`
- `knowledge/php/15-testing.md`
- `knowledge/php/24-psr-standards.md`
- `knowledge/php/25-debugging.md`
- `knowledge/php/26-best-practices.md`
