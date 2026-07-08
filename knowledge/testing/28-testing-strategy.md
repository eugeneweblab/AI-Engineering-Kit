---
id: testing/28-testing-strategy
topic: testing
slug: testing-strategy
title: "Testing Strategy"
type: doc
order: 28
status: ready
tags: [testing, testing-strategy]
related: [testing/01-testing-fundamentals, testing/02-unit-testing, testing/03-integration-testing, testing/04-e2e-testing, testing/19-test-coverage]
when_to_use: "Read before deciding how to allocate testing effort across a feature, service, or codebase."
---
# Testing Strategy

## Purpose

This document is about *allocation*: given finite time, what kinds of tests to write, at
what level, and in what proportion, to maximize confidence per minute spent. Individual
docs teach how to write a [unit](02-unit-testing.md), [integration](03-integration-testing.md),
or [e2e](04-e2e-testing.md) test; strategy decides how many of each and where to aim them.

A strategy is a bet about where defects will appear and what they will cost. Good strategy
concentrates effort on high-risk, high-change code and refuses to spend equally on
everything.

## Why It Matters

Testing effort is not free and its return is wildly uneven. A thousand tests on trivial
getters give false comfort while a single untested payment path ships a bug that costs
real money. Without a strategy, teams default to whatever is easy to test rather than what
is risky, and the suite grows expensive and slow without growing trustworthy. A deliberate
strategy makes the trade-offs explicit: which layer catches which failure, why a check is
placed where it is, and what is deliberately *not* tested.

## Core Principles

- **Push tests down.** Prefer the lowest level that can catch a given defect. Unit tests
  are fast, precise, and stable; e2e tests are slow, broad, and flaky. Use the cheapest
  test that gives real confidence.
- **Shape the suite like a pyramid (or trophy).** Many fast unit/integration tests, fewer
  e2e tests. An inverted suite — mostly e2e — is slow and brittle and stalls the team.
- **Test by risk, not by uniform ratio.** Coverage targets follow blast radius: payment,
  auth, and data-integrity code earns exhaustive tests; a display formatter does not.
- **Test seams, not internals.** Aim tests at stable contracts (public APIs, module
  boundaries) so they survive refactors and catch integration bugs.
- **Know what you're buying at each level.** Each layer answers a different question; don't
  duplicate the same assertion at three levels or leave a layer's question unanswered.

## Best Practices

- Default new logic to **unit tests** at the pure-function level; reserve integration
  tests for wiring (DB, queue, HTTP) and e2e for a handful of critical user journeys.
- Write **integration tests over mocks** for anything that touches a real boundary —
  serialization, SQL, transactions — because that is exactly where unit mocks lie.
- Pick **critical paths for e2e** deliberately (login, checkout, signup) and keep the set
  small; each e2e test is a maintenance liability, so it must protect real revenue or
  safety.
- Use **contract tests** at service boundaries so services can be tested independently yet
  stay compatible (see [contract testing](11-contract-testing.md)).
- Match **coverage targets to risk tiers**, e.g. critical modules ~90%+, standard ~70–80%,
  throwaway/generated code untested — and say so in the repo.
- Decide **explicitly what not to test**: third-party libraries, trivial pass-throughs,
  and framework glue. Document it so gaps are choices, not accidents.
- Reassess the shape when the suite gets slow or flaky — usually it has drifted top-heavy.

## Examples

**Good Example** — the right defect caught at the right level

```text
Feature: transfer funds
  unit:        balance math, overdraft rule, rounding      (dozens, milliseconds)
  integration: repository debits/credits in one DB tx      (a few, seconds)
  e2e:         user completes a transfer end-to-end         (one, the money path)
# Fast tests carry the load; the single e2e proves the whole path is wired.
```

**Bad Example** — inverted, uniform, aimed at internals

```text
Feature: transfer funds
  e2e:  40 browser tests covering every rounding edge case  (30 min, flaky)
  unit: asserts a private _validate() was called once       (breaks on refactor)
# Rounding bugs are found in a slow browser; the fast layer tests implementation, not math.
# The suite is slow, brittle, and still misses the transaction-integrity case.
```

## Common Mistakes

- An inverted pyramid: most confidence riding on slow, flaky e2e tests.
- Uniform coverage targets that over-test trivial code and under-test risky code.
- Duplicating the same assertion at unit, integration, and e2e levels — cost without gain.
- Mocking the database in a test whose entire point is the SQL/transaction behavior.
- No e2e at all, so no test proves the pieces are actually wired together.
- Never writing down what is intentionally untested, so real gaps hide among choices.
- Letting the suite drift top-heavy and slow without ever rebalancing.

## Production Tips

- Track the suite's shape (counts and runtime per level) and watch for drift toward slow
  layers; rebalance before developers start skipping it.
- When a production bug slips through, add the test at the *lowest* level that would have
  caught it, and ask why that level was empty.
- Tie risk tiers to real signals — change frequency, incident history, blast radius — not
  gut feel, and revisit them as the system evolves.

## AI Review Checklist

- Is each behavior tested at the lowest level that can catch its likely defects?
- Is the suite shaped like a pyramid/trophy, not inverted toward e2e?
- Do coverage expectations scale with each module's risk, not a flat number?
- Are boundary behaviors (DB, HTTP, serialization) covered by integration, not mocks?
- Is the e2e set small and aimed at genuinely critical journeys?
- Is what's deliberately *not* tested documented as an explicit choice?
- After an escaped bug, was a test added at the lowest level that would have caught it?

## Related

- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/19-test-coverage.md`
