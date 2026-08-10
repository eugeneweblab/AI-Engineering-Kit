---
id: testing/06-mocking
topic: testing
slug: mocking
title: "Mocking"
type: doc
order: 6
status: ready
tags: [testing, mocking, Checkout, mockReturnValue, mockResolvedValue, toHaveBeenCalledBefore, toHaveBeenCalledTimes, asserts, was, called]
related: [testing/05-test-doubles, testing/03-integration-testing, testing/11-contract-testing, testing/22-flaky-tests, testing/29-test-review]
when_to_use: "Read before replacing a real dependency with a mock, or when a test asserts on how a collaborator was called."
---
# Mocking

## Purpose

This document defines when and how to replace a real collaborator with a mock — a test
double that records calls and lets you assert on them. It is the practical companion to
[test doubles](05-test-doubles.md), which defines the vocabulary (stub, mock, fake, spy).
Read this before you reach for `jest.mock`, `vi.mock`, `unittest.mock`, or a mocking
framework in any language.

A mock verifies an *interaction*: "the code called `charge()` once, with this amount." A
stub only supplies a canned return value. Knowing which one you need is the whole skill —
most tests that reach for a mock actually want a stub or a fake.

## Why It Matters

Mocks are the most abused tool in testing. Over-mocking produces tests that pass while the
system is broken: you assert that a method was called, but the method itself is wrong, or
the real dependency changed its contract and your mock did not. Such a suite is green
theater — it grows, it runs, it lies. Worse, mock-heavy tests couple to *implementation*
(which methods run, in what order), so every refactor breaks them even when behavior is
unchanged. The cost is a suite people delete rather than maintain. Mock deliberately, at
real boundaries only, and you keep the confidence; mock reflexively and you trade it away.

## Core Principles

- **Prefer real objects, then fakes, then stubs, then mocks — in that order.** Each step
  down loses fidelity to the real system. Take the smallest step that isolates the unit.
- **Mock roles, not data.** Replace a collaborator that *does* something with side effects
  (payment gateway, email sender, clock). Never mock a value object or your own DTO.
- **Only mock what you own, or wrap what you don't.** Mocking a third-party client directly
  couples your test to their API shape; wrap it in your own interface and mock that.
- **Assert on outcomes, not incantations.** Verify the observable result. Reach for
  call-verification only when the side effect *is* the behavior (an email was sent).
- **A mock is a claim about a contract.** If the real dependency's contract drifts, your
  mock is now a lie. [Contract tests](11-contract-testing.md) are what keep it honest.

## Best Practices

- Mock at architectural seams — the ports of your application (repository, gateway,
  publisher) — not at internal method boundaries within a unit.
- Set an explicit expectation *and* nothing else: verify the one interaction that matters,
  not the entire call sequence, so incidental refactors don't break the test.
- Prefer a hand-written fake (an in-memory implementation of the interface) when several
  tests need the same collaborator; it is reusable and stays honest about the contract.
- Reset or recreate mocks between tests (`beforeEach`, `restoreAllMocks`) so state never
  leaks between cases — leaked mock state is a classic [flaky test](22-flaky-tests.md).
- Never mock the unit under test. If you find yourself mocking part of the thing you are
  testing, the unit is too big — split it.
- Type your mocks against the real interface so a signature change breaks compilation, not
  silently passes a stale stub.

## Examples

**Good Example** — mock the side-effecting boundary, assert the outcome

```ts
// The clock and the mailer are real side effects we own via interfaces.
test("sends a receipt after a successful charge", async () => {
  const gateway = { charge: vi.fn().mockResolvedValue({ id: "ch_1", ok: true }) };
  const mailer = { send: vi.fn().mockResolvedValue(undefined) };
  const checkout = new Checkout(gateway, mailer);

  const result = await checkout.pay({ userId: "u1", amountCents: 500 });

  expect(result.status).toBe("paid");          // assert the OUTCOME first
  expect(gateway.charge).toHaveBeenCalledWith({ amountCents: 500 }); // the side effect IS the behavior
  expect(mailer.send).toHaveBeenCalledTimes(1); // sending the receipt is a real requirement
});
```

**Bad Example** — mocks everything, asserts nothing real

```ts
test("pay works", async () => {
  const checkout = new Checkout(gateway, mailer);
  // Mocking a method ON the unit under test — now the test proves nothing about pay().
  checkout.validate = vi.fn().mockReturnValue(true);
  checkout.buildReceipt = vi.fn().mockReturnValue({});

  await checkout.pay({ userId: "u1", amountCents: 500 });

  // Verifying internal call order couples the test to implementation, not behavior.
  expect(checkout.validate).toHaveBeenCalledBefore(checkout.buildReceipt);
  // No assertion on the actual result — the payment could be wrong and this stays green.
});
```

## Common Mistakes

- Mocking value objects, DTOs, or pure functions instead of just constructing them.
- Asserting the full sequence of internal calls, so any refactor reddens the suite.
- Mocking a third-party library's API directly instead of a wrapper you control.
- Letting a stub drift from the real contract, so tests pass against a shape production
  no longer returns (guard with [contract tests](11-contract-testing.md)).
- Shared mock state leaking across tests because mocks aren't reset between cases.
- Using a mock where a stub would do — verifying a call that has no behavioral meaning.

## Production Tips

- In CI, run a fast unit tier that mocks external systems *and* a slower integration tier
  that hits real ones (a container, a sandbox). Mocks alone never prove the wiring works.
- Periodically delete a mock and run the test against the real fake — if confidence drops,
  the mock was carrying more than it should.
- Track "assertion-free" tests (tests that only call `toHaveBeenCalled`) as a smell; they
  often signal a mock standing in for a missing real assertion.

## AI Review Checklist

- Is each mock at a real architectural boundary (a port), not an internal method?
- Does the test assert an observable outcome, not merely that a method was called?
- Is call-verification used only where the interaction itself is the required behavior?
- Are third-party dependencies wrapped and the wrapper mocked, rather than mocked directly?
- Are mocks typed against the real interface and reset between tests?
- Would this test survive a behavior-preserving refactor of the unit's internals?
- Is there a fake or contract test keeping the mock honest to the real contract?

## Related

- `knowledge/testing/05-test-doubles.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/11-contract-testing.md`
- `knowledge/testing/22-flaky-tests.md`
- `knowledge/testing/29-test-review.md`
