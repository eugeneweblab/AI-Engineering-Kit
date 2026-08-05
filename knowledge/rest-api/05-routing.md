---
id: rest-api/05-routing
topic: rest-api
slug: routing
title: "REST API Routing"
type: doc
order: 5
status: ready
tags: [rest-api, routing]
related: [rest-api/04-endpoints, rest-api/03-resource-design, rest-api/14-versioning, rest-api/08-validation, rest-api/16-authorization]
when_to_use: "Read before defining route paths, ordering routes, or wiring middleware for an HTTP API."
---
# REST API Routing

## Purpose

This document defines how requests are dispatched to handlers: path structure, path
versus query parameters, route ordering, versioning in the path, and where cross-cutting
middleware belongs. It is written so an agent can wire routes that are unambiguous, safe,
and consistent with the resource model.

Routing is where [resource design](03-resource-design.md) and [endpoints](04-endpoints.md)
become executable. A clean resource model can still be undermined by ambiguous route
ordering or parameters used for the wrong purpose.

## Why It Matters

Routing bugs are both functional and security-relevant. A shadowed route sends requests
to the wrong handler; a greedy wildcard swallows paths it should not; a missing auth
middleware on one route leaves a hole while every other route looks fine. Because routing
runs before your business logic, a mistake here bypasses all the correctness you built
downstream — the safest handler never runs if the router sends the request elsewhere.

## Core Principles

- **Path identifies a resource; query refines a collection.** Use path segments for
  identity (`/orders/{id}`) and query parameters for filtering, sorting, and pagination
  (`/orders?status=open&limit=20`). Never encode identity in the query.
- **Static routes before dynamic ones.** `/orders/summary` must be registered before
  `/orders/{id}`, or `summary` gets captured as an `{id}`.
- **Versioning lives at the front of the path.** `/v1/...` keeps every route grouped and
  lets `/v2` coexist. Decide the strategy once (see [versioning](14-versioning.md)).
- **Middleware order is contract.** Auth, rate limiting, and validation run in a defined
  order, before the handler. A route that skips a middleware is a defect, not a shortcut.
- **Routes are explicit, not magic.** Prefer an explicit route table over convention-based
  auto-routing that hides which paths exist and how they resolve.

## Best Practices

- Reserve path params for resource identity and required hierarchy; put everything
  optional (filters, `sort`, `page`, `limit`, `q`) in the query string. This keeps URLs
  cacheable and the resource addressable.
- Register specific/literal routes before parameterized and wildcard routes so the
  first match is the intended one. Verify with the framework's route-list output.
- Prefix all routes with the API version and mount routers per resource
  (`/v1/orders`, `/v1/users`) to keep the table readable and versionable.
- Apply cross-cutting concerns as ordered middleware — authentication →
  [authorization](16-authorization.md) → rate limiting → [validation](08-validation.md) →
  handler — and apply them at the router/group level so no route is accidentally exempt.
- URL-decode and validate path params (type, range, format) before using them; never
  interpolate a raw param into a query or file path (injection / path traversal).
- Return `404` for unknown routes and `405 Method Not Allowed` (with an `Allow` header)
  when the path exists but the method does not — do not collapse both into `404`.

## Examples

**Good Example** — ordered routes, params by purpose, group middleware

```ts
const orders = Router();

orders.use(authenticate, authorize("orders"));   // runs before every handler below

orders.get("/summary", getSummary);              // STATIC route registered first
orders.get("/:id", validateId, getOrder);        // dynamic route; param validated
orders.get("/", listOrders);                     // /orders?status=open&limit=20 → filters in query

app.use("/v1/orders", orders);                   // version + resource prefix, one place
```

**Bad Example** — shadowed route, identity in query, per-route auth gaps

```ts
app.get("/orders/:id", getOrder);        // registered FIRST → captures everything
app.get("/orders/summary", getSummary);  // DEAD: "summary" already matched as :id

app.get("/order", authorize, getOrder);  // auth on THIS route only...
app.get("/orders", getOrder);            // ...but this near-duplicate has NONE → open hole

// identity smuggled into the query instead of the path:
app.get("/orders", (req) => db.find(req.query.id)); // uncacheable, unRESTful, easy to miss
```

## Common Mistakes

- Registering `/{id}` before a literal sibling route, permanently shadowing the literal.
- Putting resource identity in the query string instead of the path.
- Attaching auth/validation per-route and forgetting one, leaving a single route exposed.
- Greedy catch-all/wildcard routes that swallow paths meant for other handlers.
- Returning `404` for a wrong method instead of `405` with an `Allow` header.
- Interpolating an unvalidated path param into a DB query or filesystem path.

## Production Tips

- Dump the resolved route table at boot (most frameworks can) and diff it in review to
  catch shadowing and missing-middleware regressions before they ship.
- Label metrics and traces with the route template (`/v1/orders/{id}`), never the raw
  path, to keep cardinality bounded and dashboards readable.
- Add a contract test that hits an unknown path (expect `404`) and a wrong method on a
  known path (expect `405`) so routing regressions fail CI.

## AI Review Checklist

- Are static/literal routes registered before dynamic and wildcard routes?
- Is resource identity in the path and are filters/sort/paging in the query string?
- Is every route prefixed with the API version per the [versioning](14-versioning.md) plan?
- Is auth/authorization/rate-limit/validation middleware applied at the group level so no
  route is accidentally exempt, in the correct order?
- Are path params decoded and validated before use (no injection/traversal)?
- Does an existing path with an unsupported method return `405` (with `Allow`), not `404`?

## Related

- `knowledge/rest-api/04-endpoints.md`
- `knowledge/rest-api/03-resource-design.md`
- `knowledge/rest-api/14-versioning.md`
- `knowledge/rest-api/08-validation.md`
- `knowledge/rest-api/16-authorization.md`
