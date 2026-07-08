---
id: backend/27-production
topic: backend
slug: production
title: "Production"
type: doc
order: 27
status: ready
tags: [backend, production]
related: [backend/26-deployment, backend/22-observability, backend/19-performance, backend/20-scalability, backend/98-production-checklist]
when_to_use: "Read before taking a service live, or when hardening one that already runs under real traffic."
---
# Production

## Purpose

This document defines what it means for a backend service to be *production-ready*: able to
run under real, hostile, unpredictable load and keep working, degrade gracefully, and recover
without a human on the keyboard. It covers reliability patterns (timeouts, retries, circuit
breakers), graceful degradation, resource limits, health signalling, and the operational
posture a live service needs. Correctness in a test suite is table stakes; this is about
survival in the real world.

## Why It Matters

Test environments are calm; production is not. In production, dependencies time out, disks
fill, traffic spikes 10x, a bad deploy lands, and a slow downstream drags everything with it.
Code that assumes the network is reliable, the dependency is up, and the input is well-formed
will fail — the only question is how badly. A production-ready service fails *small*: it sheds
load instead of falling over, isolates a broken dependency instead of cascading, and tells its
operators what is wrong before customers do. This is the difference between a blip and an outage.

## Core Principles

- **The network always fails; design for it.** Every remote call has a timeout, a bounded
  retry, and a defined behavior when it fails. No unbounded waits, ever.
- **Isolate failure, do not propagate it.** A slow or down dependency must not consume all
  your threads/connections. Use timeouts, bulkheads, and circuit breakers to contain the blast.
- **Degrade gracefully.** When a non-critical dependency is down, serve a reduced experience,
  not an error page. Shed load before you collapse under it.
- **Bound every resource.** Connection pools, queues, request bodies, concurrency, and memory
  all have hard limits. Unbounded anything eventually exhausts and takes down the process.
- **Make the service observable and self-reporting.** It must expose health, metrics, and
  structured logs so failures are detectable before they are catastrophic.

## Best Practices

- Set an explicit **timeout on every I/O call** (DB, cache, HTTP, queue). Default client
  timeouts are often infinite; an infinite timeout under load exhausts the thread pool.
- Retry only **idempotent** operations, with **exponential backoff and jitter** and a small
  cap. Blind retries amplify an outage into a self-inflicted DDoS.
- Wrap flaky dependencies in a **circuit breaker**: after N failures, fail fast for a cooldown
  instead of piling requests onto a dead service.
- Apply **backpressure and load shedding**: reject or queue-with-limit when saturated, and
  return `429`/`503` with `Retry-After` rather than accepting work you cannot finish.
- Bound connection pools and configure them below the database's max connections; a pool larger
  than the DB allows just moves the failure.
- Make writes **idempotent** (idempotency keys) so retries and redeliveries do not double-charge
  or duplicate.
- Expose readiness that reflects real dependency health, and shut down gracefully on `SIGTERM`.
- Run with resource limits (CPU/memory) and autoscaling tied to a real signal (latency, queue
  depth), not just CPU.

## Examples

**Good Example** — bounded timeout, capped retry with jitter, fail-fast breaker

```python
async def fetch_quote(symbol: str) -> Quote:
    # Every call is time-bounded; without this, one slow upstream stalls all workers.
    if breaker.is_open():                      # dependency known-bad: fail fast, don't pile on
        raise DependencyUnavailable("quotes")

    for attempt in range(3):                   # capped retries, not infinite
        try:
            return await http.get(url(symbol), timeout=2.0)   # hard timeout
        except (Timeout, ConnError) as e:
            breaker.record_failure()
            if attempt == 2:
                raise
            await sleep(backoff(attempt) + random_jitter())   # backoff + jitter avoids sync retry storms
```

**Bad Example** — no timeout, infinite retry, cascading failure

```python
async def fetch_quote(symbol: str) -> Quote:
    while True:                                 # retries forever
        try:
            return await http.get(url(symbol))  # no timeout -> waits indefinitely
        except Exception:
            continue                            # hammers a dying service, holds a worker hostage
    # One slow upstream drains the whole worker pool; the entire service goes down with it.
```

## Common Mistakes

- Remote calls with no timeout, so one slow dependency exhausts all workers and cascades.
- Retrying non-idempotent writes, causing duplicate charges or records.
- Retries without backoff/jitter, turning a hiccup into a synchronized retry storm.
- Connection pool sized larger than the database permits, so saturation just relocates.
- Returning `500` when a *non-critical* dependency is down instead of degrading.
- No load shedding: accepting unlimited work until memory or the queue explodes.
- Autoscaling on CPU when the real bottleneck is latency or queue depth.

## Production Tips

- Run game days / chaos tests: kill a dependency in staging and confirm the service degrades
  instead of collapsing.
- Define SLOs and an error budget; let them decide when to prioritize reliability over features.
- Alert on symptoms users feel (latency, error rate, saturation), not on internal causes that
  may not matter.

## AI Review Checklist

- Does every I/O call have an explicit, finite timeout?
- Are retries limited, jittered, and restricted to idempotent operations?
- Are flaky dependencies protected by a circuit breaker or equivalent fail-fast?
- Is there load shedding / backpressure with `429`/`503` when saturated?
- Are pools, queues, request sizes, and concurrency all bounded?
- Does the service degrade gracefully when a non-critical dependency is down?
- Does readiness reflect real dependency health, and does shutdown drain in-flight work?

## Related

- `knowledge/backend/26-deployment.md`
- `knowledge/backend/22-observability.md`
- `knowledge/backend/19-performance.md`
- `knowledge/backend/20-scalability.md`
- `knowledge/backend/98-production-checklist.md`
