---
id: graphql/11-directives
topic: graphql
slug: directives
title: "Directives"
type: doc
order: 11
status: ready
tags: [graphql, directives]
related: [graphql/02-schema, graphql/19-authorization, graphql/12-fragments, graphql/23-federation, graphql/29-schema-evolution]
when_to_use: "Read before using a built-in directive in a query or authoring a custom schema directive for auth, formatting, or deprecation."
---
# Directives

## Purpose

This document defines GraphQL **directives**: annotations (`@name(arg: value)`) that modify
execution or schema behaviour. It is written so an agent uses the built-in directives
correctly and authors custom directives that stay declarative, order-independent, and safe —
without hiding critical logic like authorization inside a directive nobody audits.

Directives come in two families: **executable** directives that appear in queries
(`@skip`, `@include`, `@defer`) and **type-system** (schema) directives that appear in the
SDL (`@deprecated`, `@specifiedBy`, plus custom ones like `@auth`).

## Why It Matters

Directives are metadata that changes behaviour, and that is exactly what makes them
double-edged. Used well, `@deprecated` drives safe [schema evolution](29-schema-evolution.md)
and a `@auth` directive centralizes a policy so it cannot be forgotten on a new field. Used
badly, they become invisible control flow: authorization logic buried in a directive is easy
to overlook in review, and a directive whose behaviour depends on ordering relative to other
directives produces results that differ by position in ways no one expects. Because
directives run inside the execution engine, a bug in a custom directive affects every field
it annotates at once.

## Core Principles

- **Use built-in directives before inventing your own.** `@skip`, `@include`, `@deprecated`,
  `@specifiedBy`, and (where supported) `@defer`/`@stream` cover most needs. Reach for a
  custom directive only for genuinely cross-cutting schema concerns.
- **Directives declare intent; they must not hide essential business logic.** A field's core
  behaviour belongs in its resolver, where it is testable and visible — not smuggled into a
  directive.
- **`@skip` and `@include` are mutually aware but not ordered — do not put both on one field
  with conflicting intent.** `@skip(if:true)` wins; keep each field to one conditional.
- **Custom directive behaviour must be order-independent and idempotent.** Do not rely on the
  relative order of two directives on the same location; engines do not guarantee it.
- **`@deprecated` is the contract for removal, not a suggestion.** Always give a `reason`
  pointing to the replacement so clients can migrate.

## Best Practices

- Use `@deprecated(reason: "...")` on fields/enum values you intend to remove; monitor usage
  and only remove after it drops to zero. Never delete a field without deprecating first.
- Prefer `@skip(if:)` / `@include(if:)` with query variables for conditional field selection
  instead of maintaining multiple near-identical queries or [fragments](12-fragments.md).
- Implement custom schema directives via the schema-transform pattern (e.g.
  `mapSchema`/`getDirective` in `@graphql-tools`), wrapping the field's `resolve`, rather
  than the removed `SchemaDirectiveVisitor` class API.
- If you build an `@auth`/`@hasRole` directive, treat it as defence-in-depth over explicit
  resolver checks, not a replacement — a missing directive must fail closed, and the policy
  should still be readable at the resolver. See [authorization](19-authorization.md).
- Validate custom directive arguments at schema-build time; a typo in a directive arg should
  fail the build, not silently no-op at runtime.
- In a [federated](23-federation.md) graph, respect the reserved federation directives
  (`@key`, `@shareable`, `@external`, etc.) and namespace your own to avoid collisions.
- Use `@specifiedBy(url:)` to point custom scalars at their specification for tooling.

## Examples

**Good Example** — built-ins plus a wrapping auth directive

```graphql
directive @auth(requires: Role!) on FIELD_DEFINITION

type Query {
  # @deprecated documents the migration path; tooling warns clients.
  legacyStats: Stats @deprecated(reason: "Use `metrics` instead; removal 2026-12.")
  # Declarative auth as defence-in-depth over the resolver's own check.
  adminPanel: AdminData @auth(requires: ADMIN)
}

query Feed($detailed: Boolean!) {
  posts {
    id
    # @include keeps ONE query for both list and detail views.
    body @include(if: $detailed)
  }
}
```

```ts
// Schema-transform pattern: wrap resolve; fail CLOSED if identity is missing.
function authDirectiveTransformer(schema) {
  return mapSchema(schema, {
    [MapperKind.OBJECT_FIELD]: (fieldConfig) => {
      const directive = getDirective(schema, fieldConfig, "auth")?.[0];
      if (!directive) return fieldConfig;
      const { resolve = defaultFieldResolver } = fieldConfig;
      fieldConfig.resolve = (src, args, ctx, info) => {
        if (!ctx.user || !ctx.user.roles.includes(directive.requires)) {
          throw new GraphQLError("Forbidden", { extensions: { code: "FORBIDDEN" } });
        }
        return resolve(src, args, ctx, info);
      };
      return fieldConfig;
    },
  });
}
```

**Bad Example** — business logic hidden in a directive, no deprecation path

```graphql
type Query {
  # A directive that silently recomputes/overwrites the price: invisible control flow,
  # untestable outside the engine, and reviewers never see it in the resolver.
  price: Money @computeDiscount(strategy: "seasonal")
  # Field removed outright — no @deprecated, breaking every client with no warning.
}
```

## Common Mistakes

- Burying authorization or pricing/business logic inside a directive where review misses it.
- Removing a field without `@deprecated` first, breaking clients silently.
- Writing custom directives whose result depends on ordering relative to other directives.
- Using the removed `SchemaDirectiveVisitor` API instead of the `mapSchema` transform pattern.
- An `@auth` directive that fails *open* (no-ops) when identity is absent instead of denying.
- Maintaining duplicate queries instead of one query with `@skip`/`@include` variables.
- Colliding custom directive names with reserved federation directives.

## AI Review Checklist

- Are built-in directives used where they suffice, before any custom directive?
- Does every deprecated field carry `@deprecated(reason: ...)` pointing to a replacement?
- Is a custom directive implemented with the `mapSchema`/`getDirective` transform pattern?
- Does an auth directive fail *closed* and complement (not replace) resolver-level checks?
- Is directive behaviour order-independent and idempotent?
- Are directive arguments validated at schema-build time, not silently ignored?
- Do custom directive names avoid colliding with reserved federation directives?

## Related

- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/19-authorization.md`
- `knowledge/graphql/12-fragments.md`
- `knowledge/graphql/23-federation.md`
- `knowledge/graphql/29-schema-evolution.md`
