---
id: backend/04-hexagonal-architecture
topic: backend
slug: hexagonal-architecture
title: "Backend Hexagonal Architecture"
type: doc
order: 4
status: ready
tags: [backend, hexagonal-architecture, OrderRepository, execute, PlaceOrderInput, port, save]
related: [backend/01-backend-architecture, backend/03-clean-architecture, backend/05-ddd, backend/23-testing]
when_to_use: "Read before building a service whose core logic must be driven by many transports or backed by many providers."
---
# Backend Hexagonal Architecture

## Purpose

This document defines Hexagonal Architecture (Ports and Adapters): a structure where a
technology-agnostic application core is surrounded by *ports* (interfaces it defines)
and *adapters* (implementations that connect those ports to the outside world). It tells
an agent how to keep the core independent of how it is invoked and what it talks to.

Hexagonal and [Clean](03-clean-architecture.md) architecture express the same principle
— dependencies point inward, toward the domain — with different vocabulary. Hexagonal
frames it around *I/O direction*: things that drive the app versus things the app
drives. Use this framing when swappable inputs and outputs are the central concern.

## Why It Matters

Most systems are eventually driven by more than one thing — an HTTP API, a CLI, a
message consumer, a test harness — and eventually talk to more than one provider — a
database, a cache, a payment gateway, a mock. If each of those is wired directly into
the logic, adding a second transport or provider means rewriting the core. Ports and
adapters make those the *edges*: the core stays fixed while adapters come and go. The
concrete win is testability — you drive the core through the same port a fake uses — and
the cost is the interface indirection you must maintain.

## Core Principles

- **The core defines the ports; adapters implement them.** The application owns the
  interfaces. External code adapts to the core, never the reverse.
- **Two kinds of ports.** *Driving* (primary) ports are the API the outside world uses
  to invoke the core (use-case interfaces). *Driven* (secondary) ports are the
  interfaces the core uses to reach the outside (repository, notifier, clock).
- **Two kinds of adapters.** *Driving* adapters call the core through a driving port
  (HTTP controller, CLI, queue consumer). *Driven* adapters implement a driven port
  (SQL repository, SMTP mailer, Stripe gateway).
- **The core depends on nothing external.** No framework, ORM, or SDK import crosses
  into the core. All external concepts live in adapters.
- **Symmetry.** Both left (input) and right (output) sides go through ports, so a real
  adapter and a test double are interchangeable at every edge.

## Best Practices

- Define driving ports as use-case interfaces (`PlaceOrderUseCase`) and driven ports as
  capability interfaces (`OrderRepository`, `PaymentGateway`) inside the core.
- Make each adapter thin and single-purpose: an HTTP adapter maps request↔port call; a
  SQL adapter maps port call↔query. Business decisions never live in an adapter.
- Inject driven adapters into the core at the composition root; the core receives
  interfaces, not concrete classes.
- Use in-memory or fake adapters to test the core with zero infrastructure — this is the
  primary reason to adopt the pattern, so exploit it. See [testing](23-testing.md).
- Keep DTOs at the adapter edge and map to/from domain types; do not let a transport or
  persistence shape flow into the core.
- Do not multiply ports speculatively. Add a port when a second adapter (or a test
  double) actually needs it, not "just in case."

## Examples

**Good Example** — core defines both ports; adapters plug in on each side

```ts
// ---- core: driving port (how the world calls in) ----
interface PlaceOrderUseCase {
  execute(input: PlaceOrderInput): Promise<OrderId>;
}
// ---- core: driven port (what the core needs from the world) ----
interface OrderRepository { save(o: Order): Promise<void>; }

// ---- core: implementation, free of HTTP and SQL ----
class PlaceOrder implements PlaceOrderUseCase {
  constructor(private readonly orders: OrderRepository) {} // depends on the port only
  async execute(input: PlaceOrderInput) {
    const order = Order.create(input.items);
    await this.orders.save(order);
    return order.id;
  }
}

// ---- driving adapter: HTTP maps request -> port call ----
router.post("/orders", async (req, res) => {
  const id = await placeOrder.execute(PlaceOrderInput.parse(req.body));
  res.status(201).json({ id });
});
// ---- driven adapter: SQL implements the port. Swap for InMemoryOrderRepository in tests. ----
class SqlOrderRepository implements OrderRepository { /* ...maps to rows... */ }
```

**Bad Example** — the "core" is glued to HTTP and SQL; no ports at all

```ts
class OrderService {
  // takes the framework's request object -> can only ever be driven by HTTP
  async place(req: Request, db: PgPool) {
    const items = req.body.items;                 // transport shape leaks into logic
    const order = Order.create(items);
    await db.query(                               // driven side hard-wired to Postgres
      "INSERT INTO orders(id) VALUES($1)", [order.id]
    ); // cannot test without a real DB; cannot add a CLI or queue without a rewrite
    return order.id;
  }
}
```

## Common Mistakes

- **No real ports** — calling directly into a concrete DB/SDK from the core, so nothing
  is actually swappable and the hexagon is decorative.
- **Ports defined by the adapter** — the interface living in the infrastructure module,
  which points the dependency the wrong way (outward).
- **Fat adapters** — business decisions creeping into a controller or repository instead
  of staying in the core.
- **Transport/persistence types in the core** — passing `req`, `res`, or an ORM entity
  through a port, coupling the core to the edge it was meant to be free of.
- **Over-porting** — an interface for every class, adding indirection with no second
  implementation to justify it.

## Production Tips

- The fastest, most stable tests exercise the core through its driving port with fake
  driven adapters; reserve slow integration tests for the adapters themselves.
- Enforce the boundary with import rules: the core module must not import from any
  adapter/infrastructure module. A violating import should fail CI.
- When a new delivery channel appears (webhook, gRPC, scheduled job), it should be a new
  driving adapter over the *existing* port — if it forces a core change, a boundary has
  leaked.

## AI Review Checklist

- Does the core define its ports, with adapters depending inward on them?
- Are driving ports (use cases) and driven ports (repositories/gateways) both present
  and owned by the core?
- Is the core free of framework, ORM, and SDK imports and of transport types like `req`?
- Are adapters thin, holding mapping only and no business decisions?
- Can the core be exercised with in-memory adapters and no infrastructure?
- Are ports justified by a real second implementation or test double, not speculation?

## Related

- `knowledge/backend/01-backend-architecture.md`
- `knowledge/backend/03-clean-architecture.md`
- `knowledge/backend/05-ddd.md`
- `knowledge/backend/23-testing.md`
