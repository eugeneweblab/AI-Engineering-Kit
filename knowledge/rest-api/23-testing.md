---
id: rest-api/23-testing
topic: rest-api
slug: testing
title: "REST API Testing"
type: doc
order: 23
status: ready
tags: [rest-api, testing, send, toBe, toContainEqual, toMatch, objectContaining, toBeDefined]
related: [rest-api/09-error-handling, rest-api/08-validation, rest-api/21-openapi, rest-api/16-authorization, rest-api/07-status-codes]
when_to_use: "Read before writing tests for a REST API — endpoint behavior, contracts, auth, or error paths."
---
# REST API Testing

## Purpose

This document defines how to test a REST API so that its contract, not just its
internals, is verified. It covers what to test at each layer (unit, integration,
contract, end-to-end), how to assert on HTTP behavior — status, headers, body — and how
to cover the failure paths that matter most. The goal is a suite that catches a broken
contract before a client does.

Testing answers "does this API still do what it promises, for every caller, on every
path?".

## Why It Matters

An API's tests are its safety net for change. Untested endpoints mean every refactor is
a gamble and every deploy carries the risk of silently breaking a client you cannot see.
The failures that hurt most in production are rarely the happy path — they are the
`401` that became a `500`, the validation that stopped rejecting bad input, the
pagination that broke on an empty page, the status code that changed from `201` to
`200`. These are cheap to catch in a test and expensive to catch in an incident.
Because an API is a contract with external consumers, its tests must exercise the
contract from the outside — the same way a client experiences it — not just the
functions behind it.

## Core Principles

- **Test the HTTP contract, not the handler internals.** Send real requests and assert
  on status code, headers, and response body. A test that calls the service function
  directly misses routing, serialization, middleware, and auth — exactly where contract
  bugs live.
- **Cover the failure paths deliberately.** Wrong input, missing auth, forbidden access,
  not-found, conflict, and rate-limit responses each need a test. Untested error paths
  are where a `4xx` quietly degrades into a `500`.
- **Make tests deterministic and isolated.** No shared mutable state, no reliance on
  test order, no wall-clock or network flakiness. Each test sets up its own data and
  tears it down. A flaky suite gets ignored, which is worse than no suite.
- **Shape the pyramid.** Many fast unit tests, a solid layer of integration tests
  through the real HTTP stack, and a few end-to-end tests. Do not push everything to
  slow E2E tests.
- **Verify against the contract source.** Assert responses conform to the
  [OpenAPI](21-openapi.md) schema so the spec and the implementation cannot drift apart.

## Best Practices

- Use an HTTP-level client (e.g. `supertest`) against the real app instance so routing,
  middleware, and serialization are exercised.
- Assert on the full contract of a response: status code, key headers (`Location`,
  `Content-Type`, `Cache-Control`), and body shape — not just the status.
- Test authorization explicitly: same request as the owner (`200`), as another user
  (`403`/`404`), and with no credentials (`401`). Auth bugs hide between these cases.
- Drive validation tests from boundary and malformed inputs; assert the error status and
  the machine-readable error body, per [error handling](09-error-handling.md).
- Run integration tests against a real database (a disposable container), not mocks, so
  query and transaction behavior is covered. Reset state between tests.
- Add contract tests that validate live responses against the OpenAPI schema, failing
  the build when the implementation diverges from the spec.
- Keep tests fast and parallelizable; put them in CI as a merge gate.

## Examples

**Good Example** — behavioral test through the HTTP stack

```ts
import request from "supertest";
import { app } from "../app";

describe("POST /orders", () => {
  it("creates an order and returns 201 with a Location header", async () => {
    const res = await request(app)
      .post("/orders")
      .set("Authorization", `Bearer ${userToken}`)
      .send({ sku: "ABC-1", qty: 2 });

    expect(res.status).toBe(201);              // contract: created
    expect(res.headers.location).toMatch(/\/orders\/.+/); // contract: where it lives
    expect(res.body).toMatchObject({ sku: "ABC-1", qty: 2, status: "pending" });
  });

  it("rejects a missing qty with 422 and a field error", async () => {
    const res = await request(app)
      .post("/orders")
      .set("Authorization", `Bearer ${userToken}`)
      .send({ sku: "ABC-1" });                 // invalid input on purpose

    expect(res.status).toBe(422);              // failure path is a first-class test
    expect(res.body.errors).toContainEqual(expect.objectContaining({ field: "qty" }));
  });

  it("returns 401 without a token", async () => {
    const res = await request(app).post("/orders").send({ sku: "ABC-1", qty: 1 });
    expect(res.status).toBe(401);              // auth boundary is explicitly asserted
  });
});
```

**Bad Example** — tests internals, ignores the contract

```ts
it("creates an order", async () => {
  // Calls the service directly: skips routing, auth middleware, and serialization —
  // the exact layers where contract bugs occur. A broken route still passes.
  const order = await orderService.create({ sku: "ABC-1", qty: 2 });
  expect(order).toBeDefined(); // asserts nothing about status, headers, or body shape
  // No failure-path, no auth, no validation coverage at all.
});
```

## Common Mistakes

- Testing service functions directly and never the HTTP layer, so routing, auth, and
  serialization bugs ship untested.
- Asserting only the status code and ignoring headers and body shape.
- Covering only the happy path, leaving `401`/`403`/`404`/`422` untested until they
  break in production.
- Flaky tests from shared state, ordering assumptions, or real external network calls.
- Over-mocking the database so query and transaction bugs never surface in tests.
- Letting the spec and implementation drift because nothing tests responses against the
  contract.

## Production Tips

- Gate merges on the suite; a green build should mean the contract still holds.
- Run smoke tests against a staging deploy to catch environment and config differences
  that unit tests cannot.
- Track coverage on error branches specifically — happy-path coverage numbers hide
  untested failure paths.

## AI Review Checklist

- Do tests exercise real HTTP requests through the app, not just internal functions?
- Is each response asserted on status, relevant headers, and body shape?
- Are the auth cases (owner, other user, anonymous) each tested?
- Are validation and error paths covered with their status and error body?
- Are integration tests run against a real database with state reset between them?
- Are responses validated against the OpenAPI contract to prevent drift?
- Is the suite deterministic and wired as a CI merge gate?

## Related

- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/21-openapi.md`
- `knowledge/rest-api/16-authorization.md`
- `knowledge/rest-api/07-status-codes.md`
