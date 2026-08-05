---
id: architecture/17-fault-tolerance
topic: architecture
slug: fault-tolerance
title: "Fault Tolerance"
type: doc
order: 17
status: ready
tags: [architecture, fault-tolerance, valid, Timeout, Retry, except]
related: [architecture/16-high-availability, architecture/12-integration-patterns, architecture/21-distributed-systems, architecture/18-observability, architecture/20-message-brokers]
when_to_use: "Read when a request depends on something that can fail — a network call, a database, a queue — and must degrade instead of crashing."
---
# Fault Tolerance

## Purpose

This document defines how a single request survives partial failure: timeouts,
retries with backoff, circuit breakers, bulkheads, graceful degradation, and
idempotency. It is written so an agent can make a service that bends under failure
instead of breaking, and does not turn one failing dependency into a total outage.

Fault tolerance is the request-level counterpart to [high-availability](16-high-availability.md).
HA gives you redundant infrastructure; fault tolerance is the code that uses it — the
timeouts and fallbacks that keep a request meaningful when a dependency is slow or down.
Redundancy without these patterns still cascades into failure.

## Why It Matters

In any distributed system, dependencies fail *partially and constantly* — a call is slow,
a node is flaky, a queue is backed up. The default behavior of naive code in these
conditions is the worst possible one: it waits forever, retries in a tight loop, and holds
resources until it exhausts them. That is how a single slow dependency becomes a
system-wide outage — threads pile up waiting, retries amplify the load on the struggling
service, and the failure cascades upstream. Fault tolerance is the set of patterns that
break this chain: fail fast, contain the failure, and give the caller a degraded-but-valid
answer instead of a hang or a crash.

## Core Principles

- **Everything remote can fail; plan the failure path.** Every network call needs a defined
  behavior for timeout, error, and slowness — not just the happy path. The failure path is
  the design, not an afterthought.
- **Fail fast, not forever.** A bounded timeout that returns an error beats an unbounded wait
  that ties up a thread. Slow is worse than down, because slow exhausts resources silently.
- **Contain failure with bulkheads.** Isolate resources (thread pools, connection pools) per
  dependency so one saturated dependency cannot consume the capacity the others need.
- **Stop hammering a failing service.** A circuit breaker trips after repeated failures and
  fails fast for a cooldown, giving the dependency room to recover instead of amplifying its load.
- **Degrade gracefully.** When a non-essential dependency is down, return a reduced result
  (cached data, a default, a partial page) rather than failing the whole request.

## Best Practices

- Set an explicit, tight timeout on every remote call. Choose it from the dependency's normal
  latency (e.g. p99 + margin), not an arbitrary large number.
- Retry only **transient** failures (timeouts, 503, connection resets), with **exponential
  backoff and jitter**, and a hard cap. Retrying without backoff turns a blip into a
  self-inflicted DDoS on the recovering service.
- Only retry **idempotent** operations, or use an idempotency key, so a retry cannot duplicate
  a side effect (see [integration-patterns](12-integration-patterns.md)).
- Wrap unstable dependencies in a circuit breaker; when open, serve a fallback immediately
  instead of queuing calls that will fail.
- Use bulkheads: give each downstream dependency its own bounded pool so one hang cannot starve
  the whole service of threads or connections.
- Define a fallback for every non-critical dependency — a stale cache read, an empty list, a
  feature-flagged "unavailable" state — so the core request still succeeds.
- Make consumers idempotent so at-least-once delivery and retries are safe by construction.

## Examples

**Good Example** — timeout, capped backoff, breaker, fallback

```python
# Bounded timeout + circuit breaker + graceful fallback. WHY: a slow or down
# recommendations service can never stall the page; the breaker stops hammering it,
# and the user still gets a valid (if generic) response.
@circuit_breaker(failure_threshold=5, reset_timeout=30)
def get_recommendations(user_id: str) -> list[Item]:
    return client.get(
        f"/recommend/{user_id}",
        timeout=Timeout(connect=1.0, read=2.0),          # fail fast, not forever
        retries=Retry(total=2, backoff=0.3, jitter=True, # backoff+jitter avoids a
                      retry_on=[503, 504]),              # synchronized retry storm
    ).json()

def recommendations_for(user_id: str) -> list[Item]:
    try:
        return get_recommendations(user_id)
    except (Timeout, CircuitOpen):
        return popular_items_cached()  # degrade gracefully, keep the page working
```

**Bad Example** — no timeout, unbounded retries, cascade

```python
def get_recommendations(user_id):
    while True:                       # retry forever, no backoff, no cap
        try:
            # No timeout: a hung dependency holds this thread indefinitely. Under load
            # every worker ends up stuck here and the whole service stops responding —
            # one slow dependency becomes a total outage.
            return requests.get(f"https://rec/recommend/{user_id}").json()
        except Exception:
            continue                  # tight loop hammers the failing service harder
```

## Common Mistakes

- No timeout on a remote call, so a slow dependency ties up threads until the service hangs.
- Retrying immediately and unboundedly, amplifying load on a service that is already failing.
- Retrying non-idempotent operations, so a retry double-charges or double-sends.
- Sharing one thread/connection pool across all dependencies, so one hang starves everything
  (no bulkhead).
- No fallback, so a non-critical dependency's outage fails the entire request.
- Treating "slow" as fine — unbounded latency is an outage in slow motion and exhausts
  resources just as surely as a crash.
- Adding a circuit breaker but never testing the open state, so the fallback path is broken
  exactly when it is needed.

## Production Tips

- Expose circuit-breaker state, retry counts, and timeout rates as metrics; a rising timeout
  rate is the earliest sign a dependency is degrading (see [observability](18-observability.md)).
- Tune timeouts from real latency percentiles and revisit them — a timeout set once and never
  reviewed drifts out of sync with the dependency.
- Test failure paths explicitly: inject latency and errors (fault injection) in staging so the
  fallbacks are exercised before production needs them.
- Keep a dead-letter queue for messages that repeatedly fail so a poison message cannot block
  the pipeline (see [message-brokers](20-message-brokers.md)).

## AI Review Checklist

- Does every remote call have an explicit, tight timeout?
- Are retries limited to transient errors, with exponential backoff, jitter, and a hard cap?
- Are retried operations idempotent or idempotency-keyed?
- Is there a circuit breaker around unstable dependencies, with a fast fallback when open?
- Are dependencies isolated by bulkheads so one hang cannot starve the whole service?
- Does each non-critical dependency have a graceful-degradation fallback?
- Have the failure paths (timeout, error, open circuit) actually been tested?

## Related

- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/12-integration-patterns.md`
- `knowledge/architecture/21-distributed-systems.md`
- `knowledge/architecture/18-observability.md`
- `knowledge/architecture/20-message-brokers.md`
