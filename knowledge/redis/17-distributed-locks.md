---
id: redis/17-distributed-locks
topic: redis
slug: distributed-locks
title: "Distributed Locks"
type: doc
order: 17
status: ready
tags: [redis, distributed-locks, DEL, INCR, EXPIRE, eval, randomUUID]
related: [redis/11-lua-scripting, redis/12-expiration, redis/10-transactions, redis/13-caching, redis/18-replication]
when_to_use: "Read before using Redis to make sure only one process runs a critical section at a time."
---
# Distributed Locks

## Purpose

This document defines how to build a mutual-exclusion lock on Redis so that only
one process across a fleet executes a critical section at a time. It covers the
correct acquire/release pattern, why the lock token matters, the safety limits of
Redis locks, and when *not* to use one. It is written so an agent can add a lock
without creating a deadlock or a silent double-execution.

A distributed lock is easy to write and easy to write *wrong*. The naive version
looks correct and fails exactly when it matters — under contention and after a
crash.

## Why It Matters

Locks exist to prevent two workers from doing the same one-time action: sending a
payout twice, running a migration concurrently, processing the same job in
parallel. A broken lock doesn't error — it lets both workers through, and the
damage (a duplicate charge, corrupted state) is discovered later.

The two classic failures are a **deadlock** (a holder crashes and never releases,
so the lock is stuck forever) and a **stolen lock** (a slow holder's lock expires,
another worker acquires it, and then the first worker's release deletes the *new*
holder's lock). Both come from skipping two small details: an expiry on acquire,
and a unique token checked on release.

## Core Principles

- **Acquire atomically with an expiry.** Use `SET key token NX PX <ttl>` in one
  command. `NX` makes it a lock; `PX` guarantees it auto-releases if the holder
  dies. Never `SET NX` then `EXPIRE` — a crash between them deadlocks.
- **Every lock carries a unique token.** Store a random value the holder keeps.
  It is what lets release verify *you* still own the lock.
- **Release must be conditional and atomic.** Delete only if the stored token is
  still yours, via a Lua script (check-and-delete in one step). A bare `DEL` can
  delete a lock another worker now holds.
- **The TTL bounds correctness, not just cleanup.** If work can outlive the TTL,
  the lock can be stolen mid-execution. Size the TTL above worst-case work time,
  or extend it (fence), or don't rely on the lock alone for safety.
- **A single-node Redis lock is not perfectly safe.** Failover can lose the lock
  key. For correctness-critical mutual exclusion, add a fencing token the
  protected resource verifies — don't trust the lock in isolation.

## Best Practices

- Acquire: `SET lock:<resource> <token> NX PX 30000`. A non-`OK` reply means the
  lock is held; back off and retry with jitter, or fail fast.
- Release with a Lua compare-and-delete so it is atomic:

  ```lua
  -- release.lua — KEYS[1]=lock key, ARGV[1]=my token
  if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])   -- only delete MY lock
  else
    return 0                            -- someone else holds it now; do nothing
  end
  ```
- Keep the critical section **short and idempotent** so a lost lock does minimal
  damage. The lock reduces the odds of double-execution; idempotency makes it
  survivable.
- If work may exceed the TTL, run a **watchdog** that periodically extends the TTL
  (compare-and-`PEXPIRE` with the same Lua guard) while work is in progress.
- For high-stakes correctness across Redis failover, use a **fencing token**: an
  ever-increasing number (e.g. from `INCR`) passed to the protected resource,
  which rejects writes carrying a stale token. This is the only real protection
  against a lock held by two processes.
- Prefer a battle-tested library (Redlock implementations, `redis-lock`, etc.)
  over hand-rolling; they encode the token and Lua-release correctly.

## Examples

**Good Example** — atomic acquire with token, safe compare-and-delete release

```ts
const token = crypto.randomUUID();               // unique per acquisition
const key = "lock:invoice:42";

// Atomic acquire WITH expiry: auto-releases if this process dies.
const ok = await redis.set(key, token, "NX", "PX", 30000);
if (!ok) throw new LockBusy();                    // someone else holds it

try {
  await doExactlyOnceWork();                      // keep this short + idempotent
} finally {
  // Atomic check-and-delete: only release the lock if it is still MINE.
  await redis.eval(
    `if redis.call("GET", KEYS[1]) == ARGV[1] then return redis.call("DEL", KEYS[1]) else return 0 end`,
    1, key, token,
  );
}
```

**Bad Example** — non-atomic acquire, blind release

```ts
const key = "lock:invoice:42";

// BUG 1: SET NX then EXPIRE are two commands. A crash in between leaves the
// lock with no TTL -> permanent deadlock, nobody can ever acquire it again.
const ok = await redis.set(key, "1", "NX");
if (ok) await redis.expire(key, 30);

try {
  await doExactlyOnceWork();                      // may run longer than 30s...
} finally {
  // BUG 2: unconditional DEL. If our lock already expired and another worker
  // acquired it, this deletes THEIR lock -> two workers run at once.
  await redis.del(key);
}
```

## Common Mistakes

- `SET NX` followed by a separate `EXPIRE`, leaving a crash window that deadlocks
  the lock forever. Always use `SET ... NX PX`.
- Releasing with a plain `DEL` instead of a token-checked Lua script, letting a
  stale holder delete the current holder's lock.
- No expiry at all, so a crashed holder never releases and the resource is stuck.
- A TTL shorter than the worst-case work time, so the lock is silently stolen
  mid-execution and two workers proceed.
- Assuming a single Redis node lock is perfectly safe across failover — trusting
  it for money-moving operations without a fencing token.
- Using a lock where a simpler primitive fits: a `SET NX` dedupe key or an atomic
  `INCR` often replaces a lock entirely and can't be "stolen".

## Production Tips

- Instrument lock wait time and contention; high wait time means the critical
  section is too long or too coarse-grained — split the resource key.
- On Redis Cluster, keep the lock key on one slot (it is a single key, so this is
  automatic) and remember that failover can drop it — fence anything critical.
- Prefer designing the operation to be **idempotent** so that even a lock failure
  degrades to a harmless retry rather than corruption. The best lock is the one
  whose failure doesn't matter.

## AI Review Checklist

- Is the lock acquired atomically with its expiry (`SET ... NX PX`), never
  `SET NX` + `EXPIRE`?
- Does the lock store a unique token, and does release compare it before deleting?
- Is release an atomic Lua check-and-delete, never a bare `DEL`?
- Is the TTL longer than the worst-case critical section, or is there a watchdog
  extending it?
- For correctness-critical work, is there a fencing token the resource verifies,
  rather than trusting the Redis lock alone?
- Could a simpler idempotent design (dedupe key, `INCR`) avoid the lock entirely?

## Related

- `knowledge/redis/11-lua-scripting.md`
- `knowledge/redis/12-expiration.md`
- `knowledge/redis/10-transactions.md`
- `knowledge/redis/13-caching.md`
- `knowledge/redis/18-replication.md`
