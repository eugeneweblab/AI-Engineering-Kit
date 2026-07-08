---
id: nginx/19-proxying-applications
topic: nginx
slug: proxying-applications
title: "Proxying Applications"
type: doc
order: 19
status: ready
tags: [nginx, proxying-applications]
related: [nginx/05-reverse-proxy, nginx/06-load-balancing, nginx/20-websockets, nginx/18-performance, nginx/13-security]
when_to_use: "Read before putting nginx in front of a Node, Python, Go, or Ruby application server."
---
# Proxying Applications

## Purpose

This document defines how to proxy a dynamic application server — Node, Gunicorn,
Puma, a Go binary — behind nginx over HTTP. It covers the headers the backend needs,
the timeouts and buffering that keep it stable, and the failure handling that keeps a
slow backend from taking nginx down with it.

The base mechanics of `proxy_pass` live in [reverse proxy](05-reverse-proxy.md); this
document is about proxying an *application* correctly: preserving client identity,
setting sane timeouts, and choosing where a request goes when the backend misbehaves.

## Why It Matters

The application behind nginx makes security and business decisions — rate limits, IP
allowlists, HTTPS redirects, audit logs — based on what nginx tells it about the client.
If nginx forwards the wrong host, scheme, or client IP, the app logs nginx's own address,
builds broken redirect URLs, and mis-applies access rules. These bugs are subtle: the
app works, it is just wrong about who is calling it. And a missing timeout means one hung
backend request pins an nginx worker connection until it, too, runs out.

## Core Principles

- **The backend must learn the real client.** Always forward `Host`, the client IP via
  `X-Forwarded-For`, and the original scheme via `X-Forwarded-Proto`. The app cannot
  recover this later.
- **Every upstream call needs a timeout.** `proxy_connect_timeout`, `proxy_send_timeout`,
  and `proxy_read_timeout` bound how long nginx waits. Without them a stuck backend ties
  up connections indefinitely.
- **Bind to a socket, not the world.** The app server should listen on `127.0.0.1` or a
  Unix socket so only nginx can reach it. A directly reachable app bypasses nginx entirely.
- **Fail predictably.** Decide up front what happens on backend error: retry another
  upstream, serve stale cache, or return 502 cleanly — never hang.
- **Do not double up.** Let the app do app logic and nginx do edge logic (TLS, gzip,
  static files, rate limiting). Compressing or serving statics from the app wastes it.

## Best Practices

- Set the standard proxy headers once in a shared snippet and `include` it:
  `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.
- Set explicit timeouts (`proxy_connect_timeout 5s;`, `proxy_read_timeout 60s;`) matched
  to the app's real behavior, not the defaults.
- Prefer a Unix socket (`proxy_pass http://unix:/run/app.sock;`) for a co-located backend —
  it avoids the TCP stack and cannot be reached from the network.
- Use upstream keepalive (see [performance](18-performance.md)) so nginx reuses backend
  connections instead of reconnecting per request.
- Configure `proxy_next_upstream` deliberately. Retrying is safe for idempotent GETs;
  retrying a POST can double-charge a customer — exclude non-idempotent methods.
- Serve static assets from nginx directly (see [static files](07-static-files.md)); never
  proxy `/static` or `/assets` to the app.
- Return the client IP the app expects: if nginx is behind another proxy/CDN, set
  `set_real_ip_from` and `real_ip_header` so `$remote_addr` is the true client.

## Examples

**Good Example** — full client context, bounded waits, safe retries

```nginx
upstream app {
    server unix:/run/app.sock;   # local-only socket, unreachable from the network
    keepalive 32;                # reuse backend connections
}

server {
    listen 443 ssl;
    server_name app.example.com;

    location / {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_set_header Host              $host;               # app builds correct URLs
        proxy_set_header X-Real-IP         $remote_addr;        # true client IP
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;             # app knows it's HTTPS

        proxy_connect_timeout 5s;    # give up fast if the backend won't accept
        proxy_read_timeout   60s;    # bound a slow response, don't hang forever

        proxy_next_upstream error timeout;  # retry on connect/timeout only — never on a POST result
    }
}
```

**Bad Example** — anonymous client, unbounded wait, unsafe retry

```nginx
server {
    location / {
        proxy_pass http://127.0.0.1:3000;
        # no Host header → app sees "127.0.0.1", builds broken redirects
        # no X-Forwarded-* → app logs nginx's IP, mis-applies rate limits and HTTPS checks
        # no timeouts → one hung backend request pins an nginx connection indefinitely

        proxy_next_upstream error timeout http_500;  # retries POSTs on 500 → duplicate side effects
    }
}
```

## Common Mistakes

- Not forwarding `Host` / `X-Forwarded-Proto`, so the app builds `http://` redirects on
  an HTTPS site or serves the wrong virtual host.
- Trusting `X-Forwarded-For` from the client without `real_ip` config, letting anyone
  spoof their IP past app-level allowlists.
- Leaving default timeouts (or none), so a stuck backend exhausts nginx worker connections.
- Enabling `proxy_next_upstream` for `http_500`/non-idempotent methods, silently
  retrying POSTs and causing duplicate writes.
- Exposing the app server's port to the network in parallel with nginx, bypassing all
  edge protections.
- Proxying static assets through the app instead of serving them from nginx.

## Production Tips

- Log `$upstream_addr`, `$upstream_status`, and `$upstream_response_time` so you can tell
  a nginx problem from a backend problem in one line.
- Add an active health check or use `max_fails`/`fail_timeout` so nginx stops sending
  traffic to a dead backend instead of timing out every request.
- Keep a `proxy_intercept_errors` + custom error page for 502/504 so users see a branded
  page, not nginx's default, during a backend outage.
- Match nginx `proxy_read_timeout` to the app's own request timeout; if nginx gives up
  first, the app keeps working on a request nobody will read.

## AI Review Checklist

- Are `Host`, `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Proto` all forwarded?
- Are `proxy_connect_timeout` and `proxy_read_timeout` set to concrete values?
- Is the backend bound to localhost or a Unix socket, unreachable from the network?
- Does `proxy_next_upstream` exclude non-idempotent methods and 5xx retries?
- If nginx is behind a CDN/proxy, are `set_real_ip_from` and `real_ip_header` configured?
- Are static assets served by nginx rather than proxied to the app?
- Is upstream keepalive enabled with `proxy_http_version 1.1`?

## Related

- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/06-load-balancing.md`
- `knowledge/nginx/20-websockets.md`
- `knowledge/nginx/18-performance.md`
- `knowledge/nginx/13-security.md`
