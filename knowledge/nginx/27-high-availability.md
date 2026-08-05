---
id: nginx/27-high-availability
topic: nginx
slug: high-availability
title: "Nginx High Availability"
type: doc
order: 27
status: ready
tags: [nginx, high-availability, max_fails, proxy_next_upstream_tries, fail_timeout, upstream, proxy_next_upstream, backup]
related: [nginx/06-load-balancing, nginx/25-production, nginx/05-reverse-proxy, nginx/17-monitoring, nginx/08-caching]
when_to_use: "Read before designing an nginx tier that must survive a node failure, or when reviewing whether a single nginx instance is a hidden single point of failure."
---
# Nginx High Availability

## Purpose

This document defines how to run nginx so that no single failure — a dead backend, a
crashed nginx node, a failed reload — takes the service down. It covers upstream
health checking and failover, running redundant nginx instances behind a floating IP
or DNS, graceful reloads, and connection draining. The goal is that any one component
can die and traffic keeps flowing.

High availability builds on [load balancing](06-load-balancing.md) (distributing
traffic) and [production](25-production.md) (a hardened single node); here the focus
is surviving failure, not just handling load.

## Why It Matters

nginx is often the single point every request passes through, which makes it the most
dangerous place to have no redundancy: if that one process or box dies, the whole
service is down regardless of how many healthy backends exist. Just as damaging is a
correctly-redundant backend tier fronted by nginx that keeps routing to a dead peer
because failover was never configured. HA is the difference between a failure being a
non-event and a failure being an outage — and it must be designed in, because it
cannot be added during the incident.

## Core Principles

- **Eliminate every single point of failure.** Two nginx nodes minimum, multiple
  upstream peers, and no shared component that can take both down at once.
- **Detect failure and route around it automatically.** `max_fails`/`fail_timeout`
  and `proxy_next_upstream` must eject a dead backend without human action.
- **Reloads must be graceful.** `nginx -s reload` drains old workers so config changes
  and cert rotations never drop connections.
- **Fail over the nginx tier itself.** A floating VIP (keepalived/VRRP) or DNS/anycast
  must move traffic off a dead nginx node within seconds.
- **Health checks must test the real path.** Checking that a port is open is not the
  same as checking that the app can serve a request.

## Best Practices

- Run at least two nginx instances and put a VIP in front with keepalived (VRRP), or
  use DNS/anycast/a cloud L4 load balancer. One nginx box is a single point of failure
  no matter how well it is tuned.
- Give every `upstream` multiple `server` entries with `max_fails` and `fail_timeout`
  so passive health checks eject a peer that starts erroring.
- Set `proxy_next_upstream error timeout http_502 http_503;` so a failed request
  retries a healthy peer — but bound it with `proxy_next_upstream_tries` to avoid
  hammering the whole pool on a systemic failure.
- Use active health checks (`health_check` in nginx Plus, or a sidecar/`ngx_http_upstream_check`
  on OSS) to eject a backend *before* a user hits it, not after.
- Add a `backup` server to the upstream so there is a last-resort peer when the primary
  pool is exhausted.
- Drain before deploy: mark a backend `down` in the config and reload, let in-flight
  requests finish, then take it out of rotation.
- Keep nginx nodes stateless — no local session store; put shared state (cache, sessions)
  in a replicated tier so either node can serve any request.

## Examples

**Good Example** — redundant peers, health-based failover, bounded retries

```nginx
upstream app {
    zone app 64k;                          # shared memory so all workers see peer state
    server 10.0.0.11:8080 max_fails=3 fail_timeout=15s;
    server 10.0.0.12:8080 max_fails=3 fail_timeout=15s;
    server 10.0.0.13:8080 backup;          # last-resort peer if the pool is exhausted
    keepalive 64;
}

server {
    location / {
        proxy_pass http://app;
        proxy_next_upstream error timeout http_502 http_503;  # retry a healthy peer
        proxy_next_upstream_tries 2;        # bounded: don't storm the whole pool
        proxy_connect_timeout 2s;           # detect a dead peer fast
    }

    location = /healthz {
        access_log off;
        return 200 "ok\n";                  # cheap endpoint for the VIP's health probe
    }
}
# Fronted by keepalived: a VIP floats between two nginx nodes on VRRP failover.
```

**Bad Example** — single backend, no failover, single nginx node

```nginx
upstream app {
    server 10.0.0.11:8080;   # one peer: its death is a full outage
    # no max_fails/fail_timeout → nginx keeps sending traffic to a dead backend
}

server {
    location / {
        proxy_pass http://app;
        # no proxy_next_upstream → a 502 from the (only) peer reaches the user
    }
}
# Runs on a single nginx box with no VIP → that box is a single point of failure.
```

## Common Mistakes

- Treating "load balanced" as "highly available" — one nginx node balancing across
  backends is still a single point of failure.
- A single `upstream server`, or multiple with no `max_fails`, so a dead peer keeps
  receiving traffic.
- No `proxy_next_upstream`, so a transient backend error reaches the user instead of
  retrying a healthy peer.
- Unbounded retries (`proxy_next_upstream_tries` unset) turning one bad request into a
  storm across every backend during an incident.
- Storing session or cache state locally on nginx nodes, so failover loses user state.
- Reload/deploy that does not drain, dropping in-flight requests on every change.

## Production Tips

- Test failover regularly: kill a backend and an nginx node in a game day and confirm
  traffic recovers within your SLA — untested failover usually does not work.
- Alert on `upstream` peer state and 5xx rate (see [monitoring](17-monitoring.md)); a
  silently-ejected backend is a capacity loss you must know about.
- Keep the two nginx configs byte-identical (same version control, same deploy) so a
  VIP failover does not change behavior mid-incident.
- Put a short TTL on any DNS-based failover so clients actually move when a node dies.

## AI Review Checklist

- Is there more than one nginx instance, with a VIP/DNS/L4 LB in front?
- Does every critical `upstream` have multiple peers with `max_fails`/`fail_timeout`?
- Is `proxy_next_upstream` set and bounded with `proxy_next_upstream_tries`?
- Are active or passive health checks ejecting dead backends automatically?
- Are nginx nodes stateless, with shared state in a replicated tier?
- Do reloads and deploys drain connections instead of dropping them?
- Has failover been tested by actually killing a node?

## Related

- `knowledge/nginx/06-load-balancing.md`
- `knowledge/nginx/25-production.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/17-monitoring.md`
- `knowledge/nginx/08-caching.md`
