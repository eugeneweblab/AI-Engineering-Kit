---
id: backend/08-domain-modeling
topic: backend
slug: domain-modeling
title: "Domain Modeling"
type: doc
order: 8
status: ready
tags: [backend, domain-modeling]
related: [backend/05-ddd, backend/07-business-logic, backend/09-validation, backend/18-database-design, backend/03-clean-architecture]
when_to_use: "Read before defining entities, value objects, or aggregates, or when a bug traces back to invalid in-memory state."
---
# Domain Modeling

## Purpose

This document defines how to represent the business's concepts in code: entities, value
objects, aggregates, and the invariants that keep them valid. It is written so an agent
can design a model where invalid states are hard or impossible to construct, rather than
guarded by scattered runtime checks.

A domain model is the vocabulary of the system made concrete. Get the nouns and their
rules right and the rest of the code becomes obvious; get them wrong and every feature
fights the model.

## Why It Matters

Most stubborn backend bugs are really *invalid state* bugs: a negative quantity, an order
with no line items, an email that isn't an email. When the model lets those states exist,
every consumer must defensively re-check them, and one forgotten check becomes a
corrupted database row. A model that makes illegal states unrepresentable moves those
guarantees from discipline to the type system, where they can't be skipped.

## Core Principles

- **Make illegal states unrepresentable.** Encode constraints in types and constructors
  so an invalid object cannot be built — the cost is a few small types, the payoff is
  deleting dozens of downstream `if` checks.
- **Distinguish entities from value objects.** An *entity* has identity and a lifecycle
  (a `User` with an id). A *value object* is defined by its data and is immutable (an
  `Email`, a `Money`). Two value objects with the same data are equal.
- **Validate on construction, then trust.** An object should be valid the moment it
  exists. After construction, code can rely on it without re-checking.
- **Guard invariants at the aggregate boundary.** An aggregate (e.g. `Order` + its lines)
  is the consistency unit; enforce cross-field rules through its root, not by mutating
  parts directly.
- **Use the ubiquitous language.** Name types and methods as the business does. See
  [DDD](05-ddd.md).

## Best Practices

- Wrap primitives that carry rules in value objects (`Email`, `Money`, `Quantity`) instead
  of passing raw `string`/`number` around — this prevents mixing a price with a count.
- Make value objects immutable; "changes" return a new instance. Immutability removes a
  whole class of aliasing bugs.
- Keep the domain model separate from the persistence model. The database schema serves
  storage; the domain serves rules. Map between them. See
  [database design](18-database-design.md).
- Express optionality explicitly (an option/nullable type), never a magic sentinel like
  `-1` or `""`.
- Put behavior on the model (`order.addLine(...)`), not in external "manager" classes that
  reach in and mutate fields — that recreates the invalid-state problem.
- Keep aggregates small; reference other aggregates by id, not by embedding them.

## Examples

**Good Example** — value object that cannot hold an invalid value

```ts
class Money {
  private constructor(readonly cents: number, readonly currency: string) {}

  // The ONLY way to build a Money runs the rules — an invalid Money can't exist.
  static of(cents: number, currency: string): Result<Money> {
    if (!Number.isInteger(cents)) return err("MONEY_NOT_INTEGER"); // no float cents
    if (cents < 0) return err("MONEY_NEGATIVE");
    if (!/^[A-Z]{3}$/.test(currency)) return err("BAD_CURRENCY");
    return ok(new Money(cents, currency));
  }

  add(other: Money): Money {
    if (other.currency !== this.currency) throw new Error("currency mismatch"); // invariant
    return new Money(this.cents + other.cents, this.currency); // immutable: new instance
  }
}
```

**Bad Example** — primitives everywhere, invariants unenforced

```ts
// Anyone can construct nonsense: negative price, wrong-typed args silently swapped.
interface Order {
  total: number;      // dollars? cents? which currency? unknown from the type
  currency: string;   // never validated — "usd", "Dollars", "" all pass
  items: any[];       // an order with zero items is representable and will ship
}

function applyDiscount(o: Order, pct: number) {
  o.total = o.total - o.total * pct; // mutates in place; pct=2 makes total negative, no guard
}
```

## Common Mistakes

- "Primitive obsession": passing raw `string`/`number` for concepts that have rules,
  letting a user id and an order id be swapped without a type error.
- Using the ORM entity as the domain model, so persistence concerns dictate business
  design.
- Mutable value objects shared by reference, causing spooky action at a distance.
- Sentinel values (`-1`, `""`, `0000-00-00`) instead of an explicit optional type.
- Anemic models: data bags with all behavior in external services, so invariants aren't
  guarded on the object.
- Giant aggregates that embed unrelated entities and load half the database at once.

## Production Tips

- When a bug is found, ask "what type would have made this unrepresentable?" and fix the
  model, not just the instance.
- Keep construction the single validation point; property-based tests on constructors
  catch edge cases cheaply.
- Map domain ↔ persistence explicitly in a repository so a schema change never silently
  weakens a domain invariant.

## AI Review Checklist

- Are concepts with rules (money, email, quantity) modeled as value objects, not raw
  primitives?
- Can an invalid instance be constructed at all, or do constructors enforce every rule?
- Are entities (identity + lifecycle) clearly distinguished from value objects (equal by
  data)?
- Are value objects immutable, with "changes" returning new instances?
- Are cross-field invariants enforced through the aggregate root?
- Is the domain model kept separate from the persistence/ORM model?
- Is optionality explicit rather than expressed with magic sentinels?

## Related

- `knowledge/backend/05-ddd.md`
- `knowledge/backend/07-business-logic.md`
- `knowledge/backend/09-validation.md`
- `knowledge/backend/18-database-design.md`
- `knowledge/backend/03-clean-architecture.md`
