---
id: graphql/01-graphql-fundamentals
topic: graphql
slug: graphql-fundamentals
title: "GraphQL Fundamentals"
type: doc
order: 1
status: ready
tags: [graphql, graphql-fundamentals, subscription, mutation, errors]
related: [graphql/02-schema, graphql/04-queries, graphql/05-mutations, graphql/07-resolvers, graphql/00-overview]
when_to_use: "Read before designing or reviewing any GraphQL API, to ground decisions in how the execution model actually works."
---
# GraphQL Fundamentals

## Purpose

This document defines the GraphQL execution model: how a request becomes a
response, what the runtime guarantees, and where GraphQL differs from REST. It
exists so an agent reasons about GraphQL as it actually behaves — a per-field
resolution engine over a typed schema — not as a vague "flexible API."

## Why It Matters

Most GraphQL production failures trace back to a wrong mental model. Engineers
who picture GraphQL as "REST that returns JSON" ship N+1 storms, unbounded
queries, and schemas that leak the database. GraphQL inverts control: the client
decides the shape and cost of the response, and the server executes a tree of
resolvers to satisfy it. If you do not internalize that inversion, you cannot
predict what your server will do under a query you did not write.

## Core Principles

- **One endpoint, many operations.** A GraphQL service exposes a single URL
  (usually `POST /graphql`). The operation is in the request body, not the path.
  HTTP verbs and status codes are not the contract — the schema is.
- **Three operation types.** `query` reads, `mutation` writes, `subscription`
  streams. Only mutations are guaranteed to run their top-level fields serially;
  query fields may resolve in parallel.
- **Execution is a depth-first walk of the selection set.** The runtime resolves
  each requested field by calling its resolver with `(parent, args, context,
  info)`, then recurses into the child selection using the returned value as the
  new parent.
- **The type system validates shape before execution.** A query is parsed and
  validated against the schema first; invalid queries are rejected without any
  resolver running. Types guarantee structure, never business correctness.
- **Responses can be partial.** The response is `{ data, errors }`. A field can
  fail and return `null` while sibling fields succeed — so error handling is a
  first-class design concern, not an afterthought.

## Best Practices

- Design the schema around client use cases and the domain graph, then map
  resolvers onto your data sources — never expose tables directly.
- Assume every list field will be requested with all its children; plan batching
  (see [DataLoader](16-dataloader.md)) before you write the resolver.
- Bound the client's power: enforce query depth and complexity limits on any
  public endpoint (see [Security](17-security.md)).
- Return meaningful `nullability` — mark a field non-null only when it can truly
  never be null, because a null in a non-null field nulls the whole parent.
- Keep resolvers thin: they orchestrate; business logic lives in services you can
  test and reuse across operations.

## Examples

**Good Example** — a query and the exact response it produces

```graphql
# The client asks for precisely the fields it needs, across a relationship,
# in ONE round trip. No over-fetching, no under-fetching.
query GetUser {
  user(id: "42") {
    name
    posts(first: 2) {   # bounded: never "give me all posts"
      title
    }
  }
}
```

```json
{
  "data": {
    "user": {
      "name": "Ada",
      "posts": [{ "title": "On Engines" }, { "title": "Notes" }]
    }
  }
}
```

**Bad Example** — treating GraphQL as REST and ignoring the execution model

```graphql
# One coarse field per screen mirrors REST endpoints and defeats the point:
# the client cannot pick fields, and the resolver must over-fetch everything.
query {
  homeScreenPayload          # returns a giant fixed blob
  # posts here would be unbounded — the resolver loads ALL posts and
  # then loads each post's author one-by-one → classic N+1 under the hood.
}
```

## Common Mistakes

- Thinking in endpoints instead of a graph, producing one bespoke field per UI
  screen that cannot be composed or reused.
- Assuming HTTP status codes signal GraphQL errors — a GraphQL error is usually
  returned with HTTP 200 in the `errors` array.
- Marking fields non-null for convenience; one null then propagates up and nulls
  an entire object.
- Forgetting that list fields multiply resolver calls, so a "simple" nested query
  fans out into hundreds of database calls.
- Trusting the type system to enforce business rules (ownership, ranges, format).

## AI Review Checklist

- Is the schema modeled on the domain/client needs, not the database tables?
- Are nested and list fields bounded (pagination) and batched (DataLoader)?
- Are depth/complexity limits present on public endpoints?
- Is nullability chosen deliberately, aware that a null nulls its non-null parent?
- Are business validations done in resolvers/services, not assumed from types?

## Related

- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/04-queries.md`
- `knowledge/graphql/05-mutations.md`
- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/00-overview.md`
