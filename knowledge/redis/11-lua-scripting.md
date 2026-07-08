---
id: redis/11-lua-scripting
topic: redis
slug: lua-scripting
title: "Lua Scripting"
type: doc
order: 11
status: ready
tags: [redis, lua-scripting]
related: [redis/10-transactions, redis/17-distributed-locks, redis/14-rate-limiting, redis/19-clustering, redis/100-common-antipatterns]
when_to_use: "Read before writing an EVAL/EVALSHA script, or when you need read-decide-write logic to run atomically on the server."
---
# Lua Scripting

## Purpose

This document defines how to run **server-side Lua** in Redis (`EVAL`, `EVALSHA`,
`SCRIPT LOAD`, and Functions): a way to execute custom logic atomically inside the server,
seeing intermediate values and branching on them. It is written so an agent can move
read-decide-write logic into a script when [transactions](10-transactions.md) are not
enough — without breaking atomicity, replication, or cluster routing.

A Lua script is the tool when you must read a value, make a decision based on it, and write —
all as one indivisible unit. Unlike a `MULTI`/`EXEC` transaction, a script *can* see the
result of one command and branch before running the next. This is how correct rate limiters,
[distributed locks](17-distributed-locks.md), and conditional updates are built.

## Why It Matters

Redis runs a script atomically: while it executes, no other command interleaves. That is an
enormous safety guarantee — it turns a racy read-modify-write into a single atomic
operation. But the same property is a loaded gun: because the whole server is blocked for the
script's duration, one slow or looping script freezes every client. And scripts have strict
rules — all keys must be declared, no non-deterministic calls that break replication — that,
if violated, corrupt replicas or fail on a cluster. Used well, Lua eliminates whole classes
of concurrency bugs; used carelessly, it takes the entire instance down.

## Core Principles

- **Atomic and blocking.** A script runs to completion with nothing else interleaving. Keep
  it **short and O(1)-ish**; a long script blocks the entire server, not just one client.
- **Declare every key in `KEYS`.** Pass keys as `KEYS[1..n]` and other arguments as
  `ARGV[1..n]`. Never build a key name from `ARGV` and access it — the cluster router and
  replication depend on knowing the keys up front.
- **Scripts must be deterministic.** Given the same keys/args and data, they must produce the
  same writes. Avoid `TIME`, `RANDOMKEY`, and unseeded randomness for anything you write —
  pass such values in via `ARGV` from the client instead.
- **Cache with `EVALSHA`.** `SCRIPT LOAD` returns a SHA; call `EVALSHA <sha> ...` to avoid
  resending the body. Fall back to `EVAL` on a `NOSCRIPT` error (e.g., after a restart).
- **Errors abort the script; there is no partial rollback of writes already done.** A script
  that writes then errors leaves those writes. Validate first, write last.

## Best Practices

- Use Lua for read-decide-write atomicity: check a value, then conditionally write, in one
  server round trip with no race — the canonical fix for TOCTOU bugs a transaction can't cover.
- Pass all keys via `KEYS`, never hard-code or compute them from `ARGV`, so the script works
  in Redis Cluster (all `KEYS` must hash to the same slot — use hash tags if needed).
- Load once with `SCRIPT LOAD`, call with `EVALSHA`, and handle `NOSCRIPT` by re-loading —
  this minimizes bandwidth without risking a missing-script failure after failover/restart.
- Keep scripts tiny and bounded. No unbounded loops, no `O(N)` scans over large keys inside a
  script; that blocks the whole instance.
- Return simple values (numbers, strings, arrays). Map Lua types deliberately — Lua `nil`
  becomes a Redis nil and truncates arrays; Lua `false` also maps to nil.
- For reusable, named, persisted logic, consider **Redis Functions** (`FUNCTION LOAD`,
  Redis 7+): they are the modern successor to ad-hoc `EVAL` scripts and survive restarts.
- Never `redis.call` a command whose keys you did not declare — it breaks cluster and
  replication guarantees.

## Examples

**Good Example** — atomic conditional decrement (e.g., reserve stock)

```lua
-- KEYS[1] = stock key, ARGV[1] = quantity to reserve.
-- Read, decide, and write atomically: no other client interleaves, so the
-- classic check-then-decrement race cannot happen. Returns new count or -1.
local qty = tonumber(ARGV[1])
local current = tonumber(redis.call('GET', KEYS[1]) or '0')
if current < qty then
  return -1                       -- validate BEFORE any write; nothing changed
end
return redis.call('DECRBY', KEYS[1], qty)
```

```bash
# Load once, then call by SHA to save bandwidth; fall back to EVAL on NOSCRIPT.
SCRIPT LOAD "<script above>"      # -> "a1b2c3..."
EVALSHA a1b2c3... 1 stock:sku42 3
```

**Bad Example** — non-deterministic writes and undeclared keys

```lua
-- Uses server TIME (non-deterministic) to build a value it writes, so the
-- master and replica store DIFFERENT data — replication diverges.
local now = redis.call('TIME')[1]
-- Builds a key from ARGV instead of KEYS: the cluster can't route it and
-- replication doesn't know the key was touched.
local key = 'log:' .. ARGV[1]
redis.call('SET', key, now)       -- undeclared key + non-deterministic value
```

## Common Mistakes

- Writing values derived from `TIME`/random inside the script, causing replica divergence —
  pass the timestamp/random from the client via `ARGV`.
- Building or accessing keys not passed in `KEYS`, breaking Redis Cluster and replication.
- Long-running or looping scripts that block the entire server for every other client.
- Using only `EVAL` (resending the body each call) instead of `SCRIPT LOAD` + `EVALSHA`.
- Not handling `NOSCRIPT` after a restart/failover, so cached-SHA calls suddenly fail.
- Writing before validating, then erroring — leaving partial writes with no rollback.
- Forgetting Lua `nil`/`false` map to Redis nil and can silently truncate a returned array.

## Production Tips

- Set `busy-reply-threshold` (formerly `lua-time-limit`) and know that `SCRIPT KILL` only
  works if the script has not yet written; a writing runaway needs `SHUTDOWN NOSAVE`. Keep
  scripts fast so you never get there.
- Version and store scripts in source control, deployed via `SCRIPT LOAD` or `FUNCTION LOAD`
  at startup — never paste anonymous `EVAL` bodies inline in application code paths.
- Prefer Redis Functions for anything reused across services: they are named, listed by
  `FUNCTION LIST`, and persisted with the dataset, unlike ephemeral script SHAs.

## AI Review Checklist

- Are all accessed keys passed via `KEYS`, never computed from `ARGV` or hard-coded?
- Is the script deterministic — no writes derived from `TIME`/random generated server-side?
- Is it short and bounded, with no unbounded loops or large scans that block the server?
- Does it validate before writing, given there is no rollback on error?
- Is it invoked via `EVALSHA` with a `NOSCRIPT` fallback, not repeated `EVAL`?
- In a cluster, do all `KEYS` share a hash slot (via hash tags if needed)?

## Related

- `knowledge/redis/10-transactions.md`
- `knowledge/redis/17-distributed-locks.md`
- `knowledge/redis/14-rate-limiting.md`
- `knowledge/redis/19-clustering.md`
- `knowledge/redis/100-common-antipatterns.md`
