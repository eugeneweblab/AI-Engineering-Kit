---
id: graphql/02-schema
topic: graphql
slug: schema
title: "GraphQL Schema"
type: doc
order: 2
status: ready
tags: [graphql, schema, publishPost, PublishPostInput, comments, CommentConnection, PublishPostPayload, Mutation]
related: [graphql/03-types, graphql/10-input-types, graphql/29-schema-evolution, graphql/04-queries, graphql/05-mutations]
when_to_use: "Read before writing or changing any SDL, so the schema is designed around the domain and stays evolvable."
---
# GraphQL Schema

## Purpose

This document defines how to design a GraphQL schema: the Schema Definition
Language (SDL), the root types, and the design rules that keep a schema clear,
client-friendly, and safe to evolve. The schema is the API's contract, so this is
where most durable decisions are made.

## Why It Matters

The schema outlives the code behind it. Clients bind to field names, types, and
nullability; once a field ships to third parties, you cannot rename or narrow it
without breaking them. A schema that leaks database columns, uses vague types, or
marks everything nullable creates permanent liabilities. A well-designed schema,
by contrast, hides implementation, expresses the domain precisely, and grows by
adding fields — never by breaking existing ones.

## Core Principles

- **Design for the consumer, not the storage.** The schema models the domain and
  the client's needs. It is not a projection of your tables — that couples every
  client to your database and blocks refactoring.
- **The three roots.** `Query` (reads), `Mutation` (writes), and optionally
  `Subscription` (streams) are the entry points. Everything reachable in the
  graph hangs off these.
- **Nullability is a promise.** Non-null (`!`) means "this can never be null."
  Because a null in a non-null field nulls the parent, default to nullable and
  add `!` only where truly guaranteed.
- **Additive change is safe; subtractive change breaks.** Adding a field or an
  optional argument is backward-compatible. Removing, renaming, or narrowing a
  type is a breaking change (see [Schema Evolution](29-schema-evolution.md)).
- **Name for meaning, consistently.** Fields and types are `camelCase`/`PascalCase`
  and read like the domain. Names are part of the public API.

## Best Practices

- Keep the schema in SDL as the source of truth (schema-first) or generate SDL
  from code and check it into version control, so diffs are reviewable.
- Use dedicated [input types](10-input-types.md) for mutation arguments instead
  of long positional argument lists — inputs are versionable and self-documenting.
- Give every field, argument, and type a `"""description"""`. The schema is the
  documentation; tooling surfaces these to clients.
- Deprecate, don't delete: mark fields `@deprecated(reason: "...")` and remove
  them only after clients have migrated.
- Constrain lists: any field returning a collection should be paginated and
  bounded, never "return everything."
- Split large schemas into modules by domain and compose them, rather than one
  unreadable file.

## Examples

**Good Example** — domain-modeled, documented, evolvable

```graphql
"""A published article."""
type Post {
  id: ID!
  title: String!
  """Null while the post is still a draft."""
  publishedAt: DateTime
  author: User!               # non-null: a post always has an author
  comments(first: Int = 20, after: String): CommentConnection!  # bounded
}

type Query {
  post(id: ID!): Post         # nullable: id may not exist
}

type Mutation {
  publishPost(input: PublishPostInput!): PublishPostPayload!
}

input PublishPostInput { postId: ID! }   # input type, not loose args
```

**Bad Example** — leaks the database, unsafe nullability, unbounded

```graphql
type Post {
  post_id: ID!                # snake_case leaks column names
  fk_author_id: ID!           # exposes foreign keys → tight DB coupling
  comments: [Comment!]!       # unbounded: loads every comment, no pagination
  internal_status_code: Int!  # internal enum leaked to clients as a magic int
}

type Mutation {
  # positional args are hard to evolve; adding one is awkward and unversioned
  publishPost(postId: ID!, notify: Boolean, at: String): Post
}
```

## Common Mistakes

- Mirroring database tables and column names, coupling clients to storage and
  leaking internal structure (foreign keys, status codes).
- Marking fields non-null by reflex; a single null then nulls the entire parent
  object at runtime.
- Returning raw lists (`[T!]!`) for collections that can grow, creating unbounded
  queries and N+1 fan-out.
- Passing many positional mutation arguments instead of a single input type,
  making the mutation hard to evolve.
- Deleting or renaming fields in place instead of deprecating, breaking live
  clients silently.

## Production Tips

- Run schema-diff checks in CI (e.g. `graphql-inspector`) to fail the build on
  breaking changes before they reach clients.
- Track field usage in production so you know when a `@deprecated` field is safe
  to remove.
- Keep a single canonical schema artifact published for client codegen, so
  clients never drift from the deployed contract.

## AI Review Checklist

- Does the schema model the domain rather than the database tables?
- Is nullability deliberate, with `!` only where a value is truly guaranteed?
- Do mutations take input types instead of many positional arguments?
- Are all collection fields paginated and bounded?
- Are removed fields `@deprecated` rather than deleted, and is the change
  additive where possible?
- Does every type, field, and argument carry a description?

## Related

- `knowledge/graphql/03-types.md`
- `knowledge/graphql/10-input-types.md`
- `knowledge/graphql/29-schema-evolution.md`
- `knowledge/graphql/04-queries.md`
- `knowledge/graphql/05-mutations.md`
