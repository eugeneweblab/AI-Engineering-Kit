---
id: rest-api/99-ai-review-checklist
topic: rest-api
slug: ai-review-checklist
title: "REST API AI Review Checklist"
type: doc
order: 99
status: ready
tags: [rest-api, ai-review-checklist]
related: [rest-api/09-error-handling, rest-api/08-validation, rest-api/16-authorization, rest-api/18-idempotency, rest-api/07-status-codes]
when_to_use: "Read when reviewing a pull request that adds or changes a REST endpoint, before approving it."
---
# REST API AI Review Checklist

## Purpose

This is the checklist an AI agent runs when *reviewing* REST API code — a diff, a new
endpoint, a handler change. Each item is a concrete, verifiable question tied to code you
can point at. It differs from the [production checklist](98-production-checklist.md), which
gates a whole release; this page gates a single change. Flag any "no" as a review comment
with the specific file and line.

## How To Use

Read the diff, then answer each question against the actual code — not the PR description.
An item passes only when you can name the line that satisfies it. If a section does not
apply to the change (e.g. no auth touched), say so explicitly rather than skipping it
silently.

## Contract & Shape

**Rules:** [Resource Design](03-resource-design.md) · [Versioning](14-versioning.md)

- [ ] Are URLs resource-oriented nouns, with the action carried by the HTTP method (no `/createX`, `/doY`)?
- [ ] Does the response shape match the rest of the API (envelope, [casing](03-resource-design.md), date format)?
- [ ] For a changed field, is this additive — not a rename or removal that breaks existing clients?
- [ ] Is any new breaking change gated behind a new [version](14-versioning.md)?

## Status Codes & Errors

**Rules:** [Status Codes](07-status-codes.md) · [Error Handling](09-error-handling.md)

- [ ] Does each path return the correct [status code](07-status-codes.md), never `200` on failure?
- [ ] Do errors use the shared [error shape](09-error-handling.md) with a stable machine-readable `code`?
- [ ] Do error messages avoid leaking stack traces, SQL, or internal identifiers?
- [ ] Is `4xx` used for client mistakes and `5xx` reserved for genuine server faults?

## Validation & Input

**Rules:** [Validation](08-validation.md)

- [ ] Is every input [validated](08-validation.md) against an explicit schema before use?
- [ ] Are numeric/string bounds enforced (lengths, ranges, enums) rather than assumed?
- [ ] Is request body size bounded so a large payload cannot exhaust memory?
- [ ] Are user-supplied values parameterized, never string-concatenated into queries?

## Security

**Rules:** [Security](24-security.md) · [Authorization](16-authorization.md)

- [ ] Does the endpoint require [authentication](15-authentication.md) if it is not explicitly public?
- [ ] Is [authorization](16-authorization.md) checked on the specific object, not just the route (no IDOR)?
- [ ] Are secrets/tokens/PII kept out of URLs, logs, and responses?
- [ ] Is the returned payload scoped to what the caller may see (no over-fetching another user's data)?

## Reliability

**Rules:** [Idempotency](18-idempotency.md) · [Rate Limiting](17-rate-limiting.md)

- [ ] Are mutating endpoints safe to retry via idempotency ([idempotency](18-idempotency.md))?
- [ ] Do list endpoints [paginate](10-pagination.md) with an enforced max page size?
- [ ] Do downstream/database calls have timeouts, and are errors handled rather than swallowed?
- [ ] Are N+1 queries avoided on list and nested-resource responses?

## Observability & Tests

**Rules:** [Monitoring](26-monitoring.md) · [Testing](23-testing.md)

- [ ] Does the change log a `request_id` and enough context to debug a failure (without secrets)?
- [ ] Are there tests for the happy path *and* the negative paths (unauthorized, invalid, not found)?
- [ ] Do contract tests assert the status code and response schema for the changed endpoint?

## Reviewer Guidance

- Treat a missing negative-path test as a blocking finding: untested error handling is
  usually broken error handling.
- Prefer one specific, actionable comment per finding over a vague "improve error handling".
- When an item is genuinely N/A, state why — an unexplained skip reads as an oversight.

## Related

- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/16-authorization.md`
- `knowledge/rest-api/18-idempotency.md`
- `knowledge/rest-api/07-status-codes.md`
