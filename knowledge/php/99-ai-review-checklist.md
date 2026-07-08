---
id: php/99-ai-review-checklist
topic: php
slug: ai-review-checklist
title: "AI Review Checklist"
type: doc
order: 99
status: ready
tags: [php, ai-review-checklist]
related: [php/100-common-antipatterns, php/22-clean-code, php/13-security, php/15-testing, php/30-engineering-principles]
when_to_use: "Read when reviewing any PHP diff before approving or merging it."
---
# AI Review Checklist

## Purpose

A focused checklist an AI agent runs over a PHP diff before approving it. Each item is a
concrete yes/no tied to a defect class that is common, cheap to catch here, and expensive
to catch in production. Use it alongside [common antipatterns](100-common-antipatterns.md),
which explains *why* each smell is wrong.

## Why It Matters

PHP's permissiveness lets defects pass tests and review by looking harmless: a missing
`strict_types`, a `==` instead of `===`, an unparameterized query. These do not fail
loudly in the diff — they fail in production against real data and real attackers. A
disciplined review pass converts a subjective read into a repeatable gate.

## Types & Correctness

- [ ] Does every new/changed file declare `declare(strict_types=1)`?
- [ ] Are all parameters, returns, and properties typed as specifically as the domain
      allows (no bare `mixed`/`array` where a type or DTO fits)?
- [ ] Are comparisons `===`/`!==` unless loose equality is explicitly intended?
- [ ] Is `null` handled explicitly (nullsafe `?->`, null coalescing, or a guard) rather
      than assumed absent?
- [ ] Are enums/match used for closed sets instead of magic strings and `switch` fallthrough?

## Security

- [ ] Are all SQL queries parameterized, with no user input concatenated into the query?
- [ ] Is all dynamic output escaped for its context, or emitted through an auto-escaping
      template?
- [ ] Is untrusted input validated/allow-listed before use in file paths, shell, or
      `unserialize`?
- [ ] Are secrets read from config/env, never hard-coded or logged?
- [ ] Are state-changing endpoints CSRF-protected and authorization-checked, not just
      authenticated?

## Errors & Resources

- [ ] Do error conditions throw typed exceptions instead of returning `false`/`null`?
- [ ] Are exceptions caught specifically (not a bare `catch (\Throwable)` that swallows)?
- [ ] Is the `@` error-suppression operator absent from the diff?
- [ ] Are file handles, streams, and DB transactions closed/committed/rolled back on every
      path, including failures?

## Design & Testability

- [ ] Are dependencies injected via interfaces rather than `new`ed or fetched from statics
      /singletons inside logic?
- [ ] Are functions single-purpose and small, with early returns over deep nesting?
- [ ] Do value objects use `readonly` and validate in the constructor?
- [ ] Is there no dead code, commented-out block, or `var_dump`/`dd`/`error_log` debug
      residue?

## Tests & Tooling

- [ ] Do new behaviors have unit tests, including the failure and edge paths?
- [ ] Do `phpstan`/`psalm` pass at the configured level with no new baseline entries?
- [ ] Does the style fixer (`php-cs-fixer`/PSR-12) leave the diff unchanged?
- [ ] Is `composer.lock` updated when `composer.json` changed, and does `composer audit`
      stay clean?

## AI Review Checklist

- Have you confirmed `strict_types`, precise types, and strict comparisons in the diff?
- Have you verified every query is parameterized and every output escaped?
- Have you checked that errors throw, resources close, and dependencies are injected?
- Have you confirmed tests cover new behavior and static analysis stays green?

## Related

- `knowledge/php/100-common-antipatterns.md`
- `knowledge/php/22-clean-code.md`
- `knowledge/php/13-security.md`
- `knowledge/php/15-testing.md`
- `knowledge/php/30-engineering-principles.md`
