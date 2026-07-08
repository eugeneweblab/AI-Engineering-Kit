---
id: testing/12-api-testing
topic: testing
slug: api-testing
title: "API Testing"
type: doc
order: 12
status: ready
tags: [testing, api-testing]
related: [testing/03-integration-testing, testing/11-contract-testing, testing/04-e2e-testing, testing/17-security-testing, testing/09-assertions]
when_to_use: "Read before writing or reviewing tests that exercise an HTTP, GraphQL, or RPC endpoint through its real contract."
---
# API Testing

## Purpose

This document defines how to test an API through its public contract: routing, status
codes, headers, request validation, response shape, and error semantics. It covers the
layer between a single-unit test and a full browser [E2E test](04-e2e-testing.md) — you
send a real request to a running handler and assert on the real response.

An API test treats the service as a black box reachable over the wire. It does not reach
into internal functions; it proves the *observable contract* other systems depend on.

## Why It Matters

An API is a promise to every client that already ships against it. A silently changed
status code, a renamed field, or a loosened validation rule breaks callers you cannot
see and cannot redeploy. Unit tests miss these failures because they never exercise
serialization, routing, middleware, auth, or content negotiation — the exact seams
where API bugs live. API tests are the cheapest place to catch a contract break before a
consumer does, which is why they sit just above integration tests in the pyramid.

## Core Principles

- **Assert the contract, not the implementation.** Test status code, body shape,
  headers, and error format. A refactor that preserves the response must keep the test
  green.
- **Test through the real transport.** Send an actual HTTP request to the app's router
  and middleware stack. Calling the controller function directly skips the layers where
  bugs hide.
- **Every endpoint has a negative contract.** Validation errors, auth failures, and
  not-found responses are part of the API — test them as deliberately as the happy path.
- **Each test owns its data.** Create the state a test needs and clean it up. Tests that
  depend on shared, pre-existing rows are order-dependent and flaky.
- **Status code and error shape are load-bearing.** Clients branch on them. `400` vs
  `422`, `401` vs `403`, and the error envelope are behavior, not decoration.

## Best Practices

- Drive the app with an in-process HTTP client (`supertest`, `httpx`, `TestClient`,
  `MockMvc`) so you exercise routing and middleware without a network port.
- Assert status, then body, then headers — in that order. A wrong status often makes
  body assertions meaningless.
- Validate the response against a schema (JSON Schema, Zod, Pydantic) so an unexpected
  extra or missing field fails the test, not just the fields you happened to check.
- Cover the auth matrix per endpoint: unauthenticated, authenticated-but-forbidden, and
  authorized. Missing authz checks are the most common API vulnerability.
- Test boundary inputs: empty body, oversized payload, wrong content type, malformed
  JSON, and unknown fields. Assert the exact `4xx` the contract promises.
- Seed data through the API or a factory, not raw SQL, so tests break when the write path
  breaks — that is a feature.
- Keep provider-side [contract tests](11-contract-testing.md) separate: API tests verify
  *your* behavior; contract tests verify agreement with a named consumer.

## Examples

**Good Example** — real request, contract asserted, negative path covered

```ts
import request from "supertest";
import { app } from "../app";

it("rejects a user with an invalid email (422 + error shape)", async () => {
  const res = await request(app)
    .post("/users")
    .send({ email: "not-an-email", name: "Ada" });

  expect(res.status).toBe(422);                 // validation failure, not 400 or 500
  expect(res.body).toEqual({                    // full envelope, so a shape change fails
    error: "validation_error",
    fields: { email: "must be a valid email" },
  });
});

it("creates a user and returns 201 with a Location header", async () => {
  const res = await request(app)
    .post("/users")
    .send({ email: "ada@example.com", name: "Ada" });

  expect(res.status).toBe(201);
  expect(res.headers.location).toMatch(/^\/users\/[\w-]+$/); // header is part of contract
  expect(res.body).toMatchObject({ email: "ada@example.com", name: "Ada" });
});
```

**Bad Example** — bypasses transport, asserts nothing that clients depend on

```ts
import { createUser } from "../controllers/users";

it("creates a user", async () => {
  // Calls the controller directly: skips routing, validation middleware, and
  // serialization — the exact layers an API test exists to cover.
  const user = await createUser({ email: "not-an-email", name: "Ada" });

  expect(user).toBeDefined(); // passes even when the API returns a 500 to real clients
});
```

## Common Mistakes

- Calling controller/handler functions directly instead of sending a request, so routing,
  middleware, and serialization go untested.
- Asserting only `res.status === 200` and never checking the body or error shape.
- Testing only the happy path; leaving validation, auth, and not-found responses uncovered.
- Depending on data created by a previous test, making the suite order-dependent.
- Hard-coding volatile fields (timestamps, generated IDs) into exact-match assertions,
  causing flakiness — match their shape instead.
- Hitting real third-party APIs in the test; stub them at the network boundary so tests
  are deterministic and offline-safe.

## Production Tips

- Generate tests or fixtures from the OpenAPI/GraphQL schema so the spec and the suite
  cannot drift apart.
- Run the API test suite in CI against an ephemeral database and record request/response
  logs on failure — they make triage a glance instead of a repro.
- Add a smoke subset that runs against a deployed staging URL after each release to catch
  environment- and infra-specific breakage.

## AI Review Checklist

- Does each test send a real request through routing and middleware, not call a handler?
- Are status code, body shape, and load-bearing headers all asserted?
- Is the negative contract (validation, `401`/`403`, `404`) covered per endpoint?
- Is the response validated against a schema so unexpected fields fail the test?
- Does each test create and clean up its own data, with no cross-test dependency?
- Are external services stubbed at the boundary so the suite is deterministic?

## Related

- `knowledge/testing/03-integration-testing.md`
- `knowledge/testing/11-contract-testing.md`
- `knowledge/testing/04-e2e-testing.md`
- `knowledge/testing/17-security-testing.md`
- `knowledge/testing/09-assertions.md`
