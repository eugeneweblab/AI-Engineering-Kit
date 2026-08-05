---
id: architecture/10-modular-monolith
topic: architecture
slug: modular-monolith
title: "Modular Monolith"
type: doc
order: 10
status: ready
tags: [architecture, modular-monolith, handle, PlaceOrderHandler, OrderPlaced, PlaceOrder, publish, EventBus]
related: [architecture/09-microservices, architecture/06-domain-driven-design, architecture/03-clean-architecture, architecture/05-layered-architecture, architecture/08-event-driven-architecture]
when_to_use: "Read before starting a new system, or when tempted to reach for microservices without a proven scaling or team-autonomy driver."
---
# Modular Monolith

## Purpose

This document defines the modular monolith: a single deployable application internally
divided into well-bounded, loosely coupled modules that communicate only through explicit
interfaces. It is the pragmatic default for most systems — it captures the design
discipline of [microservices](09-microservices.md) without the distributed-systems tax.

Each module is a [bounded context](06-domain-driven-design.md) with its own domain, data,
and public API, but they run in one process and share one deployment. This doc covers how
to keep modules genuinely independent so the monolith stays maintainable and, if ever
needed, a module can be extracted into a service cleanly.

## Why It Matters

The choice most teams get wrong is monolith vs. microservices, and they usually jump to
microservices too early — paying for network calls, eventual consistency, and distributed
debugging before they have any team or scaling problem those solve. A modular monolith
gives you the thing that actually matters — clear boundaries and independent modules —
while keeping in-process calls, ACID transactions, and one thing to deploy and debug. The
risk it must guard against is degrading into a *big ball of mud*: with no enforced
boundaries, modules quietly reach into each other until the monolith is one tangled unit
that must always ship together.

## Core Principles

- **Modules own their data.** A module's tables are private; other modules reach them only
  through its public API. Shared tables are the fastest route to an unmaintainable tangle.
- **Communicate through explicit interfaces.** A module exposes a small public surface and
  hides everything else. No importing another module's internal classes.
- **Depend on abstractions across boundaries.** Cross-module calls go through an interface,
  so a module can be replaced or later extracted without rewriting its callers.
- **Prefer in-process events for decoupling.** When a module reacts to another's fact, use
  an in-process [domain event](08-event-driven-architecture.md) rather than a direct call.
- **Keep one transaction per module.** Even in one process, do not span a single business
  transaction across two modules' data — that coupling blocks future extraction.
- **Boundaries are the product.** The discipline that makes a monolith modular is exactly
  what makes microservices possible later. Get it right in-process first, where it is cheap.

## Best Practices

- Enforce module boundaries with tooling (package/namespace visibility, ArchUnit-style
  tests, dependency-cruiser, lint import rules), because a boundary that is only a
  convention will be violated the first time someone is in a hurry.
- Give each module its own schema or table prefix and forbid cross-schema joins; this keeps
  data ownership real and makes later extraction mechanical rather than surgical.
- Expose each module through a single public entry point (a facade/API) and mark
  everything else internal/private.
- Use in-process event dispatch for cross-module reactions so modules do not hold direct
  references to each other.
- Keep the option open: design cross-module contracts as if the call *might* someday cross
  the network (serializable payloads, no shared mutable objects), so extraction to a
  [service](09-microservices.md) is a deployment change, not a redesign.
- Split modules by business capability, mirroring how you would split services.

## Examples

**Good Example** — modules talk through a public interface and events

```ts
// Billing module exposes a narrow public port. Its internals stay private.
export interface BillingApi {
  chargeForOrder(orderId: string, amountCents: number): Promise<PaymentResult>;
}

// Orders depends on the INTERFACE, not on Billing's internals. This call could later
// become a network call with no change to Orders' logic.
class PlaceOrderHandler {
  constructor(private billing: BillingApi, private events: EventBus) {}

  async handle(cmd: PlaceOrder) {
    const order = await this.orders.save(Order.create(cmd)); // Orders owns Orders data
    await this.billing.chargeForOrder(order.id, order.totalCents);
    this.events.publish(new OrderPlaced(order.id)); // Shipping reacts in its own module
  }
}
```

**Bad Example** — modules share tables and reach into internals

```ts
class PlaceOrderHandler {
  async handle(cmd: PlaceOrder) {
    const order = await this.db.orders.insert(cmd);

    // Reaching directly into Billing's table and its internal class → boundary erased.
    // Now Orders cannot compile without Billing's internals, and neither can move.
    await this.db.billing_invoices.insert({ orderId: order.id, ... });
    new BillingInternalCalculator().recomputeLedger(order.id);
    // One transaction now spans two modules' data: they must forever deploy together.
  }
}
```

## Common Mistakes

- **Big ball of mud**: no enforced boundaries, so modules import each other's internals
  freely and the "modular" monolith is modular in name only.
- Shared database tables across modules, destroying data ownership.
- Cross-module calls into concrete internal classes instead of a published interface.
- One business transaction spanning multiple modules' data, welding them together.
- Splitting by technical layer (controllers/services/repos as "modules") instead of by
  business capability.
- Jumping to microservices before proving the boundaries hold in-process.

## Production Tips

- Add an architecture test to CI that fails the build on illegal cross-module imports;
  make boundary erosion impossible to merge, not merely discouraged.
- Track per-module ownership (CODEOWNERS) so a module has a clear team, mirroring the
  autonomy microservices would give without the deployment split.
- When a module genuinely needs independent scaling or a dedicated team, extract just that
  one into a service — the clean boundary makes it a contained change.

## AI Review Checklist

- Does each module own its data, with no cross-module table access or joins?
- Do cross-module calls go through a published interface, not internal classes?
- Are boundaries enforced by tooling/tests, not just convention?
- Is each business transaction confined to a single module's data?
- Are cross-module reactions done via in-process events where appropriate?
- Are modules split by business capability rather than technical layer?
- Could a module be extracted to a service without a redesign of its callers?

## Related

- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/06-domain-driven-design.md`
- `knowledge/architecture/03-clean-architecture.md`
- `knowledge/architecture/05-layered-architecture.md`
- `knowledge/architecture/08-event-driven-architecture.md`
