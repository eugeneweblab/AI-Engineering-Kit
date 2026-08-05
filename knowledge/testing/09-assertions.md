---
id: testing/09-assertions
topic: testing
slug: assertions
title: "Assertions"
type: doc
order: 9
status: ready
tags: [testing, assertions, price, toBeTruthy, toBe, toEqual, toBeInstanceOf, toThrow]
related: [testing/08-test-organization, testing/01-testing-fundamentals, testing/22-flaky-tests, testing/06-mocking, testing/29-test-review]
when_to_use: "Read before writing the checks that decide whether a test passes or fails."
---
# Assertions

## Purpose

This document defines how to write the checks that make a test pass or fail — the part that
turns "the code ran" into "the code is correct." It covers what to assert, how specific to
be, and how to write assertions that produce a diagnosis, not just a red mark.

An assertion is the entire point of a test; everything before it is setup. A test with weak
or missing assertions runs green while the code is broken. The skill is asserting *enough*
to catch real defects and *no more*, on the observable behavior a caller cares about.

## Why It Matters

The assertion decides two things: whether the test can catch a bug, and how fast you can
diagnose it when it fails. Over-assert — pinning every field of a large object — and the
test breaks on every unrelated change, so people stop trusting it. Under-assert — only
checking that a call didn't throw — and the test passes while returning garbage. And a
vague assertion (`toBeTruthy` on a number) yields a failure message that says nothing,
turning a five-second fix into a debugging session. Precise, behavior-focused assertions
are what make a suite both trustworthy and fast to act on.

## Core Principles

- **Assert the outcome, not the mechanism.** Check the returned value, the persisted row,
  the response a caller sees — not which internal method ran to produce it.
- **One behavior, one concept.** Multiple `expect` lines are fine if they describe a single
  behavior; unrelated concepts belong in separate tests (see [organization](08-test-organization.md)).
- **Be as specific as the behavior, no more.** Assert the exact value when it is defined;
  assert a property (length, membership) when the exact value is legitimately variable.
- **Prefer equality over truthiness.** `toBe(3)` catches a wrong number; `toBeTruthy()`
  passes for `1`, `"x"`, and `[]`. Vague matchers hide bugs and produce useless failures.
- **A good failure names the defect.** Use matchers that print expected vs. actual, and
  add a message only when the values alone won't explain the failure.

## Best Practices

- Use the tightest matcher that fits: `toEqual` for value equality, `toBe` for identity,
  `toMatchObject` for a partial-but-exact subset, `toThrow(SpecificError)` for failures.
- When asserting on an object, assert the fields the behavior defines and let volatile
  fields (timestamps, generated IDs) be matched loosely or injected — not pinned to a value.
- Assert error *behavior* explicitly: that the right error type is thrown, with the right
  message or code — not merely that "something threw."
- Avoid asserting on unstable ordering unless order is the behavior; sort first or assert
  set membership to prevent [flaky](22-flaky-tests.md) failures.
- For floating point, assert within a tolerance (`toBeCloseTo`), never exact equality.
- Keep custom messages factual and short; the matcher's diff usually says more than prose.

## Examples

**Good Example** — specific, behavior-focused, diagnosable

```ts
test("applies a 10% discount to the subtotal", () => {
  const result = price({ subtotalCents: 1000, discountPct: 10 });

  // Exact value: the arithmetic is fully defined, so pin it — this catches an off-by-one.
  expect(result.totalCents).toBe(900);
  // Volatile field matched loosely, not to a fixed value that would break every run.
  expect(result.pricedAt).toBeInstanceOf(Date);
});

test("rejects a negative discount", () => {
  // Assert the error TYPE, not just that something threw.
  expect(() => price({ subtotalCents: 1000, discountPct: -5 }))
    .toThrow(InvalidDiscountError);
});
```

**Bad Example** — vague, over-broad, uninformative

```ts
test("price works", () => {
  const result = price({ subtotalCents: 1000, discountPct: 10 });

  expect(result).toBeTruthy();          // passes for ANY non-null object — proves nothing
  expect(result.totalCents > 0).toBe(true); // 901 would pass; the bug slips through
  // Pinning the whole object including a timestamp — breaks on every run, unrelated to logic.
  expect(result).toEqual({ totalCents: 900, pricedAt: new Date("2020-01-01") });
});
```

## Common Mistakes

- `toBeTruthy` / `toBeFalsy` where an exact value is known, hiding wrong-but-truthy results.
- No assertion at all — a test that only checks the code "didn't throw."
- Pinning entire large objects, so volatile fields make the test break on every run.
- Asserting `threw` without checking the error type or message.
- Depending on collection order that the code does not guarantee.
- Exact equality on floating-point numbers instead of a tolerance.
- Custom messages that restate the matcher instead of adding missing context.

## Production Tips

- Treat an assertion-free test as a failing review: it cannot catch a regression.
- When a failure message is confusing, improve the assertion (tighter matcher, better
  message) rather than adding a comment — the next failure should self-explain.
- Use snapshot assertions sparingly and review every snapshot diff; an unreviewed,
  auto-updated snapshot asserts nothing.

## AI Review Checklist

- Does every test contain at least one assertion on an observable outcome?
- Is each assertion as specific as the behavior allows (exact value where defined)?
- Are volatile fields (time, IDs) matched loosely or injected, not pinned?
- Do error cases assert the specific error type or code, not just that it threw?
- Are floating-point and unordered-collection comparisons done safely?
- Would the failure message alone let a reader diagnose the defect?

## Related

- `knowledge/testing/08-test-organization.md`
- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/06-mocking.md`
- `knowledge/testing/29-test-review.md`
