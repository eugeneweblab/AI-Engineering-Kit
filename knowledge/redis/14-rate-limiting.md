---
id: redis/14-rate-limiting
topic: redis
slug: rate-limiting
title: "Redis Rate Limiting"
type: doc
order: 14
status: ready
tags: [redis, rate-limiting]
related: [redis/11-lua-scripting, redis/12-expiration, redis/06-sorted-sets, redis/10-transactions, redis/17-distributed-locks]
when_to_use: "Read before building an API throttle, login-attempt limiter, or any per-user quota on Redis."
---
# Redis Rate Limiting

## Purpose

This document defines how to build correct rate limiters on Redis: fixed-window,
sliding-window, and token-bucket algorithms, and the atomicity rules that keep
them accurate under concurrency. It is written so an agent can enforce a quota
that cannot be bypassed by racing requests.

Redis is the standard home for rate-limit counters because they are small,
hot, shared across app instances, and naturally expiring. The hard part is not
counting — it is counting *atomically*.

## Why It Matters

A rate limiter is a security and cost control: it stops brute-force login
attempts, credential stuffing, scraping, and runaway API bills. A limiter that
"mostly works" is worthless — an attacker only needs the race condition, not the
happy path.

The core hazard is the check-then-act gap. If two requests both read a counter of
`99`, both see "under the limit of 100", and both increment to `100`, you served
101 requests. Under attack, thousands of concurrent requests widen this gap
dramatically. Correct rate limiting means the read-decide-write step is a single
atomic operation, always.

## Core Principles

- **Increment and check must be atomic.** Never `GET` then `SET`. Use `INCR`
  (atomic) or a Lua script that does the whole decision server-side in one step.
- **The counter key must always carry a TTL.** The window is defined by the
  expiry. Set it on the *first* increment of a window, atomically, or the key
  leaks and the limit never resets.
- **Choose the algorithm for the guarantee you need.** Fixed-window is cheapest
  but allows a 2x burst at the boundary; sliding-window is smoother; token-bucket
  models sustained rate plus burst allowance.
- **Fail open or closed on purpose.** Decide explicitly what happens when Redis is
  unreachable — allow the request (availability) or deny it (protection) — and
  document it. Don't let it be accidental.
- **Identify the subject correctly.** Rate-limit by a key you trust (authenticated
  user id, API key), not just client IP, which is shared and spoofable behind
  proxies.

## Best Practices

- For a simple fixed window, use `INCR` and set the TTL only when the counter is
  first created:

  ```
  INCR rl:{user}:{window}
  # if the returned value == 1, this is a new window -> set its expiry
  EXPIRE rl:{user}:{window} 60 NX
  ```

  Even better, collapse both into one Lua script so there is zero gap.
- For accuracy without boundary bursts, use a **sliding-window log** with a
  sorted set: score = timestamp, prune old entries with `ZREMRANGEBYSCORE`, count
  with `ZCARD`. Costs more memory but is precise.
- For sustained-rate control, use a **token bucket** in a Lua script: store
  `tokens` and `last_refill`, refill based on elapsed time, decrement on request.
- Return standard headers so clients can back off: `RateLimit-Limit`,
  `RateLimit-Remaining`, `RateLimit-Reset` (and `Retry-After` on 429).
- Keep limiter keys short and namespaced (`rl:`); they are numerous and hot.
- Combine with application-level lockout for auth endpoints (see
  [authentication](../security/03-authentication.md)) — rate limiting slows brute
  force; lockout stops it.

## Examples

**Good Example** — atomic fixed window in one Lua script

```lua
-- rate_limit.lua  — KEYS[1]=counter key, ARGV[1]=limit, ARGV[2]=window secs
-- Runs atomically on the server: no check-then-act gap between requests.
local current = redis.call("INCR", KEYS[1])
if current == 1 then
  -- first hit of this window: attach the TTL that defines the window
  redis.call("EXPIRE", KEYS[1], ARGV[2])
end
if current > tonumber(ARGV[1]) then
  return 0            -- denied
end
return 1              -- allowed
```

```ts
// One round trip, fully atomic. EVALSHA in production after SCRIPT LOAD.
const allowed = await redis.eval(script, 1, `rl:${userId}`, "100", "60");
if (allowed === 0) return res.status(429).set("Retry-After", "60").end();
```

**Bad Example** — non-atomic GET/SET, TTL that never sets

```ts
// BUG 1: read and write are separate -> two racing requests both pass at 99.
const n = Number(await redis.get(key)) || 0;
if (n >= 100) return res.status(429).end();
await redis.set(key, n + 1);        // last writer wins; increments are lost

// BUG 2: TTL is only set here, and SET above already wiped any prior TTL,
// so the window never actually resets and the counter drifts.
await redis.expire(key, 60);
```

## Common Mistakes

- Using `GET`/`SET` (or read-modify-write in app code) instead of `INCR` or Lua,
  leaving a race that lets bursts exceed the limit.
- Setting the TTL on every request instead of only on window creation — a plain
  `SET` wipes the TTL each time, so the window slides forever and never resets.
- Forgetting the TTL entirely, so counters accumulate and permanently lock a user
  out (or leak memory).
- Rate-limiting purely by IP behind a load balancer or NAT, punishing many users
  who share an address and missing per-account abuse.
- Ignoring the fixed-window boundary burst when the SLA actually requires a smooth
  rate — switch to sliding-window or token-bucket.
- Not deciding fail-open vs fail-closed for a Redis outage.

## Production Tips

- Preload scripts with `SCRIPT LOAD` and call `EVALSHA` to avoid shipping the Lua
  body on every request.
- On a Redis Cluster, ensure all keys a single script touches share a hash slot
  (use a `{user}` hash tag) — cross-slot scripts error.
- Emit a metric for allowed vs denied per rule so you can spot both attacks and
  overly-tight limits that hurt real users.
- Keep limits in config, not hardcoded, so you can tighten them during an incident
  without a deploy.

## AI Review Checklist

- Is the increment-and-check a single atomic operation (`INCR` or Lua), never
  `GET` then `SET`?
- Is the TTL set exactly once per window (on first increment), and never wiped by
  later writes?
- Does the limiter key include a trustworthy subject (user/API key), not just IP?
- Is the fail-open/fail-closed behavior on Redis outage explicit and intentional?
- Does the response return 429 with `Retry-After` / `RateLimit-*` headers?
- On Cluster, do multi-key scripts use a hash tag to stay in one slot?

## Related

- `knowledge/redis/11-lua-scripting.md`
- `knowledge/redis/12-expiration.md`
- `knowledge/redis/06-sorted-sets.md`
- `knowledge/redis/10-transactions.md`
- `knowledge/redis/17-distributed-locks.md`
