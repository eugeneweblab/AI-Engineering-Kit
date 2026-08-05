---
id: graphql/29-schema-evolution
topic: graphql
slug: schema-evolution
title: "Schema Evolution"
type: doc
order: 29
status: ready
tags: [graphql, schema-evolution, reason, displayName, deprecated]
related: [graphql/02-schema, graphql/26-best-practices, graphql/28-tooling, graphql/27-production, graphql/13-pagination]
when_to_use: "Read before changing an existing GraphQL schema — renaming, removing, or retyping any field a client may use."
---
# Schema Evolution

## Purpose

This document defines how to change a GraphQL schema without breaking the clients already
depending on it: which changes are safe, how to deprecate and retire fields, and how to run
old and new shapes side by side during a migration. It exists because in GraphQL you almost
never version the whole API — you evolve one continuously living schema.

The governing idea is *additive change plus deprecation*. GraphQL has no `/v2`; instead you
add the new shape, mark the old one deprecated, wait for clients to move, and only then remove.

## Why It Matters

Clients select exactly the fields they use, so any field can be depended on by consumers you
cannot see — mobile apps in the field, third-party integrations, cached queries. Renaming or
removing that field, tightening its nullability, or changing its type breaks those clients at
runtime with no compile error on their side. Unlike REST, you cannot ship a parallel `/v2` and
retire `/v1`; the schema is one shared object. That makes the discipline of additive-only,
deprecate-then-remove the difference between a smooth migration and a silent outage.

## Core Principles

- **Additive changes are safe; subtractive and narrowing changes are breaking.** Adding types,
  fields, and *optional* arguments is safe. Removing, renaming, or making things stricter is not.
- **Deprecate before you remove.** Mark the old field `@deprecated(reason: "...")` with the
  replacement, keep it working, and remove it only after usage drops to zero.
- **Nullability changes cut one way.** Nullable → non-null is breaking (clients that sent null
  now fail); non-null → nullable is also breaking for clients that assumed a value. Treat both
  as breaking. Prefer adding a new field over changing an existing one's nullability.
- **Add fields; don't repurpose them.** Changing a field's type or meaning is a breaking change
  wearing the same name. Introduce a new field instead.
- **Measure before removing.** Use real operation usage data to prove no client still selects the
  field. See [tooling](28-tooling.md) and [monitoring](25-monitoring.md).

## Best Practices

- Introduce changes additively: to rename `fullName` → `displayName`, add `displayName`, resolve
  both, deprecate `fullName`, migrate clients, then remove `fullName` in a later release.
- Always give `@deprecated` a `reason` that names the replacement, so tooling and humans know
  the migration path.
- For argument changes, add a new *optional* argument rather than changing or requiring an
  existing one; a newly required argument breaks every current caller.
- To change an enum, add new values freely, but treat removing or renaming a value as breaking —
  clients may send or match on it.
- Run a breaking-change diff in CI against the deployed schema and block breaking changes unless
  a migration is explicitly approved. See [testing](24-testing.md) and [tooling](28-tooling.md).
- Coordinate rollout: deploy the additive schema and resolvers first (old and new coexist),
  migrate clients, then remove — never remove and rename in one step. See [production](27-production.md).

## Examples

**Good Example** — additive rename with deprecation and a resolver for both

```graphql
type User {
  id: ID!
  fullName: String! @deprecated(reason: "Use `displayName`. Removal after 2026-10-01.")
  displayName: String!   # new field added alongside; old one still resolves
}
```

```ts
const User = {
  displayName: (u) => u.displayName,
  // Keep the deprecated field working until usage hits zero — never break in place.
  fullName: (u) => u.displayName,
};
// Rollout: ship this → dashboards show fullName usage → migrate clients → drop fullName.
```

**Bad Example** — breaking rename and narrowing in one deploy

```graphql
type User {
  id: ID!
  # Renamed in place: every client selecting `fullName` now gets a validation error.
  displayName: String!
  # nickname went from nullable to non-null: clients/servers that produced null now error,
  # and the error nulls the whole User object.
  nickname: String!
}
```

## Common Mistakes

- Renaming a field in place instead of adding the new name and deprecating the old.
- Removing a field (or enum value) without first proving via usage data that no client uses it.
- Tightening nullability (`String` → `String!`) or a type, breaking clients that relied on null.
- Adding a new *required* argument to an existing field, breaking every current caller.
- Deprecating without a `reason`, leaving clients no migration path.
- Removing and renaming in a single rolling deploy, breaking clients mid-rollout.
- Repurposing a field's meaning while keeping its name — a silent, untyped break.

## Production Tips

- Put a target removal date in the `@deprecated` reason and track deprecated-field usage on a
  dashboard so removals are driven by data, not guesswork.
- Publish each schema version to a registry and diff against the schema serving production, not
  a branch, so rollout-window differences are visible. See [tooling](28-tooling.md).
- For unavoidable breaking changes, stand up the new shape as a distinct field/type and run a
  timed migration; treat a hard cut as a last resort with explicit consumer sign-off.

## AI Review Checklist

- Is every change additive, or is a breaking change explicitly justified and approved?
- Are removed/renamed fields first added under the new name and deprecated, not changed in place?
- Does each `@deprecated` include a `reason` naming the replacement (and ideally a date)?
- Are nullability and type changes treated as breaking rather than shipped silently?
- Are new arguments optional, never newly required on existing fields?
- Is a breaking-change diff gate against the deployed schema enforced in CI?
- Is removal backed by usage data proving no client still selects the field?

## Related

- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/26-best-practices.md`
- `knowledge/graphql/28-tooling.md`
- `knowledge/graphql/27-production.md`
- `knowledge/graphql/13-pagination.md`
