---
id: architecture/30-engineering-principles
topic: architecture
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [architecture, engineering-principles]
related: [architecture/28-best-practices, architecture/03-clean-architecture, architecture/26-architecture-decision-records, architecture/100-common-antipatterns, architecture/14-performance]
when_to_use: "Read before making any non-trivial design decision, so trade-offs are reasoned rather than guessed."
---
# Engineering Principles

## Purpose

This document defines the durable principles that govern *how* to make architecture
decisions — the reasoning an agent applies before choosing a pattern, drawing a
boundary, or adding a dependency. Patterns come and go; these principles decide when a
pattern earns its place. Read this before the concrete pattern docs
([clean architecture](03-clean-architecture.md), [CQRS](07-cqrs.md),
[event-driven](08-event-driven-architecture.md)); they tell you *what*, this tells you
*whether* and *why*.

## Why It Matters

Most architecture damage is not one catastrophic choice — it is a hundred small,
unreasoned defaults that compound. An unneeded abstraction, a premature service split, a
"temporary" shared table: each looks harmless in isolation and each raises the cost of
every future change. Principles matter because they make the trade-off *explicit at the
moment of the decision*, when it is cheap to change your mind, instead of two years later
when it is not. An agent that can name the cost of a choice will avoid the expensive ones.

## Core Principles

- **Optimize for change, not for cleverness.** The dominant cost of software is
  modification, not initial construction. Prefer the design that is easiest to change
  later, even when it is more verbose now. The cost is more code today; the payoff is
  cheaper change for the software's whole life.
- **Every abstraction must pay rent.** An abstraction is justified only when it removes
  more complexity than it adds. Do not introduce an interface, layer, or generic for a
  single caller. The cost of a wrong abstraction is higher than the cost of duplication.
- **Defer decisions until they are cheap to reverse.** Distinguish one-way doors
  (data models, public APIs, service boundaries) from two-way doors (internal structure).
  Invest analysis in the irreversible ones; move fast and cheap on the rest.
- **Make the boundary match the change and ownership axis.** Split modules and services
  where they change independently and are owned by different teams — not where a diagram
  looks tidy. A boundary in the wrong place creates coupling *and* overhead.
- **Coupling is the enemy; cohesion is the goal.** Minimize what a module must know about
  another. Maximize how much of a module belongs together. High coupling is what makes a
  system rigid; low cohesion is what makes it incoherent.
- **The simplest thing that could possibly work, first.** Add complexity only in response
  to a demonstrated need (a measured limit, a real requirement), never in anticipation.

## Best Practices

- Write down the decision *and its alternatives* in an
  [ADR](26-architecture-decision-records.md) whenever a choice is hard to reverse. The
  reasoning is worth more than the conclusion.
- Duplicate before you abstract. Wait for the third occurrence before extracting a shared
  abstraction — by then you actually know the shape of what varies.
- Design against interfaces you own, not against third-party types, so a vendor change is
  contained to one adapter (see [hexagonal architecture](04-hexagonal-architecture.md)).
- Prefer boring, proven technology for the core of the system; spend your limited
  "innovation budget" on the one thing that is genuinely novel about your product.
- Make illegal states unrepresentable in the type/schema, so whole classes of bugs cannot
  compile rather than being caught by tests.
- Measure before optimizing. A [performance](14-performance.md) change without a
  before/after number is a guess, and guesses about performance are usually wrong.
- Keep the number of ways to do a thing small. Consistency lowers the cost of reading
  code, which is what engineers spend most of their time doing.

## Examples

**Good Example** — an abstraction that pays rent, introduced at the right time

```ts
// Two real payment providers already exist, and a third is coming. The interface
// now removes more complexity (callers stop branching on provider) than it adds.
interface PaymentGateway {
  charge(amountCents: number, token: string): Promise<ChargeResult>;
}

// Business code depends on the owned interface, not on Stripe's SDK types.
// Cost: one small indirection. Payoff: swapping providers touches one file.
class Checkout {
  constructor(private readonly gateway: PaymentGateway) {}
}
```

**Bad Example** — speculative abstraction with a single implementation

```ts
// Only one provider exists and none is planned. This interface, factory, and
// config layer add indirection that removes no complexity — an abstraction
// that does not pay rent. Every reader now chases three files to find one call.
interface IPaymentGatewayProvider { create(): PaymentGateway; }
class PaymentGatewayFactory implements IPaymentGatewayProvider { /* ... */ }
// You will guess the extension points wrong and refactor them anyway once a
// second provider actually arrives. Duplication would have been cheaper.
```

## Common Mistakes

- Adding layers, interfaces, or microservices "for flexibility" with no second use case
  in sight — paying the cost of an abstraction while getting none of its benefit.
- Treating a reversible internal choice as if it were irreversible, and over-analyzing it.
- Splitting a service along a technical seam (all controllers, all repositories) instead
  of a business-capability seam, so every feature spans every service.
- Optimizing code paths that no measurement showed to be slow.
- Copying a pattern (CQRS, event sourcing, hexagonal) from a talk without the problem the
  pattern solves — cargo-culting structure the system does not need.
- Not recording *why* a decision was made, forcing the next engineer to reverse-engineer
  intent from code.

## Production Tips

- Track the reversibility of decisions in your ADRs; revisit one-way doors before, not
  after, they ship.
- Budget deliberate time to delete code and collapse abstractions that never earned their
  keep — reducing complexity is real engineering work, not cleanup.
- When two principles conflict (e.g., simplicity vs. decoupling), state which one you
  prioritized and why, so the trade-off is auditable in [review](27-architecture-review.md).

## AI Review Checklist

- Does every new abstraction, layer, or service have at least two real callers or a
  concrete, imminent second use case?
- Is the reasoning and the rejected alternatives recorded for each hard-to-reverse choice?
- Are module and service boundaries drawn on change/ownership axes, not technical layers?
- Was any performance optimization backed by a before/after measurement?
- Is the design the simplest one that meets the *current* requirements, with complexity
  added only for demonstrated needs?
- Does business logic depend on owned interfaces rather than vendor SDK types?

## Related

- `knowledge/architecture/28-best-practices.md`
- `knowledge/architecture/03-clean-architecture.md`
- `knowledge/architecture/26-architecture-decision-records.md`
- `knowledge/architecture/100-common-antipatterns.md`
- `knowledge/architecture/14-performance.md`
