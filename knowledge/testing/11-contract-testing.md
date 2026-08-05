---
id: testing/11-contract-testing
topic: testing
slug: contract-testing
title: "Contract Testing"
type: doc
order: 11
status: ready
tags: [testing, contract-testing, mockResolvedValue, orderId, toBe]
related: [testing/06-mocking, testing/03-integration-testing, testing/12-api-testing, testing/05-test-doubles, testing/04-e2e-testing]
when_to_use: "Read before relying on a mock of an external service, or when two services communicate across a versioned API."
---
# Contract Testing

## Purpose

This document defines how to verify that two independently deployed services agree on the
shape of their communication — the *contract* — without running both together in one slow
end-to-end test. A contract test captures a consumer's expectations of a provider (the
requests it sends, the responses it needs) and verifies the provider actually satisfies
them.

Contract testing exists to solve the central weakness of [mocking](06-mocking.md) across a
service boundary: your mock encodes an *assumption* about the provider, and nothing checks
that the assumption stays true when the provider changes. Contract testing turns that
assumption into a verified, shared artifact.

## Why It Matters

In a distributed system, the most expensive failures are integration failures found in
production: the consumer mocked a `POST /orders` that returns `{ id }`, the provider quietly
renamed it to `orderId`, both test suites stayed green, and the break only surfaces once
they are deployed together. Full E2E tests catch this but are slow, flaky, and require every
service running at once — you cannot run them on every commit. Contract tests catch the same
class of break with the speed of a unit test, per service, without deploying the other side.
They are how you keep fast isolated tests *and* trust that the seams hold.

## Core Principles

- **The consumer defines the contract.** It states exactly what it sends and what it needs
  back. The provider's job is to satisfy that, not the reverse — this keeps providers from
  shipping fields nobody uses and consumers from depending on undocumented behavior.
- **Both sides verify the same contract.** The consumer test proves it works against the
  contract; the provider test replays the contract against the real provider. A mock that
  isn't verified against the provider is just a hopeful guess.
- **Test the shape and semantics, not exact data.** Match types, required fields, and status
  codes — use matchers, not literal values — so the contract survives legitimate data change.
- **A contract is a versioned, shared artifact.** It lives where both teams can see it and
  breaking it fails CI. An unshared contract enforces nothing.
- **Contract tests complement, not replace, integration tests.** They prove the interface
  agrees; they do not prove either side's internal logic is correct.

## Best Practices

- Use a consumer-driven contract tool (Pact and OpenAPI-based verifiers are the common
  choices in 2026) so the consumer's expectations are generated from real consumer tests.
- Verify the provider against the published contract in the provider's CI, and gate its
  deploy on that verification — a provider must not merge a change that breaks a consumer.
- Match on types and constraints (`like`, `eachLike`, regex), never on exact sample values,
  so the contract does not break every time real data differs.
- Include error responses and status codes in the contract; consumers depend on `404` vs
  `409` behavior as much as on the happy path.
- Version contracts and track which consumer versions a provider must still satisfy, so you
  can retire an expectation only when no live consumer needs it.
- Keep contract tests fast and provider-independent on the consumer side by replaying the
  contract against a stub the tool generates — no live provider needed in consumer CI.

## Examples

**Good Example** — consumer states expectations by type; provider verifies

```ts
// Consumer test: declares WHAT it needs, matched by TYPE not literal value.
provider
  .given("an order exists")
  .uponReceiving("a request for order ord_1")
  .withRequest({ method: "GET", path: "/orders/ord_1" })
  .willRespondWith({
    status: 200,
    body: { id: like("ord_1"), status: term({ matcher: "paid|pending", generate: "paid" }) },
    // matchers, not fixed strings → survives real data change, still pins the SHAPE
  });

// This publishes a contract. The PROVIDER's CI replays it against the real service,
// so a rename of `id`→`orderId` fails the provider build before it ever deploys.
```

**Bad Example** — an unverified mock standing in for a contract

```ts
// Consumer hand-mocks the provider. Nothing checks this matches the real service.
const orders = { get: vi.fn().mockResolvedValue({ id: "ord_1", status: "paid" }) };

test("shows order status", async () => {
  const view = await renderOrder(orders, "ord_1");
  expect(view.badge).toBe("Paid");
  // Green forever — even after the provider renames `id` to `orderId` and this breaks
  // in production. The mock encodes an assumption no test ever verifies.
});
```

## Common Mistakes

- Treating a hand-written mock as a contract, with nothing verifying it against the provider.
- Matching on exact sample values, so the contract breaks on every legitimate data change.
- Verifying only the consumer side and never replaying the contract against the provider.
- Omitting error responses and status codes, so failure-path assumptions go unchecked.
- Not gating the provider's deploy on contract verification, so a breaking change ships.
- Using contract tests to check business logic — that belongs in unit/integration tests.

## Production Tips

- Publish contracts to a shared broker and record verification results per version, so a
  provider knows exactly which consumers a change would break before merging.
- Run consumer contract tests on every consumer commit and provider verification on every
  provider commit — the value is in catching drift early, per side, not in a nightly job.
- For third-party providers you cannot run in CI, pin the contract to a recorded response
  and re-verify on a schedule against their sandbox to detect upstream drift.

## AI Review Checklist

- Is the consumer's expectation captured as a shared contract, not just a local mock?
- Is the same contract verified against the real provider in the provider's CI?
- Are matchers used for types/constraints rather than exact sample values?
- Does the contract cover error responses and status codes, not only the happy path?
- Is the provider's deploy gated on passing contract verification?
- Are contracts versioned so obsolete expectations can be retired safely?

## Related

- `knowledge/testing/06-mocking.md`
- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/12-api-testing.md`
- `knowledge/testing/05-test-doubles.md`
- `knowledge/testing/04-e2e-testing.md`
