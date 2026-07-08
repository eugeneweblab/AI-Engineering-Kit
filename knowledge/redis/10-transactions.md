---
id: redis/10-transactions
topic: redis
slug: transactions
title: "Transactions"
type: doc
order: 10
status: ready
tags: [redis, transactions]
related: [redis/11-lua-scripting, redis/17-distributed-locks, redis/06-sorted-sets, redis/23-performance, redis/100-common-antipatterns]
when_to_use: "Read before using MULTI/EXEC or WATCH, or when you need several Redis commands to run without another client interleaving."
---
# Transactions

## Purpose

This document defines how Redis **transactions** work — `MULTI`, `EXEC`, `DISCARD`, and the
optimistic-locking primitive `WATCH` — and their real guarantees. It is written so an agent
understands that a Redis transaction is *not* an SQL transaction: it provides isolation and
all-or-nothing queuing, but **no rollback** and only optimistic concurrency control.

Use a transaction when several commands must execute back-to-back with no other client
interleaving between them, and when a check-then-act must abort if the watched state
changed. For anything involving conditional logic on values read mid-sequence, a
[Lua script](11-lua-scripting.md) is usually simpler and stronger.

## Why It Matters

Developers coming from relational databases assume `MULTI`/`EXEC` means "atomic with
rollback on error." It does not. If one command in a transaction fails at runtime (say,
`INCR` on a string that holds text), the *other commands still execute* and there is no
rollback. Meanwhile the real concurrency tool, `WATCH`, is optimistic: it does not lock,
it aborts `EXEC` if the watched key changed — and code that ignores the aborted result
silently loses the update. Misunderstanding either point produces bugs that only appear
under concurrency, which is exactly where they are hardest to reproduce and most damaging.

## Core Principles

- **`MULTI`/`EXEC` queues then runs commands with no interleaving.** Between `EXEC` starting
  and finishing, no other client's commands run. That is the isolation guarantee.
- **No rollback.** Errors detected *before* `EXEC` (syntax, unknown command) abort the whole
  transaction. Errors that surface *during* `EXEC` (wrong type on a valid command) do **not**
  stop the others and do **not** undo prior commands. Redis has no undo.
- **`WATCH` is optimistic concurrency control.** `WATCH key ... MULTI ... EXEC`: if any
  watched key was modified by anyone between `WATCH` and `EXEC`, `EXEC` returns nil (aborts).
- **An aborted `EXEC` must be retried by you.** A nil reply means "someone else won the race."
  You must loop: re-`WATCH`, re-read, re-queue, re-`EXEC`.
- **You cannot branch inside a transaction.** Queued commands cannot see each other's results,
  so conditional logic on mid-transaction values is impossible — that is Lua's job.

## Best Practices

- Use `WATCH` + `MULTI`/`EXEC` for check-then-set over multiple keys, and **always handle the
  nil (aborted) reply with a bounded retry loop** — otherwise a lost race is silently ignored.
- Keep the watch window short: `WATCH`, read, immediately `MULTI`/`EXEC`. The longer the
  window, the more likely a conflicting write aborts you and forces a retry.
- Prefer a single atomic command when one exists (`INCR`, `SETNX`, `ZADD GT`, `HINCRBY`) over
  a transaction — it is simpler and cannot abort.
- For read-decide-write logic that must be atomic, prefer a [Lua script](11-lua-scripting.md):
  it runs atomically, *can* branch on values, and needs no retry loop.
- Use `DISCARD` to abandon a queued transaction and clear any `WATCH`es.
- Do not run slow operations inside `MULTI`/`EXEC`; the whole block blocks the server since no
  other command interleaves.
- Remember `EXEC` and `DISCARD` clear all watches — you do not `UNWATCH` manually in the normal path.

## Examples

**Good Example** — optimistic locking with a retry loop

```python
# Atomically move funds between two Redis-held balances using WATCH.
def transfer(r, src, dst, amount):
    while True:                      # bounded retry in real code
        with r.pipeline() as p:
            p.watch(src)             # abort EXEC if src changes under us
            balance = int(p.get(src) or 0)
            if balance < amount:
                p.unwatch()
                raise ValueError("insufficient funds")
            p.multi()                # start queuing
            p.decrby(src, amount)
            p.incrby(dst, amount)
            try:
                p.execute()          # nil/WatchError => someone changed src; loop
                return
            except redis.WatchError:
                continue             # retry: re-read, re-queue — the update is NOT lost
```

**Bad Example** — assuming rollback, ignoring the aborted result

```python
def transfer(r, src, dst, amount):
    p = r.pipeline()
    p.multi()
    p.decrby(src, amount)
    p.incrby(dst, amount)
    # No WATCH: a concurrent transfer can interleave the read the caller did
    # earlier, so the balance check is stale. And if DECRBY errored at runtime,
    # INCRBY would STILL run — there is no rollback. EXEC's result is discarded,
    # so a conflict/abort passes unnoticed and the transfer is silently lost.
    p.execute()
```

## Common Mistakes

- Expecting rollback: a runtime error on one command leaves the rest applied.
- Using `WATCH` but not checking for the nil/`WatchError` result, silently dropping updates.
- No retry loop around an optimistic transaction, so any contention loses the write.
- Holding the `WATCH` window open across slow work, guaranteeing frequent aborts.
- Trying to branch on a value read inside `MULTI` — queued commands cannot see each other.
- Reaching for a transaction where a single atomic command (`INCR`, `SETNX`) would do.
- Running a long `MULTI`/`EXEC`, blocking every other client for its duration.

## Production Tips

- Cap retries and add jitter/backoff on `WATCH` conflicts to avoid a thundering herd on a
  hot key; if conflicts are frequent, the key is a contention hotspot — reconsider the model
  or move the logic into Lua.
- When correctness depends on reading a value and acting on it, default to Lua over
  `WATCH`/`MULTI`; it removes the retry loop and the whole class of abort bugs.
- In Redis Cluster, all keys in a transaction must live on the same slot — use hash tags
  (`{user:42}:a`, `{user:42}:b`) or the transaction is rejected.

## AI Review Checklist

- Is the code relying on rollback that Redis does not provide?
- Does every `WATCH`-based transaction check the aborted (nil/`WatchError`) result?
- Is there a bounded retry loop around optimistic transactions?
- Is the `WATCH`-to-`EXEC` window kept short, with no slow work inside it?
- Would a single atomic command or a [Lua script](11-lua-scripting.md) be simpler and safer here?
- In a cluster, do all touched keys share a hash slot?

## Related

- `knowledge/redis/11-lua-scripting.md`
- `knowledge/redis/17-distributed-locks.md`
- `knowledge/redis/06-sorted-sets.md`
- `knowledge/redis/23-performance.md`
- `knowledge/redis/100-common-antipatterns.md`
