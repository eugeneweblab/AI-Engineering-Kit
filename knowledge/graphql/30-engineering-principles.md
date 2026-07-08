---
id: graphql/30-engineering-principles
topic: graphql
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [graphql, engineering-principles]
related: [graphql/02-schema, graphql/07-resolvers, graphql/15-n1-problem, graphql/17-security, graphql/29-schema-evolution]
when_to_use: "Read before designing a new GraphQL schema or service, or when reviewing whether an existing one follows sound engineering foundations."
---
# Engineering Principles

## Purpose

This document defines the durable engineering principles behind a well-built GraphQL
API: how to model a schema, structure resolvers, control cost, and evolve safely. It is
the foundation the other GraphQL docs build on. Read it to make design decisions that
stay correct as the graph grows from one type to hundreds.

GraphQL is a contract language, not a database and not a transport gimmick. The schema
is your public API forever — once a field ships, clients depend on it. These principles
exist so that early decisions do not become permanent liabilities.

## Why It Matters

A GraphQL schema is uniquely unforgiving. A single query can fan out into thousands of
database calls, a single nullable-vs-non-null choice can break every client on error,
and a single leaked field can expose internal data across the whole graph. Unlike REST,
where each endpoint is bounded, GraphQL lets clients compose arbitrary shapes — so the
server must be correct for queries no one has written yet. Getting the principles right
up front is far cheaper than retrofitting cost controls and schema discipline onto a
graph that already has consumers.

## Core Principles

- **Design the schema for clients, not for your tables.** Model the domain in the
  language of the API consumer. Exposing your database structure couples clients to your
  storage and blocks refactoring.
- **The schema is a contract; additive change only.** You can add types and fields
  freely. Removing or changing a field is a breaking change — deprecate first, remove
  after telemetry shows zero use. See [schema evolution](29-schema-evolution.md).
- **Every field has a resolver, so every field has a cost.** Assume any resolver may hit
  the network or database. Design for batching from day one — the [N+1 problem](15-n1-problem.md)
  is the default, not an edge case.
- **Nullability is a promise.** A non-null field that throws nulls out its entire parent
  object. Make a field non-null only when you can always produce it.
- **Bound every query.** A schema with no depth, complexity, or pagination limits is a
  denial-of-service vector. Cost must be predictable before execution.
- **Errors are part of the schema.** Model expected failures as data (result unions),
  and reserve GraphQL errors for exceptional faults.

## Best Practices

- Make list fields return **connections** (edges + pageInfo), never unbounded arrays.
  Cursor pagination is the only shape that stays correct as data grows. See
  [pagination](13-pagination.md).
- Batch and cache per-request with **DataLoader** (or your framework's equivalent) so
  repeated entity fetches collapse into one query. See [DataLoader](16-dataloader.md).
- Enforce **query depth and cost limits** and a timeout on every operation before it
  reaches resolvers.
- Keep resolvers **thin**: parse/authorize/delegate. Business logic belongs in a service
  layer the resolver calls, so it is testable and reusable.
- Pass request-scoped state (viewer, loaders, tracing) through **context**, never through
  module globals — globals leak data across requests.
- Prefer **non-null** for arguments and inputs, but be conservative with non-null on
  output fields that depend on downstream systems.
- Version by **evolution, not URLs**. There is no `/v2`; you grow one graph.

## Examples

**Good Example** — client-oriented type, batched resolver, bounded list

```graphql
type Post {
  id: ID!
  title: String!
  author: User!                       # resolved via DataLoader, not a per-row query
  comments(first: Int!, after: String): CommentConnection!  # bounded, paginated
}
```

```ts
// Resolver batches author lookups: N posts -> 1 query, not N queries.
const resolvers = {
  Post: {
    author: (post, _args, ctx) => ctx.loaders.userById.load(post.authorId),
  },
};
```

**Bad Example** — leaks storage shape, unbounded, N+1

```graphql
type Post {
  id: ID!
  user_id: Int!                       # exposes DB column; couples clients to schema
  comments: [Comment!]!               # unbounded list -> can return millions of rows
}
```

```ts
const resolvers = {
  Post: {
    // One SQL query per post -> classic N+1 under any list of posts.
    author: (post) => db.query("SELECT * FROM users WHERE id = ?", post.user_id),
  },
};
```

## Common Mistakes

- Mirroring database tables and column names directly into the schema, permanently
  coupling clients to storage.
- Marking output fields non-null "to be safe," so one downstream failure nulls the whole
  parent object.
- Returning raw arrays for lists instead of paginated connections, then discovering the
  DoS in production.
- Writing resolvers that each issue their own query, with no batching layer.
- Putting business logic inside resolvers, making it impossible to unit-test or reuse.
- Treating GraphQL as REST-over-POST: one fat query field per screen instead of a
  composable graph.

## Production Tips

- Publish the schema to a registry and run **breaking-change checks** in CI against the
  last shipped version. See [schema evolution](29-schema-evolution.md).
- Track **field-level usage** so deprecations can be retired safely with data, not guesses.
- Disable introspection and set query cost limits per environment; keep the playground
  off in production.

## AI Review Checklist

- Does the schema model the domain, not the database tables?
- Is every list field a bounded, cursor-paginated connection?
- Does each entity fetch go through a batching loader (no N+1)?
- Are non-null output fields ones the server can always produce?
- Are depth, complexity, and timeout limits enforced before resolvers run?
- Are all changes additive, with removals gated behind deprecation + usage data?
- Are resolvers thin, delegating to a testable service layer?

## Related

- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/29-schema-evolution.md`
