---
id: nginx/24-debugging
topic: nginx
slug: debugging
title: "Nginx Debugging"
type: doc
order: 24
status: ready
tags: [nginx, debugging]
related: [nginx/16-logging, nginx/29-troubleshooting, nginx/05-reverse-proxy, nginx/17-monitoring, nginx/02-configuration]
when_to_use: "Read before diagnosing a misbehaving nginx config — 502s, wrong routing, unexpected rewrites, or requests that never reach the backend."
---
# Nginx Debugging

## Purpose

This document defines how to find out *why* nginx is doing something you did not
expect: a request lands on the wrong `location`, a `rewrite` loops, a proxied
backend returns 502, or a header vanishes. Debugging nginx is about observing the
request as nginx sees it — which server block matched, which location won, what
was sent upstream — not guessing from the browser side.

Debugging is distinct from [troubleshooting](29-troubleshooting.md) (fixing known
failure classes) and [monitoring](17-monitoring.md) (watching healthy traffic).
Here you have one broken request and need the exact reason.

## Why It Matters

nginx config is declarative and order-sensitive, so a wrong assumption about which
directive fired sends you editing the wrong block for hours. The matching rules
(`location` priority, `server_name` selection, `rewrite` phases) are precise but
non-obvious, and nginx will silently do exactly what you told it. A disciplined
debugging loop — reproduce, read the log, confirm the reload, isolate — turns a
vague "it's broken" into a single directive you can point at. Guessing does not.

## Core Principles

- **Validate before you reload.** Run `nginx -t` on every change. A config that
  fails the test keeps the *old* config live, so your edit had no effect at all.
- **Confirm the reload actually happened.** After `nginx -s reload`, check the
  error log for the reload line. Editing a file is not applying it.
- **Read the error log first, always.** `error_log` at `debug` level tells you which
  location matched, every rewrite step, and the exact upstream error.
- **Reproduce with `curl -v`, not a browser.** Browsers add caching, HTTP/2, and
  cookies that hide what nginx received. `curl` shows the raw request and response.
- **Isolate the layer.** A 502 is nginx reaching the backend and failing; a 404 from
  nginx is nginx not matching. Know which side of the proxy the error came from.

## Best Practices

- Build a debug-capable nginx (`--with-debug`, standard on most distro packages) and
  raise the level per-server: `error_log /var/log/nginx/debug.log debug;`. Scope it to
  one `server` or one client IP so you do not flood the disk.
- Add a request id and echo the matched location into the response while debugging:
  `add_header X-Debug-Location "api-v2" always;` — remove it before production.
- Log what you actually send upstream, not just what you received. A custom
  `log_format` with `$upstream_addr $upstream_status $upstream_response_time`
  reveals whether the backend was even reached.
- Use `curl -v --resolve host:443:127.0.0.1` to test a specific server block by name
  without touching DNS or `/etc/hosts`.
- When a `rewrite` misbehaves, add `rewrite_log on;` (needs `error_log ... notice;`)
  to log every rewrite and its result.
- Reproduce against `127.0.0.1` on the box itself to remove the CDN, firewall, and
  client network from the picture.

## Examples

**Good Example** — scoped debug logging that names the matched path

```nginx
# Debug only this server, only this client, so the log stays readable.
server {
    listen 443 ssl;
    server_name api.example.com;

    error_log /var/log/nginx/api-debug.log debug;  # verbose, scoped to one server
    rewrite_log on;                                 # log every rewrite step

    location /v2/ {
        add_header X-Debug-Location "v2" always;    # prove which location won
        proxy_pass http://backend_v2;
        # log the upstream result, not just the client-facing status
        access_log /var/log/nginx/api-upstream.log upstream_time;
    }
}

# curl -v https://api.example.com/v2/orders  → X-Debug-Location: v2 confirms match
```

**Bad Example** — guessing from the browser, never confirming the reload

```nginx
server {
    server_name api.example.com;

    # error_log left at default; no visibility into which location matched
    location /v2 {           # missing trailing slash → also matches /v2xyz
        proxy_pass http://backend_v2;
    }
}
# Edited the file, forgot `nginx -t` and reload → old config still live.
# "Tested" in a browser with a warm cache, so a 302 looked like a 200.
```

## Common Mistakes

- Editing config and testing without `nginx -t` + reload, so the change never applied.
- Debugging in a browser: cached responses, HTTP/2 multiplexing, and service workers
  mask what nginx actually returned.
- Reading `access_log` only and ignoring `error_log`, where the real reason lives.
- Assuming `location` matches top-to-bottom; prefix vs regex priority is not source
  order (see [location blocks](04-location-blocks.md)).
- Leaving `debug` logging or `X-Debug-*` headers enabled in production.
- Confusing an nginx-generated 404 with a backend 404 — check `$upstream_status`.

## Production Tips

- Keep a `map $arg_debug $loglevel` trick or a dedicated debug `server` on an internal
  port so you can capture verbose logs on demand without a global reload.
- Ship `error.log` to your log pipeline with structured fields; grep-on-the-box does
  not scale across a fleet.
- Reproduce production 502s by curling the upstream directly from the nginx host —
  it isolates nginx-to-backend network and TLS issues from client-side ones.

## AI Review Checklist

- Does every config change run `nginx -t` before reload, and is the reload confirmed?
- Is debug-level `error_log` scoped to a single server or client, not global?
- Are upstream fields (`$upstream_addr`, `$upstream_status`, `$upstream_response_time`)
  logged so backend failures are visible?
- Is reproduction done with `curl -v` against the origin, not a browser?
- Are `X-Debug-*` headers and `debug` log levels removed before shipping?
- Is the error attributed to the correct layer (nginx match vs upstream response)?

## Related

- `knowledge/nginx/16-logging.md`
- `knowledge/nginx/29-troubleshooting.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/17-monitoring.md`
- `knowledge/nginx/02-configuration.md`
