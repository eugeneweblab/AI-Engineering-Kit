---
id: tools/08-static-analysis
topic: tools
slug: static-analysis
title: "Static Analysis"
type: doc
order: 8
status: ready
tags: [tools, static-analysis, get_post, WP_Post, WordPress]
related: [tools/07-php-code-standards, tools/03-typescript-compiler, tools/04-eslint, tools/27-dependency-management, tools/30-engineering-principles, php/28-tooling]
when_to_use: "Read before adding static analysis to a project — configuring PHPStan or Psalm, choosing a rule level, or introducing analysis to a legacy codebase with a baseline."
---
# Static Analysis

## Purpose

This document defines how to use static analysis to find defects without running code:
PHPStan and Psalm for PHP, and how analysis differs from linting and type checking. It covers
choosing a level, adopting analysis in an existing codebase, and keeping the signal useful.

## Why It Matters

A linter checks whether code follows conventions. A static analyzer checks whether it can
work: whether a method exists on that object, whether a nullable value is dereferenced,
whether a branch is unreachable, whether an argument type matches. In PHP — dynamically typed
and historically untyped — that is the difference between finding a defect now and finding it
in production.

The reason projects skip it is the first run: thousands of errors on an existing codebase.
The baseline mechanism exists precisely for that, and makes adoption a one-day task rather
than a rewrite.

## Core Principles

- **Analysis is not linting.** Run both; they detect disjoint problems.
- **Start at a level you can pass, then raise it.** A permanently red analyzer teaches the
  team to ignore it.
- **Baseline the legacy, gate the new.** Existing violations go into a baseline file; new code
  must be clean.
- **Types are the analyzer's input.** Adding parameter, return, and property types makes every
  subsequent run more useful — untyped code is invisible to analysis.

## Best Practices

```neon
# phpstan.neon.dist
parameters:
    level: 8                    # 0 (loose) … 9 (max); 8 adds strict null checks
    paths:
        - src
        - acme-events.php
    excludePaths:
        - vendor
        - tests/fixtures

    # Analysis is only as good as the stubs for your framework.
    bootstrapFiles:
        - tests/phpstan-bootstrap.php

    treatPhpDocTypesAsCertain: false   # docblocks lie in legacy code
    reportUnmatchedIgnoredErrors: true # a stale ignore is itself a finding

includes:
    - vendor/phpstan/phpstan-strict-rules/rules.neon
    - vendor/szepeviktor/phpstan-wordpress/extension.neon   # WordPress function signatures
```

```json
{
  "require-dev": {
    "phpstan/phpstan": "^1.12",
    "phpstan/phpstan-strict-rules": "^1.6",
    "szepeviktor/phpstan-wordpress": "^1.3"
  },
  "scripts": { "analyse": "phpstan analyse --memory-limit=1G" }
}
```

For WordPress, the `phpstan-wordpress` extension is not optional. Without it, every core
function is unknown and the analyzer produces noise instead of findings.

## Adopting It on a Legacy Codebase

```bash
# 1. Find the highest level that reports a manageable number of errors.
vendor/bin/phpstan analyse --level=5

# 2. Freeze what exists today.
vendor/bin/phpstan analyse --generate-baseline

# 3. Commit phpstan-baseline.neon and include it.
```

```neon
includes:
    - phpstan-baseline.neon
```

From that point the analyzer is green, new code is checked at full strength, and the baseline
shrinks as files are touched. Review the baseline occasionally: it is an inventory of known
technical debt, and an entry that keeps growing indicates a file worth refactoring.

## Examples

**Good Example** — defects an analyzer finds that a linter cannot

```php
function acme_get_event_title( int $id ): string {
	$post = get_post( $id );

	// PHPStan level 8: get_post() returns WP_Post|null — dereferencing null here.
	return $post->post_title;
}
```

```php
// Corrected: the null case is handled, and the analyzer is satisfied.
function acme_get_event_title( int $id ): string {
	$post = get_post( $id );

	if ( ! $post instanceof WP_Post ) {
		return '';
	}

	return $post->post_title;
}
```

Other findings typical of level 8: calling a method that does not exist on the resolved type,
comparing values whose types can never be equal, passing `string|false` where `string` is
required (the classic `strpos()` result), and dead branches after a type narrowing.

**Bad Example** — suppression that removes the value

```php
/** @phpstan-ignore-next-line */
return $post->post_title;
```

```neon
parameters:
    ignoreErrors:
        - '#.*#'      # ignores everything; the tool now reports nothing, forever
```

## Common Mistakes

- Starting at level 9 on a legacy codebase, drowning in errors, and removing the tool.
- No framework extension, so core functions are unknown and findings are noise.
- Broad `ignoreErrors` patterns instead of a baseline.
- A baseline that is regenerated on every failure — that converts the gate into a formality.
- Treating docblocks as truth (`treatPhpDocTypesAsCertain: true`) in a codebase where they
  are stale.
- Running analysis only locally, so failures land on main.
- Assuming analysis replaces tests: it proves the code is consistent, not that it is correct.
- Leaving `reportUnmatchedIgnoredErrors` off, so obsolete suppressions accumulate silently.

## Production Tips

- Run analysis as its own CI job, in parallel with lint and tests, with
  `--error-format=github` for inline annotations on pull requests.
- Cache the result directory between CI runs; PHPStan is slow on cold cache and fast on warm.
- Raise the level one step at a time in dedicated commits, so the diff shows what each level
  bought.
- Regenerate the baseline only in an explicit "reduce baseline" commit, never as a fix for a
  failing build.
- For TypeScript, the equivalent gate is `tsc --noEmit` plus type-aware ESLint rules — see
  [TypeScript Compiler](03-typescript-compiler.md) and [ESLint](04-eslint.md).

## AI Review Checklist

- Is a static analyzer configured and running in CI as a required check?
- Is the level as high as the codebase can currently sustain, with a plan to raise it?
- Are framework extensions installed so core APIs are understood?
- Is legacy debt handled by a baseline rather than broad ignore patterns?
- Are individual suppressions narrow and justified?
- Is `reportUnmatchedIgnoredErrors` enabled?
- Is the baseline shrinking over time rather than being regenerated?

## Related

- `knowledge/tools/07-php-code-standards.md`
- `knowledge/tools/03-typescript-compiler.md`
- `knowledge/tools/04-eslint.md`
- `knowledge/tools/27-dependency-management.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/php/28-tooling.md`
