---
id: backend/07-business-logic
topic: backend
slug: business-logic
title: "Business Logic"
type: doc
order: 7
status: ready
tags: [backend, business-logic, load, OrderRepo, send, save, object]
related: [backend/08-domain-modeling, backend/03-clean-architecture, backend/17-transactions, backend/09-validation, backend/06-api-design]
when_to_use: "Read before writing or reviewing any code that enforces a business rule, workflow, or use case."
---
# Business Logic

## Purpose

This document defines where the *rules of the business* live and how to keep them
correct: use cases, invariants, workflows, and the decisions that make the software
worth money. It is written so an agent can implement a rule in the right place, testable
and isolated from frameworks and I/O.

Business logic is the answer to "what is this system actually for?". Everything else —
HTTP, the database, the message queue — is plumbing that carries data to and from these
decisions.

## Why It Matters

Business rules are the part of the codebase most likely to change and most expensive to
get wrong: a mispriced order or a skipped approval step costs real money and trust. When
that logic is smeared across controllers, ORM callbacks, and SQL triggers, no one can
find it, test it, or reason about it. Concentrating it in a plain, framework-free layer
is what keeps the system understandable as it grows and requirements shift.

## Core Principles

- **Keep business logic pure and framework-free.** A use case should not import the web
  framework, the ORM, or the HTTP request. It takes plain inputs and returns plain
  results, so it is testable without a server or database — the cost is an interface at
  the I/O boundary, the payoff is fast tests and portability.
- **One use case = one responsibility.** Each operation ("place order", "cancel
  subscription") is an explicit unit with a clear pre- and post-condition.
- **Push I/O to the edges.** Fetch data before the decision, persist after it. The
  decision itself is a pure function over already-loaded state.
- **Enforce invariants in one place.** A rule ("an order over its credit limit is
  rejected") must be checked in the domain, not duplicated in the UI and three endpoints.
- **Make illegal states unrepresentable.** Prefer types and constructors that cannot hold
  invalid data over runtime checks scattered after the fact. See
  [domain modeling](08-domain-modeling.md).

## Best Practices

- Structure each operation as a use-case/service function that orchestrates: load →
  decide → persist → emit events. Keep the "decide" step pure.
- Depend on abstractions (repository interfaces), not concrete infrastructure, so logic
  is independent of the database. See [clean architecture](03-clean-architecture.md).
- Distinguish **validation** (is this input well-formed?) from **business rules** (is this
  allowed given current state?). Input shape is checked at the boundary; rules live in the
  domain. See [validation](09-validation.md).
- Wrap multi-step state changes in a transaction so a partial failure cannot leave broken
  invariants. See [transactions](17-transactions.md).
- Return rich, typed results (success / typed failure), not booleans or thrown strings, so
  callers can react to each outcome.
- Keep controllers thin: parse input, call the use case, map the result to a response.
  No business rules in controllers.

## Examples

**Good Example** — pure decision, I/O at the edges, single invariant

```ts
interface OrderRepo { load(id: string): Promise<Order>; save(o: Order): Promise<void>; }

// Use case orchestrates I/O; the RULE lives on the domain object (order.approve).
async function approveOrder(repo: OrderRepo, id: string): Promise<Result<Order>> {
  const order = await repo.load(id);          // I/O first
  const decision = order.approve();           // pure decision, no I/O, easily unit-tested
  if (!decision.ok) return decision;          // typed failure, caller can branch
  await repo.save(decision.value);            // I/O last
  return decision;
}

class Order {
  approve(): Result<Order> {
    if (this.status !== "pending")            // invariant enforced in ONE place
      return err("ORDER_NOT_PENDING");
    return ok(new Order({ ...this, status: "approved" }));
  }
}
```

**Bad Example** — rules in the controller, tangled with I/O

```ts
app.post("/orders/:id/approve", async (req, res) => {
  const order = await db.query("SELECT * FROM orders WHERE id=$1", [req.params.id]);
  if (order.status !== "pending")            // rule buried in HTTP layer, untestable
    return res.status(400).send("nope");     // and duplicated in every other endpoint
  order.status = "approved";
  await db.query("UPDATE orders SET status='approved' WHERE id=$1", [order.id]);
  await email.send(order.userEmail, "approved"); // side effect inside the request, no txn
  res.json(order);                           // no transaction: crash leaves half-done state
});
```

## Common Mistakes

- Business rules living in controllers, ORM hooks, or database triggers where they can't
  be found or unit-tested.
- Mixing I/O into the decision so the logic can only be tested with a live database.
- Duplicating the same invariant in the UI and multiple endpoints; they drift apart.
- Anemic services that are just pass-throughs to the ORM, with rules leaking elsewhere.
- Multi-step changes without a transaction, leaving invariants broken on partial failure.
- Confusing input validation with business rules and putting both in the same soup.

## Production Tips

- Unit-test use cases with in-memory repositories; they should run in milliseconds with
  no external dependencies.
- Emit a domain event after a successful state change rather than calling side effects
  inline, so the core stays pure. See [events](14-events.md).
- Track key rule outcomes (rejections, overrides) as metrics — they are business signal,
  not just logs.

## AI Review Checklist

- Is the core decision a pure function, free of framework, HTTP, and ORM imports?
- Is each invariant enforced in exactly one place in the domain?
- Are controllers thin — parse, call use case, map result — with no business rules?
- Is I/O pushed to the edges (load before, persist after the decision)?
- Are multi-step state changes wrapped in a transaction?
- Are outcomes returned as typed results rather than booleans or thrown strings?
- Is input validation kept separate from business-rule enforcement?

## Related

- `knowledge/backend/08-domain-modeling.md`
- `knowledge/backend/03-clean-architecture.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/09-validation.md`
- `knowledge/backend/06-api-design.md`
