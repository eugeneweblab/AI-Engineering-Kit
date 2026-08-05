---
id: backend/05-ddd
topic: backend
slug: ddd
title: "DDD"
type: doc
order: 5
status: ready
tags: [backend, ddd, DomainError, OrderLine, OrderPlaced, Email, addLine, place]
related: [backend/03-clean-architecture, backend/04-hexagonal-architecture, backend/07-business-logic, backend/08-domain-modeling]
when_to_use: "Read before modeling a non-trivial business domain, or when logic is scattering across services instead of living on the model."
---
# DDD

## Purpose

This document defines Domain-Driven Design (DDD): a way to model a business domain so
the code speaks the domain's language and enforces its rules structurally. It gives an
agent the building blocks — entities, value objects, aggregates, domain services,
repositories, and bounded contexts — and the rules for using them.

DDD is orthogonal to the architecture patterns: [clean](03-clean-architecture.md) and
[hexagonal](04-hexagonal-architecture.md) tell you where the domain sits; DDD tells you
what goes *inside* it. It pays off when the domain is complex; for simple CRUD it is
overkill.

## Why It Matters

The hardest part of most systems is not the technology but understanding the business
correctly and keeping that understanding in the code as rules change. When logic is
scattered across anemic services and data-bag models, no single place is authoritative,
invariants are enforced inconsistently, and every change risks corrupting state. DDD
concentrates each rule on the object that owns it, so an invariant is enforced in one
place and cannot be bypassed. The cost is modeling discipline and more types; the return
is a domain that resists corruption and reads like the business it represents.

## Core Principles

- **Ubiquitous language.** Code, conversation, and documentation use the same terms as
  domain experts. If experts say "policy" and the code says "record," the model is
  already drifting.
- **Entities have identity; value objects do not.** An entity is defined by a stable id
  over time (a `Customer`). A value object is defined by its attributes and is immutable
  (a `Money`, an `Email`). Model attribute-defined concepts as value objects.
- **Aggregates guard invariants.** An aggregate is a cluster of objects with one root
  entity as the only entry point. All changes go through the root, which enforces the
  aggregate's invariants and keeps it internally consistent.
- **One transaction, one aggregate.** A single transaction should modify only one
  aggregate instance. Coordinate across aggregates with domain events, not by editing
  several in one commit.
- **Domain services for cross-entity logic.** Behavior that does not belong to any one
  entity lives in a stateless domain service, still in the domain layer, still in the
  ubiquitous language.
- **Bounded contexts.** A large domain splits into contexts, each with its own model and
  language. The same word ("account") can mean different things in different contexts;
  do not force one shared model.

## Best Practices

- Put behavior on the model. A method like `order.cancel()` that enforces the rules
  beats a service that reads the order, mutates fields, and saves it back.
- Make value objects immutable and self-validating: an `Email` that cannot be
  constructed from an invalid string makes invalid state unrepresentable.
- Reference other aggregates by id, not by object. Holding a direct object reference
  invites multi-aggregate writes and loads the whole graph.
- Keep aggregates small — ideally the root plus what must change together to stay valid.
  Large aggregates cause contention and slow loads.
- Load and save aggregates whole through a repository (one repository per aggregate
  root), so the root always enforces consistency.
- Publish domain events for things the business cares about (`OrderPlaced`); use them to
  update other aggregates or contexts asynchronously.
- Draw explicit boundaries between contexts and translate at the seam (anti-corruption
  layer) rather than sharing entities across them.

## Examples

**Good Example** — aggregate root enforces invariants; value object is self-validating

```ts
class Email {                                   // value object: immutable, always valid
  private constructor(readonly value: string) {}
  static of(raw: string): Email {
    if (!/^[^@\s]+@[^@\s]+$/.test(raw)) throw new DomainError("invalid email");
    return new Email(raw.toLowerCase());
  }
}

class Order {                                   // aggregate root: sole entry point
  private constructor(readonly id: OrderId, private lines: OrderLine[], private status: Status) {}

  addLine(product: ProductId, qty: number) {
    if (this.status !== "DRAFT")                // invariant lives on the root...
      throw new DomainError("cannot modify a placed order");
    if (qty <= 0) throw new DomainError("qty must be positive");
    this.lines.push(new OrderLine(product, qty)); // ...so it cannot be bypassed
  }

  place(): OrderPlaced {
    if (this.lines.length === 0) throw new DomainError("empty order");
    this.status = "PLACED";
    return new OrderPlaced(this.id);            // domain event for other aggregates
  }
}
```

**Bad Example** — anemic model, rules smeared across a service, invariant bypassable

```ts
class Order { id: string; lines: any[]; status: string; } // data bag, no behavior

class OrderService {
  addLine(order: Order, product: string, qty: number) {
    // nothing stops another code path from pushing directly to order.lines and
    // skipping this check — the invariant is not owned by the aggregate.
    if (order.status === "DRAFT") order.lines.push({ product, qty });
  }
  place(order: Order) {
    order.status = "PLACED"; // no check that lines is non-empty; invalid state slips in
  }
}
```

## Common Mistakes

- **Anemic domain model** — entities are field bags and all logic sits in services, so
  no object owns its invariants and rules are enforced inconsistently.
- **Huge aggregates** — modeling half the schema as one aggregate, causing lock
  contention and loading enormous object graphs per request.
- **Multi-aggregate transactions** — mutating several aggregates in one commit instead
  of using domain events, coupling their consistency and their storage.
- **Object references between aggregates** — holding a `Customer` object on an `Order`
  rather than a `CustomerId`, pulling in the whole graph and blurring boundaries.
- **One model for everything** — refusing bounded contexts and forcing a single
  "shared" entity that means subtly different things in different parts of the system.
- **DDD on a CRUD app** — importing the full tactical toolkit where a plain table and a
  service would do, paying modeling cost for no complexity to tame.

## Production Tips

- Let the aggregate boundary drive the transaction boundary: if a use case must change
  two aggregates atomically, that is a signal the boundaries may be wrong, or that an
  eventual-consistency flow with events is the right design.
- Keep the ubiquitous language alive in reviews — rename code when the business renames
  a concept, or drift sets in silently.
- Persist domain events (outbox pattern) so cross-aggregate and cross-context updates
  survive crashes and are delivered exactly once downstream.

## AI Review Checklist

- Do entities and aggregates hold their own behavior and invariants, not just data?
- Are attribute-defined concepts (money, email, address) modeled as immutable value
  objects that cannot be constructed invalid?
- Does every change to an aggregate go through its root?
- Does each transaction modify a single aggregate, with cross-aggregate work handled by
  events?
- Are other aggregates referenced by id rather than by object?
- Does the code use the domain's ubiquitous language, with bounded contexts drawn
  where meanings diverge?

## Related

- `knowledge/backend/03-clean-architecture.md`
- `knowledge/backend/04-hexagonal-architecture.md`
- `knowledge/backend/07-business-logic.md`
- `knowledge/backend/08-domain-modeling.md`
