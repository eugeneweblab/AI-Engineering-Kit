---
id: graphql/19-authorization
topic: graphql
slug: authorization
title: "GraphQL Authorization"
type: doc
order: 19
status: ready
tags: [graphql, authorization, UNAUTHENTICATED, FORBIDDEN, load, includes, findMany, findById]
related: [graphql/18-authentication, graphql/07-resolvers, graphql/16-dataloader, graphql/17-security, graphql/20-error-handling]
when_to_use: "Read before deciding which fields, objects, or mutations a caller may access in a GraphQL API."
---
# GraphQL Authorization

## Purpose

This document defines how to decide *what* an authenticated (or anonymous) caller may
read and do in a GraphQL API — per field, per object, and per mutation. It assumes
identity is already established by [authentication](18-authentication.md); here we enforce
policy on the graph.

## Why It Matters

GraphQL lets a client compose arbitrary shapes: a single query can walk from a `User` to
their `Orders` to another user's `PaymentMethod` through a relationship the API author
never imagined. There are no fixed endpoints to guard. Authorization must therefore be a
property of the *data*, checked wherever the graph is traversed, not a gate on a route.
Miss one edge and the whole object graph leaks. Because clients pick the fields,
object-level checks alone are not enough — a field-level bypass exposes exactly the
column an attacker asked for.

## Core Principles

- **Authorize on the data, at the resolver that returns it.** The only place you reliably
  know both the caller and the specific object is the field resolver. Enforce there, or in
  a policy layer it calls — never trust the client to omit forbidden fields.
- **Deny by default.** A field with no explicit rule is private. New fields are locked
  until someone writes a policy, not open until someone remembers to close them.
- **Check ownership on the object, not just the type.** "Can read `Order`" is not "can read
  *this* `Order`". Compare the caller against the specific row's owner/tenant.
- **Do not leak existence.** For objects a caller may not see, return `null` (or the same
  "not found" as a missing row), not "forbidden". Distinguishing the two enumerates ids.
- **Keep policy out of resolvers' business logic.** Centralize rules in a policy
  module/service so they are testable and consistent across the graph.

## Best Practices

- Prefer field- and object-level checks in resolvers over schema directives when rules
  depend on the *object instance* (ownership, tenancy). Use directives (`@auth(role:)`)
  only for coarse, role-based gates that need no instance data.
- Batch authorization lookups with [DataLoader](16-dataloader.md) so a per-object check
  over a list does not become an N+1 of permission queries.
- Enforce mutation authorization before any side effect, and re-check inside the
  transaction to avoid a check-then-act race.
- Filter lists at the data layer (`WHERE tenant_id = ?`), not by resolving everything and
  dropping forbidden items — the latter leaks counts, timing, and pagination cursors.
- Return `UNAUTHENTICATED` (401-equivalent) when there is no identity and `FORBIDDEN`
  (403-equivalent) when identity exists but lacks permission (see [error handling](20-error-handling.md)).
- Cover authorization in tests for every sensitive field, including the negative case of a
  valid but unauthorized caller.

## Examples

**Good Example** — object-level ownership check, batched, existence not leaked

```ts
const resolvers = {
  Query: {
    // Filter at the data layer so forbidden rows never enter the result set.
    invoices: (_p, _a, ctx: Ctx) =>
      db.invoice.findMany({ where: { tenantId: ctx.user.tenantId } }),
  },
  Invoice: {
    // Ownership is a property of THIS invoice, so it is checked on the object.
    lineItems: async (invoice, _a, ctx: Ctx) => {
      if (invoice.tenantId !== ctx.user.tenantId) return null; // no "forbidden" → no enumeration
      return ctx.loaders.lineItems.load(invoice.id);           // batched, no N+1 of checks
    },
  },
};
```

**Bad Example** — type-level check only, filters in memory, leaks existence

```ts
const resolvers = {
  Query: {
    invoice: async (_p, { id }, ctx) => {
      if (!ctx.user.roles.includes("billing")) throw new Error("forbidden");
      const inv = await db.invoice.findById(id); // any billing user reads ANY tenant's invoice
      if (inv.tenantId !== ctx.user.tenantId)
        throw new Error("forbidden");            // "forbidden" vs null → enumerate valid ids
      return inv;
    },
  },
};
```

## Common Mistakes

- Checking only the type/role, not the specific object's owner or tenant.
- Returning "forbidden" for objects the caller can't see, enabling id enumeration.
- Filtering results in the resolver after fetching everything, leaking counts and timing.
- Relying on the client to not request a field — clients control the query, you don't.
- Authorizing a mutation but not re-checking inside the transaction (check-then-act race).
- Per-object permission queries with no batching, turning a list into an N+1 of auth checks.
- Putting all rules inline in resolvers, so they drift and cannot be tested in isolation.

## Production Tips

- Log authorization *denials* with caller id, field, and object id for abuse detection.
- Add a lint/test that fails CI when a resolver returning sensitive data has no policy call.
- For federated graphs, decide whether authorization lives at the gateway or subgraphs and
  document it — split ownership is how gaps appear (see [federation](23-federation.md)).

## AI Review Checklist

- Is every sensitive field authorized at the resolver that returns it, deny-by-default?
- Are object-level (ownership/tenant) checks done on the instance, not just the type?
- Do inaccessible objects return `null`/not-found rather than a distinct "forbidden"?
- Are lists filtered at the data layer instead of in memory after fetching?
- Are per-object permission checks batched to avoid an N+1?
- Is `UNAUTHENTICATED` vs `FORBIDDEN` used correctly, per [authentication](18-authentication.md)?

## Related

- `knowledge/graphql/18-authentication.md`
- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/20-error-handling.md`
