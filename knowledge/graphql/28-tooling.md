---
id: graphql/28-tooling
topic: graphql
slug: tooling
title: "Tooling"
type: doc
order: 28
status: ready
tags: [graphql, tooling]
related: [graphql/02-schema, graphql/03-types, graphql/24-testing, graphql/29-schema-evolution, graphql/26-best-practices]
when_to_use: "Read before choosing a GraphQL server, setting up codegen, or wiring schema checks into CI."
---
# Tooling

## Purpose

This document defines the tooling that makes a GraphQL project safe to build and evolve:
type codegen, schema linting, breaking-change detection, and a schema registry. It focuses
on wiring these into the build so the machine enforces the schema contract instead of humans
remembering to.

GraphQL's payoff is a typed, introspectable contract. That payoff only materializes if the
tooling turns the schema into compile-time types and CI gates. Without it, you have a typed
schema and untyped, hope-based clients.

## Why It Matters

The schema is a strongly typed contract, but nothing enforces that your resolvers and clients
match it unless tooling does. Hand-written resolver and client types drift from the SDL the
moment someone edits one and not the other — and the drift surfaces as a runtime `null` or a
production error, not a red build. Codegen closes that gap by making the schema the single
source of truth for types on both ends. Schema-diff tooling closes the other gap: it catches a
breaking change in review, before it reaches the clients you cannot see.

## Core Principles

- **The schema is the single source of truth.** Generate resolver and operation types from it;
  never hand-maintain types that duplicate the schema. Duplicated types drift and lie.
- **Enforce the contract in CI, not in review comments.** Lint, diff, and validate the schema
  in the pipeline. A human forgetting to check is not a control.
- **Type both ends.** Server resolvers and client operations should both be generated, so a
  schema change breaks the *build*, not production.
- **Pin and publish the schema.** Keep a canonical schema artifact (registry or committed SDL)
  so every consumer and check diffs against the same reference. See [schema evolution](29-schema-evolution.md).
- **Prefer boring, standard tooling.** GraphQL Code Generator, GraphQL Inspector, and a
  standard server (Apollo, GraphQL Yoga, Mercurius) are well-trodden; exotic stacks cost you.

## Best Practices

- Run GraphQL Code Generator to produce (a) typed resolver signatures for the server and
  (b) typed hooks/documents for clients. Fail the build if generated files are stale.
- Add a schema linter (e.g. GraphQL Inspector or `graphql-schema-linter`) enforcing naming,
  nullability, and deprecation-reason conventions from [best practices](26-best-practices.md).
- Gate every PR with a breaking-change diff against the deployed schema; block `BREAKING`
  unless a reviewer explicitly approves a migration. See [testing](24-testing.md).
- Publish the schema to a registry on each deploy so clients and CI diff against the exact
  schema serving production, not against a branch.
- Keep codegen output committed and checked in CI (generate + `git diff --exit-code`) so a
  drifted type is a failed pipeline, not a surprise at runtime.
- Use editor tooling (GraphQL LSP) so field names and types autocomplete against the live
  schema, catching typos before they compile.

## Examples

**Good Example** — codegen + drift check + breaking-change gate in CI

```yaml
# codegen.yml — one config generates types for BOTH server and client.
schema: ./schema.graphql
generates:
  ./src/generated/resolvers.ts:
    plugins: [typescript, typescript-resolvers]   # typed resolver map
  ./src/generated/operations.ts:
    documents: ./src/**/*.graphql
    plugins: [typescript, typescript-operations]  # typed client documents
```

```bash
# CI: fail if generated types drifted, and block breaking schema changes.
pnpm graphql-codegen
git diff --exit-code src/generated  # stale codegen → red build, not runtime null

# Diff the PR schema against what production is actually serving.
graphql-inspector diff "git:origin/main:schema.graphql" "schema.graphql" \
  --rule considerUsage   # a removal used by no client is downgraded from BREAKING
```

**Bad Example** — hand-written types, no CI enforcement

```ts
// Hand-maintained resolver types that duplicate the schema.
type Resolvers = {
  Query: { user: (id: string) => User };  // schema says ID!, args are an object —
};                                          // this signature is already wrong and won't fail
// No codegen, so renaming `user` → `viewer` in the SDL compiles fine here.
// No schema diff in CI, so removing a field ships and breaks clients silently.
```

## Common Mistakes

- Hand-writing resolver or client types that duplicate the schema, then letting them drift.
- Running codegen locally but not checking for staleness in CI, so drift ships anyway.
- No breaking-change gate, so field removals and renames reach production unreviewed.
- Diffing against `main` instead of the schema actually deployed, missing rollout-window drift.
- Skipping the schema linter, so naming and nullability conventions erode PR by PR.
- Treating introspection JSON as the source of truth instead of committed SDL, losing history.

## Production Tips

- Wire the schema registry publish step into the deploy job, not a manual command, so the
  registry never lags what is actually running.
- Use `considerUsage` (real operation traffic from [monitoring](25-monitoring.md)) to
  distinguish a truly breaking removal from a removal of a field no client uses.
- Keep codegen fast and incremental in watch mode locally so developers get typed feedback
  as they edit `.graphql` files.

## AI Review Checklist

- Are resolver and client types generated from the schema, not hand-maintained?
- Does CI fail when generated code is stale (generate + `git diff --exit-code`)?
- Is there a breaking-change diff gate against the deployed schema on every PR?
- Is a schema linter enforcing naming, nullability, and deprecation conventions?
- Is the schema published to a registry as part of the deploy, not manually?
- Does the diff run against the production schema rather than a branch?

## Related

- `knowledge/graphql/02-schema.md`
- `knowledge/graphql/03-types.md`
- `knowledge/graphql/24-testing.md`
- `knowledge/graphql/29-schema-evolution.md`
- `knowledge/graphql/26-best-practices.md`
