---
id: graphql/26-best-practices
topic: graphql
slug: best-practices
title: "GraphQL Best Practices"
type: doc
order: 26
status: ready
tags: [graphql, best-practices, updatePost, publishPost, PublishPostPayload, PublishPostInput, PostStatus, camelCase, quality, existing, one]
related: [graphql/02-schema, graphql/13-pagination, graphql/16-dataloader, graphql/20-error-handling, graphql/29-schema-evolution]
when_to_use: "Read before designing a new GraphQL schema or reviewing an existing one for design quality."
---
# GraphQL Best Practices

## Purpose

This document collects the cross-cutting design rules that make a GraphQL API pleasant to
consume, safe to evolve, and cheap to operate. It focuses on schema design decisions — the
ones that are expensive to reverse — rather than any single feature, which its own doc covers.

Think of this as the checklist a Principal engineer applies when reviewing a schema PR: is
the graph modeled around the domain, is it evolvable, and does every field pay for itself.

## Why It Matters

The schema is a public contract. Once a client depends on a field, its name, type, and
nullability are frozen for the life of that client. A REST endpoint can be versioned and
retired; a GraphQL field is forever until every consumer migrates. That permanence means
design mistakes compound: a leaky enum, a poorly chosen nullability, or a resolver that
mirrors your database table becomes a load-bearing part of clients you do not control.
Getting the schema right up front is cheaper than any migration later.

## Core Principles

- **Design the schema for clients, not for your tables.** Model the domain and the use
  cases. A schema that mirrors database columns leaks your internals and ages badly.
- **Nullable by default; non-null only when guaranteed.** A non-null field that errors nulls
  its whole parent. Mark `!` only when the value can never legitimately be absent.
- **Prefer additive change.** You can add types, fields, and optional arguments freely.
  Renames and removals are breaking. See [schema evolution](29-schema-evolution.md).
- **Every field is a resolver with a cost.** Adding a field adds latency and an N+1 risk.
  Fields are not free; justify each one.
- **Names are the API.** Use clear, consistent, domain names. `camelCase` fields, `PascalCase`
  types, `SCREAMING_SNAKE_CASE` enum values. Names are the hardest thing to change later.

## Best Practices

- Return object types, never bare scalars, from mutations — a `MutationPayload` wrapper lets
  you add fields (errors, the mutated node, related entities) without a breaking change.
- Use enums for closed sets of values instead of `String`; the schema documents the options
  and the server validates them for free.
- Paginate every list that can grow. Use cursor-based connections, not offset, so pages stay
  stable under insertion. See [pagination](13-pagination.md).
- Batch every field that fetches per-parent data through a DataLoader to avoid N+1. See
  [DataLoader](16-dataloader.md).
- Make mutations specific and intent-revealing (`publishPost`) rather than a generic
  `updatePost` that accepts every field — specific mutations are easier to authorize and audit.
- Put stable, machine-readable codes in `errors[].extensions.code`; keep human messages out
  of control flow. See [error handling](20-error-handling.md).
- Give inputs their own `Input` types and validate them in the resolver, not the schema alone.
- Deprecate with `@deprecated(reason: "...")` and a migration path; never silently remove.

## Examples

**Good Example** — payload wrapper, enum, nullable-by-default

```graphql
enum PostStatus { DRAFT PUBLISHED ARCHIVED } # closed set is validated + documented

type Post {
  id: ID!
  title: String!          # non-null: a post always has a title
  status: PostStatus!     # enum, not String
  publishedAt: DateTime   # nullable: null until published — correct, not `!`
}

input PublishPostInput { id: ID! }

type PublishPostPayload {
  post: Post              # nullable so a failed publish can return errors + null
  userErrors: [UserError!]!
}

type Mutation {
  # Intent-revealing mutation returning a wrapper we can extend later.
  publishPost(input: PublishPostInput!): PublishPostPayload!
}
```

**Bad Example** — table mirror, stringly-typed, over-eager non-null

```graphql
type Post {
  id: ID!
  title: String!
  status: String!         # stringly-typed: any value passes, clients guess options
  published_at: String!   # snake_case + non-null: nulls the whole Post before publish
  author_id: ID!          # exposes a foreign key instead of an `author: Author` edge
}

type Mutation {
  # Generic CRUD returning the bare type: can't add errors without a breaking change.
  updatePost(id: ID!, data: String!): Post!
}
```

## Common Mistakes

- Mirroring database columns (`author_id`, `snake_case`, raw enums-as-strings) in the schema.
- Marking fields non-null "to be safe," so one downstream error nulls an entire object.
- Returning the bare type from a mutation, leaving no room to add errors or side-effect data.
- Using `String` where an `enum` belongs, pushing validation onto every client.
- Unbounded list fields with no pagination, which become unbounded queries in production.
- Generic god-mutations (`update`) that are impossible to authorize or audit precisely.
- Removing or renaming a field without deprecation, breaking clients you cannot see.

## Production Tips

- Enforce naming and nullability conventions with a schema linter in CI, so review focuses
  on domain modeling rather than style nits.
- Keep a single source of truth for the schema (SDL or code-first), and generate client types
  from it so drift is caught at compile time. See [tooling](28-tooling.md).
- Review new fields for their resolver cost, not just their shape — a cheap-looking field can
  hide an N+1 or an external call.

## AI Review Checklist

- Does the schema model the domain rather than the database tables?
- Are fields nullable by default, with `!` only where the value is truly guaranteed?
- Do mutations return an extensible payload type rather than a bare scalar or entity?
- Are closed value sets modeled as enums instead of `String`?
- Is every growable list paginated with cursors?
- Are removals/renames done via `@deprecated` with a migration path, never silently?
- Do names follow `camelCase` fields / `PascalCase` types / `SCREAMING_SNAKE_CASE` enums?

## Related

- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/13-pagination.md`
- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/20-error-handling.md`
- `knowledge/graphql/29-schema-evolution.md`
