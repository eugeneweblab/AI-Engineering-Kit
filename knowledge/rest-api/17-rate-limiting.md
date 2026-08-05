---
id: rest-api/17-rate-limiting
topic: rest-api
slug: rate-limiting
title: "REST API Rate Limiting"
type: doc
order: 17
status: ready
tags: [rest-api, rate-limiting, rateLimit, ceil, Retry-After, RateLimit-Reset, RateLimit-Remaining]
related: [rest-api/15-authentication, rest-api/16-authorization, rest-api/07-status-codes, rest-api/24-security, rest-api/25-performance]
when_to_use: "Read before exposing any public or authenticated endpoint that could be called in a loop."
---
# REST API Rate Limiting

## Purpose

This document defines how a REST API caps request volume per client: which algorithm to use,
what to key the limit on, which headers and status code to return, and how to protect the API
without punishing well-behaved clients. It is written so an agent can add rate limiting that
actually holds under abuse and communicates clearly to callers.

Rate limiting is a defense-in-depth control that protects availability and cost. It complements
[authentication](15-authentication.md) and [authorization](16-authorization.md): even a
correctly authenticated caller must not be able to exhaust the service.

## Why It Matters

Without rate limiting, one client — buggy, malicious, or just enthusiastic — can consume all
capacity, driving up latency and cost for everyone and enabling brute-force against login and
token endpoints. The failure mode is a self-inflicted denial of service: the API stays "up"
but is unusable, and cloud bills spike from unbounded traffic. Rate limits turn an unbounded
risk into a bounded, predictable one, and they make abuse visible instead of silent. They are
not optional on any endpoint reachable from the open internet.

## Core Principles

- **Limit every public endpoint.** Unauthenticated endpoints (login, signup, search, token)
  are the highest priority — they are the cheapest to attack and the most damaging.
- **Key the limit on identity, then fall back to IP.** Rate-limit per API key / user for
  authenticated calls; per IP (with proxy-aware client extraction) for anonymous ones.
- **Communicate limits explicitly.** Return `429 Too Many Requests` with `Retry-After` and
  `RateLimit` headers so well-behaved clients can back off instead of hammering.
- **Fail closed on the limiter, open on availability — decide deliberately.** If the limiter
  store is down, choose whether to allow or reject, and make that choice conscious, not accidental.
- **Different endpoints deserve different limits.** A cheap read and an expensive report or a
  login attempt should not share one budget.

## Best Practices

- Use a **token-bucket** or **sliding-window** algorithm, not a fixed calendar window. Fixed
  windows allow a burst of 2× the limit across the window boundary; sliding/token-bucket smooth
  that out.
- Store counters in a shared, fast store (Redis) so the limit holds across all API instances.
  An in-process counter resets per instance and is trivially bypassed by load balancing.
- Return `429` with:
  - `Retry-After: <seconds>` — when the client may try again.
  - `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` — the standardized draft
    headers — on *every* response, not just on `429`, so clients self-throttle.
- Apply **stricter limits to auth endpoints** (login, MFA, password reset, token) and add
  progressive backoff / lockout to blunt credential stuffing — see [authentication](15-authentication.md).
- Extract the real client IP from the trusted proxy header (`X-Forwarded-For` left-most trusted
  hop), not the raw socket, or every request behind your load balancer shares one bucket.
- Set limits per **route class and per plan/tier**, and document them. Silent limits frustrate
  integrators; published limits let them design around them.
- Combine with quotas (daily/monthly caps) for cost control, distinct from per-second burst limits.

## Examples

**Good Example** — sliding window in Redis, standard headers, per-identity key

```ts
async function rateLimit(req: Request, res: Response, cfg: { limit: number; windowMs: number }) {
  // Key on API key when present, else the proxy-resolved client IP.
  const key = req.apiKeyId ?? clientIp(req); // shared bucket only for truly anonymous callers
  const { count, resetMs } = await redisSlidingWindow(key, cfg.windowMs); // shared store, atomic

  res.set("RateLimit-Limit", String(cfg.limit));
  res.set("RateLimit-Remaining", String(Math.max(0, cfg.limit - count)));
  res.set("RateLimit-Reset", String(Math.ceil(resetMs / 1000)));

  if (count > cfg.limit) {
    res.set("Retry-After", String(Math.ceil(resetMs / 1000))); // tell the client when to retry
    throw new TooManyRequests(); // 429, not 403 or 503
  }
}
```

**Bad Example** — in-memory fixed window, no client feedback

```ts
const hits = new Map<string, number>(); // per-process: resets on deploy, not shared across pods

function rateLimit(req: Request) {
  const minute = new Date().getMinutes();
  const key = `${req.ip}:${minute}`;         // fixed window -> 2x burst at the boundary
  const n = (hits.get(key) ?? 0) + 1;
  hits.set(key, n);
  if (n > 100) throw new Error("slow down"); // generic 500, no 429, no Retry-After header
  // req.ip is the load balancer's IP, so ALL users share one bucket.
}
```

## Common Mistakes

- Counting requests in process memory, so the limit resets on deploy and is bypassed by having
  multiple instances.
- Using a fixed calendar window, allowing a 2× burst across the boundary.
- Returning `500` or `403` instead of `429`, and omitting `Retry-After` — clients cannot back off.
- Keying on the raw socket IP behind a proxy, so every client shares the load balancer's bucket.
- Applying one global limit to login and to cheap reads alike, so auth stays brute-forceable.
- No `RateLimit-*` headers on normal responses, so clients only discover the limit by hitting it.
- Forgetting quotas: a per-second limit still allows unbounded cost over a day.

## Production Tips

- Emit metrics for `429` rate per route and per client; a rising `429` rate is either abuse or a
  limit set too low for legitimate traffic — both need attention.
- Make limits configurable without a deploy (config store / feature flag) so you can tighten
  them during an incident.
- Decide the limiter's failure mode explicitly: for auth endpoints, fail *closed* (reject) when
  the counter store is unavailable; for read endpoints you may fail open to preserve availability.

## AI Review Checklist

- Is every public endpoint rate-limited, with stricter limits on auth endpoints?
- Are counters kept in a shared store so the limit holds across all instances?
- Is a sliding-window or token-bucket algorithm used instead of a fixed window?
- Does exceeding the limit return `429` with `Retry-After` and `RateLimit-*` headers?
- Is the limit keyed on API key/user, falling back to a proxy-resolved client IP?
- Is the limiter's behavior when its store is unavailable decided deliberately?

## Related

- `knowledge/rest-api/15-authentication.md`
- `knowledge/rest-api/16-authorization.md`
- `knowledge/rest-api/07-status-codes.md`
- `knowledge/rest-api/24-security.md`
- `knowledge/rest-api/25-performance.md`
