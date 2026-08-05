---
id: security/21-rate-limiting
topic: security
slug: rate-limiting
title: "Security Rate Limiting"
type: doc
order: 21
status: ready
tags: [security, rate-limiting]
related: [security/03-authentication, security/22-security-headers, security/25-monitoring, security/26-incident-response]
when_to_use: "Read before protecting login, signup, password-reset, or any expensive endpoint from abuse."
---
# Security Rate Limiting

## Purpose

This document defines how to limit the rate of requests an actor may make, so that
brute-force, credential-stuffing, scraping, and denial-of-service attempts are throttled
before they succeed or exhaust resources. It is written so an agent can add rate limiting
that actually holds under a distributed attack, not one that a second server or a rotated
IP walks around.

Rate limiting is both a security control (slowing guessing attacks) and an availability
control (protecting shared resources). It complements, but does not replace,
[authentication](03-authentication.md) and account lockout.

## Why It Matters

Any endpoint that verifies a secret — login, MFA, password reset, coupon redemption — is a
guessing target. Without a limit, an attacker sends millions of attempts and only needs one
to work. Expensive endpoints (search, report generation, sign-up email) are DoS targets:
unbounded traffic exhausts CPU, database connections, or third-party quotas and takes the
whole service down for everyone. Rate limiting is cheap to add and one of the highest-value
controls per line of code — but only if it is enforced server-side, shared across
instances, and keyed on something the attacker cannot trivially rotate.

## Core Principles

- **Enforce on the server, in shared state.** A per-process in-memory counter resets on
  deploy and is bypassed by hitting a different instance. Use a shared store (Redis or an
  edge/gateway limiter) so the limit is global.
- **Choose the key deliberately.** IP alone is weak (NAT groups many users; attackers
  rotate IPs). Rate-limit sensitive actions by account/identifier *and* IP, and apply a
  coarser IP limit as a backstop.
- **Fail closed for security limits, open for availability limits.** If the limiter store
  is unreachable, a login limiter should deny (protect the secret); a generic API limiter
  may allow (protect availability) — decide per endpoint.
- **Layer the limits.** A single global limit is either too loose for login or too tight for
  browsing. Apply tiered limits: strict on auth, moderate on writes, generous on reads.
- **Communicate the limit.** Return `429 Too Many Requests` with `Retry-After` so
  legitimate clients back off instead of hammering.

## Best Practices

- Use a proven algorithm — **token bucket** or **sliding-window counter** — over a naive
  fixed window, which allows a 2x burst at the window boundary.
- Store counters in Redis (or the API gateway/WAF) with atomic increments and a TTL, so all
  app instances share one view and stale counters expire automatically.
- Key auth endpoints on `(account_identifier, ip)` and add a separate global per-IP cap.
  Combine with exponential backoff / lockout for repeated failures.
- Send standard headers: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, and
  `Retry-After` on `429`.
- Put a coarse limit at the edge (CDN/WAF) to absorb volumetric attacks before they reach
  app servers, and a precise, identity-aware limit in the application.
- Rate-limit by expensive operation, not just endpoint — a single request that triggers ten
  downstream calls deserves a tighter budget.

## Examples

**Good Example** — atomic sliding window in shared Redis, keyed by account and IP

```ts
// Redis Lua-backed sliding window (sorted-set log). Prune-old + count + add + set-TTL run
// as ONE atomic script per request, so concurrent requests across all app instances share
// one accurate count and the key always gets a TTL — no request can leave it un-expired.
// Returns -1 when allowed, else the seconds until the oldest hit leaves the window.
const SLIDING_WINDOW = `
  local now    = tonumber(ARGV[1])
  local window = tonumber(ARGV[2])
  local limit  = tonumber(ARGV[3])
  redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, now - window)  -- drop hits older than the window
  local count = redis.call('ZCARD', KEYS[1])
  if count < limit then
    redis.call('ZADD', KEYS[1], now, ARGV[4])               -- record this request
    redis.call('PEXPIRE', KEYS[1], window)                  -- TTL always set; key can't leak
    return -1                                               -- allowed
  end
  redis.call('PEXPIRE', KEYS[1], window)
  local oldest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
  return math.ceil(((tonumber(oldest[2]) + window) - now) / 1000)  -- deny; retry-after (s)
`;

async function checkLoginLimit(email: string, ip: string): Promise<void> {
  const key = `rl:login:${email}:${ip}`;          // identity + IP, not IP alone
  const now = Date.now();
  const windowMs = 15 * 60 * 1000;                // 15-minute sliding window
  const limit = 10;
  const member = `${now}:${crypto.randomUUID()}`; // unique so same-ms hits don't collide
  const retryAfter = (await redis.eval(
    SLIDING_WINDOW, 1, key, String(now), String(windowMs), String(limit), member,
  )) as number;
  if (retryAfter >= 0) {
    // Fail CLOSED: deny the sensitive action and tell the client when to retry.
    throw new RateLimitError(429, { retryAfter });
  }
}
```

**Bad Example** — per-process counter keyed only on IP

```ts
const hits = new Map<string, number>(); // in-memory: resets on deploy, not shared

function checkLoginLimit(ip: string) {
  const n = (hits.get(ip) ?? 0) + 1;
  hits.set(ip, n);
  // Keyed on IP only: many users behind one NAT are throttled together, while an
  // attacker rotating IPs is never throttled at all. A second instance has its own map,
  // so the "limit" is really limit * instanceCount.
  if (n > 1000) throw new Error("Too many requests"); // and no expiry → grows forever
}
```

## Common Mistakes

- Counting in per-process memory, so the limit multiplies by instance count and resets on
  every deploy.
- Keying solely on IP — punishes shared-NAT users, ignores IP-rotating attackers.
- Using a fixed window, permitting a double burst across the boundary.
- Failing open on the limiter store for a security-critical endpoint, silently disabling it.
- No `Retry-After`, so well-behaved clients retry aggressively and worsen load.
- Limiting only the login form while password-reset and MFA endpoints stay unlimited.
- Forgetting counter TTLs, leaking memory and permanently locking out an actor.

## Production Tips

- Emit metrics on `429` rates and top limited keys; a sudden spike is an attack signal for
  [monitoring](25-monitoring.md) and [incident response](26-incident-response.md).
- Make limits configurable without a deploy so you can tighten them during an incident.
- Test the limiter in CI: assert the Nth request returns `429` with `Retry-After`, and that
  the window resets after the TTL.
- For authenticated APIs, consider per-API-key quotas in addition to per-request limits.

## AI Review Checklist

- Is the counter stored in shared state (Redis/gateway), not per-process memory?
- Are sensitive endpoints keyed on identity *and* IP, not IP alone?
- Is the algorithm token-bucket or sliding-window (not a burst-prone fixed window)?
- Do security-critical limiters fail closed when the store is unreachable?
- Does the response return `429` with `Retry-After` and rate-limit headers?
- Are login, signup, MFA, and password-reset all covered — not just one of them?
- Do counters have TTLs so they expire and cannot leak or permanently lock an actor?

## Related

- `knowledge/security/03-authentication.md`
- `knowledge/security/22-security-headers.md`
- `knowledge/security/25-monitoring.md`
- `knowledge/security/26-incident-response.md`
