---
id: rest-api/14-versioning
topic: rest-api
slug: versioning
title: "REST API Versioning"
type: doc
order: 14
status: ready
tags: [rest-api, versioning, Sunset, Deprecation, change, Link]
related: [rest-api/03-resource-design, rest-api/06-request-response, rest-api/09-error-handling, rest-api/21-openapi, rest-api/27-best-practices]
when_to_use: "Read before shipping a public API or making a change that could break existing clients."
---
# REST API Versioning

## Purpose

This document defines how to version a REST API so that existing clients keep working while
the API evolves: what counts as a breaking change, which versioning scheme to use, and how
to deprecate and retire old versions safely. It is written so an agent can introduce or
change an endpoint without silently breaking the clients already calling it.

Versioning is a contract-management discipline. It exists because you cannot redeploy your
clients — once a response shape ships, someone depends on it. See
[request/response](06-request-response.md) design for the shapes a version locks in.

## Why It Matters

An API is a promise about the shape of requests and responses. Break that promise and every
integrated client fails at once, usually in production, usually without a stack trace on
your side — the client's parser throws, not your server. Unlike a UI bug, you cannot hotfix
your way out, because the broken code runs on machines you do not control. A disciplined
versioning strategy is the only way to change an API at all without a coordinated,
all-clients-at-once redeploy that is impossible at scale.

## Core Principles

- **Additive changes are safe; removals and renames are not.** Adding an optional field or
  a new endpoint does not break clients. Removing a field, renaming it, tightening
  validation, or changing a type does. Only the second class requires a new version.
- **Version the contract, not the code.** A version identifies a stable request/response
  shape. Internal refactors that preserve the shape need no version bump.
- **One scheme, applied consistently.** Pick URI, header, or media-type versioning and use
  it everywhere. Mixing schemes confuses clients and tooling.
- **Deprecate before you delete.** Every retirement follows announce → deprecate → sunset,
  with a published date and machine-readable signals. Never remove a version without notice.
- **Default to stability.** When in doubt, add rather than change. A slightly redundant API
  is far cheaper than a broken client.

## Best Practices

- Prefer **URI versioning** (`/v1/orders`) for public APIs: it is explicit, cacheable,
  browsable, and trivial to route. Reserve header/media-type versioning for cases needing
  fine-grained content negotiation.
- Version by **major number only** (`v1`, `v2`). Do not put minor/patch versions in the
  URL; ship backward-compatible improvements into the current major without a new path.
- Treat these as **breaking** and requiring a new major: removing/renaming a field, changing
  a field's type or meaning, making an optional field required, changing default behavior,
  removing an endpoint, or changing an error's status code.
- Announce deprecation with the standard `Deprecation` and `Sunset` HTTP response headers,
  plus a `Link` to migration docs, so clients can detect it programmatically.
- Keep the previous major version running through a documented support window (commonly
  6–12 months) after the successor is stable. Publish the sunset date up front.
- Never reuse or "silently upgrade" a version in place. Once `v1` ships, its behavior is
  frozen; changes go to `v2`.
- Version your [OpenAPI](21-openapi.md) spec alongside the API so each major has a
  published, testable contract.

## Examples

**Good Example** — additive change, explicit deprecation signaling

```http
# v1 response gains a NEW optional field. Existing clients ignore unknown fields,
# so this ships into v1 without a version bump — additive is non-breaking.
GET /v1/orders/42
200 OK
{ "id": 42, "total": 30.0, "currency": "USD", "discount": 2.5 }  // discount added

# A genuinely breaking change (renaming total -> amount) goes to a new major,
# and v1 advertises its retirement so clients can migrate on their own schedule.
GET /v1/orders/42
200 OK
Deprecation: Sun, 01 Nov 2026 00:00:00 GMT
Sunset: Wed, 01 Apr 2026 00:00:00 GMT
Link: <https://api.example.com/docs/v2-migration>; rel="deprecation"
```

**Bad Example** — breaking change shipped in place

```http
# v1 used to return "total". Someone renamed it to "amount" in the SAME version.
GET /v1/orders/42
200 OK
{ "id": 42, "amount": 30.0 }   // every client reading order.total now gets undefined

# No new version, no Deprecation header, no notice. The change is invisible until
# thousands of clients break in production simultaneously.
```

## Common Mistakes

- Making a breaking change (rename, type change, tighter validation) inside an existing
  version instead of cutting a new one.
- Encoding minor/patch versions in the URL, forcing clients to update for compatible changes.
- Removing a version with no deprecation window, `Sunset` header, or migration path.
- Treating "adding a required request field" as safe — it breaks every existing caller.
- Mixing versioning schemes across endpoints, so clients cannot predict how to target a version.
- Changing an endpoint's error status codes without a version bump; clients branch on status.
- Never sunsetting anything, accumulating unbounded versions no team can maintain.

## Production Tips

- Log the API version per request and dashboard traffic by version; you cannot retire a
  version safely until you can see who still uses it.
- Contract-test each supported version in CI against its frozen OpenAPI spec so an accidental
  breaking change fails the build, not a client.
- When a deprecated version's traffic reaches zero (or a long-tail floor), notify the
  remaining callers directly before enforcing the sunset.

## AI Review Checklist

- Does this change remove, rename, or retype a field, or tighten validation? If so, is it a
  new major version rather than an in-place edit?
- Is the versioning scheme (URI vs header) the same one the rest of the API uses?
- Are only major versions exposed in the URL, with compatible changes shipped additively?
- Do deprecated versions send `Deprecation`/`Sunset` headers and link to migration docs?
- Is there a documented support window and sunset date for each retired version?
- Is each major version's [OpenAPI](21-openapi.md) contract published and contract-tested?

## Related

- `knowledge/rest-api/03-resource-design.md`
- `knowledge/rest-api/06-request-response.md`
- `knowledge/rest-api/09-error-handling.md`
- `knowledge/rest-api/21-openapi.md`
- `knowledge/rest-api/27-best-practices.md`
