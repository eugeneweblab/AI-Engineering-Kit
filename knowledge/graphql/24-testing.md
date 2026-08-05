---
id: graphql/24-testing
topic: graphql
slug: testing
title: "GraphQL Testing"
type: doc
order: 24
status: ready
tags: [graphql, testing, errors, graphql, toBe, toEqual, serialize, parseValue]
related: [graphql/07-resolvers, graphql/16-dataloader, graphql/20-error-handling, graphql/29-schema-evolution, graphql/25-monitoring]
when_to_use: "Read before writing or reviewing tests for a GraphQL schema, resolvers, or client operations."
---
# GraphQL Testing

## Purpose

This document defines how to test a GraphQL API: unit-testing resolvers, running
integration tests against an executable schema, asserting on the response envelope,
and guarding the schema against breaking changes in CI. It is written so an agent can
add tests that catch real defects instead of restating the resolver's implementation.

GraphQL shifts where bugs hide. The transport is uniform, so the interesting failures
live in resolvers, in the `data`/`errors` split, in N+1 batching, and in schema drift.
Test those, not the HTTP plumbing the framework already covers.

## Why It Matters

A GraphQL response is always HTTP `200` even when a resolver throws — the failure is in
the `errors` array, not the status code. A test that only asserts `status === 200` passes
while the query is completely broken. GraphQL also lets clients select fields freely, so
one endpoint has a combinatorial surface: partial failures, nullability propagation, and
per-field authorization all need their own coverage. And because the schema is a shared
contract, an untested field rename silently breaks every consumer at once.

## Core Principles

- **Assert on `data` and `errors`, never on the HTTP status.** A `200` with an `errors`
  array is a failed operation. Check both halves of the envelope.
- **Execute against the real schema.** Run operations through the executable schema (via
  `graphql()` / `executor`), not by calling resolver functions in isolation only. That is
  the layer clients actually hit.
- **Test the contract, not the implementation.** Assert on the query result shape, so the
  test survives a resolver refactor. Snapshotting internal call counts makes tests brittle.
- **Cover nullability and partial failure.** A non-null field that errors nulls its parent;
  a nullable field that errors returns `null` plus an `errors` entry. Both need a test.
- **Fail the build on breaking schema changes.** Run a schema-diff check in CI so a
  contract break is a red pipeline, not a production incident.

## Best Practices

- Write integration tests that submit a real operation document and assert on the JSON
  result. Prefer this over calling resolvers directly — it exercises validation, coercion,
  and error mapping too.
- Keep unit tests for the parts with real logic: DataLoader batch functions, custom scalar
  `serialize`/`parseValue`, complex field resolvers, and authorization guards.
- Assert that a DataLoader batches: seed the DB, run a list query, and assert the loader's
  batch function was called once — this is the only reliable regression test for N+1.
- Test the error path explicitly: unauthorized access returns the right `errors[].extensions.code`
  and a `null` (not a leaked internal message). See [error handling](20-error-handling.md).
- Run `assertValidSchema` (or your codegen build) in CI so an invalid SDL fails fast.
- Diff every schema change against the deployed version with a tool like GraphQL Inspector;
  block `BREAKING` changes unless explicitly approved. See [schema evolution](29-schema-evolution.md).
- Type client operations with codegen and let the type-checker catch selection-set drift.

## Examples

**Good Example** — execute against the schema, assert the full envelope

```ts
import { graphql } from "graphql";
import { schema } from "../schema";

test("returns the user, no errors", async () => {
  const result = await graphql({
    schema,
    source: `{ user(id: "1") { id name } }`,
    contextValue: { loaders: makeLoaders(), viewer: adminViewer },
  });

  // Assert BOTH halves: a 200 with errors is still a failure.
  expect(result.errors).toBeUndefined();
  expect(result.data).toEqual({ user: { id: "1", name: "Ada" } });
});

test("unauthorized access surfaces a coded error, not data", async () => {
  const result = await graphql({
    schema,
    source: `{ user(id: "1") { email } }`,
    contextValue: { loaders: makeLoaders(), viewer: anonViewer },
  });

  expect(result.data?.user).toBeNull();
  // Assert the machine-readable code, not the human message (which may change).
  expect(result.errors?.[0].extensions?.code).toBe("FORBIDDEN");
});
```

**Bad Example** — asserts transport, ignores GraphQL errors

```ts
test("user query works", async () => {
  const res = await request(app)
    .post("/graphql")
    .send({ query: `{ user(id: "1") { name } }` });

  expect(res.status).toBe(200); // ALWAYS 200 in GraphQL — proves nothing
  // Never inspects res.body.errors, so a thrown resolver passes this test.
  // Never inspects res.body.data, so a null field passes too.
});
```

## Common Mistakes

- Asserting `status === 200` and stopping — the operation can fail inside a `200`.
- Testing resolvers as plain functions only, bypassing validation, coercion, and directives.
- Snapshotting the entire response, so every legitimate field addition breaks the test.
- No N+1 regression test, so a lost DataLoader silently reintroduces per-row queries.
- Forgetting the null-propagation case: a non-null child error nulls the whole parent.
- No schema-diff gate, so a field rename ships and breaks clients unnoticed.
- Mocking the schema so heavily the test no longer reflects the real executable schema.

## Production Tips

- Run the schema-diff check against the schema currently serving production traffic, not
  against `main` — those can differ during a rollout.
- Seed integration tests through the same persistence layer the resolvers use, so batching
  and transaction behavior are exercised realistically.
- Add a smoke test that runs your top production operations (pulled from monitoring) after
  each deploy. See [monitoring](25-monitoring.md).

## AI Review Checklist

- Do tests assert on both `data` and `errors`, never on the HTTP status alone?
- Are operations executed through the real executable schema, not just raw resolver calls?
- Is there a test proving each DataLoader batches (batch function called once)?
- Are authorization failures asserted via `extensions.code`, with no internal leak?
- Is a breaking-schema-change diff gate wired into CI?
- Do tests assert result shape rather than snapshotting internal call sequences?
- Is the null-propagation behavior of non-null fields covered?

## Related

- `knowledge/graphql/07-resolvers.md`
- `knowledge/graphql/16-dataloader.md`
- `knowledge/graphql/20-error-handling.md`
- `knowledge/graphql/29-schema-evolution.md`
- `knowledge/graphql/25-monitoring.md`
