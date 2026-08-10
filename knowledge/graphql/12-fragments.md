---
id: graphql/12-fragments
topic: graphql
slug: fragments
title: "Fragments"
type: doc
order: 12
status: ready
tags: [graphql, fragments, ProfilePage, UserAvatar, UserCard, sets, requirements, reusable]
related: [graphql/04-queries, graphql/07-resolvers, graphql/03-types, graphql/22-performance, graphql/11-directives]
when_to_use: "Read before defining reusable selection sets, co-locating data requirements with UI components, or reviewing client queries."
---
# Fragments

## Purpose

This document defines how to use GraphQL **fragments**: named, reusable selection
sets that let a client request the same fields in many places without repeating them.
It covers plain fragments, inline fragments on interfaces and unions, fragment
arguments, and the client-side pattern of co-locating a fragment with the component
that consumes it. It is written so an agent can author and review fragments that stay
correct as the schema and UI evolve.

A fragment is a client concern, not a server one — the server never sees fragment
names, only the flattened selection set they expand into. Getting fragments right is
about maintainability and cache correctness, not query results.

## Why It Matters

Duplicated selection sets are the single largest source of drift in a growing GraphQL
client. When five queries each list the same twelve `User` fields by hand, adding a
field means editing five places, and missing one means a component silently renders
stale or empty data. Fragments make the data requirement live in exactly one place.

Fragments also drive **cache normalization** in clients like Apollo and Relay. If a
component reads a field it never declared in a fragment, it reads `undefined` at
runtime even though the field exists in the schema — a class of bug that type
generation catches only when fragments are the unit of composition. Get fragments
wrong and you get "works in the query, breaks in the component" failures.

## Core Principles

- **Co-locate the fragment with its consumer.** The component that renders a `User`
  card owns the `UserCard_user` fragment. Data requirements move with the code that
  needs them, so deleting the component deletes the requirement.
- **Compose, do not copy.** A page query should spread child fragments, never re-list
  their fields. The parent declares *which* components it renders, not *what fields*
  they need.
- **Name fragments after the component, not the type.** `UserCard_user` tells you who
  owns it; `UserFields` tells you nothing and invites unrelated code to depend on it.
- **A fragment must declare every field its consumer reads.** Reading an undeclared
  field returns `undefined` under a normalized cache even if the server could provide
  it. The fragment is the contract.
- **Use inline fragments for polymorphism.** Interface and union results need
  `... on ConcreteType` to select type-specific fields; nothing else can.

## Best Practices

- Give every fragment a type condition (`fragment X on User`) and let codegen produce
  a typed object; consume only the generated type, never a hand-written interface.
- Always select `__typename` (most clients add it automatically) so the cache can
  normalize objects and so inline fragments can discriminate unions.
- Prefer many small fragments over one large one — a fragment should map to a single
  component or hook, so unused fields do not travel with used ones.
- Use **fragment arguments** (`@arguments`/`@argumentDefinitions` in Relay, or variables
  threaded from the operation) to make a fragment parameterizable instead of forking it.
- Keep fragments free of operation-level concerns: no `@skip`/`@include` logic that
  belongs to the query, and no assumptions about pagination the parent controls.
- When spreading a fragment on an interface into a concrete field, verify the type
  condition is assignable; the server rejects `... FooFragment` if `Foo` cannot apply.

## Examples

**Good Example** — co-located, composed fragments; each component owns its fields

```graphql
# UserAvatar.tsx owns exactly the fields it renders.
fragment UserAvatar_user on User {
  __typename           # lets the normalized cache key this object
  id
  avatarUrl
}

# UserCard spreads the child fragment instead of re-listing avatar fields.
fragment UserCard_user on User {
  id
  displayName
  ...UserAvatar_user   # composition, not duplication
}

# The page query only names the components it renders.
query ProfilePage($id: ID!) {
  user(id: $id) {
    ...UserCard_user
  }
}
```

**Bad Example** — duplicated fields, no `__typename`, type-named fragment

```graphql
fragment UserFields on User {  # named after the type → becomes a dumping ground
  id
  displayName
  avatarUrl
}

query ProfilePage($id: ID!) {
  user(id: $id) {
    id            # duplicated: also in UserFields
    displayName   # duplicated
    avatarUrl     # UserAvatar reads this, but it is not in a fragment it owns
    ...UserFields # missing __typename → cache cannot normalize reliably
  }
}
```

## Common Mistakes

- Naming fragments after types (`UserFields`) so unrelated components couple to them
  and the fragment grows without bound.
- Reading a field in a component that its fragment does not declare, yielding
  `undefined` at runtime under a normalized cache.
- Re-listing a child component's fields in the parent instead of spreading its
  fragment, reintroducing the drift fragments exist to prevent.
- Forgetting `... on ConcreteType` on interface/union fields, so type-specific fields
  are never selectable.
- Duplicating a fragment with one extra field instead of adding a fragment argument.
- Omitting `__typename`, breaking cache normalization and union discrimination.

## Production Tips

- Run a schema-aware linter (`graphql-eslint`) in CI to reject unused fragments,
  undeclared field reads, and fragments not spread anywhere.
- Generate types from fragments (GraphQL Code Generator, Relay compiler) and fail the
  build on type errors — this is what turns "undeclared field" into a compile error.
- Track fragment size in review: a fragment feeding more than one component is a signal
  to split it.

## AI Review Checklist

- Is each fragment named after the component that owns it, not the type?
- Does every fragment declare exactly the fields its consumer reads — no more, no less?
- Do parent queries spread child fragments instead of re-listing fields?
- Is `__typename` present so the cache can normalize and unions can discriminate?
- Are interface/union selections wrapped in `... on ConcreteType`?
- Is variation handled with fragment arguments rather than near-duplicate fragments?

## Related

- `knowledge/graphql/04-queries.md`
- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/03-types.md`
- `knowledge/graphql/22-performance.md`
- `knowledge/graphql/11-directives.md`
