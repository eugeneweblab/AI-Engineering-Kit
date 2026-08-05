---
id: nginx/05-reverse-proxy
topic: nginx
slug: reverse-proxy
title: "Reverse Proxy"
type: doc
order: 5
status: ready
tags: [nginx, reverse-proxy, X-Forwarded-For, proxy_pass, Connection, X-Forwarded-Proto, real_ip, Upgrade]
related: [nginx/06-load-balancing, nginx/04-location-blocks, nginx/20-websockets, nginx/19-proxying-applications, nginx/13-security]
when_to_use: "Read before putting nginx in front of an application server or debugging proxied requests."
---
# Reverse Proxy

## Purpose

This document defines how to proxy requests from nginx to an upstream application:
setting the right headers, choosing `proxy_pass` semantics, tuning timeouts and
buffering, and handling WebSockets. An agent that follows this delivers the client's
real identity and protocol to the backend without introducing header-spoofing holes.

## Why It Matters

A reverse proxy is the seam between the internet and your application, and the defaults
are wrong for almost every real backend. Forget `proxy_set_header Host` and the app
sees `localhost`; forget `X-Forwarded-Proto` and the app builds `http://` redirects
behind your HTTPS; trust an inbound `X-Forwarded-For` blindly and a client can spoof
its own IP past your rate limiter and audit log. These are silent failures — the app
runs, but identity, redirects, and security are quietly broken.

## Core Principles

- **Forward the client's real context, don't drop it.** The backend needs `Host`, the
  original scheme, and the real client IP. nginx does not pass these usefully by
  default; you must set them.
- **Never blindly trust inbound forwarding headers.** `X-Forwarded-*` from an untrusted
  client is attacker-controlled. Reset it at the trust boundary, or use `real_ip` with
  an explicit trusted-proxy list.
- **`proxy_pass` trailing slash changes URI rewriting.** With a trailing slash, the
  matched `location` prefix is stripped; without it, the full URI is passed. This is a
  frequent source of wrong upstream paths.
- **Buffering and timeouts are safety, not decoration.** Tune them to the backend's
  behavior so a slow client or slow upstream can't exhaust workers.

## Best Practices

- Set the core proxy headers on every proxied `location`, ideally via a shared
  `include proxy_params;`: `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.
- Configure `set_real_ip_from <trusted-cidr>;` and `real_ip_header X-Forwarded-For;`
  only for proxies you control, so nginx computes a trustworthy `$remote_addr`.
- For WebSockets, set `proxy_http_version 1.1` and forward `Upgrade`/`Connection`
  headers; otherwise the upgrade fails. See [WebSockets](20-websockets.md).
- Set explicit `proxy_connect_timeout`, `proxy_read_timeout`, and `proxy_send_timeout`
  to values matching the backend; the 60s defaults are often too long or too short.
- Use an `upstream` block (even for one server) so you can add
  [load balancing](06-load-balancing.md) and health handling without rewriting locations.
- Be deliberate about the `proxy_pass` trailing slash; test the resulting upstream path.
- Pass `proxy_ssl_*` and verify the upstream cert if proxying over TLS to the backend.

## Examples

**Good Example** — full client context, WebSocket-ready, tuned

```nginx
upstream app { server 127.0.0.1:3000; keepalive 32; }  # keepalive reuses upstream conns

map $http_upgrade $connection_upgrade {                 # correct Connection header per request
    default upgrade;
    ''      close;
}

server {
    set_real_ip_from 10.0.0.0/8;        # trust ONLY our internal load balancer...
    real_ip_header   X-Forwarded-For;   # ...then derive a trustworthy $remote_addr

    location / {
        proxy_pass http://app;                          # no trailing slash: full URI preserved
        proxy_http_version 1.1;                         # required for keepalive + WebSockets
        proxy_set_header Host              $host;        # backend sees the real hostname
        proxy_set_header X-Real-IP         $remote_addr; # real client IP, post real_ip
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;      # so backend builds https:// URLs
        proxy_set_header Upgrade           $http_upgrade;
        proxy_set_header Connection        $connection_upgrade;
        proxy_read_timeout 30s;                          # match backend's expected latency
    }
}
```

**Bad Example** — lost identity, spoofable, broken redirects

```nginx
server {
    location / {
        proxy_pass http://127.0.0.1:3000;
        # No Host header: backend sees "127.0.0.1", virtual-host routing and links break
        # No X-Forwarded-Proto: backend behind HTTPS emits http:// redirects (mixed content)
        proxy_set_header X-Forwarded-For $http_x_forwarded_for;
        # ^ blindly trusts inbound header: any client can forge its own IP past rate limits/logs
    }
}
```

## Common Mistakes

- Omitting `proxy_set_header Host`, so the backend sees `localhost`/upstream IP.
- Missing `X-Forwarded-Proto`, causing `http://` redirects and mixed-content errors.
- Trusting inbound `X-Forwarded-For` instead of resetting it or using `real_ip` with a
  trusted-proxy allowlist.
- Forgetting `proxy_http_version 1.1` + `Upgrade`/`Connection`, breaking WebSockets.
- Getting the `proxy_pass` trailing slash wrong, producing doubled or stripped paths.
- Leaving default timeouts, so a slow upstream ties up workers indefinitely.

## Production Tips

- Centralize proxy headers in `proxy_params` and `include` it, so every location stays
  consistent and a fix lands everywhere at once.
- Enable upstream `keepalive` with `proxy_http_version 1.1` and a cleared `Connection`
  header for non-WebSocket traffic to cut connection churn.
- Return a clean `502`/`504` page and consider `proxy_next_upstream` for retryable
  failures across a pool. See [high availability](27-high-availability.md).
- Log `$upstream_addr`, `$upstream_status`, and `$upstream_response_time` to diagnose
  backend issues. See [logging](16-logging.md).

## AI Review Checklist

- Are `Host`, `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Proto` all set?
- Is inbound `X-Forwarded-For` reset or scoped to a trusted-proxy list via `real_ip`?
- For WebSocket paths, are `proxy_http_version 1.1` and `Upgrade`/`Connection` set?
- Is the `proxy_pass` trailing slash chosen deliberately and the upstream path verified?
- Are connect/read/send timeouts set to match the backend, not left at defaults?
- Is the backend fronted by an `upstream` block for future scaling and failover?

## Related

- `knowledge/nginx/06-load-balancing.md`
- `knowledge/nginx/04-location-blocks.md`
- `knowledge/nginx/20-websockets.md`
- `knowledge/nginx/19-proxying-applications.md`
- `knowledge/nginx/13-security.md`
