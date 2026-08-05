---
id: testing/29-test-review
topic: testing
slug: test-review
title: "Test Review"
type: doc
order: 29
status: ready
tags: [testing, test-review, toBeTruthy, not.toThrow, checkout, toHaveBeenCalledWith, mockResolvedValue, toHaveBeenCalled]
related: [testing/24-best-practices, testing/09-assertions, testing/22-flaky-tests, testing/20-test-maintenance, testing/19-test-coverage]
when_to_use: "Read before reviewing a pull request's tests, or when your own tests are about to be reviewed."
---
# Test Review

## Purpose

This document defines how to review the *tests* in a change, not just the production code.
Tests are usually skimmed or skipped in review, yet a weak test is the most expensive kind
of code: it looks like protection while providing none. Reviewing tests means judging
whether they would actually fail when the behavior breaks — and pass when it doesn't.

Reviewing tests is a distinct skill from reviewing code. The question is not "is this
elegant?" but "does this test earn its place, and can I trust its verdict?" See
[best practices](24-best-practices.md) for the standard each test should meet.

## Why It Matters

A test that cannot fail is worse than no test: it adds runtime, review load, and false
confidence. These tests slip through because reviewers assume that if code is under test,
it is safe — but tautological assertions, over-mocking, and untested error paths all pass
review while proving nothing. The only reliable way to catch them is to review tests
adversarially: assume each one is broken until it demonstrates otherwise. The payoff is a
suite whose green genuinely means the behavior is protected.

## Core Principles

- **Assume the test can't fail until proven.** The core review move: could this test ever
  go red? Mentally break the code and check the test would catch it.
- **Read the assertion first.** If the assertion is vague (`toBeTruthy`, `not.toThrow`) or
  absent, the rest doesn't matter — it proves nothing (see [assertions](09-assertions.md)).
- **Weigh coverage of behavior, not of lines.** A diff can hit 100% line coverage while
  asserting nothing meaningful. Ask what *behavior* is pinned, not what executed.
- **Suspect the mocks.** Over-mocking turns a test into a test of the mocks. Check that
  what's mocked is a true boundary, not the logic under test.
- **Demand the negative cases.** Error paths, empty inputs, and boundaries are where bugs
  live and where tests are most often missing.

## Best Practices

- For each new test, **ask "what one-line bug would this catch?"** If you can't name one,
  the test is decorative — request a stronger assertion.
- Check the **assertion is specific**: exact values, exact errors, exact shape — not
  presence checks that pass on wrong data.
- Verify **error and edge paths** are tested, not just the happy path. A change with only
  happy-path tests is under-tested by default.
- Scrutinize **mocks**: is the mocked thing an external boundary (network, clock, payment
  gateway) or the very logic being verified? Mocking the latter is a red flag.
- Confirm tests are **deterministic** — no real time, randomness, ordering assumptions, or
  network — before approving (see [flaky tests](22-flaky-tests.md)).
- Reject tests that assert on **implementation details** (private methods, call counts)
  when an observable output was available; they'll break on refactor.
- Check the test **name matches what it asserts**; a mismatched name hides gaps and
  misleads the next reader.
- Watch for **copy-paste tests** where the body was duplicated but the assertion wasn't
  updated, so several tests re-check one case.

## Examples

**Good Example** — review comments that strengthen a test

```ts
test("charges the card", async () => {
  const gateway = mock(PaymentGateway);       // OK: external boundary, correct to mock
  await checkout(cart, gateway);
  expect(gateway.charge).toHaveBeenCalled();  // REVIEW: weak — only proves it was called
  // Ask for the value and the failure path:
  //   expect(gateway.charge).toHaveBeenCalledWith(cart.totalCents, "usd");
  //   and a test for a declined charge that asserts the order is NOT created.
});
```

**Bad Example** — a test that cannot fail, waved through review

```ts
test("processes order", async () => {
  const svc = mock(OrderService);             // the unit under test is mocked away
  svc.process.mockResolvedValue({ ok: true }); // the answer is hard-coded
  const res = await svc.process(order);
  expect(res).toBeTruthy();                    // asserts the mock returned its own stub
  // No real code ran. This passes even if process() is deleted. Reviewer approved anyway.
});
```

## Common Mistakes

- Approving tests without asking whether they could ever fail.
- Accepting `toBeTruthy`/`not.toThrow` where an exact value was checkable.
- Missing that the unit under test was mocked, so the test verifies the stub.
- Signing off on happy-path-only changes with no error or boundary coverage.
- Judging by coverage percentage instead of by what behavior is actually asserted.
- Letting tests assert on private internals, guaranteeing refactor breakage.
- Overlooking non-determinism (real clock, ordering) that will flake later.

## Production Tips

- Add a review-comment convention (e.g. `test-nit:` / `test-blocker:`) so test feedback is
  visible and triaged, not buried among code comments.
- When you can, verify a suspicious test by mutating the code locally and confirming it
  goes red — the fastest proof a test is real (mutation testing automates this at scale).
- Make "tests reviewed adversarially" an explicit line in the PR checklist so it isn't
  skipped under deadline.

## AI Review Checklist

- For each test, can you name a concrete one-line bug it would catch?
- Are assertions specific values/errors, not presence or truthiness checks?
- Is the actual unit under test executed, or is it mocked away?
- Are error paths, empty inputs, and boundaries tested, not just the happy path?
- Are the tests deterministic (no real time, randomness, ordering, or network)?
- Do tests assert observable behavior rather than private internals or call counts?
- Does each test's name match what it actually asserts?

## Related

- `knowledge/testing/24-best-practices.md`
- `knowledge/testing/09-assertions.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/20-test-maintenance.md`
- `knowledge/testing/19-test-coverage.md`
