---
id: databases/13-eventual-consistency
topic: databases
slug: eventual-consistency
title: "Eventual Consistency"
type: doc
order: 13
status: ready
tags: [databases, eventual-consistency, OutOfStock, reserve, transaction]
related: [databases/12-acid, databases/14-replication, databases/15-sharding, databases/22-high-availability, databases/02-relational-vs-nosql]
when_to_use: "Read before building read paths against replicas, distributed stores, or caches that can return stale data."
---
# Eventual Consistency

## Purpose

This document defines what "eventual consistency" actually promises, when it is the
right trade, and how to write application code that stays correct while data is
temporarily stale. It exists so an agent can decide whether a given read may tolerate
staleness — and, when it may not, avoid a design that quietly returns wrong answers.

Eventual consistency is the deliberate relaxation of the `I` and instantaneous
propagation you get from [ACID](12-acid.md). In exchange for availability and scale,
you accept that a write becomes visible everywhere *eventually*, not immediately.

## Why It Matters

Any system with read replicas, a cache, a CDN, or a distributed store is already
eventually consistent — whether the developer planned for it or not. The danger is
that it works perfectly in testing (one node, no lag) and breaks in production under
load, when replication lag stretches from microseconds to seconds. A user updates
their profile and sees the old value; a "read-your-own-write" reads a stale replica;
a balance check passes against data that is 400ms behind. These are not crashes —
they are plausible-looking wrong answers. Because the failure only appears under real
concurrency and lag, it is easy to ship and hard to catch.

## Core Principles

- **Eventual means "given no new writes, all replicas converge."** It says nothing
  about *how long*. Under load, lag is unbounded unless you bound it.
- **CAP is a real trade, not a slogan.** During a network partition a system must
  choose availability (serve possibly-stale data) or consistency (reject the read).
  Most distributed stores default to availability; know which yours picks.
- **Not all data tolerates staleness equally.** A follower count can lag; an account
  balance, an auth token, or an inventory count used to sell the last item cannot.
  Classify each read.
- **Stronger guarantees are available on demand.** Read-your-writes, monotonic reads,
  and bounded staleness are opt-in tools, not automatic. Use them where correctness
  needs them and pay the latency only there.
- **Design for convergence conflicts.** Concurrent writes to the same key must have a
  defined resolution: last-write-wins, version vectors, or a CRDT. "Undefined" means
  silent data loss.

## Best Practices

- Route reads that must reflect a user's own just-made write to the primary, or use a
  read-your-writes token/session so the same session sees its update.
- For money, inventory, and uniqueness, do the critical read and the write in one
  strongly-consistent transaction on the primary. Never gate a sell-the-last-unit
  decision on a replica read.
- Make writes idempotent (keyed by a client-supplied id) so a retry after uncertain
  propagation does not double-apply.
- Bound staleness where the store allows it (e.g. "read within 5s of latest") instead
  of accepting unbounded lag.
- Show the user the truth: display "pending" states and reconcile, rather than
  pretending a not-yet-propagated write is done.
- Pick and document a conflict-resolution strategy per dataset; prefer commutative
  operations (increments, set-adds) that converge without coordination.
- Monitor replication lag and alert; treat lag over your SLA as an incident, because
  correctness assumptions depend on it.

## Examples

**Good Example** — critical decision on primary, tolerant read on replica

```ts
// Selling the last unit is a correctness-critical invariant, so it runs in one
// strong transaction on the PRIMARY — no replica in the decision path.
async function reserve(itemId: string) {
  return db.primary.transaction(async (tx) => {
    const updated = await tx.query(
      `UPDATE inventory SET qty = qty - 1
        WHERE id = $1 AND qty >= 1 RETURNING qty`, [itemId]);
    if (updated.rowCount === 0) throw new OutOfStock();
  });
}

// A product's view count only needs to be roughly right, so a possibly-stale
// replica read is fine and takes load off the primary.
const views = await db.replica.query(
  "SELECT view_count FROM items WHERE id = $1", [itemId]);
```

**Bad Example** — correctness decision on a lagging replica

```ts
// Reads qty from a replica that may be seconds behind. Two buyers both see
// qty=1, both "reserve", and the item is oversold. The write is correct in
// isolation; the stale READ is what breaks the invariant.
const { qty } = await db.replica.query(
  "SELECT qty FROM inventory WHERE id = $1", [itemId]);
if (qty < 1) throw new OutOfStock();
await db.primary.query(
  "UPDATE inventory SET qty = qty - 1 WHERE id = $1", [itemId]);
```

## Common Mistakes

- Assuming a read replica is "instantly" up to date and using it for correctness
  checks.
- Gating a uniqueness or inventory decision on stale data instead of an atomic write
  on the primary.
- Retrying a write after a timeout without idempotency, double-applying it once the
  original finally lands.
- Leaving concurrent-write conflicts with no defined resolution, so one write is
  silently lost.
- Confusing eventual consistency with "no consistency" — convergence still requires
  correct conflict handling.
- Never measuring replication lag, so the staleness window is unknown.

## Production Tips

- Export replication lag as a first-class metric with alerting thresholds tied to
  your consistency SLA.
- Provide a "read from primary" escape hatch on endpoints that occasionally need
  strong reads, rather than downgrading everything.
- Load-test with artificial replica lag injected, so read-your-writes bugs surface
  before production does.

## AI Review Checklist

- Is every correctness-critical read (money, inventory, uniqueness, auth) served by a
  strongly-consistent path, not a replica or cache?
- Do users see their own writes immediately (primary routing or a session token)?
- Are writes idempotent so retries after uncertain propagation are safe?
- Is there a defined conflict-resolution strategy for concurrent writes to the same
  key?
- Is replication lag measured and alerted against a stated SLA?
- Where staleness is accepted, is it a deliberate, documented choice — not an
  accident?

## Related

- `knowledge/databases/12-acid.md`
- `knowledge/databases/14-replication.md`
- `knowledge/databases/15-sharding.md`
- `knowledge/databases/22-high-availability.md`
- `knowledge/databases/02-relational-vs-nosql.md`
