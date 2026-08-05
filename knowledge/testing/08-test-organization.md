---
id: testing/08-test-organization
topic: testing
slug: test-organization
title: "Test Organization"
type: doc
order: 8
status: ready
tags: [testing, test-organization, canRefund, toBe, describe, works, beforeEach]
related: [testing/01-testing-fundamentals, testing/09-assertions, testing/07-test-data, testing/10-fixtures, testing/20-test-maintenance]
when_to_use: "Read before naming a test, choosing where the test file lives, or structuring a growing test suite."
---
# Test Organization

## Purpose

This document defines how to structure tests so a suite stays navigable as it grows: where
test files live, how test cases are named, how they are grouped, and how each case is laid
out internally. It applies at every level of the pyramid — the same conventions make unit,
integration, and E2E suites readable.

Organization is not cosmetic. When a test fails at 2 a.m., its name and location are the
first diagnosis. A well-organized suite tells you *what broke and where* before you read a
single line of code.

## Why It Matters

A test suite is read far more often than it is written — on every failure, every review,
every refactor. Disorganized tests impose a tax on all of that: vague names (`test1`,
`works`) force a reader to reverse-engineer intent from the body; giant test files hide the
one relevant case; setup scattered across a file makes each test a puzzle. The suite still
runs, so the cost is invisible until the team stops trusting failures and starts skipping
them. Consistent structure is what keeps a thousand-test suite as legible as a ten-test one.

## Core Principles

- **One behavior per test.** A test that asserts three unrelated things gives one failure
  for three possible causes. Split them so a failure names its cause.
- **The name is a specification.** A good name states condition and expected outcome, so a
  failing test is self-diagnosing without opening the body.
- **Arrange–Act–Assert, visibly.** Structure every test in three phases so a reader sees
  setup, the single action, and the checks at a glance.
- **Group by behavior, not by method.** Organize around what the code *does* in a scenario,
  not one `describe` block per public method — behavior is what readers reason about.
- **Colocate or mirror, but be consistent.** Tests either sit next to the code or mirror
  its directory tree. Pick one convention per repo and never mix.

## Best Practices

- Name tests as a sentence: `it("rejects a refund when the order is unpaid")`, or the
  `should_x_when_y` / `methodName_condition_expected` form. Avoid `test1`, `happy path`.
- Keep the Act phase to a single call. If you need two actions to trigger the behavior, the
  test is describing a flow that probably belongs one level up the pyramid.
- Put shared setup in a `beforeEach` only when it is truly common to every test in the
  block; per-test specifics stay in the test via a [factory](07-test-data.md).
- Group edge cases under a nested `describe` for the behavior they vary, so related cases
  read together and a gap in coverage is visible.
- Match file naming to the runner's convention (`*.test.ts`, `*_test.py`, `*Test.java`) so
  discovery is automatic and no test is silently skipped.
- Keep one assertion *concept* per test; multiple `expect` lines are fine if they verify
  one behavior (see [assertions](09-assertions.md)).

## Examples

**Good Example** — one behavior, AAA phases, self-describing names

```ts
describe("refund eligibility", () => {
  it("allows a refund when the order is paid and within the window", () => {
    const order = anOrder({ status: "paid", ageDays: 5 }); // Arrange
    const result = canRefund(order);                        // Act (single call)
    expect(result).toBe(true);                              // Assert (one concept)
  });

  it("rejects a refund when the order is unpaid", () => {
    const order = anOrder({ status: "pending" });
    expect(canRefund(order)).toBe(false); // name already told us the expected outcome
  });
});
```

**Bad Example** — vague name, many behaviors, no structure

```ts
test("refund", () => {
  // Three unrelated behaviors in one test: a failure names none of them.
  expect(canRefund(anOrder({ status: "paid", ageDays: 5 }))).toBe(true);
  expect(canRefund(anOrder({ status: "pending" }))).toBe(false);
  expect(canRefund(anOrder({ status: "paid", ageDays: 400 }))).toBe(false);
  // No Arrange/Act/Assert separation; if line 2 fails, lines 3-4 never run.
});
```

## Common Mistakes

- Names like `test1`, `works`, or `happy path` that force the reader into the body.
- Asserting several unrelated behaviors in one test, so a failure is ambiguous.
- Mixing colocated and mirrored test layouts in the same repo, so tests are hard to find.
- Overloading `beforeEach` with setup only some tests use, hiding what each test depends on.
- One `describe` per method rather than per behavior, scattering related scenarios.
- File names that don't match the runner's glob, so tests are silently never executed.

## Production Tips

- Enforce the file-naming convention in CI and fail the build if a source file has no
  corresponding test where policy requires one.
- Keep test file size bounded; when a file passes a few hundred lines, split by behavior —
  large files hide gaps and slow reviews.
- Tag slow or integration tests so developers can run the fast tier locally and the full
  tier in CI (see [CI/CD](21-cicd.md)).

## AI Review Checklist

- Does each test verify exactly one behavior, with a single Act step?
- Does the test name state the condition and the expected outcome?
- Are Arrange, Act, and Assert visually distinct in each test?
- Are tests grouped by behavior rather than one block per method?
- Is the file-location convention (colocated or mirrored) consistent across the repo?
- Does the file name match the runner's discovery pattern so it actually runs?

## Related

- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/09-assertions.md`
- `knowledge/testing/07-test-data.md`
- `knowledge/testing/10-fixtures.md`
- `knowledge/testing/20-test-maintenance.md`
