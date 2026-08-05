---
id: rest-api/28-production
topic: rest-api
slug: production
title: "REST API Production"
type: doc
order: 28
status: ready
tags: [rest-api, production]
related: [rest-api/26-monitoring, rest-api/24-security, rest-api/25-performance, rest-api/17-rate-limiting, rest-api/14-versioning]
when_to_use: "Read before deploying a REST API to production or reviewing its operational readiness."
---
# REST API Production

## Purpose

This document defines what a REST API needs to survive real traffic, real failures, and
real deploys. It covers operational concerns: safe rollouts, graceful degradation,
resilience to dependency failure, configuration, and shutdown. Correctness and security
(covered elsewhere) get you to the door; this doc keeps you running once you are through
it. It assumes [monitoring](26-monitoring.md) is in place — you cannot operate what you
cannot see.

## Why It Matters

Production is a hostile, chaotic environment: dependencies time out, nodes restart mid-
request, traffic spikes 10x without warning, and a bad deploy can take down every client at
once. Code that works on a laptop routinely fails in production because the laptop never
had a database outage, a full disk, or a thundering herd. The difference between a resilient
API and a fragile one is not the happy path — it is what happens when a downstream service
dies. An API that fails gracefully sheds load and recovers; one that does not turns a single
slow dependency into a total outage. Design for failure, because failure is the normal case.

## Core Principles

- **Deploy safely and reversibly.** Use rolling or blue-green deploys with health gates,
  and keep every release rollback-ready. A deploy you cannot undo is a bet, not a release.
- **Fail gracefully, isolate failures.** A dead dependency should degrade one feature, not
  crash the API. Use timeouts, retries with backoff, and circuit breakers to contain it.
- **Shut down gracefully.** On `SIGTERM`, stop accepting new requests, drain in-flight ones,
  close pools, then exit — so a deploy or scale-down does not drop live requests.
- **Externalize configuration.** Read config and secrets from the environment, never
  hard-code them; the same artifact must run in every environment. See [security](24-security.md).
- **Protect the API from overload.** Rate-limit, cap concurrency, and set body-size limits
  so a spike sheds load instead of collapsing. See [rate limiting](17-rate-limiting.md).
- **Make deploys backward-compatible.** During a rolling deploy, old and new code run at
  once; schema and API changes must work with both. See [versioning](14-versioning.md).

## Best Practices

- Set a timeout on every outbound call (DB, cache, HTTP). An unbounded call under a
  dependency slowdown exhausts the connection pool and cascades into a full outage.
- Retry only idempotent operations, with exponential backoff and jitter and a low cap.
  Retrying non-idempotent writes duplicates side effects; retrying without backoff
  amplifies an outage into a thundering herd.
- Wrap flaky dependencies in a circuit breaker that opens on sustained failure and returns
  a fast fallback, so callers are not blocked on a known-dead service.
- Gate rollouts on `/ready` health checks; halt the deploy if new instances fail readiness.
- Handle `SIGTERM`: stop the listener, wait for in-flight requests up to a deadline, close
  DB/cache pools, then exit non-zero only on failure.
- Run migrations in a backward-compatible, expand-then-contract sequence so the old version
  still works during and after the deploy.
- Load config at startup and fail fast if a required value is missing — a misconfigured
  instance should refuse to start, not serve wrong data.
- Run stateless instances behind a load balancer so any node can be replaced or scaled
  freely; keep session state in a shared store, not in process memory.

## Examples

**Good Example** — timeout, capped retry with backoff, graceful shutdown

```ts
// Outbound call: bounded time, retried only because it is a safe GET.
async function fetchRates() {
  return retry(() => http.get("/rates", { timeout: 2000 }), {
    retries: 3,
    backoff: "exponential",   // 200ms, 400ms, 800ms + jitter — avoids a retry storm
    jitter: true,
  });
}

// Drain in-flight requests before exiting so a deploy drops nothing.
process.on("SIGTERM", async () => {
  server.close();                 // stop accepting new connections
  await inFlight.drain(30_000);   // let running requests finish, up to 30s
  await db.end();                 // release the pool cleanly
  process.exit(0);
});
```

**Bad Example** — no timeout, blind retry, hard exit

```ts
async function fetchRates() {
  // No timeout: if /rates hangs, this request hangs, holding a pool slot until it dies.
  // Retried 5x with no backoff → hammers an already-failing dependency (thundering herd).
  return retry(() => http.get("/rates"), { retries: 5 });
}

// SIGTERM kills the process instantly, dropping every in-flight request mid-response.
process.on("SIGTERM", () => process.exit(0));
```

## Common Mistakes

- Outbound calls with no timeout, letting one slow dependency exhaust the whole pool.
- Retrying non-idempotent writes, duplicating charges or records.
- Retrying without backoff/jitter, turning a blip into a self-inflicted DDoS.
- Hard `process.exit` on shutdown, dropping in-flight requests on every deploy.
- Breaking schema migrations that assume all instances upgrade atomically.
- Hard-coded config or secrets, so the artifact cannot move between environments.
- Storing session or cache state in process memory, breaking horizontal scaling.

## Production Tips

- Run game days / chaos tests: kill a dependency in staging and confirm graceful degradation.
- Keep a documented, rehearsed rollback and an incident runbook per service.
- Set autoscaling on a leading signal (latency, queue depth), not just CPU.
- Use feature flags to decouple deploy from release, so risky changes ship dark.

## AI Review Checklist

- Does every outbound call have a timeout?
- Are retries limited to idempotent operations, with backoff and jitter?
- Are flaky dependencies isolated with circuit breakers and fallbacks?
- Does the service drain in-flight requests on `SIGTERM` before exiting?
- Are migrations backward-compatible with the previous running version?
- Is all config and every secret read from the environment, with fail-fast on missing values?
- Are instances stateless and safe to scale or replace behind a load balancer?

## Related

- `knowledge/rest-api/26-monitoring.md`
- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/25-performance.md`
- `knowledge/rest-api/17-rate-limiting.md`
- `knowledge/rest-api/14-versioning.md`
