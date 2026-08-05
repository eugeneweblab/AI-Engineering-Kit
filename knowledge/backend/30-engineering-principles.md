---
id: backend/30-engineering-principles
topic: backend
slug: engineering-principles
title: "Backend Engineering Principles"
type: doc
order: 30
status: ready
tags: [backend, engineering-principles]
related: [backend/01-backend-architecture, backend/12-error-handling, backend/23-testing, backend/22-observability, backend/28-best-practices]
when_to_use: "Read before making a design decision on the backend and you need a default to reason from."
---
# Backend Engineering Principles

## Purpose

This document defines the durable principles that govern backend engineering decisions:
how to structure code, handle failure, manage change, and reason about trade-offs. These
are the defaults an agent should apply when a more specific doc does not dictate an
answer. They are not style preferences — each principle exists to reduce a concrete class
of production incident or maintenance cost.

Principles guide judgment; they do not replace it. When two principles conflict, name the
trade-off explicitly and choose based on the cost you are willing to pay, not on habit.

## Why It Matters

Backend code lives for years, is read far more often than it is written, and fails in
production where the cost is real: lost data, downtime, corrupted state, security holes.
Most of that cost is not caused by exotic bugs — it comes from ordinary decisions made
without a principle to anchor them: a shared mutable global, a swallowed error, an
untested edge case, an abstraction added "just in case." Principles make the cheap,
correct choice the default so that scarce attention is spent only where the problem is
genuinely hard.

## Core Principles

- **Correctness before cleverness.** A boring, obviously-correct implementation beats a
  fast or elegant one you cannot verify. Optimize only after a measurement proves you
  must; the cost of premature optimization is unreadable code that hides bugs.
- **Make illegal states unrepresentable.** Encode invariants in types and schemas so bad
  data cannot exist, instead of checking for it everywhere. The cost is more upfront
  modeling; the payoff is entire bug classes that become impossible.
- **Fail loud and fail fast.** Detect invalid input at the boundary and reject it with a
  clear error. A swallowed error turns a cheap, local crash into an expensive, distant
  corruption you cannot trace.
- **Explicit over implicit.** Pass dependencies, config, and context as arguments. Hidden
  globals and ambient state make behavior depend on invisible history and destroy
  testability.
- **Idempotency by default.** Design writes so that retrying them is safe. Networks
  retry; if a duplicate call double-charges or double-inserts, the bug is yours.
- **Isolate side effects.** Keep pure logic (decisions) separate from effects (I/O,
  clock, randomness). Pure code is trivially testable; effectful code is not.
- **Design for the reader.** Name things for intent, keep functions short, and delete
  dead code. The next reader is often a future agent with no context.

## Best Practices

- Validate and normalize all external input at the system boundary (HTTP, queue, file);
  treat everything past the boundary as already-trusted. See [validation](09-validation.md).
- Keep functions small and single-purpose; a function that both decides and performs I/O
  is two functions wearing one name.
- Prefer immutability. Return new values instead of mutating arguments so callers cannot
  be surprised by aliasing.
- Handle errors where you have the context to act; otherwise propagate them typed and
  unchanged. Never `catch` just to log and swallow. See [error handling](12-error-handling.md).
- Make every write idempotent via a unique key, upsert, or dedup check.
- Delete code aggressively. Unused abstractions are liabilities, not assets — YAGNI beats
  speculative generality.
- Add an abstraction only on the **third** concrete use, when the shape is known. Two
  cases rarely reveal the right seam; a wrong abstraction is costlier than duplication.
- Instrument before you optimize: measure with real data, change one thing, measure again.

## Examples

**Good Example** — pure decision separated from effect, idempotent, explicit deps

```ts
// Pure: no I/O, no clock, no globals — fully testable in isolation.
function computeCharge(cart: Cart, now: Date): Charge {
  if (cart.items.length === 0) throw new EmptyCartError(); // fail fast at the boundary
  return { amountCents: total(cart), currency: cart.currency, at: now };
}

// Effectful shell: dependencies passed in, write is idempotent by request key.
async function checkout(cart: Cart, deps: { payments: PaymentGateway; now: () => Date }) {
  const charge = computeCharge(cart, deps.now());
  // idempotencyKey makes a retried request a no-op instead of a double charge
  return deps.payments.charge(charge, { idempotencyKey: cart.id });
}
```

**Bad Example** — hidden globals, swallowed error, non-idempotent write

```ts
import { db, stripe, logger } from "./globals"; // ambient state: untestable, order-dependent

async function checkout(cart: Cart) {
  try {
    // decision and I/O tangled together; clock read from global Date.now()
    const total = cart.items.reduce((s, i) => s + i.price, 0);
    await stripe.charge(total); // no idempotency key → a retry double-charges
    await db.orders.insert({ cart, total }); // duplicate rows on retry
  } catch (e) {
    logger.warn(e); // swallowed: caller thinks it succeeded, money may be gone
  }
}
```

## Common Mistakes

- Catching an error only to log it, letting a corrupted operation appear to succeed.
- Reaching for globals, singletons, or module-level mutable state instead of passing
  dependencies, which makes code untestable and order-dependent.
- Optimizing before measuring, trading readability for a speedup that does not matter.
- Adding a layer of abstraction for a single caller "in case we need it later."
- Non-idempotent writes that corrupt data the first time a network retry fires.
- Mutating input arguments, causing action-at-a-distance bugs in the caller.
- Validating the same untrusted input repeatedly in the core instead of once at the edge.

## Production Tips

- Encode invariants once, at the boundary, and let the type system carry them inward so
  downstream code needs no defensive checks.
- Make retries safe end-to-end: idempotency keys on writes, `at-least-once` assumptions on
  every consumer. See [background jobs](16-background-jobs.md).
- Emit a structured log and a metric at every failure branch so a swallowed error is
  impossible by construction. See [observability](22-observability.md).

## AI Review Checklist

- Is pure decision logic separated from I/O, clock, and randomness?
- Are dependencies passed explicitly rather than imported as globals or singletons?
- Is every external input validated and normalized at the boundary exactly once?
- Are all writes idempotent under retry (unique key, upsert, or dedup)?
- Are errors propagated with context, never caught-and-swallowed?
- Is any new abstraction justified by three real uses, not speculation?
- Was any optimization backed by a measurement, or is it premature?

## Related

- `knowledge/backend/01-backend-architecture.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/23-testing.md`
- `knowledge/backend/22-observability.md`
- `knowledge/backend/28-best-practices.md`
