---
id: nginx/14-rate-limiting
topic: nginx
slug: rate-limiting
title: "Rate Limiting"
type: doc
order: 14
status: ready
tags: [nginx, rate-limiting]
related: [nginx/13-security, nginx/15-authentication, nginx/05-reverse-proxy, nginx/17-monitoring]
when_to_use: "Read before adding `limit_req` / `limit_conn` throttling in nginx or reviewing abuse-protection config."
---
# Rate Limiting

## Purpose

This document defines how to throttle traffic in nginx with `limit_req` (request rate)
and `limit_conn` (concurrent connections): choosing a key, sizing the zone, setting a
sane burst, and returning the right status. It is written so an agent can add
protection that stops abuse without breaking legitimate bursty clients.

Rate limiting is the cheapest defense against brute-force, credential stuffing,
scraping, and accidental client loops. nginx applies it before the request reaches the
application, so it protects the backend even when the app is overwhelmed.

## Why It Matters

Without a limit, one client — malicious or buggy — can consume all of the backend's
capacity, turning a single bad actor into a full outage for everyone. Login and
password-reset endpoints are attacked continuously; unthrottled, they are brute-forced.
But a badly tuned limit is its own outage: too strict and every real user hits 503;
keyed wrong and one shared NAT or CDN IP throttles a whole population; sized too small
and the zone silently overflows. The failure modes are opposite, so the value is in
tuning, not merely in turning it on.

## Core Principles

- **Limit at the edge, before the app.** nginx rejecting a flood costs almost nothing;
  the application doing it costs a worker, a DB call, and often the outage you feared.
- **Choose the key deliberately.** `$binary_remote_addr` throttles per client IP; a
  header or cookie throttles per user or API key. The wrong key punishes the wrong people.
- **Allow bursts, then queue or reject.** Real traffic is bursty; `burst` absorbs
  spikes and `nodelay` serves them immediately while still capping the sustained rate.
- **Fail loudly and correctly.** Return `429 Too Many Requests` (not the default 503)
  so clients and monitoring understand what happened.
- **Layer limits.** A global connection cap plus a per-endpoint request rate plus a
  tight login limit each guard a different failure.

## Best Practices

- Define zones once at `http` scope: `limit_req_zone $binary_remote_addr zone=api:10m
  rate=10r/s;` — `$binary_remote_addr` is compact (a 10m zone holds ~160k IPs).
- Apply per `location` with `limit_req zone=api burst=20 nodelay;`. `nodelay` serves
  the burst immediately rather than trickling it out.
- Set a **much tighter** limit on auth endpoints (e.g. `5r/m`) than on general API traffic.
- Override the status: `limit_req_status 429;` and `limit_conn_status 429;`.
- Behind a proxy/CDN, key on the **real** client IP (`set_real_ip_from` +
  `real_ip_header`), or every request appears to come from one edge address.
- Use `limit_conn` to cap concurrent connections per key for slow-loris and download abuse.
- Whitelist trusted internal callers with a `geo`/`map` that sets an empty key so they
  are exempt.

## Examples

**Good Example** — layered limits, real IP, correct status

```nginx
http {
    # Compact per-IP zones defined once; general API vs. strict auth.
    limit_req_zone  $binary_remote_addr zone=api:10m   rate=10r/s;
    limit_req_zone  $binary_remote_addr zone=login:10m rate=5r/m;
    limit_conn_zone $binary_remote_addr zone=conns:10m;
    limit_req_status  429;                       # honest status, not default 503
    limit_conn_status 429;

    server {
        set_real_ip_from 10.0.0.0/8;             # trust our LB so the key is the real client
        real_ip_header   X-Forwarded-For;

        location /api/ {
            limit_req  zone=api burst=20 nodelay; # absorb spikes, cap sustained rate
            limit_conn conns 10;                  # at most 10 concurrent per client
            proxy_pass http://app;
        }
        location = /login {
            limit_req zone=login burst=3 nodelay; # brute-force protection: 5/min + tiny burst
            proxy_pass http://app;
        }
    }
}
```

**Bad Example** — wrong key, no burst, wrong status

```nginx
http {
    # Keyed on full text remote addr wastes zone memory; tiny zone overflows silently.
    limit_req_zone $remote_addr zone=all:1m rate=100r/s;

    server {
        # Behind a CDN, $remote_addr is the CDN edge IP → every user shares one bucket,
        # so a handful of real users trip the limit for everyone.
        location / {
            limit_req zone=all;                  # no burst → normal bursty traffic gets 503
            # Default 503 tells clients "server down", not "you were throttled".
            proxy_pass http://app;
        }
        # No separate, stricter limit on /login → brute force runs at 100r/s.
    }
}
```

## Common Mistakes

- Keying on the CDN/proxy edge IP instead of the real client, throttling everyone at once.
- No `burst`, so ordinary bursty browsers get rejected on legitimate traffic.
- Leaving the default `503` instead of `429`, confusing clients and dashboards.
- One global limit with no tighter rule on login/reset, leaving brute force wide open.
- Undersized zones that overflow (nginx then applies the limit to *all* new keys).
- Using `$remote_addr` (text) instead of `$binary_remote_addr`, wasting zone memory.
- Forgetting that `limit_req`/`limit_conn` do not inherit into a nested `location` that
  omits them — the child is then unthrottled.

## Production Tips

- Log the limiting decision (`$limit_req_status` via a custom log format) and alert when
  the rejection rate climbs — it distinguishes an attack from a misconfiguration.
- Start permissive, watch real traffic percentiles, then tighten; guessing the rate
  blind usually breaks real users first.
- Combine with [authentication](15-authentication.md) and firewall/WAF rules — rate
  limiting slows abuse, it does not authenticate or block a determined attacker alone.

## AI Review Checklist

- Is the limit keyed on the real client IP (or user/API key), not a shared proxy edge?
- Do auth/reset endpoints have a distinctly tighter limit than general traffic?
- Is `burst` set so legitimate bursty clients are not rejected?
- Is the response status `429`, not the default `503`?
- Is `$binary_remote_addr` used and the zone sized for the expected key cardinality?
- Are `limit_req`/`limit_conn` present in every `location` that needs them (no missed inheritance)?
- Are rejections logged and monitored?

## Related

- `knowledge/nginx/13-security.md`
- `knowledge/nginx/15-authentication.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/17-monitoring.md`
