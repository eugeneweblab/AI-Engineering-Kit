---
id: testing/05-test-doubles
topic: testing
slug: test-doubles
title: "Test Doubles"
type: doc
order: 5
status: ready
tags: [testing, test-doubles, TokenService, mockReturnValue, toHaveBeenCalledTimes, toHaveBeenCalled, toBe]
related: [testing/02-unit-testing, testing/03-integration-testing, testing/06-mocking, testing/11-contract-testing, testing/01-testing-fundamentals]
when_to_use: "Read before replacing any real dependency in a test with a stub, mock, fake, or spy."
---
# Test Doubles

## Purpose

This document defines the family of *test doubles* — stubs, fakes, spies, mocks, and dummies
— and, more importantly, when to use each and when to use none. A test double is a stand-in
for a real dependency. It is written so an agent replaces a collaborator deliberately,
without turning a test into a test of its own mocks.

The precise vocabulary matters because the words are routinely confused, and the confusion
leads to bad tests. "Mock everything" is not a strategy; it is how suites end up green while
the app is broken.

## Why It Matters

Every double is a *claim*: "the real dependency behaves like this." When the claim is right,
the double buys you speed and determinism. When the claim drifts from reality — the API added
a field, the DB rejects the row, the service now returns 429 — the double keeps agreeing with
your code while production disagrees. That is the central danger: over-doubling produces tests
that cannot fail for the reasons that matter. The skill is using the *least powerful* double
that removes the real problem (slowness, non-determinism, cost) and no more.

## Core Principles

- **Know the five kinds.** *Dummy*: passed but unused. *Stub*: returns canned answers.
  *Spy*: a stub that also records how it was called. *Fake*: a working lightweight
  implementation (an in-memory repo). *Mock*: a double with pre-programmed expectations that
  fails if they are not met.
- **Prefer state verification over interaction verification.** Assert the *result* (a
  stub + outcome check) rather than that a method *was called* (a mock). Interaction
  assertions couple the test to implementation.
- **Double only across boundaries you own understanding of.** Replace slow, non-deterministic,
  or costly collaborators — not the pure logic under test.
- **A double must honor the real contract.** If the real service can return an error or a
  429, the double must be able to as well, or your error paths are never tested.
- **The fewer doubles, the more real the test.** Reach for a real object first; reach for a
  fake before a mock; reach for a mock last.

## Best Practices

- Use a **stub** to supply inputs (the clock returns a fixed time, the repo returns a known
  user) and assert on the *outcome*. This is the default and the most robust.
- Use a **fake** for stateful collaborators you call repeatedly — an in-memory repository is
  far more faithful than a pile of one-off stubs, and it catches ordering bugs.
- Reserve **mocks** (call expectations) for verifying genuinely important side effects with
  no observable result — e.g. "an audit event was published." Do not mock a call whose effect
  you could assert directly.
- Back every double of a service you do not own with a [contract test](11-contract-testing.md),
  so the double cannot silently drift from the real API.
- Reset all doubles between tests so recorded calls and canned answers never leak.
- If a test needs five mocks to construct, treat that as a design smell: the unit has too
  many dependencies — see [mocking](06-mocking.md).

## Examples

**Good Example** — stub the input, assert the outcome (state verification)

```ts
// Stub the clock so time is deterministic; assert the RESULT, not that a method was called.
test("marks a token expired once its deadline passes", () => {
  const clock = { now: () => 1_000 };           // stub: canned time
  const svc = new TokenService(clock);

  const status = svc.status({ expiresAt: 900 }); // deadline already passed

  expect(status).toBe("expired"); // observable outcome — survives refactors
});
```

**Bad Example** — mock everything, assert on calls (interaction verification)

```ts
test("status", () => {
  const clock = { now: jest.fn().mockReturnValue(1_000) };
  const repo = { load: jest.fn(), save: jest.fn() }; // dependencies mocked reflexively
  const svc = new TokenService(clock, repo);

  svc.status({ expiresAt: 900 });

  // Asserts HOW the code runs, not WHAT it produces. A wrong return value still passes,
  // and any internal refactor makes it red for no real reason.
  expect(clock.now).toHaveBeenCalled();
  expect(repo.load).toHaveBeenCalledTimes(1);
});
```

## Common Mistakes

- Mocking everything by reflex, so the test verifies the mocks agree with themselves and
  catches no real defect.
- Asserting a method *was called* when you could assert the actual result — coupling the
  test to implementation and breaking it on refactors.
- Building doubles that cannot express real failure modes, leaving error paths untested.
- Letting a hand-written double drift from the real dependency's contract with no
  contract test to catch it.
- Using a mock where a stub or fake would do, adding brittleness for no added confidence.
- Forgetting to reset doubles between tests, causing leaked state and order dependence.

## Production Tips

- Prefer a shared in-memory **fake** implementation of key ports (repository, clock, queue)
  over ad-hoc mocks scattered across tests — it is faithful, reusable, and refactor-safe.
- When a bug slips past a mocked test, ask whether the mock was lying; often the fix is to
  replace it with a real dependency in an [integration test](03-integration-testing.md).
- Periodically re-run contract tests against the live service so long-lived fakes stay honest.

## AI Review Checklist

- Is each double the least powerful kind that solves the real problem (stub/fake over mock)?
- Does the test verify the outcome (state) rather than that a method was called (interaction)?
- Are real dependencies used where they are fast and deterministic enough?
- Can each double express the real dependency's failure modes, so error paths are tested?
- Is every double of an external service backed by a contract test?
- Are doubles reset between tests, and does the number of mocks not signal a design smell?

## Related

- `knowledge/testing/01-testing-fundamentals.md`
- `knowledge/testing/02-unit-testing.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/06-mocking.md`
- `knowledge/testing/11-contract-testing.md`
