---
id: backend/100-common-antipatterns
topic: backend
slug: common-antipatterns
title: "Backend Common Antipatterns"
type: doc
order: 100
status: ready
tags: [backend, common-antipatterns, LIMIT]
related: [backend/30-engineering-principles, backend/12-error-handling, backend/17-transactions, backend/19-performance, backend/99-ai-review-checklist]
when_to_use: "Read before writing backend code, to recognize and avoid the recurring failure patterns."
---
# Backend Common Antipatterns

## Purpose

This document catalogs the backend antipatterns that cause the most production incidents
and the most expensive rewrites. Each entry names the pattern, explains *why it is wrong*
(the concrete failure it produces), and gives *the fix*. An agent should recognize these
in a diff and refuse to introduce them.

## Why It Matters

Antipatterns are attractive because they are the shortest path to a passing happy-path
test. The cost shows up later — under load, under retry, under concurrency, or during an
incident at 3am — far from where the shortcut was taken. Naming them makes the cheap
shortcut visible as the expensive liability it is.

## Data and Correctness

**Non-idempotent writes.**
Why it is wrong: networks and queues retry. A `charge()` or `INSERT` with no dedup runs
twice, double-charging or duplicating rows.
The fix: attach an idempotency key or use an upsert keyed on a natural unique constraint.

**Read-modify-write races.**
Why it is wrong: two requests read a value, both compute a new one, and one write is
silently lost (e.g., decrementing inventory below zero).
The fix: use an atomic update (`UPDATE ... SET qty = qty - 1 WHERE qty >= 1`), optimistic
locking with a version column, or a transaction with the right isolation level. See
[transactions](17-transactions.md).

**Floating-point money.**
Why it is wrong: `0.1 + 0.2 !== 0.3`; rounding errors accumulate into real financial
discrepancies.
The fix: store money as integer minor units (cents) or a fixed-precision decimal type.

**Missing transaction on a multi-step write.**
Why it is wrong: a crash between step one and step two leaves the system in a half-applied
state (order created, payment never recorded).
The fix: wrap the steps in one transaction, or use the outbox/saga pattern when they span
services.

## Error Handling

**Swallowing errors.**
Why it is wrong: `catch (e) { log(e) }` lets a failed operation report success; the
corruption surfaces far away with no trace back to the cause.
The fix: handle where you can act, otherwise rethrow with context. Never catch just to log.

**Catching everything at the top and returning 200.**
Why it is wrong: clients and monitors believe the request succeeded, so retries and alerts
never fire.
The fix: map errors to correct status codes; let unexpected errors surface as 5xx and page
someone. See [error handling](12-error-handling.md).

**Leaking internals in error responses.**
Why it is wrong: stack traces, SQL, and file paths in a 500 body hand attackers a map of
the system.
The fix: return a generic message plus a correlation id; log the detail server-side only.

## Performance and Scale

**N+1 queries.**
Why it is wrong: loading a list then querying per item turns one request into hundreds of
round-trips; latency explodes under real data volume.
The fix: batch with a join, an `IN` query, or a dataloader. See [performance](19-performance.md).

**Unbounded queries.**
Why it is wrong: `SELECT * FROM events` works in dev with 100 rows and OOMs the process at
10 million.
The fix: paginate every list, always cap with `LIMIT`, and stream large exports.

**Premature optimization.**
Why it is wrong: complex caching or hand-tuned code added without a measurement obscures
logic and hides bugs, while the real bottleneck sits elsewhere.
The fix: measure first, optimize the proven hot path, keep the rest simple.

**Caching without invalidation.**
Why it is wrong: a cache with no TTL or invalidation serves stale data indefinitely,
producing "impossible" bugs.
The fix: set a TTL, invalidate on write, and treat the cache as disposable, never the
source of truth. See [caching](13-caching.md).

## Architecture

**Fat controllers / anemic everything else.**
Why it is wrong: business logic in HTTP handlers cannot be reused by jobs or queues and
cannot be unit-tested without an HTTP layer.
The fix: keep handlers thin (parse, authorize, delegate); put logic in a service/domain
layer. See [business logic](07-business-logic.md).

**Hidden globals and singletons.**
Why it is wrong: modules that import a shared `db` or `config` are untestable and behave
differently depending on invisible init order.
The fix: inject dependencies as arguments or via a container.

**Distributed monolith.**
Why it is wrong: services split over the network but still deployed and changed in
lockstep get microservice latency with monolith coupling — the worst of both.
The fix: split on real bounded contexts with independent data and deploy cadence, or stay
a modular monolith until the seam is proven.

**Chatty synchronous service calls.**
Why it is wrong: a request that makes ten blocking downstream calls multiplies latency and
fails if any one is slow.
The fix: parallelize independent calls, use async messaging for non-critical work, and add
timeouts and circuit breakers.

## Operations

**Config and secrets in source.**
Why it is wrong: secrets in git leak permanently (history is forever) and config baked into
the image cannot vary per environment.
The fix: inject config via env, pull secrets from a manager.

**No timeouts on outbound calls.**
Why it is wrong: one hung dependency holds a connection open, threads pile up, and the pool
exhausts — a single slow service takes the whole app down.
The fix: set an explicit timeout on every network and DB call, plus a circuit breaker on
critical dependencies.

## AI Review Checklist

- Are all writes idempotent and multi-step writes transactional?
- Are read-modify-write sequences made atomic or version-guarded?
- Are there any swallowed errors, or handlers that hide failures behind a 200?
- Are there N+1 or unbounded queries on hot paths?
- Is business logic out of controllers and dependencies injected, not global?
- Do all outbound calls have timeouts, and are secrets kept out of source?

## Related

- `knowledge/backend/30-engineering-principles.md`
- `knowledge/backend/12-error-handling.md`
- `knowledge/backend/17-transactions.md`
- `knowledge/backend/19-performance.md`
- `knowledge/backend/99-ai-review-checklist.md`
