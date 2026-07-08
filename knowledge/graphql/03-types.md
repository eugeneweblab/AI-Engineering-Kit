---
id: graphql/03-types
topic: graphql
slug: types
title: "Types"
type: doc
order: 3
status: ready
tags: [graphql, types]
related: [graphql/02-schema, graphql/09-scalars, graphql/10-input-types, graphql/11-directives, graphql/29-schema-evolution]
when_to_use: "Read when defining objects, enums, interfaces, unions, or choosing nullability for a field."
---
# Types

## Purpose

This document defines the GraphQL type system: the categories of types (scalars,
objects, enums, interfaces, unions, lists, non-null), and how to choose the right
one. Types are what the runtime validates, so choosing them well is how you make
invalid states unrepresentable in the API.

## Why It Matters

The type system is GraphQL's only enforced guarantee. If you model a fixed set of
states as a `String`, every client must guess the valid values and no tool can
check them. If you mark a field non-null when it can be null, the runtime nulls
the whole parent object at the first missing value. Type choices are load-bearing:
they determine what clients can rely on, what tooling can generate, and what
breaks when data is imperfect.

## Core Principles

- **Scalars are leaves; objects are branches.** `Int`, `Float`, `String`,
  `Boolean`, `ID`, and [custom scalars](09-scalars.md) hold values. Object types
  hold fields and are where resolvers run.
- **Enums encode closed sets.** A field with a known, finite set of values is an
  `enum`, not a `String`. This is validated by the runtime and documents itself.
- **Interfaces share fields; unions share nothing.** Use an `interface` when
  types share common fields and clients query them polymorphically. Use a `union`
  when a field returns one of several unrelated types.
- **Non-null (`!`) propagates failure upward.** A `null` returned for a non-null
  field nulls its parent, and so on up to the nearest nullable ancestor. Choose
  `!` only where the value is genuinely always present.
- **Input types are separate from output types.** Object types cannot be used as
  arguments; arguments use [input types](10-input-types.md).

## Best Practices

- Prefer an `enum` over a `String` for any closed set (status, role, kind); it
  gives compile-time client safety and free documentation.
- Make `id` fields `ID!` and stable — an `ID` serializes as a string and should
  be opaque, not a leaking database primary key you might change.
- Default fields to nullable; add `!` only when the field can never be null and
  you are willing to null the parent if that promise breaks.
- Use interfaces for shared-shape polymorphism (`Node`, `SearchResult` items with
  common fields) and unions for heterogeneous results with no shared fields.
- When adding an enum value, remember clients may not handle it — treat new enum
  values as a potentially breaking change for exhaustive clients.

## Examples

**Good Example** — precise types make invalid states unrepresentable

```graphql
enum PostStatus { DRAFT PUBLISHED ARCHIVED }   # closed set, runtime-validated

interface Node { id: ID! }                     # shared identity for caching

type Post implements Node {
  id: ID!
  status: PostStatus!          # never a free-form string
  title: String!
  publishedAt: DateTime        # nullable: absent while DRAFT
}

# A search returns unrelated shapes → union, not a stringly-typed blob
union SearchResult = Post | User | Comment
```

**Bad Example** — stringly-typed and over-strict nullability

```graphql
type Post {
  id: ID!
  status: String!              # any string allowed; clients must guess values
  publishedAt: DateTime!       # non-null, but drafts have no date →
                               # one draft nulls the whole Post at runtime
  tags: [String!]              # fine, but a closed vocabulary should be an enum
}
```

## Common Mistakes

- Using `String` for a closed set of values, losing validation and forcing every
  client to hardcode magic strings.
- Marking a field non-null when the underlying value is sometimes absent, causing
  the parent object to null out unexpectedly.
- Exposing raw database primary keys as `ID`, coupling the API to storage and
  leaking internal counts/structure.
- Reaching for a `union` when types share fields (use an `interface`) or an
  `interface` when there is no shared shape (use a `union`).
- Assuming adding an enum value is always safe — exhaustive client switches can
  break on unknown values.

## AI Review Checklist

- Is every closed-set field an `enum` rather than a `String`?
- Is each non-null (`!`) field genuinely never null, given nulls propagate to the
  parent?
- Are `ID` values opaque and stable rather than raw database keys?
- Are interfaces used for shared-field polymorphism and unions for unrelated
  result shapes?
- Are arguments defined with input types, not object types?

## Related

- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/09-scalars.md`
- `knowledge/graphql/10-input-types.md`
- `knowledge/graphql/11-directives.md`
- `knowledge/graphql/29-schema-evolution.md`
