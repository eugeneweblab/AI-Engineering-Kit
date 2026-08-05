---
id: rest-api/98-production-checklist
topic: rest-api
slug: production-checklist
title: "REST API Production Checklist"
type: checklist
order: 98
status: ready
tags: [rest-api, production-checklist, Deprecation, Sunset, Idempotency-Key, request_id, PATCH, Retry-After]
related: [rest-api/24-security, rest-api/17-rate-limiting, rest-api/19-caching, rest-api/26-monitoring, rest-api/28-production]
when_to_use: "Read before promoting a REST API to production or sign off on a release that changes the public surface."
---
# REST API Production Checklist

## Purpose

This is a pre-flight checklist for shipping a REST API to production. Every item is a
verifiable yes/no gate — if you cannot answer "yes" with evidence (a test, a config, a
dashboard), the item is not done. Work top to bottom; the groups are ordered roughly by
how much damage a miss causes. Use it alongside the deeper docs it links to; this page is
the gate, those pages are the reasoning.

## Contract & Versioning

**Rules:** [Versioning](14-versioning.md) · [OpenAPI](21-openapi.md)

- [ ] Every endpoint is documented in a published [OpenAPI](21-openapi.md) spec that matches the running server.
- [ ] The API is versioned (URL prefix or header) and this release introduces no breaking change to an existing version.
- [ ] Response envelope, field casing, and date/time format (ISO 8601, UTC) are consistent across all endpoints.
- [ ] Error responses share one machine-readable shape with a stable `code` field.
- [ ] Deprecated fields/endpoints emit a `Deprecation` (or `Sunset`) header with a removal date.

## Correctness & HTTP Semantics

**Rules:** [HTTP](01-http.md) · [Status Codes](07-status-codes.md)

- [ ] Each endpoint returns the correct [status code](07-status-codes.md) — never `200` for a failure.
- [ ] `GET`/`HEAD` are side-effect free; mutations use `POST`/`PUT`/`PATCH`/`DELETE`.
- [ ] Money-moving and create endpoints accept an `Idempotency-Key` and are proven safe to retry.
- [ ] All list endpoints are [paginated](10-pagination.md) with an enforced maximum page size.
- [ ] Input is validated against an explicit schema; unexpected fields are rejected or ignored deliberately.

## Security

**Rules:** [Security](24-security.md) · [Authentication](15-authentication.md)

- [ ] Every non-public endpoint requires [authentication](15-authentication.md) and enforces [authorization](16-authorization.md) per object, not just per route.
- [ ] TLS is required; HTTP is redirected to HTTPS and HSTS is set.
- [ ] Secrets, tokens, and PII never appear in URLs, logs, or error messages.
- [ ] CORS allows only known origins — no `Access-Control-Allow-Origin: *` on authenticated endpoints.
- [ ] Security headers are set (`Content-Type` enforced, `X-Content-Type-Options: nosniff`).
- [ ] Request body size is capped so a large payload cannot exhaust memory.

## Reliability & Performance

**Rules:** [Idempotency](18-idempotency.md) · [Performance](25-performance.md)

- [ ] Every endpoint has a request [timeout](25-performance.md) and downstream calls have their own timeouts.
- [ ] [Rate limiting](17-rate-limiting.md) is enforced per client with `429` and a `Retry-After` header.
- [ ] `Cache-Control` and `ETag` are set intentionally; cacheable responses are actually cacheable.
- [ ] A load test confirms p95/p99 latency and throughput meet the target under expected traffic.
- [ ] Graceful shutdown drains in-flight requests before the process exits.

## Observability

**Rules:** [Monitoring](26-monitoring.md)

- [ ] Structured logs include a `request_id` propagated to every downstream call.
- [ ] Metrics track request rate, error rate, and latency per route ([monitoring](26-monitoring.md)).
- [ ] A `/health` (and `/ready`) endpoint reflects real dependency status, not a hardcoded `200`.
- [ ] Alerts fire on elevated `5xx` rate, latency regression, and rate-limit saturation.
- [ ] `4xx` and `5xx` responses are distinguished in dashboards so client errors do not mask server failures.

## Data & Operations

**Rules:** [Pagination](10-pagination.md) · [Production](28-production.md)

- [ ] Database migrations are backward compatible with the currently deployed version (deploy runs both at once).
- [ ] Rollback is tested: the previous version can serve traffic against the new schema.
- [ ] Pagination and filters are backed by indexes; no endpoint triggers a full-table scan.
- [ ] Bulk/expensive operations are async (job + status endpoint), not a synchronous long request.

## Release Gate

- [ ] Contract tests assert status code and response schema for each endpoint and pass in CI.
- [ ] Negative paths are tested: unauthorized, invalid input, not found, rate limited, retried.
- [ ] A canary or staged rollout is in place with automatic rollback on error-rate spike.

## AI Review Checklist

- Is every box above checked with concrete evidence, not assumption?
- For any unchecked box, is there a written, owned decision to defer it?
- Do the automated tests actually exercise the security and retry items, or only the happy path?

## Related

- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/17-rate-limiting.md`
- `knowledge/rest-api/19-caching.md`
- `knowledge/rest-api/26-monitoring.md`
- `knowledge/rest-api/28-production.md`
