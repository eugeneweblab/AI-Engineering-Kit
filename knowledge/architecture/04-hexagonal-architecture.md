---
id: architecture/04-hexagonal-architecture
topic: architecture
slug: hexagonal-architecture
title: "Architecture Hexagonal Architecture"
type: doc
order: 4
status: ready
tags: [architecture, hexagonal-architecture]
related: [architecture/03-clean-architecture, architecture/05-layered-architecture, architecture/06-domain-driven-design, architecture/12-integration-patterns, architecture/01-software-architecture]
when_to_use: "Read before building a service that must be driven by multiple inputs (HTTP, CLI, queue) or swap infrastructure without touching business logic."
---
# Architecture Hexagonal Architecture

## Purpose

This document defines Hexagonal Architecture (Ports and Adapters): the application core is
surrounded by *ports* (interfaces) it owns, and *adapters* connect those ports to the
outside world. It is written so an agent can build a core that is driven identically by
HTTP, a CLI, a test, or a message queue — and can swap any piece of infrastructure without
editing business logic.

It is the same dependency-inversion idea as [clean architecture](03-clean-architecture.md),
framed around the port/adapter boundary rather than concentric circles. Use this doc when
the emphasis is on multiple interchangeable drivers and infrastructure.

## Why It Matters

Most bugs and rewrites come from business logic being entangled with the mechanism that
invoked it or the infrastructure it called. Tie an order-placement rule to an HTTP handler
and you cannot reuse it from a batch job; tie it to a specific database client and you
cannot test it without that database. Hexagonal architecture makes the core indifferent to
what drives it and what it drives, so the same logic serves every entry point and every
adapter is replaceable — including by an in-memory fake in tests. The cost is defining and
maintaining the interfaces; the payoff is reuse, testability, and cheap infrastructure swaps.

## Core Principles

- **The core owns the ports.** Interfaces are defined *inside* the application, in its
  vocabulary. Adapters depend on the core, never the reverse. This is the dependency
  inversion that keeps the core pure.
- **Two kinds of ports.** *Driving* (primary) ports are how the outside calls the app — the
  application's API. *Driven* (secondary) ports are how the app calls the outside — database,
  email, payment gateway. Drivers call in through the left; the app calls out through the right.
- **Adapters are thin and replaceable.** An adapter only translates between an external
  protocol and a port. All business meaning lives in the core; an adapter with logic in it is
  a leak.
- **The core has no outward imports.** No web framework, ORM, SDK, or transport type appears
  in the core. If the domain imports it, it belongs on the far side of a port.
- **One port, many adapters.** The same driving port is exercised by an HTTP controller, a
  CLI, and a test harness; the same driven port is backed by Postgres in prod and an
  in-memory map in tests. Interchangeability is the whole point.

## Best Practices

- Model every external interaction as a port named in domain terms (`PaymentGateway`,
  `NotificationSender`), not in technology terms (`StripeClient`). The name should survive a
  vendor change; the cost of leaking the vendor into the name is a rename across the codebase.
- Keep the transport-to-port mapping (parse request, call port, format response) as the
  adapter's *only* job. Logic that creeps into a controller is untestable without that
  transport and unreusable from other drivers.
- Inject driven-port implementations from a composition root; never let the core `new` up an
  adapter, which would invert the dependency and re-couple it to infrastructure.
- Test the core through its driving ports with fake driven-port adapters. This is the fast,
  infrastructure-free test suite that justifies the structure.
- Do not create a port for something with exactly one implementation that will never vary
  and needs no test double — that interface is pure overhead. Ports earn their keep through
  substitution.

## Examples

**Good Example** — one core driven by HTTP and CLI, backed by swappable adapters

```ts
// core: driving port (the app's API) + driven port (what it needs)
export interface RegisterUser { run(email: string): Promise<UserId>; }   // driving port
export interface UserStore { save(u: User): Promise<void>; }             // driven port

export class RegisterUserService implements RegisterUser {
  constructor(private users: UserStore) {}                 // injected driven port
  async run(email: string) {
    const user = User.register(email);                     // pure domain logic
    await this.users.save(user);
    return user.id;
  }
}

// adapters translate only — no business logic here
class HttpAdapter { constructor(private app: RegisterUser) {} /* req → app.run → res */ }
class CliAdapter  { constructor(private app: RegisterUser) {} /* argv → app.run → stdout */ }
class InMemoryUserStore implements UserStore { /* used in tests, no DB needed */ }
```

**Bad Example** — logic trapped in the adapter, core bypassed

```ts
// Registration rules live inside the HTTP handler → cannot be reused by the CLI or a job,
// and cannot be tested without spinning up the web framework and the real database.
app.post("/users", async (req, res) => {
  const email = req.body.email;
  if (!email.includes("@")) return res.status(400).send("bad email"); // rule stranded here
  await pg.query("INSERT INTO users(email) VALUES($1)", [email]);      // DB hard-wired in
  res.status(201).send();
});
```

## Common Mistakes

- Defining ports in the infrastructure layer (or naming them after a vendor), which flips
  the dependency so the core ends up depending on the adapter.
- Fat adapters that carry validation or business rules, making that logic unreachable from
  other drivers and untestable without the transport.
- Letting a framework or SDK type cross into the core (a `Request`, an ORM entity), quietly
  coupling the domain to the detail the port was meant to hide.
- Creating ceremony for a one-adapter, never-changing dependency — indirection with no
  substitution benefit.
- Treating hexagonal and [clean](03-clean-architecture.md)/DDD as different mechanisms and
  layering all three, producing needless indirection.

## Production Tips

- Enforce the "no outward imports in core" rule with import-boundary linting so a stray SDK
  import in the domain fails CI.
- Ship a fake adapter alongside each driven port. It documents the contract and powers the
  fast test suite; keeping the fake and real adapter behavior in sync is the maintenance cost.

## AI Review Checklist

- Are all ports defined inside the core, in domain vocabulary, not named after vendors?
- Do adapters only translate protocols, with zero business logic?
- Is the core free of framework, ORM, and SDK imports?
- Can the same core be driven by HTTP, CLI, and a test through the same driving port?
- Are driven-port implementations injected from a composition root, never constructed in core?
- Does every port earn its keep through real substitution (prod + test, or multiple backends)?

## Related

- `knowledge/architecture/03-clean-architecture.md`
- `knowledge/architecture/05-layered-architecture.md`
- `knowledge/architecture/06-domain-driven-design.md`
- `knowledge/architecture/12-integration-patterns.md`
- `knowledge/architecture/01-software-architecture.md`
