---
id: graphql/99-ai-review-checklist
topic: graphql
slug: ai-review-checklist
title: "GraphQL AI Review Checklist"
type: checklist
order: 99
status: ready
tags: [graphql, ai-review-checklist]
related: [graphql/07-resolvers, graphql/15-n1-problem, graphql/17-security, graphql/20-error-handling, graphql/100-common-antipatterns]
when_to_use: "Read when reviewing a GraphQL schema, resolver, or diff before approving it."
---
# GraphQL AI Review Checklist

## Purpose

A focused checklist for reviewing GraphQL code — schema definitions, resolvers, and the
diffs that touch them. Each item is a yes/no an agent can verify by reading the change.
Use it as the last gate before approving a pull request that adds or modifies graph
surface. It complements the [production checklist](98-production-checklist.md), which
covers the running service; this one covers the code under review.

## Why It Matters

Most GraphQL defects are invisible in a passing test suite: an N+1 that only bites under
a list, a non-null field that will null its parent on the first downstream hiccup, a
newly non-null argument that breaks every existing client. These are review-time catches,
not runtime catches. A disciplined checklist turns "looks fine" into a set of concrete
questions with concrete answers.

## Schema Changes

**Rules:** [Schema](02-schema.md) · [Schema Evolution](29-schema-evolution.md)

- [ ] Is the change **additive**? Removing/renaming a field or making an argument non-null
      is breaking — confirm deprecation and usage data first.
- [ ] Does new nullability match reality? Non-null only where the server can **always**
      produce the value.
- [ ] Do new list fields use a **paginated connection**, not a bare array?
- [ ] Do names follow the schema's conventions (camelCase fields, PascalCase types) and
      model the **domain**, not database columns?
- [ ] Are new enums used instead of free-form strings for closed value sets?

## Resolvers

**Rules:** [Resolvers](07-resolvers.md) · [DataLoader](16-dataloader.md)

- [ ] Does any new field-on-a-list resolver fetch per-item without a **DataLoader**? (N+1)
- [ ] Is the resolver **thin** — parse, authorize, delegate to a service — with no business
      logic inline?
- [ ] Does it read request state from **context**, never from module-level globals?
- [ ] Are `null` and empty-list cases handled explicitly, so a non-null field never
      returns `null`?
- [ ] Are external calls wrapped with timeouts and errors converted to modeled results?

## Security and Authorization

**Rules:** [Security](17-security.md) · [Authorization](19-authorization.md)

- [ ] Is **authorization** checked for the new field/type, not assumed from the parent?
- [ ] Do new inputs have **validation** (length, range, format) before use?
- [ ] Could the new field **expose** internal or other-tenant data through a nested path?
- [ ] Is any newly reachable expensive path covered by **cost/depth** limits?

## Errors

**Rules:** [Error Handling](20-error-handling.md)

- [ ] Are expected failures modeled as **data** (unions/result types), reserving GraphQL
      errors for faults?
- [ ] Do thrown errors carry a stable **code** and no sensitive detail (stack, SQL)?

## Tests

**Rules:** [Testing](24-testing.md)

- [ ] Is there a test that would **fail on an N+1** (asserts query count) for new list paths?
- [ ] Are authorization **negative cases** (forbidden viewer) tested for new fields?
- [ ] Are null/empty/boundary inputs tested for new arguments?

## AI Review Checklist

- Is the diff additive, or does it silently break existing clients?
- Does every new list-context fetch go through a batching loader?
- Is authorization enforced on the new field itself?
- Are expected failures modeled as data with stable error codes?
- Do tests cover N+1, authorization denial, and boundary inputs?

## Related

- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/15-n1-problem.md`
- `knowledge/graphql/17-security.md`
- `knowledge/graphql/20-error-handling.md`
- `knowledge/graphql/100-common-antipatterns.md`
