---
id: architecture/06-domain-driven-design
topic: architecture
slug: domain-driven-design
title: "Domain Driven Design"
type: doc
order: 6
status: ready
tags: [architecture, domain-driven-design, DomainError, OrderPlaced, Money, place, constructor, addLine]
related: [architecture/03-clean-architecture, architecture/07-cqrs, architecture/08-event-driven-architecture, architecture/09-microservices, architecture/10-modular-monolith]
when_to_use: "Read before modeling a complex business domain or carving a system into service or module boundaries."
---
# Domain Driven Design

## Purpose

This document defines how to model complex business logic so the code mirrors the
domain it serves. Domain-Driven Design (DDD) gives you a vocabulary — *bounded
context*, *aggregate*, *entity*, *value object*, *domain event* — and a set of rules
for keeping business rules in one place, expressed in the language the business uses.

DDD is a modeling discipline, not a framework. It answers "where does this rule live
and who owns this data?" It pairs naturally with [clean architecture](03-clean-architecture.md)
(which keeps the domain free of infrastructure), [CQRS](07-cqrs.md), and
[event-driven architecture](08-event-driven-architecture.md). Reach for it when the
domain is genuinely complex; skip it for CRUD.

## Why It Matters

Business complexity, not technical complexity, is what kills large systems. When rules
about pricing, eligibility, or state transitions are smeared across controllers,
services, and SQL, no single place is authoritative — so every change risks a
contradiction, and no one can say what the system actually does. DDD concentrates each
rule inside a model that enforces its own invariants, and draws explicit boundaries so
teams can change one context without breaking another. The cost is up-front modeling
effort and more types; the payoff is a codebase that stays changeable as the business
grows.

## Core Principles

- **Speak the ubiquitous language.** Use the exact terms the domain experts use, in
  code, tests, and conversation. If they say "policy" and the code says "record", the
  translation gap becomes bugs.
- **Draw bounded contexts.** A term means one thing inside a context. "Customer" in
  Billing is not "Customer" in Support. Give each context its own model and an explicit
  contract at the seam — never a shared, god-object schema.
- **Protect invariants inside aggregates.** An aggregate is a cluster of objects
  changed as a unit, with one *root* entity as the only entry point. All mutations go
  through the root so it can enforce the rules that must always hold.
- **Distinguish entities from value objects.** An entity has identity that persists
  across changes (an `Order`). A value object is defined only by its attributes and is
  immutable (a `Money`, an `Address`). Prefer value objects — they cannot be corrupted.
- **Keep the domain pure.** Business logic must not depend on the database, HTTP, or the
  framework. Push those to the edges (see [clean architecture](03-clean-architecture.md)).

## Best Practices

- Make one aggregate the consistency boundary of one transaction. Do not modify two
  aggregates atomically; coordinate them with a [domain event](08-event-driven-architecture.md)
  and accept eventual consistency, because a transaction spanning aggregates couples
  them and blocks independent scaling.
- Reference other aggregates **by id**, not by object reference. Holding a live object
  invites someone to mutate it outside its root and violate its invariants.
- Put invariant checks in the aggregate root's methods, not in the calling service. A
  rule enforced only at the call site is a rule that will eventually be bypassed.
- Model illegal states as unrepresentable: use value objects with validating
  constructors so an `Email` or `Quantity` cannot exist in an invalid form.
- Keep aggregates small — ideally a root plus the entities it truly owns. Large
  aggregates create contention and slow writes.
- Publish domain events for facts other contexts care about ("OrderPlaced"), and let
  each context react in its own transaction.

## Examples

**Good Example** — aggregate root enforces its own invariants

```ts
// Money is a value object: immutable, validated on construction, no identity.
class Money {
  private constructor(readonly cents: number, readonly currency: string) {}
  static of(cents: number, currency: string): Money {
    if (cents < 0) throw new DomainError("Money cannot be negative");
    return new Money(cents, currency);
  }
}

class Order {                                  // aggregate root — the only entry point
  private constructor(readonly id: OrderId, private lines: Line[], private status: Status) {}

  addLine(product: ProductId, qty: number): void {
    // Invariant lives WITH the data it protects, so it cannot be bypassed.
    if (this.status !== "Draft") throw new DomainError("Cannot edit a placed order");
    if (qty <= 0) throw new DomainError("Quantity must be positive");
    this.lines.push(new Line(product, qty));
  }

  place(): OrderPlaced {
    if (this.lines.length === 0) throw new DomainError("Cannot place an empty order");
    this.status = "Placed";
    return new OrderPlaced(this.id);           // emit a fact, do not call other aggregates
  }
}
```

**Bad Example** — anemic model, rules leak into a service

```ts
// Anemic "entity": just public data, no behavior. Rules live elsewhere → nowhere.
class Order { id!: string; lines: Line[] = []; status = "Draft"; }

class OrderService {
  place(order: Order, inventory: Inventory) {
    order.status = "Placed";                   // any caller can set any state, any time
    inventory.items.forEach(i => i.count--);   // reaches into another aggregate's guts
    // The "cannot place an empty order" rule? It is not enforced anywhere.
  }
}
```

## Common Mistakes

- **Anemic domain models**: entities are bags of getters/setters and all logic sits in
  "services", so invariants are never guaranteed.
- One giant shared model across the whole system instead of bounded contexts — every
  team blocks every other team.
- Aggregates that span half the schema, so any write locks huge object graphs.
- Loading and mutating a second aggregate inside the same transaction "for convenience".
- Leaking ORM entities, DTOs, or framework types into the domain layer.
- Inventing DDD tactical patterns (aggregates, events) for a simple CRUD app that does
  not need them — ceremony with no payoff.

## Production Tips

- Version and document each context's published contract (events, API). A downstream
  context should never depend on another's internal schema.
- Use a context map to record relationships (partnership, customer/supplier, anti-corruption
  layer) so integration expectations are explicit.
- Put an anti-corruption layer at the boundary of a legacy or third-party system to
  translate its model into your language, keeping the rot out of your domain.

## AI Review Checklist

- Do entities enforce their own invariants, or do rules live in services (anemic model)?
- Does each transaction modify exactly one aggregate?
- Are other aggregates referenced by id rather than held as live objects?
- Are value objects immutable and validated in their constructors?
- Is the domain layer free of database, HTTP, and framework dependencies?
- Does the code use the domain's ubiquitous language for names?
- Are context boundaries explicit, with a defined contract at each seam?

## Related

- `knowledge/architecture/03-clean-architecture.md`
- `knowledge/architecture/07-cqrs.md`
- `knowledge/architecture/08-event-driven-architecture.md`
- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/10-modular-monolith.md`
