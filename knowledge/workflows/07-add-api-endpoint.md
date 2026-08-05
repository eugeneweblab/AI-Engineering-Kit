---
id: workflows/07-add-api-endpoint
topic: workflows
slug: add-api-endpoint
title: "Workflow — Add an API Endpoint"
type: doc
order: 7
status: ready
tags: [workflows, add-api-endpoint]
related: [rest-api/04-endpoints, nestjs/04-controllers, examples/01-rest-endpoint]
  - rest-api/03-resource-design
  - rest-api/06-request-response
  - rest-api/07-status-codes
  - rest-api/08-validation
  - rest-api/09-error-handling
  - rest-api/14-versioning
  - rest-api/21-openapi
  - rest-api/98-production-checklist
  - architecture/11-api-first
  - security/09-input-validation
  - security/04-authorization
  - testing/12-api-testing
  - nestjs/04-controllers
when_to_use: "Follow this workflow when adding a new API endpoint to an existing project."
---
# Workflow — Add an API Endpoint

## Purpose

This workflow defines the standard process for implementing a new API endpoint in an existing project.

The objective is to create a predictable, secure, maintainable, and well-documented API that follows the project's existing architecture and conventions.

An API endpoint is part of a contract with its consumers.

Changes should be deliberate and backward compatible whenever possible.

---

## Goal

Implement an endpoint that:

- satisfies business requirements;
- follows existing API conventions;
- validates all input;
- returns consistent responses;
- handles errors correctly;
- is secure;
- is testable.

---

## Workflow Overview

```
Understand Requirements
        ↓
Analyze Existing API
        ↓
Design Contract
        ↓
Validate Inputs
        ↓
Implement Business Logic
        ↓
Implement Endpoint
        ↓
Handle Errors
        ↓
Test
        ↓
Document
        ↓
Complete
```

---

## Step 1 — Understand the Requirements

Determine:

- business objective;
- endpoint purpose;
- request flow;
- response expectations;
- authentication requirements;
- authorization requirements;
- validation rules.

Do not implement an endpoint based on assumptions.

Gather the context before designing anything — see
[Engineering — Context-First Development](../engineering/05-context-first-development.md).
The constraints that shape an endpoint are described in
[REST API — REST Principles](../rest-api/02-rest-principles.md).

---

## Step 2 — Analyze Existing APIs

Inspect similar endpoints.

Review:

- routing conventions;
- controller structure;
- services;
- DTOs;
- validation;
- error handling;
- response format;
- authentication middleware;
- logging.

New endpoints should look like existing endpoints.

Relevant knowledge:

- [REST API — Endpoints](../rest-api/04-endpoints.md) and [REST API — Routing](../rest-api/05-routing.md) — the naming and path conventions your new route must match.
- [NestJS — Controllers](../nestjs/04-controllers.md) — how request handling is structured in a NestJS codebase.

---

## Step 3 — Design the API Contract

Define the endpoint before writing code.

Specify:

Method

Path

Request body

Query parameters

Path parameters

Headers

Authentication

Authorization

Success response

Error responses

HTTP status codes

The contract should remain stable.

Relevant knowledge:

- [Architecture — API First](../architecture/11-api-first.md) — agreeing on the contract before writing the implementation.
- [REST API — Resource Design](../rest-api/03-resource-design.md) — modelling the URL as a resource rather than an action.
- [REST API — Request and Response](../rest-api/06-request-response.md) and [REST API — Status Codes](../rest-api/07-status-codes.md) — payload shape and the correct code for each outcome.
- [REST API — Versioning](../rest-api/14-versioning.md) — when the change would break existing consumers.
- [REST API — Idempotency](../rest-api/18-idempotency.md) — for operations a client may safely retry.

---

## Step 4 — Validate Input

Validate every external input.

Examples:

- required fields;
- string length;
- numeric ranges;
- enum values;
- dates;
- UUIDs;
- email addresses;
- file uploads.

Never trust client input.

Relevant knowledge:

- [REST API — Validation](../rest-api/08-validation.md) — validating at the transport boundary.
- [Security — Input Validation](../security/09-input-validation.md) — allow-list validation and why rejecting is safer than sanitizing.
- [NestJS — Validation](../nestjs/08-validation.md), [NestJS — DTO](../nestjs/07-dto.md), and [NestJS — Pipes](../nestjs/12-pipes.md) — declarative validation with DTOs and `ValidationPipe`.
- [Security — File Upload Security](../security/15-file-upload-security.md) — when the endpoint accepts uploads.

---

## Step 5 — Implement Business Logic

Business rules belong in the business layer.

Avoid placing business logic inside:

- controllers;
- route handlers;
- middleware.

Controllers should coordinate work, not perform it.

Relevant knowledge:

- [Architecture — Clean Architecture](../architecture/03-clean-architecture.md) — keeping domain rules independent of the HTTP layer.
- [NestJS — Services](../nestjs/05-services.md) and [NestJS — Repositories](../nestjs/06-repositories.md) — where business logic and data access belong.
- [Databases — Transactions](../databases/09-transactions.md) and [NestJS — Transactions](../nestjs/18-transactions.md) — when the endpoint writes to more than one table.

---

## Step 6 — Implement the Endpoint

The endpoint should:

- receive the request;
- validate input;
- call the appropriate service;
- return the response;
- handle errors consistently.

Keep controllers small.

Relevant knowledge:

- [NestJS — Guards](../nestjs/09-guards.md) and [NestJS — Interceptors](../nestjs/10-interceptors.md) — enforcing access and shaping responses without bloating the handler.
- [REST API — Pagination](../rest-api/10-pagination.md), [REST API — Filtering](../rest-api/11-filtering.md), and [REST API — Sorting](../rest-api/12-sorting.md) — for collection endpoints; never return an unbounded list.

---

## Step 7 — Handle Errors

Return predictable error responses.

Verify:

- validation failures;
- unauthorized access;
- forbidden actions;
- missing resources;
- conflicts;
- unexpected failures.

Never expose internal implementation details.

Relevant knowledge:

- [REST API — Error Handling](../rest-api/09-error-handling.md) — one error envelope for the whole API.
- [REST API — Status Codes](../rest-api/07-status-codes.md) — `400` vs `401` vs `403` vs `404` vs `409` vs `422`.
- [NestJS — Exception Filters](../nestjs/11-exception-filters.md) — centralizing error translation instead of try/catch in every handler.

---

## Step 8 — Test the Endpoint

Verify:

- valid requests;
- invalid requests;
- missing fields;
- unauthorized access;
- forbidden access;
- unexpected errors;
- edge cases.

Every public endpoint should be tested.

Relevant knowledge:

- [Testing — API Testing](../testing/12-api-testing.md) and [REST API — Testing](../rest-api/23-testing.md) — request/response coverage at the HTTP boundary.
- [Testing — Contract Testing](../testing/11-contract-testing.md) — protecting consumers from an accidental contract change.
- [Testing — Security Testing](../testing/17-security-testing.md) — proving that authentication and authorization actually reject the wrong caller.
- [NestJS — Testing](../nestjs/25-testing.md) — framework-level patterns for controller and e2e tests.

---

## Step 9 — Update Documentation

Update documentation when required.

Examples:

- OpenAPI / Swagger;
- API reference;
- README;
- Postman collection;
- environment variables;
- authentication guide.

Documentation is part of the API.

Relevant knowledge:

- [REST API — OpenAPI](../rest-api/21-openapi.md) and [REST API — Swagger](../rest-api/22-swagger.md) — keeping the machine-readable spec in step with the code.
- [Architecture — Documentation](../architecture/25-documentation.md) — what belongs in project docs versus the spec.

---

## API Design Principles

Prefer:

Resource-oriented endpoints

Consistent naming

Standard HTTP methods

Predictable responses

Consistent error format

Idempotent operations when appropriate

Avoid:

RPC-style naming

Inconsistent status codes

Multiple response formats

Hidden side effects

Breaking existing consumers

---

## AI Execution Checklist

## Investigation

☐ Read the requirements.

☐ Review similar endpoints.

☐ Review routing conventions.

☐ Review authentication.

☐ Review response format.

---

## Planning

☐ Define API contract.

☐ Define validation rules.

☐ Define error responses.

☐ Identify reusable services.

---

## Implementation

☐ Reuse existing architecture.

☐ Keep controllers thin.

☐ Validate all input.

☐ Preserve response consistency.

☐ Avoid duplicate business logic.

---

## Verification

☐ Test successful requests.

☐ Test validation failures.

☐ Test authentication.

☐ Test authorization.

☐ Test error responses.

☐ Update documentation.

---

## Security Checklist

Before completion verify:

☐ Authentication is enforced.

☐ Authorization is enforced.

☐ Input is validated.

☐ Sensitive information is not exposed.

☐ Error messages are safe.

☐ Logging contains useful information.

☐ Secrets are never returned.

Relevant knowledge:

- [Security — Authentication](../security/03-authentication.md) and [Security — Authorization](../security/04-authorization.md) — verify identity, then verify permission on the specific resource.
- [REST API — Rate Limiting](../rest-api/17-rate-limiting.md) and [Security — Rate Limiting](../security/21-rate-limiting.md) — protect expensive or unauthenticated endpoints.
- [REST API — Security](../rest-api/24-security.md) and [Security — OWASP Top 10](../security/28-owasp-top10.md) — the failure modes that recur in HTTP APIs.
- [Security — Secrets Management](../security/16-secrets-management.md) — keys and tokens never travel in a response body or a log line.

---

## Examples

**Good Example** — the contract is decided before the handler is written

```text
POST /api/v1/events/{eventId}/signups        register the current user

201  { "id": 4471, "status": "confirmed" }
400  validation failed
401  not authenticated
403  event not open to this user
404  event does not exist
409  already registered | event full | event already started
429  rate limited
```

```ts
// The handler follows the contract, and the errors are distinguishable.
export async function POST(request: NextRequest, { params }: { params: Promise<{ eventId: string }> }) {
  const session = await auth();
  if (!session) return problem(401, 'not_authenticated');

  const { eventId } = await params;
  const body = CreateSignup.safeParse(await request.json().catch(() => null));
  if (!body.success) return problem(400, 'validation_failed', z.treeifyError(body.error));

  const result = await signupsService.register(eventId, session.userId, body.data);

  if (result.error === 'EVENT_FULL') return problem(409, 'event_full');
  if (result.error === 'NOT_FOUND') return problem(404, 'event_not_found');

  return Response.json({ id: result.id, status: 'confirmed' }, { status: 201 });
}
```

Deciding the codes first is what keeps them consistent across endpoints, and it is what lets
the client handle "full" differently from "already registered".

**Bad Example** — the contract emerges from the implementation

```ts
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const id = await signup(body.eventId, body.userId);   // userId from the body
    return Response.json({ ok: true, id });
  } catch (e) {
    // Every failure is a 500 with a message string. The client cannot tell
    // "event full" from "database down", so it retries both — or neither.
    return Response.json({ ok: false, error: String(e) }, { status: 500 });
  }
}
```

`userId` from the request body means any caller can sign up any user. The contract was never
written down, so nobody noticed.

---

## Common Mistakes

Avoid:

Embedding business logic in controllers.

Skipping validation.

Returning inconsistent response formats.

Using incorrect HTTP status codes.

Creating duplicate services.

Ignoring authorization.

Breaking existing API contracts.

Forgetting documentation.

---

## Completion Criteria

The workflow is complete only if:

- requirements are satisfied;
- API contract is implemented;
- validation is complete;
- authentication and authorization are correct;
- responses follow project standards;
- tests pass;
- documentation is updated.

---

## Expected AI Output

After completing this workflow, the AI should explain:

- endpoint purpose;
- request structure;
- response structure;
- validation strategy;
- reused services;
- modified files;
- testing performed;
- remaining considerations.

---

## Self-Verification — Topic Checklists

Before marking the endpoint complete, run it through the `98`/`99`/`100` checklists of the
topics it touches:

- REST API — [Production Checklist](../rest-api/98-production-checklist.md), [AI Review Checklist](../rest-api/99-ai-review-checklist.md), [Common Antipatterns](../rest-api/100-common-antipatterns.md).
- Security — [Production Checklist](../security/98-production-checklist.md), [AI Review Checklist](../security/99-ai-review-checklist.md), [Common Antipatterns](../security/100-common-antipatterns.md).
- Testing — [Production Checklist](../testing/98-production-checklist.md), [AI Review Checklist](../testing/99-ai-review-checklist.md), [Common Antipatterns](../testing/100-common-antipatterns.md).

If the endpoint is implemented in NestJS, close with
[NestJS — Production Checklist](../nestjs/98-production-checklist.md),
[NestJS — AI Review Checklist](../nestjs/99-ai-review-checklist.md), and
[NestJS — Common Antipatterns](../nestjs/100-common-antipatterns.md). When the endpoint adds
database queries, also review
[Databases — Query Optimization](../databases/08-query-optimization.md) and
[Performance — API Performance](../performance/14-api-performance.md).

---

## Summary

A well-designed API endpoint is predictable, secure, and easy to maintain.

The endpoint should integrate seamlessly into the existing API, follow established conventions, and provide a stable contract for all consumers.

## Related

- `knowledge/rest-api/04-endpoints.md`
- `knowledge/nestjs/04-controllers.md`
- `knowledge/examples/01-rest-endpoint.md`
