---
id: rest-api/00-overview
topic: rest-api
slug: overview
title: "REST API Overview"
type: doc
order: 0
status: ready
tags: [rest-api, overview]
related: [rest-api/01-http, rest-api/02-rest-principles, rest-api/03-resource-design, rest-api/04-endpoints, rest-api/07-status-codes]
when_to_use: "Read first when starting or reviewing any HTTP/REST API to learn how this topic's docs fit together."
---
# REST API Overview

## Purpose

This document is the map for the `rest-api` topic. It orients an agent that must
design, build, or review an HTTP API and points to the specific doc that answers each
question in depth. Read this first, then jump to the doc that matches the task at hand.

A REST API is a contract exposed over HTTP: clients send requests against stable
resource URLs and receive predictable representations back. The rest of this topic
exists to make that contract *correct, consistent, and hard to misuse* — because an API
is a promise you cannot easily take back once clients depend on it.

## Why It Matters

An API is the most public surface of a system. Internal code can be refactored freely;
a published endpoint cannot — every field name, status code, and error shape becomes a
dependency for someone else's software. Mistakes here are expensive to reverse and
often require a new version to fix. Getting the fundamentals right the first time
(correct verbs, correct status codes, stable resource shapes) is far cheaper than
apologizing to integrators later.

## How The Docs Fit Together

- **Foundations** — [HTTP](01-http.md) and [REST principles](02-rest-principles.md)
  establish the protocol semantics and constraints everything else builds on. Read
  these before designing anything.
- **Shaping the API** — [Resource design](03-resource-design.md),
  [endpoints](04-endpoints.md), and [routing](05-routing.md) turn a domain into
  nouns, URLs, and the code that dispatches to them.
- **The wire format** — [Request/response](06-request-response.md),
  [status codes](07-status-codes.md), [validation](08-validation.md), and
  [error handling](09-error-handling.md) define what goes across the wire and what
  happens when it is wrong.
- **Working with collections** — [pagination](10-pagination.md),
  [filtering](11-filtering.md), [sorting](12-sorting.md), and [search](13-search.md)
  keep large result sets fast and predictable.
- **Evolution and safety** — [versioning](14-versioning.md),
  [authentication](15-authentication.md), [authorization](16-authorization.md),
  [rate limiting](17-rate-limiting.md), [idempotency](18-idempotency.md), and
  [caching](19-caching.md) let the API change and scale without breaking or being abused.
- **Contract and quality** — [OpenAPI](21-openapi.md), [Swagger](22-swagger.md),
  [testing](23-testing.md), [security](24-security.md), [performance](25-performance.md),
  and [monitoring](26-monitoring.md) verify the API does what it claims.
- **Discipline** — [best practices](27-best-practices.md), [production](28-production.md),
  [api design review](29-api-design-review.md), and
  [engineering principles](30-engineering-principles.md), plus the
  [production checklist](98-production-checklist.md),
  [AI review checklist](99-ai-review-checklist.md), and
  [common anti-patterns](100-common-antipatterns.md) close the loop before shipping.

## Core Principles

- **The API is a contract, not an implementation.** Design the interface from the
  consumer's point of view; hide how it is built. Leaking internals (table names,
  ORM shapes) welds clients to your database.
- **Consistency beats cleverness.** One naming rule, one pagination style, one error
  envelope across every endpoint. Predictability is the feature integrators pay for.
- **Use HTTP as designed.** Verbs, status codes, and headers already carry meaning;
  reuse them instead of reinventing semantics in the body.
- **Design for change.** Assume every endpoint will need to evolve; additive changes
  and explicit versioning are how you avoid breaking existing clients.

## Best Practices

- Start from the resource model (see [resource design](03-resource-design.md)), not
  from the database or the UI screen. Nouns first, then the verbs HTTP already gives you.
- Fix cross-cutting conventions once — casing, timestamps (ISO 8601 UTC), IDs, error
  shape — and apply them everywhere. Document them in your [OpenAPI](21-openapi.md) spec.
- Treat the OpenAPI document as the source of truth and generate clients, docs, and
  tests from it, so the contract and the code cannot drift apart.
- When unsure which doc applies, follow the order above: protocol → shape → wire →
  collections → evolution → contract.

## Common Mistakes

- Treating REST as "JSON over HTTP" and ignoring verb and status-code semantics.
- Designing endpoints around UI screens, producing an API no other client can reuse.
- Inventing a different convention per endpoint, forcing integrators to special-case each.
- Skipping versioning until a breaking change is already needed, then breaking clients.

## AI Review Checklist

- Does the change respect HTTP semantics defined in [HTTP](01-http.md) and
  [REST principles](02-rest-principles.md)?
- Is the resource model consistent with [resource design](03-resource-design.md) rather
  than mirroring the database?
- Do URLs and dispatch follow [endpoints](04-endpoints.md) and [routing](05-routing.md)?
- Are cross-cutting conventions (naming, errors, pagination) uniform with sibling endpoints?
- Is the OpenAPI contract updated alongside the code?

## Related

- `knowledge/rest-api/01-http.md`
- `knowledge/rest-api/02-rest-principles.md`
- `knowledge/rest-api/03-resource-design.md`
- `knowledge/rest-api/04-endpoints.md`
- `knowledge/rest-api/07-status-codes.md`
