---
id: architecture/11-api-first
topic: architecture
slug: api-first
title: "API First"
type: doc
order: 11
status: ready
tags: [architecture, api-first]
related: [architecture/12-integration-patterns, architecture/09-microservices, architecture/25-documentation, architecture/15-security, architecture/26-architecture-decision-records]
when_to_use: "Read before designing or changing any API that other teams, services, or clients depend on."
---
# API First

## Purpose

This document defines the API-first approach: designing and agreeing on an API contract
*before* writing the implementation, and treating that contract as the source of truth.
The contract — an OpenAPI, gRPC/protobuf, or GraphQL schema — is authored, reviewed, and
published first; server and clients are then built to match it.

API-first matters most at boundaries: between [services](09-microservices.md), between
frontend and backend, and for any public or partner API. This doc covers contract design,
compatibility rules, and versioning — the things that determine whether consumers can
depend on you without breaking.

## Why It Matters

An API is a promise to everyone who calls it, and unlike internal code you cannot refactor
it unilaterally — every breaking change ripples into consumers you may not control and
cannot redeploy. When the API is defined only implicitly by whatever the code happens to
return, that promise is accidental: fields appear and vanish between deploys, and clients
break without warning. Designing the contract first turns the API into a deliberate,
reviewable artifact. It lets frontend and backend teams work in parallel against a shared
spec, generates clients/servers/mocks/docs from one source, and makes breaking changes
visible in review instead of in production. The cost is up-front design discipline; the
payoff is consumers who can trust you.

## Core Principles

- **The contract is the source of truth.** The spec is authored and reviewed first; code
  conforms to it, not the reverse. Generated code and docs derive from the spec.
- **Design for the consumer.** Model the API around what callers need to accomplish, not
  around your database tables or internal object graph.
- **Backward compatibility is the default obligation.** Additive changes (new optional
  fields, new endpoints) are safe; removing or renaming a field, tightening validation, or
  changing a type is breaking and requires a new version.
- **Version explicitly and support the old version during migration.** Consumers cannot
  all upgrade at once; you must run old and new in parallel for a window.
- **The contract is validated, not just documented.** CI must check that the running server
  matches the spec, or the contract is fiction.

## Best Practices

- Author the spec (OpenAPI 3.1, protobuf, or a GraphQL SDL) first and review it like code,
  because design flaws are cheap to fix in a spec and expensive once clients are built.
- Run **contract tests** in CI that assert the implementation conforms to the spec, and
  ideally consumer-driven contract tests, so drift fails the build rather than a client.
- Enforce backward compatibility automatically (e.g. `oasdiff`, Buf breaking-change
  detection) on every change to the spec; a breaking diff should block merge.
- Version at a coarse, visible level (URL path `/v2/` or a media type) and publish a
  deprecation timeline with sunset dates before removing anything.
- Use consistent, predictable conventions: stable field names, explicit enums, RFC-style
  error bodies, cursor pagination, and idempotency keys for unsafe retried operations.
- Generate clients, server stubs, mocks, and docs from the single spec so they cannot drift
  from each other.
- Never leak internal identifiers, storage details, or domain internals through the API —
  they become a contract you did not intend to make.

## Examples

**Good Example** — spec-first, additive evolution, explicit versioning

```yaml
# openapi.yaml — the reviewed source of truth. Server and clients are generated from it.
paths:
  /v1/orders/{id}:
    get:
      operationId: getOrder
      responses:
        "200":
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Order" }
components:
  schemas:
    Order:
      type: object
      required: [id, status, totalCents]   # required set is a promise; do not shrink it
      properties:
        id: { type: string }
        status: { type: string, enum: [draft, placed, shipped] }
        totalCents: { type: integer }
        # ADDITIVE change: a new OPTIONAL field never breaks existing clients.
        discountCents: { type: integer }
```

**Bad Example** — implementation-defined contract, silent breaking change

```ts
// No spec. Whatever this returns *is* the API — and it changes with the code.
app.get("/orders/:id", async (req, res) => {
  const order = await db.orders.find(req.params.id);
  res.json(order); // leaks every DB column, including internal fields, as the "contract"
});

// Next sprint, someone renames a column and "fixes" the response shape:
//   res.json({ orderId: order.id, state: order.status })
// `id` and `status` vanished. Every client breaks at runtime, unreviewed, in production.
```

## Common Mistakes

- Code-first APIs where the contract is whatever the handler happens to serialize today.
- Serializing database rows directly, leaking internal columns as a permanent contract.
- Breaking changes shipped without a version bump — renamed fields, removed properties,
  tightened validation.
- No deprecation window: an old version is dropped before consumers can migrate.
- Docs written by hand, so they drift from the real behavior and mislead callers.
- Designing around your schema instead of the consumer's use case.
- No CI check that the implementation actually matches the published spec.

## Production Tips

- Publish the spec and a changelog where consumers can find them; treat API changes as
  releases with notes, not silent deploys.
- Track which consumers are on which version (via API keys or client version headers) so
  you know when it is safe to sunset an old one.
- Gate deploys on both contract conformance and backward-compatibility checks, so an
  accidental breaking change cannot reach production.

## AI Review Checklist

- Is there a reviewed spec (OpenAPI/protobuf/GraphQL) that is the source of truth?
- Does CI verify the implementation conforms to the spec?
- Are breaking changes detected automatically and gated behind a new version?
- Is the API modeled around consumer needs rather than database tables?
- Are internal identifiers and storage details kept out of the response?
- Is there an explicit version and a published deprecation/sunset timeline?
- Are clients, mocks, and docs generated from the single spec?

## Related

- `knowledge/architecture/12-integration-patterns.md`
- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/25-documentation.md`
- `knowledge/architecture/15-security.md`
- `knowledge/architecture/26-architecture-decision-records.md`
