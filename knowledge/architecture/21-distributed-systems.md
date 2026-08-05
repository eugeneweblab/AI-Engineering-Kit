---
id: architecture/21-distributed-systems
topic: architecture
slug: distributed-systems
title: "Architecture Distributed Systems"
type: doc
order: 21
status: ready
tags: [architecture, distributed-systems]
related: [architecture/17-fault-tolerance, architecture/16-high-availability, architecture/09-microservices, architecture/20-message-brokers, architecture/18-observability]
when_to_use: "Read before designing any system where components communicate over a network, or when debugging inconsistency, partial failure, or race conditions across services."
---
# Architecture Distributed Systems

## Purpose

This document defines how to reason about systems whose parts run on different machines and
communicate over a network. It covers the guarantees you can and cannot rely on, and the
patterns that keep such systems correct under partial failure. It is written so an agent can
design cross-service interactions without assuming a reliability the network does not provide.

The defining trait of a distributed system is *partial failure*: one component can be down,
slow, or unreachable while the rest keep running, and no single node knows the global state.
Every hard problem below — consistency, ordering, consensus, exactly-once — descends from that
one fact. Design as if any remote call may not complete, because eventually one will not.

## Why It Matters

The fallacies of distributed computing — "the network is reliable, latency is zero, bandwidth
is infinite, the topology never changes" — are seductive precisely because they hold in local
testing. They break in production, at scale, under load, at the worst time. A call that returns
in 2 ms on a laptop can hang for 30 s across a congested link, and a timeout tells you the
request failed *but not whether the work happened*. Systems built on optimistic assumptions
lose data, double-process, deadlock, or split-brain. Systems built on explicit failure handling
stay correct while degrading gracefully. There is no middle ground you discover later cheaply.

## Core Principles

- **Assume partial failure everywhere.** Any remote call may time out, and a timeout is
  ambiguous — the work may have succeeded, failed, or still be running. Design for all three.
- **You cannot have C, A, and P at once (CAP).** During a network partition you must choose
  consistency or availability. Decide per operation which one the business needs.
- **Prefer idempotent, retryable operations.** Since you must retry ambiguous calls, every
  operation must be safe to repeat. Idempotency is what makes retries safe.
- **There is no global "now."** Clocks drift and messages reorder. Never order events by
  wall-clock timestamps across nodes; use logical clocks, version vectors, or a sequencer.
- **Consensus is expensive; avoid needing it.** Agreement across nodes (leader election,
  distributed locks) is slow and fragile. Use a proven system (Raft/etcd), never hand-roll it.

## Best Practices

- Set explicit timeouts, bounded retries with exponential backoff and jitter, and circuit
  breakers on every outbound call. An unbounded retry storm turns a blip into an outage.
- Make writes idempotent with an idempotency key so a retried request is applied at most once,
  even though it may be *received* many times.
- Replace distributed transactions with the **saga pattern**: a sequence of local transactions,
  each with a compensating action to undo it. Two-phase commit across services does not scale
  and blocks on coordinator failure.
- Use the **outbox pattern** to publish events atomically with a state change: write the event
  to an outbox table in the same DB transaction, then relay it. This avoids the dual-write bug
  where the DB commit succeeds but the event publish fails (or vice versa).
- Choose the consistency model per data: strong (linearizable) where correctness demands it
  (balances, inventory), eventual where availability matters more (feeds, counters). Make the
  choice explicit — accidental eventual consistency is a bug.
- Design for graceful degradation: shed load, serve stale-but-available data, and fail a
  feature rather than the whole request when a dependency is down.
- Propagate a `trace_id` across every hop so a request that touches ten services can be
  reconstructed after it fails.

## Examples

**Good Example** — idempotent, bounded retry, ambiguity-safe

```python
async def transfer(idem_key: str, frm: str, to: str, amount: int) -> Result:
    # Idempotency key makes a retried (possibly duplicate) request a no-op:
    # a timeout on the caller's side can be safely retried without double-transfer.
    if prior := await ledger.find_by_key(idem_key):
        return prior.result
    async with retry(max_attempts=3, backoff="expo+jitter"):
        # local transaction; on network timeout we retry the SAME idem_key
        return await ledger.apply(idem_key, frm, to, amount)
```

**Bad Example** — no idempotency, blind retry, wall-clock ordering

```python
async def transfer(frm: str, to: str, amount: int) -> Result:
    while True:                                  # unbounded retry -> retry storm
        try:
            return await ledger.apply(frm, to, amount)  # no idem key -> a timed-out
        except TimeoutError:                     # but succeeded call retries -> double spend
            continue
# elsewhere: events ordered by `datetime.now()` across nodes -> clock skew reorders them
```

## Common Mistakes

- Treating a timeout as "it failed" and retrying without idempotency, causing double effects.
- Unbounded or un-jittered retries that synchronize and amplify a transient failure into an outage.
- The dual-write bug: committing to a database and separately publishing an event, with no
  atomicity, so the two diverge on a crash (fixed by the outbox pattern).
- Ordering distributed events by wall-clock timestamps, which clock skew silently reorders.
- Hand-rolling distributed locks or leader election instead of using etcd/ZooKeeper/Consul.
- Attempting two-phase commit across service boundaries, which blocks and does not scale.
- Assuming strong consistency from an eventually-consistent store, then reading stale data.

## Production Tips

- Run chaos/game-day exercises that kill nodes and inject latency; a distributed system is only
  as correct as its behavior under the failures you have actually tested.
- Alert on partition symptoms: rising cross-node latency, replication lag, and quorum loss.
- Prefer managed consensus/coordination services over self-hosted; the operational edge cases
  are where hand-rolled systems fail.

## AI Review Checklist

- Does every remote call have an explicit timeout, bounded backoff+jitter, and a fallback?
- Are ambiguous (timed-out) operations safe to retry via idempotency keys?
- Are cross-service transactions modeled as sagas with compensations, not 2PC?
- Are state change + event publish made atomic (outbox), avoiding the dual-write bug?
- Is the consistency model (strong vs eventual) chosen explicitly per operation?
- Is event ordering based on logical clocks/sequencers, never wall-clock timestamps?
- Is consensus delegated to a proven system rather than hand-rolled?

## Related

- `knowledge/architecture/17-fault-tolerance.md`
- `knowledge/architecture/16-high-availability.md`
- `knowledge/architecture/09-microservices.md`
- `knowledge/architecture/20-message-brokers.md`
- `knowledge/architecture/18-observability.md`
