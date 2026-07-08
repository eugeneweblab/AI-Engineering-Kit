---
id: graphql/100-common-antipatterns
topic: graphql
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [graphql, common-antipatterns]
related: [graphql/13-pagination, graphql/15-n1-problem, graphql/16-dataloader, graphql/17-security, graphql/20-error-handling]
when_to_use: "Read when designing or reviewing a GraphQL schema or resolver to avoid the recurring mistakes below."
---
# Common Antipatterns

## Purpose

A catalog of the GraphQL mistakes that appear again and again, each with why it is wrong
and the concrete fix. Use it as a lookup: match the smell in the code under review, then
apply the remedy. These are the patterns that pass tests in staging and fail in
production.

## Why It Matters

GraphQL's flexibility means a small local mistake has global reach — one unbatched
resolver degrades every query that touches it, one leaked field exposes data across the
whole graph. Recognizing these anti-patterns on sight is the cheapest defense; each one
below has caused real outages or breaches.

## Anti-Patterns

### 1. The N+1 resolver

**Why it is wrong:** A field resolver that fetches per parent (`author` for each `Post`)
issues one query per row. A list of 100 posts becomes 101 queries, and it scales with
result size — invisible in unit tests, fatal under load.

**The fix:** Batch with a per-request [DataLoader](16-dataloader.md); resolvers call
`loader.load(id)` and the loader coalesces keys into one query.

```ts
// Bad: one DB call per post.
author: (post) => db.users.findById(post.authorId),
// Good: batched into a single call per tick.
author: (post, _a, ctx) => ctx.loaders.userById.load(post.authorId),
```

### 2. Unbounded list fields

**Why it is wrong:** `comments: [Comment!]!` can return millions of rows and has no cost
ceiling — a denial-of-service by design.

**The fix:** Return a **connection** with a required `first`/`last` and an enforced max
page size. See [pagination](13-pagination.md).

### 3. Exposing database shape in the schema

**Why it is wrong:** Fields like `user_id`, `created_ts`, or a 1:1 mirror of tables
couple every client to your storage. You can no longer refactor the database without a
breaking API change.

**The fix:** Model the schema for the client's domain (`author: User!`, `createdAt:
DateTime!`). The mapping to storage lives in resolvers.

### 4. No query cost controls

**Why it is wrong:** Without depth, complexity, and timeout limits, a client can send a
deeply nested or alias-multiplied query that exhausts CPU, memory, or the database.

**The fix:** Enforce max depth, a complexity budget, and a per-operation timeout before
execution; add persisted queries for untrusted clients. See [security](17-security.md).

### 5. Errors as thrown exceptions for expected failures

**Why it is wrong:** Throwing on "not found" or "validation failed" puts the failure in
the top-level `errors` array, nulls the field, and gives clients no typed way to handle
it. It conflates business outcomes with server faults.

**The fix:** Model expected outcomes as a **result union** returned as data; reserve
thrown errors for genuine faults. See [error handling](20-error-handling.md).

```graphql
# Good: the failure is part of the schema, not an exception.
union CreateUserResult = User | EmailTakenError | ValidationError
```

### 6. Over-eager non-null

**Why it is wrong:** Marking a downstream-dependent field non-null (`avatarUrl: String!`)
means one failure in that dependency nulls the **entire parent object**, cascading the
error far beyond the failed field.

**The fix:** Make fields non-null only when the server can always produce them; leave
externally-sourced fields nullable so failures stay local.

### 7. Authorization only at the entry point

**Why it is wrong:** Checking access on the top-level query but not on nested fields lets
a client reach protected data through a relationship (`me { friends { privateEmail } }`).

**The fix:** Enforce authorization at the **field/type** level, using the viewer in
context, on every sensitive field — not just the root. See [security](17-security.md).

### 8. Business logic inside resolvers

**Why it is wrong:** Fat resolvers can't be unit-tested without a GraphQL server, can't
be reused by other transports, and mix parsing/auth/domain concerns.

**The fix:** Keep resolvers thin — authorize and delegate to a service layer that holds
the logic and is independently testable.

### 9. Request state in module globals

**Why it is wrong:** Storing the current user or a loader in a module-level variable leaks
state across concurrent requests — user A can see user B's data.

**The fix:** Put all request-scoped state (viewer, loaders, tracing) in **context**,
constructed fresh per request.

### 10. Versioning the URL (`/graphql/v2`)

**Why it is wrong:** GraphQL is designed to evolve one graph; parallel versioned
endpoints duplicate the schema and fracture clients.

**The fix:** Evolve additively — add new fields, `@deprecated` old ones, and remove only
after usage telemetry hits zero. See [schema evolution](29-schema-evolution.md).

### 11. Introspection and verbose errors on in production

**Why it is wrong:** Public introspection hands attackers your full schema, and unmasked
errors leak stack traces, SQL, and internal paths.

**The fix:** Disable introspection (or gate it) in production and mask error internals,
returning stable error codes in `extensions` instead.

## AI Review Checklist

- Does any list-context resolver fetch per item without a loader (N+1)?
- Are all lists bounded, paginated connections?
- Does the schema model the domain rather than database columns?
- Are depth, complexity, and timeout limits enforced?
- Are expected failures modeled as data, and downstream fields left nullable?
- Is authorization enforced at the field level, with request state in context?

## Related

- `knowledge/graphql/13-pagination.md`
- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/20-error-handling.md`
