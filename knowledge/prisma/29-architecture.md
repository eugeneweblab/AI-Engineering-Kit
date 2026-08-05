---
id: prisma/29-architecture
topic: prisma
slug: architecture
title: "Prisma Architecture"
type: doc
order: 29
status: ready
tags: [prisma, architecture, byId, UserRepository, findUnique, PrismaClient, constructor, toUser]
related: [prisma/28-patterns, prisma/06-client, prisma/22-multi-tenancy, prisma/19-testing, prisma/24-best-practices]
when_to_use: "Read when deciding where Prisma sits in an application's layers — repositories, services, dependency boundaries — before building a new module."
---
# Prisma Architecture

## Purpose

This document defines where Prisma belongs in an application's structure: which layer
owns it, how domain and service code reach the database without being coupled to Prisma,
and how the data layer stays testable and swappable. It is about boundaries and
dependency direction, not query syntax (see [best practices](24-best-practices.md)).

## Why It Matters

Prisma is easy to sprinkle everywhere — a `prisma.user.findMany` in a controller, another
in a React server component, a third in a background job. That coupling is invisible until
you need to change it: add tenant scoping, swap the client for a mock in a test, enforce
soft delete, or move a query behind a cache. When Prisma calls are scattered across every
layer, each of those changes becomes a codebase-wide edit. Confining Prisma to a data
layer turns those from migrations into single-file changes, and lets business logic be
tested without a database.

## Core Principles

- **Prisma lives in one layer.** The data-access layer (repositories / data mappers) owns
  the client. Controllers, use cases, and UI never call Prisma directly.
- **Depend on interfaces, not the client.** Business logic depends on a repository
  interface it defines; the Prisma implementation satisfies it. Dependencies point inward.
- **Inject the client, do not import a global.** Pass `PrismaClient` (or a repository) in,
  so tests and transactions can substitute it.
- **Return domain types, not raw entities.** Map at the boundary so the rest of the app is
  not shaped by Prisma's generated types or its column set.
- **One place enforces cross-cutting rules.** Tenant scope, soft delete, and audit fields
  are enforced in the data layer (via extensions), not re-checked in every caller.

## Best Practices

- Put all Prisma calls behind repositories or a data-access module; ban `@prisma/client`
  imports in controllers, route handlers, and domain code via a lint rule.
- Define repository interfaces in the domain/service layer and implement them with Prisma
  in the infrastructure layer, so the dependency arrow points away from Prisma.
- Inject the client through a constructor or DI container; the singleton is created once
  (see [client](06-client.md)) and handed to repositories, never imported ad hoc.
- Map Prisma results to domain objects/DTOs at the repository boundary; strip internal
  columns there so no layer above sees `passwordHash` or tenant keys.
- Expose transaction scope through the repository: accept a `TransactionClient` so a use
  case can span repositories atomically (see [patterns](28-patterns.md)).
- Keep the schema and migrations in the infrastructure layer; the domain must not import
  generated types as its core model on large systems — map instead.
- For serverless/edge or multiple runtimes, isolate the client construction so runtime
  differences (pooling, adapters) live in one module.

## Examples

**Good Example** — domain-owned interface, Prisma implementation, injected client

```ts
// domain/user-repository.ts — the domain owns the contract; no Prisma here
export interface UserRepository {
  byId(id: string): Promise<User | null>; // returns a domain type, not a Prisma model
}

// infra/prisma-user-repository.ts — Prisma is confined to this file
import { PrismaClient } from "@prisma/client";
export class PrismaUserRepository implements UserRepository {
  constructor(private db: PrismaClient) {}      // injected, not imported global
  async byId(id: string): Promise<User | null> {
    const row = await this.db.user.findUnique({
      where: { id },
      select: { id: true, email: true, name: true }, // no internal columns leave the layer
    });
    return row ? toUser(row) : null;             // map at the boundary
  }
}

// use case depends on the interface → testable with a fake, swappable implementation
class GetProfile { constructor(private users: UserRepository) {} }
```

**Bad Example** — Prisma leaking through every layer

```ts
// controller.ts — data access, business rules, and HTTP all tangled together
import { prisma } from "../db"; // global import, deep in the presentation layer
export async function handler(req, res) {
  const user = await prisma.user.findUnique({ where: { id: req.params.id } });
  // returns the raw entity, passwordHash and all, coupled to Prisma's shape
  res.json(user); // now every test of this handler needs a real database
}
```

## Common Mistakes

- Calling `prisma.*` directly from controllers, jobs, or UI components.
- Importing the global client everywhere instead of injecting it, making tests need a DB.
- Returning generated Prisma entities as the domain model, coupling the whole app to the schema.
- Leaking internal columns because no mapping happens at the data boundary.
- Re-checking tenant/soft-delete rules in each service instead of enforcing them once.
- No repository seam, so swapping the store, adding a cache, or mocking is a rewrite.

## Production Tips

- Enforce the boundary mechanically: an ESLint `no-restricted-imports` rule forbidding
  `@prisma/client` outside the data layer is worth more than a convention.
- Keep repository interfaces thin and intent-named (`activeSubscribers()`), not generic
  CRUD passthroughs, so business meaning lives in the domain.
- When testing, inject a Prisma client pointed at a disposable database (or a fake
  repository) rather than mocking Prisma's fluent API. See [testing](19-testing.md).

## AI Review Checklist

- Are all Prisma calls confined to a data-access/repository layer?
- Does business logic depend on repository interfaces it owns, not on `@prisma/client`?
- Is the client injected rather than imported as a global inside handlers?
- Are results mapped to domain types/DTOs at the boundary, with internal columns stripped?
- Is transaction scope exposed through repositories so use cases stay atomic?
- Are cross-cutting rules (tenant, soft delete) enforced once in the data layer?
- Is there a lint rule preventing Prisma imports outside the data layer?

## Related

- `knowledge/prisma/28-patterns.md`
- `knowledge/prisma/06-client.md`
- `knowledge/prisma/22-multi-tenancy.md`
- `knowledge/prisma/19-testing.md`
- `knowledge/prisma/24-best-practices.md`
