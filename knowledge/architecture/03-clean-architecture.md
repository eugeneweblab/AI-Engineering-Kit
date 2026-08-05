---
id: architecture/03-clean-architecture
topic: architecture
slug: clean-architecture
title: "Architecture Clean Architecture"
type: doc
order: 3
status: ready
tags: [architecture, clean-architecture]
related: [architecture/04-hexagonal-architecture, architecture/05-layered-architecture, architecture/06-domain-driven-design, architecture/01-software-architecture, architecture/100-common-antipatterns]
when_to_use: "Read before structuring a service whose business rules must outlive its framework, database, or delivery mechanism."
---
# Architecture Clean Architecture

## Purpose

This document defines Clean Architecture: organizing code as concentric layers where all
dependencies point inward toward business rules, and outer details (frameworks, databases,
UIs) are plugged in at the edges. It is written so an agent can build a service whose core
logic is independent of, and testable without, any framework or I/O.

Clean Architecture is one expression of the same idea as
[hexagonal](04-hexagonal-architecture.md) and onion architecture: protect the domain by
inverting dependencies. Use this doc for the layered-circles formulation.

## Why It Matters

Frameworks, databases, and UI libraries change on someone else's schedule; your business
rules are the thing you actually own. When core logic imports the ORM and the web
framework, every framework upgrade or database swap becomes a rewrite of the logic, and the
logic can only be tested by booting the whole stack. Clean Architecture makes the framework
a plugin: the core has no idea it exists, so it can be tested in milliseconds and survive
the details being replaced. The cost is more interfaces and mapping code — worth it exactly
when the business rules are valuable and long-lived.

## Core Principles

- **The Dependency Rule.** Source-code dependencies point only inward. An inner layer never
  names an outer one. Nothing in the domain imports a controller, repository implementation,
  or framework type.
- **Four conceptual layers, inside to outside:** Entities (enterprise rules) → Use Cases
  (application rules) → Interface Adapters (controllers, presenters, gateways) →
  Frameworks & Drivers (web, DB, external services). Volatility increases outward.
- **Cross boundaries through interfaces owned by the inner layer.** When a use case needs to
  save data, it depends on a `Repository` interface it defines; the database adapter
  implements it. This inverts the dependency so the DB depends on the core, not vice versa.
- **Entities and use cases contain no I/O.** No SQL, no HTTP, no file access, no framework
  annotations in the inner layers. If it touches the outside world, it belongs in an adapter.
- **Data crosses boundaries as simple structures.** Pass plain DTOs across layers, not ORM
  entities or framework request objects, so the inner layers stay ignorant of outer types.

## Best Practices

- Define ports (interfaces) in the use-case layer for every external dependency — data
  store, message bus, clock, email. The core states *what* it needs; adapters decide *how*.
  The benefit is a core testable with in-memory fakes; the cost is mapping code at the edge.
- Keep the dependency-injection wiring in one outer composition root (main/bootstrap). The
  core must never construct its own adapters, or the inward-only rule is broken.
- Map explicitly between layer models: request DTO → use-case input → entity → persistence
  model. Sharing one model across all layers re-couples them and defeats the whole design.
- Put validation of invariants in entities and orchestration in use cases. A use case should
  read like the business process, delegating rules to entities and I/O to ports.
- Apply the full structure only where the domain warrants it. For a CRUD-only service with
  no real rules, this ceremony is overhead — a thin [layered](05-layered-architecture.md)
  design is honest and cheaper.

## Examples

**Good Example** — use case depends on a port it owns

```ts
// core/ports.ts  (inner layer defines the interface)
export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
}

// core/place-order.ts  (use case: no DB, no HTTP, no framework)
export class PlaceOrder {
  constructor(private orders: OrderRepository) {} // inward dependency, injected
  async run(input: PlaceOrderInput): Promise<OrderId> {
    const order = Order.create(input.items); // entity enforces invariants
    await this.orders.save(order);           // persistence via the port
    return order.id;
  }
}

// infra/postgres-order-repo.ts  (outer layer implements the port → depends inward)
export class PostgresOrderRepository implements OrderRepository { /* SQL here */ }
```

**Bad Example** — use case reaches out to the framework and DB

```ts
import { db } from "../infra/knex";        // core now depends on a detail (DB driver)
import { Request } from "express";         // and on the web framework

export async function placeOrder(req: Request) {
  // Business logic tangled with transport parsing and raw SQL. Cannot be unit-tested
  // without a live database and an HTTP request; swapping either forces a rewrite here.
  const items = req.body.items;
  const [id] = await db("orders").insert({ items: JSON.stringify(items) }).returning("id");
  return id;
}
```

## Common Mistakes

- Pointing a dependency outward — the domain importing a repository *implementation* or a
  framework type — which quietly destroys the core's independence.
- Passing ORM entities or framework request/response objects through every layer, so the
  "clean" core is welded to the persistence and web libraries anyway.
- Anemic use cases that only forward calls, with the real logic sitting in controllers or
  the database — the layers exist on disk but not in behavior.
- Applying the four layers to a trivial CRUD app, producing more mapping code than domain.
- One shared model class used as entity, DTO, and DB row, coupling everything it touches.

## Production Tips

- Enforce the Dependency Rule in CI with import-boundary linting so an inward layer
  importing an outer package fails the build, not review.
- Because the core has no I/O, its unit tests need no database or network — keep that suite
  fast and run it on every change; it is the payoff for the structure.

## AI Review Checklist

- Do all source dependencies point inward, with no framework/DB imports in the core?
- Are external dependencies expressed as ports (interfaces) defined by the inner layer?
- Are entities and use cases free of SQL, HTTP, and framework annotations?
- Is data mapped between layer-specific models rather than sharing one object?
- Is all adapter wiring confined to a single outer composition root?
- Is the ceremony proportional to real domain complexity, not applied to plain CRUD?

## Related

- `knowledge/architecture/04-hexagonal-architecture.md`
- `knowledge/architecture/05-layered-architecture.md`
- `knowledge/architecture/06-domain-driven-design.md`
- `knowledge/architecture/01-software-architecture.md`
- `knowledge/architecture/100-common-antipatterns.md`
