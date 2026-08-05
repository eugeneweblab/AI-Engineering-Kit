---
id: nodejs/25-microservices
topic: nodejs
slug: microservices
title: "Node.js Microservices"
type: doc
order: 25
status: ready
tags: [nodejs, microservices]
related: [nodejs/09-http, nodejs/16-error-handling, nodejs/24-background-jobs, nodejs/26-deployment, nodejs/27-monitoring]
when_to_use: "Read before splitting a Node.js system into independently deployed services, or reviewing service-to-service communication."
---
# Node.js Microservices

## Purpose

This document defines how to build and connect Node.js services that are deployed and
scaled independently: service boundaries, inter-service communication, resilience, and
consistency. It is written so an agent can add or review a service without creating a
distributed monolith that fails as one.

A microservice owns one business capability, its own data, and its own deploy pipeline.
Services talk over the network — synchronously (HTTP/gRPC) or asynchronously (a broker).
The network is the hard part; the code is the easy part.

## Why It Matters

Splitting a system trades in-process function calls for network calls, and network calls
fail, retry, time out, and arrive out of order. A team that keeps a shared database and
synchronous chains across services gets the worst of both worlds: the operational cost of
distribution with the coupling of a monolith — one slow service cascades into a
system-wide outage. Microservices pay off only when boundaries are drawn so a service can
fail, deploy, and scale alone. Get the boundary wrong and every change touches three
repos; get resilience wrong and every dependency's outage is your outage.

## Core Principles

- **A service owns its data.** No other service reads its database directly. Sharing a
  database recouples everything and makes independent deploys a lie.
- **The network is unreliable — design for failure.** Every remote call needs a timeout,
  bounded retries with backoff, and a circuit breaker. A call with no timeout is a hang.
- **Prefer asynchronous messaging for cross-service work.** Events decouple producer from
  consumer; synchronous chains couple availability (A is down ⇒ B is down).
- **Embrace eventual consistency.** Distributed transactions across services do not scale;
  use sagas / the outbox pattern to keep data consistent without two-phase commit.
- **Make every request traceable.** Propagate a correlation/trace id across every hop, or
  a failure becomes unbelievable across a dozen logs.

## Best Practices

- Draw boundaries around business capabilities (Orders, Billing), not technical layers.
  A boundary that forces two services to deploy together is the wrong boundary.
- Define contracts explicitly (OpenAPI, gRPC/protobuf, or a schema registry for events)
  and version them. Never let a consumer depend on an undocumented field.
- Wrap every outbound call with a timeout + retry + circuit breaker (e.g. `undici` with
  `AbortSignal.timeout`, plus a breaker like `opossum`). Fail fast when a dependency is sick.
- Publish state changes as events through the **transactional outbox** (write event and
  state in one DB transaction, relay to the broker) so you never lose or duplicate events.
- Make consumers idempotent; brokers deliver at-least-once. Dedupe on an event id.
- Keep services stateless so any replica handles any request; push state to the datastore.
  See [deployment](26-deployment.md) for horizontal scaling.
- Expose `/health` (liveness) and `/ready` (readiness incl. dependency checks) per service.
- Propagate `traceparent` (W3C Trace Context) on every call for distributed tracing.

## Examples

**Good Example** — bounded, resilient outbound call

```ts
import CircuitBreaker from "opossum";
import { request } from "undici";

async function fetchInventory(sku: string, traceparent: string) {
  const res = await request(`http://inventory/items/${sku}`, {
    headers: { traceparent },            // propagate trace context across the hop
    signal: AbortSignal.timeout(2000),   // never wait forever on a peer
  });
  if (res.statusCode >= 500) throw new Error("inventory upstream error");
  return res.body.json();
}

// Breaker trips after repeated failures and serves a fallback instead of piling up calls.
const breaker = new CircuitBreaker(fetchInventory, { timeout: 2500, errorThresholdPercentage: 50 });
breaker.fallback(() => ({ available: false })); // degrade gracefully, don't cascade the outage
```

**Bad Example** — shared DB, unbounded synchronous chain

```ts
// Billing reaches directly into Orders' database — now they can never deploy independently.
const order = await ordersDb.query("SELECT * FROM orders WHERE id=$1", [id]);

// No timeout, no breaker: if shipping is slow, this request hangs, and so does its caller,
// and so does the caller's caller — one slow service stalls the whole chain.
const ship = await fetch(`http://shipping/quote?order=${id}`);
```

## Common Mistakes

- A shared database across services, silently recoupling them into a distributed monolith.
- Remote calls with no timeout, no retry limit, and no circuit breaker — cascading hangs.
- Synchronous request chains three services deep, multiplying latency and failure surface.
- Publishing events outside a transaction, so a crash loses the event or emits it twice.
- Non-idempotent consumers that double-process at-least-once deliveries.
- No correlation/trace id, making cross-service debugging guesswork.
- Splitting into services before the domain is understood, cementing wrong boundaries.

## Production Tips

- Start with a well-modularized monolith and extract services only when a boundary proves
  stable and independently scalable — premature splitting is expensive to undo.
- Centralize logs, metrics, and traces ([monitoring](27-monitoring.md)); per-service silos
  make incidents unsolvable.
- Use consumer-driven contract tests (e.g. Pact) so a provider change that breaks a
  consumer fails in CI, not in production.
- Route through an API gateway for auth, rate limiting, and TLS termination rather than
  reimplementing them in every service.

## AI Review Checklist

- Does each service own its data, with no direct cross-service database access?
- Does every outbound call have a timeout, bounded retries, and a circuit breaker?
- Are events published transactionally (outbox) and consumed idempotently?
- Are service contracts explicit and versioned (OpenAPI/protobuf/schema registry)?
- Is a correlation/trace id propagated across every hop?
- Do services expose liveness and readiness endpoints and stay stateless?
- Is the boundary a business capability that can deploy and fail independently?

## Related

- `knowledge/nodejs/09-http.md`
- `knowledge/nodejs/16-error-handling.md`
- `knowledge/nodejs/24-background-jobs.md`
- `knowledge/nodejs/26-deployment.md`
- `knowledge/nodejs/27-monitoring.md`
