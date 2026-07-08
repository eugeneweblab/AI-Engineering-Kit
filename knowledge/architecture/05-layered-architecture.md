---
id: architecture/05-layered-architecture
topic: architecture
slug: layered-architecture
title: "Layered Architecture"
type: doc
order: 5
status: ready
tags: [architecture, layered-architecture]
related: [architecture/03-clean-architecture, architecture/04-hexagonal-architecture, architecture/10-modular-monolith, architecture/01-software-architecture, architecture/100-common-antipatterns]
when_to_use: "Read before structuring a straightforward service where a simple presentation/logic/data split fits and full clean/hexagonal ceremony would be overkill."
---
# Layered Architecture

## Purpose

This document defines Layered (n-tier) Architecture: organizing code into horizontal layers
— typically Presentation, Application/Business, and Data Access — where each layer depends
only on the one beneath it. It is written so an agent can build a clear, conventional
service without over-engineering, and can recognize when a stricter style is warranted.

Layered architecture is the sensible default for most applications. It is simpler than
[clean](03-clean-architecture.md) or [hexagonal](04-hexagonal-architecture.md) and, kept
honest, gives you most of their benefits at a fraction of the ceremony.

## Why It Matters

The common failure of small and mid-size services is not too little architecture — it is
mud: controllers running SQL, business rules copy-pasted into HTTP handlers, and data
concerns smeared everywhere. Layering fixes this with one cheap, universally understood
rule: separate what the user sees, what the system decides, and how data is stored, and let
dependencies flow one direction. It is easy for any developer or agent to follow, which is
its main virtue. The risk is that layers become anemic pass-throughs or that the rule is
quietly violated — both covered below.

## Core Principles

- **Three layers, one direction of dependency.** Presentation (controllers, views) →
  Application/Business (use cases, domain rules) → Data Access (repositories, ORM). Each
  layer calls only the layer directly below it.
- **Never skip or reverse a layer.** A controller must not run SQL directly, and the data
  layer must never call back up into business logic. Skipping collapses the separation you
  built; reversing creates a cycle that couples everything.
- **Business rules live in the middle layer, not the edges.** The presentation layer parses
  and formats; the data layer reads and writes; decisions belong in between. A rule in a
  controller is trapped and untestable without the transport.
- **Each layer exposes a narrow contract.** Layers communicate through explicit interfaces
  or service methods, not by reaching into each other's internals, so a layer can change
  behind its contract.
- **Layers are logical, not necessarily physical.** They are packages/modules in one
  deployable, not separate services. Do not turn every layer into a network hop — that adds
  latency and failure modes for no gain.

## Best Practices

- Keep controllers thin: validate input, call one application-layer method, map the result
  to a response. The moment a controller branches on business conditions, that logic belongs
  one layer down. The benefit is a controller you can trust at a glance.
- Put all persistence behind a repository/data-access interface so the business layer talks
  to `OrderRepository`, not the ORM. This localizes a database change to one layer; the cost
  is a thin abstraction over the ORM.
- Do not leak ORM entities or SQL into the presentation layer. Return domain objects or DTOs
  so the UI is not coupled to the table schema.
- Enforce the downward-only dependency rule with module-boundary linting; layering that is
  only a convention erodes the first time a deadline hits.
- Choose layering over clean/hexagonal when the app is mostly straightforward request →
  logic → database. Escalate to ports-and-adapters only when you have real need for
  swappable infrastructure or multiple drivers — otherwise the extra interfaces are cost
  without benefit.

## Examples

**Good Example** — thin controller, logic in the service, DB behind a repository

```ts
// presentation layer — parse, delegate, format; no rules, no SQL
router.post("/orders", async (req, res) => {
  const id = await orderService.placeOrder(req.body); // one call down
  res.status(201).json({ id });
});

// application layer — the decision lives here
class OrderService {
  constructor(private orders: OrderRepository) {}       // depends on the layer below
  async placeOrder(input: PlaceOrderInput): Promise<string> {
    if (input.items.length === 0) throw new ValidationError("empty order"); // rule
    return this.orders.insert(input);
  }
}

// data layer — persistence only, never calls back up
class OrderRepository { async insert(o: PlaceOrderInput) { /* SQL here */ } }
```

**Bad Example** — controller skips layers and holds business logic

```ts
router.post("/orders", async (req, res) => {
  // Presentation layer doing validation, business rules, AND raw SQL: the "layers" exist
  // in folders but not in behavior. A pricing change means editing controllers; the logic
  // cannot be reused by a job or tested without an HTTP request and a live database.
  if (req.body.items.length === 0) return res.status(400).send("empty");
  const total = req.body.items.reduce((s, i) => s + i.price, 0);
  await db.query("INSERT INTO orders(total) VALUES($1)", [total]); // skips the data layer
  res.status(201).send();
});
```

## Common Mistakes

- Fat controllers that validate, decide, and query — layers on disk but not in behavior.
- Anemic middle layer whose methods only forward calls, so business logic drifts into the
  presentation or data layer where it does not belong.
- Skipping the data layer to run SQL from a controller "just this once," which becomes the
  pattern the next agent copies.
- Data-layer code calling up into services, creating a dependency cycle that couples every
  layer to every other.
- Turning each layer into a separate deployed service, buying distributed-system cost
  (latency, partial failure) for a problem that a modular deployable would solve.

## Production Tips

- Add an architecture test (import-boundary lint or ArchUnit-style check) asserting the
  downward-only rule, so violations fail CI instead of accumulating.
- If you find yourself needing to swap databases, mock infrastructure heavily, or drive the
  core from several entry points, that is the signal to graduate to
  [hexagonal](04-hexagonal-architecture.md) — not before.

## AI Review Checklist

- Do dependencies flow strictly downward, with no layer skipped or reversed?
- Are controllers thin — parse, delegate, format — with no business rules or SQL?
- Does the business layer hold the decisions, rather than forwarding to the edges?
- Is all persistence behind a data-access interface, with no ORM/SQL in presentation?
- Are the layers logical modules in one deployable, not needless network hops?
- Is layering the right fit here, versus a case that genuinely needs clean/hexagonal?

## Related

- `knowledge/architecture/03-clean-architecture.md`
- `knowledge/architecture/04-hexagonal-architecture.md`
- `knowledge/architecture/10-modular-monolith.md`
- `knowledge/architecture/01-software-architecture.md`
- `knowledge/architecture/100-common-antipatterns.md`
