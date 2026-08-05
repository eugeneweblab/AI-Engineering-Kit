---
id: backend/02-layered-architecture
topic: backend
slug: layered-architecture
title: "Backend Layered Architecture"
type: doc
order: 2
status: ready
tags: [backend, layered-architecture]
related: [backend/01-backend-architecture, backend/03-clean-architecture, backend/07-business-logic, backend/18-database-design]
when_to_use: "Read before structuring a typical CRUD service, or when logic is leaking across controller, service, and data layers."
---
# Backend Layered Architecture

## Purpose

This document defines the layered (n-tier) pattern: the default, well-understood way to
structure a server-side application as a stack of layers — presentation, application,
domain, and data — where each layer talks only to the one beneath it. It tells an agent
what belongs in each layer and, just as important, what does not.

Layered architecture is the baseline. Most services should start here and only move to
[clean](03-clean-architecture.md) or [hexagonal](04-hexagonal-architecture.md) when a
concrete pressure demands it.

## Why It Matters

The value of layering is predictability: anyone can guess where a piece of code lives
and what it may depend on. That predictability is worth more than cleverness — it makes
the codebase navigable by new engineers and by agents. The failure mode is subtle: when
a rule leaks up into a controller or down into a repository, the layering still *looks*
intact but no longer *is*, and the benefit quietly evaporates. Enforcing the direction
of calls is the whole job.

## Core Principles

- **Four layers, one direction.** Presentation (controllers) → Application (services)
  → Domain (entities, rules) → Data (repositories). Calls flow downward only.
- **A layer knows only the layer below it.** The controller calls the service; the
  service calls the repository. The repository never calls the service; the domain
  never imports the controller.
- **Each layer has one job.** Presentation translates transport to calls; application
  orchestrates a use case and owns the transaction; domain holds the rules; data
  persists. Do not mix these.
- **Depend downward on interfaces where the layer below is volatile.** In particular,
  the data layer should sit behind a repository interface so it can be tested and
  swapped.
- **No skipping layers.** A controller must not reach straight into the database;
  routing all access through the layer stack is what keeps the rules enforceable.

## Best Practices

- Keep controllers thin: validate/parse the request, call one service method, map the
  result or error to an HTTP response. No business logic here.
- Put orchestration and transaction boundaries in the service (application) layer. A
  service method is usually one use case and one transaction.
- Keep entities and invariants in the domain layer, with no framework or ORM imports,
  so rules are unit-testable in isolation.
- Access the database only through repositories that return domain objects, not raw
  rows or ORM entities leaking upward.
- Do not let a lower layer return a higher layer's type (e.g. a repository returning an
  HTTP DTO). Map at the boundary instead.
- If two services need to call each other, that logic usually belongs one layer down in
  the domain; sideways calls within a layer are a smell.

## Examples

**Good Example** — each layer does its one job, calls flow down

```ts
// Presentation: transport only
router.post("/users", async (req, res) => {
  const dto = CreateUserDto.parse(req.body);        // validate input at the edge
  const user = await userService.register(dto);     // delegate to one use case
  res.status(201).json(toUserResponse(user));       // map domain -> response
});

// Application: orchestration + transaction, no SQL, no HTTP
class UserService {
  constructor(private users: UserRepository) {}
  async register(dto: CreateUserDto): Promise<User> {
    if (await this.users.existsByEmail(dto.email))  // use-case rule
      throw new ConflictError("email already registered");
    const user = User.create(dto.email, dto.name);  // domain enforces its invariants
    await this.users.save(user);                    // persistence via the port below
    return user;
  }
}
```

**Bad Example** — layers collapsed; controller reaches the DB and holds the rules

```ts
router.post("/users", async (req, res) => {
  // presentation doing application + domain + data all at once
  const exists = await db.query(                    // controller skips the layers
    "SELECT 1 FROM users WHERE email=$1", [req.body.email]
  );
  if (exists.rowCount) return res.status(409).send("taken");
  if (!req.body.email.includes("@"))                // business rule stranded up top
    return res.status(400).send("bad email");
  await db.query(
    "INSERT INTO users(email,name) VALUES($1,$2)",
    [req.body.email, req.body.name]
  ); // no domain object, no service, no reuse — untestable without HTTP + DB
  res.status(201).send("ok");
});
```

## Common Mistakes

- **Anemic controllers that aren't** — routes that quietly grow business logic instead
  of delegating to a service.
- **Fat services, empty domain** — all logic in the service layer and none in entities,
  so the domain layer is just data bags. Rules that belong to an entity should live on
  it.
- **Skipping layers** — a controller or service issuing raw queries, bypassing the
  repository and its interface.
- **Leaky returns** — repositories returning ORM entities or DTOs, coupling upper
  layers to the persistence framework.
- **Upward dependencies** — a lower layer importing a higher one, breaking the
  one-directional rule and creating a cycle.

## Production Tips

- Enforce the call direction with lint/import-boundary rules so an upward or
  layer-skipping import fails CI rather than relying on reviewer vigilance.
- Layered ≠ slow. If N+1 queries appear because the domain layer hides the data shape,
  add a purpose-built read query in the data layer rather than abandoning the pattern.
- When the application layer starts to bloat with I/O concerns (queues, external APIs),
  that is the signal to graduate to [clean](03-clean-architecture.md) or
  [hexagonal](04-hexagonal-architecture.md), which invert those dependencies explicitly.

## AI Review Checklist

- Do calls flow strictly downward (presentation → application → domain → data)?
- Are controllers free of business logic and direct database access?
- Do repositories return domain objects, not ORM entities or DTOs?
- Are transaction boundaries owned by the application layer, one per use case?
- Does any lower layer import a higher one, creating an upward dependency or cycle?
- Are entity invariants enforced in the domain, not scattered across services?

## Related

- `knowledge/backend/01-backend-architecture.md`
- `knowledge/backend/03-clean-architecture.md`
- `knowledge/backend/07-business-logic.md`
- `knowledge/backend/18-database-design.md`
