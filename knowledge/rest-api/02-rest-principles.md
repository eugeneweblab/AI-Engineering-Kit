---
id: rest-api/02-rest-principles
topic: rest-api
slug: rest-principles
title: "Rest Principles"
type: doc
order: 2
status: ready
tags: [rest-api, rest-principles, action, Cache-Control, Content-Type]
related: [rest-api/01-http, rest-api/03-resource-design, rest-api/04-endpoints, rest-api/14-versioning, rest-api/19-caching]
when_to_use: "Read before deciding whether a design is actually RESTful, or when justifying resource/state-transfer choices in review."
---
# Rest Principles

## Purpose

This document defines the architectural constraints that make an API *REST* rather than
merely "HTTP with JSON": statelessness, uniform interface, resource-orientation,
cacheability, and layering. It is written so an agent can judge whether a design honors
these constraints and knows which are worth enforcing.

REST is a set of constraints (Fielding's dissertation), not a spec you import. Following
them buys scalability, cacheability, and loose coupling; violating them silently forfeits
those benefits even while the API still "works."

## Why It Matters

The value of REST is operational, not aesthetic. Statelessness is what lets you put ten
identical servers behind a load balancer and scale horizontally. A uniform interface is
what lets a generic client, proxy, or cache understand your API without bespoke code.
When a design breaks these constraints — server-side session affinity, verbs baked into
URLs, responses that cannot be cached — the system still passes tests but loses the
scaling and interoperability that were the whole point of choosing REST.

## Core Principles

- **Statelessness.** Every request carries everything needed to process it (auth,
  parameters). The server keeps no client session between requests, so any node can serve
  any request. This is the single most important constraint for scaling.
- **Uniform interface.** Resources are identified by URLs, manipulated through standard
  methods, and represented in standard media types. Same rules for every resource.
- **Resource orientation.** Model nouns (things), not verbs (actions). The action lives
  in the HTTP method; the URL names the thing. See [resource design](03-resource-design.md).
- **Cacheability.** Responses declare whether and how long they may be cached, so
  intermediaries can offload the origin. See [caching](19-caching.md).
- **Layered system.** A client cannot tell whether it talks to the origin or a proxy;
  this lets you insert gateways, caches, and load balancers transparently.
- **Client–server separation.** The client owns the UI/state of the interaction; the
  server owns resources. Neither dictates the other's internals.

## Best Practices

- Keep the server stateless: put session state in a signed token or a shared store the
  client references, never in per-node memory. This is what makes horizontal scaling work.
- Name resources with nouns and let methods express actions:
  `POST /articles/42/publish` only when a state transition has no clean noun; prefer
  `PATCH /articles/42 {"status":"published"}` when it does.
- Make representations self-describing: include a `Content-Type`, and where it helps,
  hypermedia links (`_links` / HAL) so clients can discover related resources (HATEOAS).
- Declare cacheability explicitly with `Cache-Control` and validators; do not leave it to
  chance.
- Version the contract, not the constraints — evolve via [versioning](14-versioning.md)
  and additive changes rather than abandoning REST semantics under pressure.

## Examples

**Good Example** — stateless, resource-oriented, cacheable

```http
GET /v1/users/42/orders?status=open HTTP/1.1
Authorization: Bearer <token>        # identity travels with the request; no server session

HTTP/1.1 200 OK
Cache-Control: private, max-age=30    # response states its own cacheability
{
  "data": [ { "id": 8821, "status": "open" } ],
  "_links": { "self": "/v1/users/42/orders?status=open" }  # self-describing
}
```

**Bad Example** — stateful, RPC-style, uncacheable

```http
POST /v1/api HTTP/1.1
Cookie: sessionState=step3           # relies on server-held session → breaks load balancing
{ "action": "getOrders", "filter": "open" }
# The verb lives in the body ("action"), so URL + method carry no meaning:
# no caching, no uniform interface, every client must speak this bespoke RPC.
```

## Common Mistakes

- Storing conversational/session state on one server, forcing sticky sessions and
  blocking horizontal scale.
- RPC-in-disguise: a single `POST /api` endpoint with an `action` field. It is not REST
  and forfeits caching, method semantics, and readable URLs.
- Modeling verbs as URLs (`/getUser`, `/createOrder`) instead of nouns plus methods.
- Making every response uncacheable "to be safe," pushing all load onto the origin.
- Insisting on strict HATEOAS everywhere at high cost when consumers never follow links —
  apply hypermedia where it pays.

## AI Review Checklist

- Is the server stateless — does each request carry its own auth and context?
- Are resources named with nouns, with actions expressed via HTTP methods?
- Does each response declare its cacheability (`Cache-Control` / validators)?
- Is there any hidden RPC endpoint (`action` in the body) that should be resourceful?
- Can any node serve any request, or does the design require sticky sessions?
- Are contract changes handled by [versioning](14-versioning.md), not by breaking semantics?

## Related

- `knowledge/rest-api/01-http.md`
- `knowledge/rest-api/03-resource-design.md`
- `knowledge/rest-api/04-endpoints.md`
- `knowledge/rest-api/14-versioning.md`
- `knowledge/rest-api/19-caching.md`
