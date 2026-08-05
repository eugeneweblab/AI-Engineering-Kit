---
id: nginx/13-security
topic: nginx
slug: security
title: "Nginx Security"
type: doc
order: 13
status: ready
tags: [nginx, security, client_max_body_size, X-Real-IP, X-Forwarded-For, location, set_real_ip_from, always]
related: [nginx/12-ssl-tls, nginx/14-rate-limiting, nginx/15-authentication, nginx/05-reverse-proxy, nginx/16-logging]
when_to_use: "Read before exposing any nginx server to the internet or reviewing its hardening and header configuration."
---
# Nginx Security

## Purpose

This document defines how to harden an internet-facing nginx: response headers,
information disclosure, request-size and method limits, safe proxy defaults, and
locking down what the server will do at all. It is written so an agent can review a
config for the ways an attacker probes a web tier before touching the application.

nginx is the first process to see every request. Most of what protects the app —
header stripping, size caps, method allow-lists, TLS — lives here, not in the app.
This doc covers the perimeter controls; TLS lives in
[ssl-tls](12-ssl-tls.md), throttling in [rate-limiting](14-rate-limiting.md).

## Why It Matters

The web tier is scanned continuously by automated tools looking for version banners,
open methods, oversized-body DoS, and header misconfigurations. Each is cheap to close
in nginx and expensive to suffer. A leaked `Server: nginx/1.25.3` tells an attacker
exactly which CVEs to try; a missing body-size limit lets one client exhaust memory;
a reflected `X-Forwarded-*` header lets a client spoof its own source IP past your
rate limiter and access rules. None of these throw errors — the server runs fine while
being trivially exploitable. Hardening is one-time work with permanent payoff.

## Core Principles

- **Reveal nothing.** Hide the version banner, error-page internals, and backend
  identity. Reconnaissance is the first step of every attack.
- **Deny by default, allow explicitly.** Return 404/403 for paths, methods, and file
  types you do not intend to serve rather than relying on the app to reject them.
- **Bound every input.** Cap body size, header size, and connection counts so a
  single client cannot exhaust the server.
- **Never trust client-supplied trust signals.** `X-Forwarded-For`, `X-Real-IP`, and
  Host from an untrusted client are attacker input until you set them yourself.
- **Send security headers from the edge.** CSP, `X-Content-Type-Options`, and frame
  controls belong where every response passes: nginx.

## Best Practices

- Set `server_tokens off;` to drop the version from banners and error pages.
- Cap request bodies with `client_max_body_size` and headers with
  `large_client_header_buffers`; size to the real need, not "unlimited".
- Restrict methods: return `405` for anything outside `GET/POST/HEAD` (or your API's set).
- Add `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` (or a CSP
  `frame-ancestors`), `Referrer-Policy`, and a real `Content-Security-Policy`.
- Block access to hidden and sensitive files (`\.git`, `\.env`, `.htaccess`) with a
  `location` that returns 404.
- When proxying, **reset** `X-Forwarded-For`/`X-Real-IP` from `$remote_addr` and only
  trust `X-Forwarded-*` from a `set_real_ip_from` allow-list of known proxies.
- Run the nginx worker as an unprivileged user and keep nginx patched — perimeter
  software is the highest-value CVE target.

## Examples

**Good Example** — quiet banner, bounded input, trustworthy forwarded headers

```nginx
server {
    server_tokens off;                       # no version banner for scanners

    client_max_body_size 10m;                # bound uploads; refuse oversized bodies (413)
    limit_except GET POST HEAD { deny all; } # everything else → 405, not the app's problem

    add_header X-Content-Type-Options nosniff always;   # stop MIME sniffing
    add_header X-Frame-Options DENY always;             # no clickjacking via <iframe>
    add_header Content-Security-Policy "default-src 'self'" always;

    location ~ /\.(git|env|ht) { return 404; }          # never serve dotfiles/secrets

    location /api/ {
        # Trust forwarded headers ONLY from our known load balancer.
        set_real_ip_from 10.0.0.0/8;
        real_ip_header X-Forwarded-For;
        # Set the header ourselves from the real peer — do not pass the client's copy.
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://app;
    }
}
```

**Bad Example** — leaks version, unbounded, trusts client headers

```nginx
server {
    # server_tokens defaults on → "Server: nginx/1.25.3" handed to every scanner.
    # No client_max_body_size → a single large POST can exhaust worker memory.

    location /api/ {
        # Blindly forwards whatever the client sent, so a client can spoof its
        # source IP and bypass IP-based rate limits and allow-lists downstream.
        proxy_set_header X-Forwarded-For $http_x_forwarded_for;
        proxy_pass http://app;
    }

    location ~ /\.git { }   # empty block → .git directory is served to the world
}
```

## Common Mistakes

- Leaving `server_tokens on`, publishing the exact version to every scanner.
- No `client_max_body_size`, allowing memory-exhaustion via huge request bodies.
- Passing the client's `X-Forwarded-For` straight through, letting IP controls be spoofed.
- Serving `.git`, `.env`, or backup files because no `location` blocks them.
- Setting security headers without `always`, so they vanish on error responses.
- Adding a header in a nested `location` — nginx `add_header` does not inherit if a
  child block defines its own, silently dropping the parent's headers.
- Relying on the application to reject bad methods instead of stopping them at the edge.

## Production Tips

- Verify headers from outside with `curl -sI https://host` and a scanner
  (e.g. Mozilla Observatory) after every change.
- Keep security headers in one included snippet so they cannot drift between servers.
- Log and alert on 4xx spikes — they are the signature of scanning and probing.
- Pin the nginx version and subscribe to its security advisories; patch promptly.

## AI Review Checklist

- Is `server_tokens off` set so no version banner leaks?
- Is `client_max_body_size` (and header buffer size) bounded to the real need?
- Are HTTP methods restricted to the intended set at the nginx layer?
- Are `X-Content-Type-Options`, frame/CSP, and `Referrer-Policy` sent with `always`?
- Are dotfiles and secret paths (`.git`, `.env`) explicitly returned as 404?
- Are `X-Forwarded-*` / `X-Real-IP` set from `$remote_addr` and trusted only from a
  `set_real_ip_from` allow-list?
- Does the worker run unprivileged, on a patched nginx build?

## Related

- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/14-rate-limiting.md`
- `knowledge/nginx/15-authentication.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/16-logging.md`
