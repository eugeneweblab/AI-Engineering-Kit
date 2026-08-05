---
id: backend/03-clean-architecture
topic: backend
slug: clean-architecture
title: "Backend Clean Architecture"
type: doc
order: 3
status: ready
tags: [backend, clean-architecture, save, PlaceOrder, OrderRepository, execute, SqlOrderRepository, PlaceOrderInput]
related: [backend/01-backend-architecture, backend/02-layered-architecture, backend/04-hexagonal-architecture, backend/05-ddd]
when_to_use: "Read before structuring a service whose business rules are complex and must outlast its framework or database."
---
# Backend Clean Architecture

## Purpose

This document defines Clean Architecture: a way to structure a system as concentric
circles where all source-code dependencies point *inward*, toward the business rules,
and never outward toward frameworks, databases, or UI. It tells an agent how to keep
the domain independent of the tools that deliver and persist it.

Clean Architecture is [layered architecture](02-layered-architecture.md) with the
dependency between the application and the database *inverted*. It shares its goal —
and most of its mechanics — with [hexagonal architecture](04-hexagonal-architecture.md);
treat them as two framings of the same principle.

## Why It Matters

In a naive layered app, the business logic depends on the database: change the ORM and
the domain breaks. Clean Architecture flips that so the database depends on the domain
instead. The payoff is that the most valuable, hardest-to-rewrite code — the rules —
has zero knowledge of Postgres, HTTP, or React, and can be tested in milliseconds with
no infrastructure. The cost is real: more interfaces, more mapping, more indirection.
That cost is worth paying when the rules are complex and long-lived, and wasteful when
the app is a thin CRUD wrapper over a table.

## Core Principles

- **The Dependency Rule.** Source dependencies point only inward. An inner circle knows
  nothing about an outer one. Names, types, and functions from an outer circle must not
  appear in inner-circle code.
- **Four circles, inner to outer.** Entities (enterprise rules) → Use Cases
  (application rules) → Interface Adapters (controllers, presenters, gateways) →
  Frameworks & Drivers (web, DB, devices).
- **Cross boundaries with interfaces the inner circle owns.** A use case defines the
  `Repository` interface it needs; the outer database layer *implements* it. Dependency
  is inverted at the boundary.
- **Data crosses as simple structures.** Pass DTOs or plain objects across boundaries,
  not ORM entities or framework request objects. Nothing from an outer ring leaks in.
- **The framework is a detail.** Web framework, database, and message broker are plugins
  to the application, not its foundation. You should be able to swap them without
  touching a use case.

## Best Practices

- Define one class/function per use case (`PlaceOrder`, `RegisterUser`) in the
  application ring. It orchestrates entities and calls outward-facing interfaces.
- Declare the ports (repository, gateway, notifier interfaces) *inside* the use-case or
  domain ring; implement them in the outer infrastructure ring and inject them in.
- Keep entities framework-free and behavior-rich: they hold invariants, not just data.
  See [domain modeling](08-domain-modeling.md) and [DDD](05-ddd.md).
- Map explicitly at each boundary: request DTO → use-case input, domain object →
  response model. Do not let one representation serve all layers.
- Wire concrete implementations to interfaces only at the composition root (startup /
  DI container) — the one place allowed to know every concrete class.
- Do not adopt Clean Architecture wholesale for a simple service. Its indirection is a
  liability when there are no complex rules to protect.

## Examples

**Good Example** — use case owns the port; the database implements it (inverted)

```ts
// ---- inner ring: application. Knows no framework, no SQL. ----
interface OrderRepository {                 // port declared by the use case
  save(order: Order): Promise<void>;
}
class PlaceOrder {
  constructor(private readonly orders: OrderRepository) {}
  async execute(input: PlaceOrderInput): Promise<OrderId> {
    const order = Order.create(input.items); // entity enforces its own invariants
    await this.orders.save(order);           // depends inward-only, on the interface
    return order.id;
  }
}

// ---- outer ring: infrastructure. Depends inward on the interface above. ----
class SqlOrderRepository implements OrderRepository {
  constructor(private readonly db: DbClient) {}
  async save(order: Order): Promise<void> {
    await this.db.orders.insert(toRow(order)); // maps domain -> row at the boundary
  }
}
// composition root wires SqlOrderRepository into PlaceOrder — the only place that knows both.
```

**Bad Example** — dependency points outward; the use case imports the ORM

```ts
import { OrderModel } from "../infra/orm"; // inner ring reaching OUTWARD — violation

class PlaceOrder {
  async execute(input: PlaceOrderInput) {
    // business rule now coupled to the ORM; swapping the DB rewrites the use case,
    // and testing this requires a real database connection.
    const order = await OrderModel.create({ items: input.items });
    if (order.items.length > 50) order.flag = "bulk"; // rule stranded on an ORM entity
    await order.save();
    return order.id;
  }
}
```

## Common Mistakes

- **Dependency Rule violations** — an entity or use case importing anything from the
  web, ORM, or driver ring. This is the one rule that defines the pattern; breaking it
  means you do not have Clean Architecture, only extra folders.
- **Leaking ORM/request objects inward** — passing a framework's entity or `req` into a
  use case instead of a plain input DTO.
- **Ports declared in the wrong ring** — putting the repository interface next to its
  SQL implementation, so the dependency is not actually inverted.
- **Ceremony without payoff** — applying all four rings to a CRUD app, drowning simple
  logic in mapping and interfaces.
- **Anemic entities** — rules living in use cases while entities are data bags; the
  innermost, most reusable ring ends up empty.

## Production Tips

- Enforce the Dependency Rule with import-boundary lint rules or separate build modules
  per ring; a violating import should fail CI.
- Because the domain is infrastructure-free, its unit tests need no database or HTTP —
  keep them fast and make them the bulk of the suite.
- Reserve integration tests for the adapter ring, where the real DB and framework live.

## AI Review Checklist

- Do all source dependencies point inward, toward entities and use cases?
- Are entities and use cases free of framework, ORM, and HTTP imports?
- Are ports (repository/gateway interfaces) declared in the inner ring and implemented
  in the outer ring?
- Does data cross boundaries as DTOs/plain objects, never as ORM or request types?
- Is concrete wiring confined to a single composition root?
- Is this level of indirection justified by genuinely complex, long-lived rules?

## Related

- `knowledge/backend/01-backend-architecture.md`
- `knowledge/backend/02-layered-architecture.md`
- `knowledge/backend/04-hexagonal-architecture.md`
- `knowledge/backend/05-ddd.md`
