---
id: testing/07-test-data
topic: testing
slug: test-data
title: "Test Data"
type: doc
order: 7
status: ready
tags: [testing, test-data, canRefund, toBe, faker, Date]
related: [testing/10-fixtures, testing/05-test-doubles, testing/03-integration-testing, testing/22-flaky-tests, testing/08-test-organization]
when_to_use: "Read before writing the setup that builds the objects, rows, or payloads a test operates on."
---
# Test Data

## Purpose

This document defines how to create the data a test operates on — the objects, database
rows, and payloads set up in the Arrange phase. It covers factories, builders, and the
discipline that keeps setup readable and tests independent. It is distinct from
[fixtures](10-fixtures.md), which manage the *lifecycle* of shared setup/teardown; here we
focus on *constructing the values themselves*.

Good test data makes the intent of a test obvious at a glance: a reader should see exactly
which field matters to this case and ignore the rest. Bad test data buries the one
relevant value under a wall of irrelevant boilerplate.

## Why It Matters

Most of a test's length is data setup, and most of a suite's fragility lives there too.
When every test hand-builds a full object, one added required field forces edits across
hundreds of tests. When tests share a mutable dataset, one test's write silently changes
another's inputs, producing order-dependent [flaky tests](22-flaky-tests.md) that pass
alone and fail in the suite. And when setup is noisy, the reader cannot tell which value
drives the assertion, so the test documents nothing. Test data is not an afterthought — it
is the single largest lever on whether a suite stays readable and independent as it grows.

## Core Principles

- **Each test owns its data.** No shared mutable state between tests. Fresh data per test
  (or a transactional rollback) is what makes tests independent and order-free.
- **Make the relevant value loud and the rest quiet.** Set only the fields the test cares
  about; let a factory supply sensible defaults for everything else.
- **Build data through one factory per type.** A single construction point means a new
  required field is a one-line change, not a suite-wide edit.
- **Prefer explicit over realistic.** Use values that make relationships obvious
  (`amount: 100`, `discount: 10`) over lifelike noise that hides the arithmetic.
- **Deterministic by default.** Random data must be seeded and reproducible; unseeded
  randomness turns a rare edge case into an intermittent failure no one can reproduce.

## Best Practices

- Use the **builder / factory pattern**: `aUser().withRole("admin").build()`. Overrides
  express exactly what this test needs; defaults handle the rest.
- Keep IDs and timestamps deterministic or injected. Never let `new Date()` or a random
  UUID leak into an assertion — freeze the clock and pass IDs in.
- For property-based tests, seed the generator and log the seed on failure so any failing
  case is reproducible.
- Store large realistic payloads (a webhook body, an API response) as named files close to
  the tests that use them; keep the inline data minimal.
- Isolate database data per test with a transaction rolled back in teardown, or a truncate
  between tests. Never rely on data left by a previous run.
- Name factory helpers by domain meaning (`anExpiredSubscription()`), so the test reads as
  a specification, not as object plumbing.

## Examples

**Good Example** — a builder surfaces only what matters

```ts
// One factory, sensible defaults; the test overrides ONLY the field under test.
const anOrder = (over: Partial<Order> = {}): Order => ({
  id: "ord_1", userId: "u1", status: "pending", totalCents: 1000, ...over,
});

test("paid orders can be refunded", () => {
  const order = anOrder({ status: "paid" }); // the ONE relevant fact stands out
  expect(canRefund(order)).toBe(true);
});

test("pending orders cannot be refunded", () => {
  const order = anOrder({ status: "pending" }); // same shape, one field differs
  expect(canRefund(order)).toBe(false);
});
```

**Bad Example** — hand-built, shared, and noisy

```ts
// Shared mutable object: one test mutating it corrupts the others (order-dependent flake).
const order = { id: "ord_1", userId: "u1", status: "paid", totalCents: 1000,
  createdAt: new Date(), currency: "USD", items: [/* 20 lines */] };

test("paid orders can be refunded", () => {
  order.status = "paid";                 // mutates SHARED state
  expect(canRefund(order)).toBe(true);   // which field made this pass? unclear
});

test("pending orders cannot be refunded", () => {
  order.status = "pending";              // depends on the previous test not having run
  expect(canRefund(order)).toBe(false);
});
```

## Common Mistakes

- Sharing one mutable dataset across tests, creating order dependence and flakiness.
- Copy-pasting full object literals, so a new required field breaks the whole suite.
- Using unseeded random or `faker` without a fixed seed, making failures unreproducible.
- Letting `new Date()` or a fresh UUID reach an assertion instead of injecting a fixed one.
- Realistic-but-opaque values that hide the arithmetic the test is supposed to prove.
- Depending on production-like seed data whose contents can change under the test.

## Production Tips

- Keep test factories beside production types and update them in the same change, so they
  never drift from the real schema.
- Anonymize any data copied from production; never let real PII into fixtures or repos.
- For integration suites, prefer per-test transactional rollback over shared seed data — it
  is faster to reason about and immune to leftover state.

## AI Review Checklist

- Does each test build its own data, with no shared mutable state between tests?
- Does the setup surface only the fields relevant to the assertion, defaulting the rest?
- Is all data constructed through a single factory/builder per type?
- Are IDs, timestamps, and randomness deterministic (frozen clock, seeded generator)?
- Would adding a required field to the type be a one-line change to the factory?
- Is any random-generated case reproducible via a logged seed?

## Related

- `knowledge/testing/10-fixtures.md`
- `knowledge/testing/05-test-doubles.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/08-test-organization.md`
