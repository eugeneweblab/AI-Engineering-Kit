---
id: backend/01-backend-architecture
topic: backend
slug: backend-architecture
title: "Backend Architecture"
type: doc
order: 1
status: ready
tags: [backend, backend-architecture]
related: [backend/00-overview, backend/02-layered-architecture, backend/03-clean-architecture, backend/04-hexagonal-architecture, backend/05-ddd]
when_to_use: "Read before designing a new service or choosing how to structure an existing one."
---
# Backend Architecture

## Purpose

This document defines how to structure a server-side application: what to separate,
which way dependencies should point, and how to choose among the common patterns. It
gives an agent a way to reason about structure so it lands new code in the right place
and can justify — or challenge — an existing design.

Architecture is the set of decisions that are hard to change later. This doc is about
making those decisions deliberately instead of by accident.

## Why It Matters

The architecture is what the code looks like after all the features are gone. It
outlives every function you write. When it is right, features slot in cleanly and tests
are cheap. When it is wrong, every change fights the structure: logic scatters, tests
require a live database, and one module's change breaks three others. That drag is
invisible on day one and dominant by month six. Because the cost is deferred and
compounding, structure must be chosen up front and defended in review.

## Core Principles

- **Separate concerns by rate of change and reason to change.** Delivery (HTTP, CLI),
  application logic, domain rules, and infrastructure (DB, queues) change for different
  reasons and at different speeds. Keep them in separate modules so a change to one
  does not ripple into the others.
- **Point dependencies toward stability.** Volatile, replaceable things (frameworks,
  drivers, third-party APIs) should depend on stable things (your domain), never the
  reverse. This is the Dependency Inversion Principle applied at module scale.
- **Depend on abstractions across boundaries.** Cross a boundary through an interface
  you own, not a concrete class from someone else's library.
- **Keep the domain pure.** The code that encodes business rules should have no import
  from a web framework, ORM, or client SDK. Purity is what makes it testable and
  portable.
- **Choose the simplest structure that fits.** Every layer and abstraction is a cost.
  Add one only when a concrete pressure justifies it.

## Best Practices

- Default to a [layered](02-layered-architecture.md) structure
  (controller → service → repository) for typical CRUD services. It is well understood
  and cheap. Escalate only when rules grow complex.
- Reach for [clean](03-clean-architecture.md) or
  [hexagonal](04-hexagonal-architecture.md) when business logic is the hard part and
  must survive changes of framework, database, or delivery mechanism.
- Isolate every external system (DB, broker, payment API) behind a port/interface, so
  it can be swapped or faked in tests without touching business code.
- Keep controllers thin: parse input, call one use case, map the result to a response.
  No business logic in the transport layer.
- Make invalid states unrepresentable in the type system where you can; push validation
  to the boundary so the core only ever sees valid data.
- Prefer a well-structured [modular monolith](../architecture/10-modular-monolith.md)
  until scale or team boundaries force distribution. Distributed systems trade a
  function call for a network call — and all the failure that comes with it.

## Examples

**Good Example** — service depends on an interface it owns; DB is a swappable detail

```ts
// domain / application layer — no ORM, no HTTP imports
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
}

class PlaceOrder {
  constructor(private readonly orders: OrderRepository) {} // depends on abstraction

  async execute(cmd: PlaceOrderCommand): Promise<OrderId> {
    const order = Order.create(cmd.items); // business rules live in the domain
    await this.orders.save(order);         // storage is a detail behind the port
    return order.id;
  }
}
// The Postgres implementation lives in the infrastructure layer and is injected in.
```

**Bad Example** — business logic welded to the framework and the database

```ts
// controller doing everything: transport + rules + SQL in one place
app.post("/orders", async (req, res) => {
  if (req.body.items.length === 0)                 // validation mixed with transport
    return res.status(400).send("no items");
  const total = req.body.items                     // business rule stranded in a route
    .reduce((s, i) => s + i.price * i.qty, 0);
  await db.query(                                  // SQL hard-wired into the handler
    "INSERT INTO orders(total) VALUES($1)", [total]
  );
  res.send("ok"); // no domain object, no reuse, untestable without HTTP + a live DB
});
```

## Common Mistakes

- Putting business logic in controllers or in the ORM model, so it cannot be reused or
  tested without the framework and a database.
- Pointing dependencies the wrong way: the domain importing the repository's concrete
  Postgres class instead of an interface.
- Adopting microservices, event sourcing, or CQRS before the domain is understood,
  paying large operational cost for no benefit.
- Confusing folder structure with architecture. Renaming directories does nothing if
  dependencies still point in every direction.
- One "God" service or util module that everything imports, recreating the big ball of
  mud inside a tidy-looking tree.

## Production Tips

- Enforce boundaries mechanically, not by convention: use module/package visibility,
  lint rules (e.g. import boundaries), or separate build targets so a forbidden import
  fails CI, not a code review.
- Record significant structural choices as short
  [architecture decision records](../architecture/26-architecture-decision-records.md);
  the reasoning is what future maintainers actually need.
- Revisit the architecture when a class of change keeps being painful — recurring pain
  is the signal that the structure no longer fits the problem.

## AI Review Checklist

- Do all cross-boundary dependencies point inward, toward stable domain code?
- Is business logic free of framework, HTTP, and database imports?
- Are external systems hidden behind interfaces the codebase owns?
- Are controllers thin — parse, delegate to one use case, map the response?
- Is the chosen pattern the simplest that fits, with the extra complexity justified?
- Is a distributed design justified by real scale or team constraints, not fashion?

## Related

- `knowledge/backend/00-overview.md`
- `knowledge/backend/02-layered-architecture.md`
- `knowledge/backend/03-clean-architecture.md`
- `knowledge/backend/04-hexagonal-architecture.md`
- `knowledge/backend/05-ddd.md`
