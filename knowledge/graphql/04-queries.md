---
id: graphql/04-queries
topic: graphql
slug: queries
title: "Queries"
type: doc
order: 4
status: ready
tags: [graphql, queries, after, first]
related: [graphql/05-mutations, graphql/13-pagination, graphql/15-n1-problem, graphql/17-security, graphql/07-resolvers]
when_to_use: "Read before designing or reviewing any read operation, list field, or query-side resolver."
---
# Queries

## Purpose

This document defines how to design and consume read operations in GraphQL:
query structure, arguments, variables, aliases, and the fields on the `Query`
root. Queries are the most-used operation and the primary surface where a client
can accidentally — or deliberately — make the server do expensive work.

## Why It Matters

A query's cost is chosen by the client, not the server. One innocent-looking
nested query (`users { posts { comments { author } } }`) can fan out into
millions of resolver calls and database round-trips. Reads are also where
over-exposure happens: a field added for one client is queryable by all. Getting
queries right means bounding cost and exposing only what should be public — both
enforced server-side, because the client is untrusted.

## Core Principles

- **Query fields resolve in parallel and must be side-effect free.** A `query`
  must never mutate state; the runtime may execute sibling fields concurrently
  and in any order.
- **The client selects fields and depth; the server bounds them.** Because the
  client controls the shape, the server must enforce depth, complexity, and rate
  limits (see [Security](17-security.md)).
- **Every list is a fan-out point.** A list of N items runs each child resolver N
  times. Paginate the list and batch the children (see
  [N+1](15-n1-problem.md), [DataLoader](16-dataloader.md)).
- **Use variables, not string interpolation.** Dynamic values belong in typed
  query variables, which are validated and safe; never build query strings by
  concatenation.
- **Nullable roots signal "may not exist."** `post(id): Post` returning null for a
  missing id is normal and is not an error.

## Best Practices

- Give every collection field pagination arguments (`first`/`after` cursor style
  preferred) with a sensible default and a hard maximum page size.
- Name operations (`query GetUser { ... }`) so they appear in logs, tracing, and
  persisted-query allowlists — anonymous queries are unobservable.
- Pass dynamic values as declared variables (`$id: ID!`) so they are typed,
  validated, and cacheable.
- Use [fragments](12-fragments.md) to share field selections across queries and
  keep client code DRY.
- Keep field resolution side-effect free; if a read needs to write (e.g. "record
  last-seen"), do it out of band, not in a query resolver.
- Return connection types for lists so you can add pagination metadata without a
  breaking change later.

## Examples

**Good Example** — named, variables, bounded, aliased

```graphql
query GetUserWithPosts($id: ID!, $pageSize: Int = 10) {
  user(id: $id) {           # nullable root: missing id → null, not an error
    name
    recent: posts(first: $pageSize) {   # alias + bounded page size
      edges { node { title } }
      pageInfo { hasNextPage endCursor }  # cursor pagination, extensible
    }
  }
}
```

**Bad Example** — unbounded, unnamed, string-built, side-effecting

```graphql
# Anonymous (invisible in logs) and unbounded at every level:
query {
  users {                   # ALL users
    posts {                 # ALL posts per user → N+1 across users
      comments {            # ALL comments per post → N+1 across posts
        author { name }     # N+1 across comments; cost is unbounded
      }
    }
  }
}
# Plus: a resolver here that increments a "views" counter would be a
# side effect inside a query — illegal, and non-deterministic under parallel
# execution.
```

## Common Mistakes

- Returning raw lists with no pagination, letting a client request the entire
  table in one query.
- Nesting relationships without batching, producing N+1 database calls that grow
  with the data.
- Building query strings via concatenation instead of typed variables, defeating
  validation and caching.
- Leaving operations anonymous, so slow or abusive queries cannot be traced.
- Performing writes or other side effects inside query resolvers, which run in
  parallel and may be cached.

## Production Tips

- Enforce a maximum query depth and a complexity budget at the gateway; reject
  queries that exceed it before any resolver runs.
- Prefer persisted/allowlisted queries for first-party clients so the server only
  executes queries you have reviewed.
- Add per-field tracing so you can find which resolver dominates a slow query.

## AI Review Checklist

- Does every list field have bounded pagination with a hard maximum page size?
- Are nested relationships batched to avoid N+1?
- Are dynamic values passed as typed variables rather than interpolated strings?
- Are operations named for observability?
- Are query resolvers free of side effects?
- Are depth and complexity limits enforced on the endpoint?

## Related

- `knowledge/graphql/05-mutations.md`
- `knowledge/graphql/13-pagination.md`
- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/07-resolvers.md`
