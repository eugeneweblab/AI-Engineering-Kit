---
id: nginx/06-load-balancing
topic: nginx
slug: load-balancing
title: "Load Balancing"
type: doc
order: 6
status: ready
tags: [nginx, load-balancing, max_fails, fail_timeout, down, non_idempotent, ip_hash, keepalive]
related: [nginx/05-reverse-proxy, nginx/08-caching, nginx/17-monitoring, nginx/27-high-availability, nginx/12-ssl-tls]
when_to_use: "Read before spreading traffic across two or more application instances behind nginx."
---
# Load Balancing

## Purpose

This document defines how to distribute traffic across multiple backend instances with
nginx's `upstream` block: choosing a balancing algorithm, wiring health checks, handling
session affinity, and draining a node safely. It builds directly on the
[reverse proxy](05-reverse-proxy.md) — load balancing is a reverse proxy pointed at a
pool instead of a single server.

Load balancing answers "which healthy instance should serve this request?". Get it wrong
and you either overload one node while others idle, or you route users to a server that is
already dead.

## Why It Matters

The load balancer is a single point of decision for every request. A bad algorithm choice
concentrates load; a missing health check sends users to a crashed node and returns 502s;
a wrong affinity setting logs users out or defeats horizontal scaling entirely. Because
the balancer sits in front of the whole pool, its mistakes are multiplied by every backend
and every request. This code must be explicit and defensive: assume backends fail, assume
they come and go, and make the config say exactly what happens when they do.

## Core Principles

- **Pick an algorithm on purpose.** Round-robin (default) suits uniform, stateless
  backends. `least_conn` suits uneven or long-lived requests. `ip_hash` or a hash key
  gives affinity. Never leave it to chance — know why you chose one.
- **Assume backends fail.** Configure `max_fails` and `fail_timeout` so nginx stops
  routing to a dead node. A pool without passive health checks is a pool that serves 502s.
- **Prefer stateless backends over sticky sessions.** Affinity (`ip_hash`, sticky cookie)
  is a workaround for server-side state; it undermines even balancing and complicates
  draining. Externalize session state instead where you can.
- **Drain, don't kill.** Mark a node `down` (or weight it out) and let in-flight requests
  finish before you remove it. Yanking a node mid-request drops live connections.
- **Never add `non_idempotent` to `proxy_next_upstream`.** Since nginx 1.9.13 the default
  already refuses to retry a non-idempotent request (POST/LOCK/PATCH) once it has been sent
  to an upstream. Adding the `non_idempotent` flag overrides that safety and can
  double-charge a customer. Constrain retries to safe methods and conditions.

## Best Practices

- Define the pool in one `upstream` block and reference it by name; do not scatter
  backend addresses across `location` blocks.
- Set `keepalive` in the upstream to reuse backend connections, and pair it with
  `proxy_http_version 1.1` plus `proxy_set_header Connection ""` so keepalive actually
  works — otherwise every request opens a fresh TCP connection.
- Use `least_conn` when request durations vary widely; round-robin assumes each request
  costs roughly the same.
- Tune `max_fails` (e.g. 3) and `fail_timeout` (e.g. 30s) rather than accepting defaults;
  the defaults (1 failure, 10s) are often too twitchy or too slow for your latency budget.
- Bound `proxy_next_upstream_tries` and `proxy_next_upstream_timeout` so a bad request
  cannot walk the entire pool and blow your latency SLA.
- For zero-downtime deploys, reload with a node marked `down` first; graceful `reload`
  keeps existing connections while new ones use the updated pool.
- If you need active health checks (probing an endpoint on an interval, not just reacting
  to real traffic), that requires nginx Plus or a module like `ngx_http_healthcheck` —
  open-source nginx only has passive checks.

## Examples

**Good Example** — explicit algorithm, health limits, keepalive, safe retries

```nginx
upstream app_pool {
    least_conn;                      # backends have uneven request durations
    server 10.0.0.11:8080 max_fails=3 fail_timeout=30s;
    server 10.0.0.12:8080 max_fails=3 fail_timeout=30s;
    server 10.0.0.13:8080 backup;    # only used when the primaries are down
    keepalive 32;                    # reuse upstream connections
}

server {
    location / {
        proxy_pass http://app_pool;
        proxy_http_version 1.1;
        proxy_set_header Connection "";           # required for upstream keepalive
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Only retry on connection-level failures, and never for non-idempotent methods.
        proxy_next_upstream error timeout http_502 http_503;
        proxy_next_upstream_tries 2;
        proxy_next_upstream_timeout 5s;
    }
}
```

**Bad Example** — no health limits, retries everything, defeats scaling

```nginx
upstream app_pool {
    ip_hash;                         # pins every client to one node -> uneven load
    server 10.0.0.11:8080;           # no max_fails: dead node still gets traffic
    server 10.0.0.12:8080;
}

server {
    location / {
        proxy_pass http://app_pool;
        # non_idempotent overrides nginx's default safety: a slow POST that already
        # reached one backend gets replayed on a second -> duplicate side effects.
        proxy_next_upstream error timeout http_502 non_idempotent;
        # No keepalive + HTTP/1.0 -> new TCP handshake per request under load.
    }
}
```

## Common Mistakes

- Leaving `max_fails`/`fail_timeout` unset, so nginx keeps routing to a crashed backend.
- Forgetting `proxy_http_version 1.1` and `Connection ""`, silently disabling `keepalive`.
- Using `ip_hash` for affinity, then wondering why load is lopsided behind a corporate NAT
  (many users share one IP and land on one node).
- Adding `non_idempotent` to `proxy_next_upstream`, overriding nginx's default and
  retrying POSTs on the next upstream, causing duplicate writes.
- Assuming open-source nginx does active health checks — it only reacts to failed real
  requests unless you add a module.
- Hard-removing a node instead of marking it `down` and draining, dropping live requests.

## Production Tips

- Emit the chosen backend in your access log via `$upstream_addr` and record
  `$upstream_response_time` and `$upstream_status`; you cannot debug balancing you cannot see.
- Alert on rising `$upstream_status` 5xx per backend to catch a degrading node before it
  fully fails.
- Keep at least one `backup` node so a partial outage degrades instead of collapsing.

## AI Review Checklist

- Is the balancing algorithm chosen deliberately and documented (round-robin vs
  `least_conn` vs hash)?
- Are `max_fails` and `fail_timeout` set so dead backends are removed from rotation?
- Is upstream `keepalive` paired with `proxy_http_version 1.1` and `Connection ""`?
- Is `proxy_next_upstream` restricted so non-idempotent requests are not retried?
- Is there a drain/`down` strategy for deploys instead of hard-killing nodes?
- Are per-backend `$upstream_*` metrics logged for observability?

## Related

- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/27-high-availability.md`
- `knowledge/nginx/17-monitoring.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/08-caching.md`
