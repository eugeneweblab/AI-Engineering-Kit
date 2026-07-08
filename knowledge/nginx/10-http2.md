---
id: nginx/10-http2
topic: nginx
slug: http2
title: "HTTP/2"
type: doc
order: 10
status: ready
tags: [nginx, http2]
related: [nginx/11-http3, nginx/12-ssl-tls, nginx/09-compression, nginx/03-server-blocks, nginx/18-performance]
when_to_use: "Read before enabling HTTP/2 on a TLS listener or debugging protocol negotiation."
---
# HTTP/2

## Purpose

This document defines how to enable and configure HTTP/2 in nginx correctly: the current
`http2` directive syntax, the TLS prerequisite, why old "optimizations" like domain
sharding and asset concatenation are now harmful, and the connection-coalescing gotchas.
HTTP/2 multiplexes many requests over one connection, eliminating head-of-line blocking at
the HTTP layer.

HTTP/2 answers "how do I get many requests down one connection efficiently?". The failures
are enabling it with deprecated syntax, forgetting it effectively requires TLS, and
carrying over HTTP/1.1-era hacks that now hurt.

## Why It Matters

HTTP/2 is the baseline modern browsers expect, and getting it wrong wastes its main
benefit. Under HTTP/1.1, browsers opened 6 connections per host and developers sharded
assets and concatenated bundles to work around per-connection limits. Under HTTP/2 those
same tricks *reduce* performance: multiplexing makes many small requests cheap, sharding
splits the multiplexed connection, and giant bundles defeat fine-grained caching. Because
nginx will happily serve HTTP/1.1 if negotiation fails, a misconfigured listener silently
gives you none of HTTP/2's benefit while everything appears to work.

## Core Principles

- **Use the current `http2` directive.** Modern nginx (1.25.1+) uses a standalone
  `http2 on;` directive inside the `server` block; the old `listen ... http2` parameter is
  deprecated. Do not copy pre-1.25 snippets.
- **HTTP/2 requires TLS in practice.** No mainstream browser speaks cleartext HTTP/2
  (h2c). Enable it on a `listen 443 ssl` server with a valid certificate — see
  [SSL/TLS](12-ssl-tls.md).
- **Drop HTTP/1.1-era workarounds.** Domain sharding, image sprites, and mega-bundles hurt
  under multiplexing. Serve many small, individually cacheable resources from one origin.
- **Multiplexing is not prioritization magic.** Many streams share one TCP connection, so
  a single lost packet still stalls all streams (TCP head-of-line blocking) — that is what
  [HTTP/3](11-http3.md) fixes, not HTTP/2.
- **Negotiation is silent.** ALPN picks the protocol; if the client or an upstream proxy
  does not offer h2, you fall back to HTTP/1.1 with no error. Verify the negotiated protocol.

## Best Practices

- Enable with `http2 on;` on a TLS `server`; keep the plain `listen 80` block for a
  redirect to HTTPS only.
- Terminate HTTP/2 at nginx and proxy to the backend over HTTP/1.1 — nginx does not speak
  HTTP/2 to upstreams, and that is fine; the client-facing hop is what matters.
- Stop concatenating and sharding: ship granular assets so a one-line change invalidates
  one small file, not a 500 KB bundle.
- Keep `keepalive_timeout` reasonable; HTTP/2 clients hold one long-lived connection, so
  overly aggressive timeouts cause needless reconnects.
- Server Push is removed from nginx and deprecated across browsers — do not use it; use
  `103 Early Hints` or `<link rel=preload>` instead.
- Pair HTTP/2 with a modern TLS config (TLS 1.2+ with the HTTP/2 cipher blocklist avoided);
  a weak cipher can force a downgrade to HTTP/1.1.

## Examples

**Good Example** — current directive syntax, TLS, HTTPS redirect

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;    # plain HTTP only redirects
}

server {
    listen 443 ssl;
    http2 on;                                # current syntax (nginx >= 1.25.1)
    server_name example.com;

    ssl_certificate     /etc/ssl/example.com/fullchain.pem;
    ssl_certificate_key /etc/ssl/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://app_pool;          # nginx speaks HTTP/1.1 to the backend — expected
        proxy_set_header Host $host;
    }
}
```

**Bad Example** — deprecated syntax, HTTP/1.1 hacks carried over

```nginx
server {
    listen 443 ssl http2;                    # deprecated listen parameter (pre-1.25 style)
    server_name example.com;
    # Assets sharded across cdn1/cdn2/cdn3 subdomains -> splits the multiplexed
    # connection and re-adds the TCP/TLS setup cost HTTP/2 was meant to remove.
    # http2_push used here -> removed from nginx, ignored or errors on reload.
}
```

## Common Mistakes

- Using the deprecated `listen ... http2` parameter on nginx 1.25.1+ instead of `http2 on;`.
- Enabling HTTP/2 on a non-TLS listener and expecting browsers to use it (they will not).
- Keeping domain sharding, sprites, or mega-bundles that actively hurt under multiplexing.
- Configuring HTTP/2 Server Push, which is removed and unsupported.
- Assuming HTTP/2 eliminates head-of-line blocking entirely — TCP-level blocking remains.
- Not verifying the negotiated protocol, so a silent fallback to HTTP/1.1 goes unnoticed.

## Production Tips

- Verify with `curl -I --http2 https://example.com` (look for `HTTP/2`) or the browser
  network panel's Protocol column — do not assume the listener is being used.
- Enable [HTTP/3](11-http3.md) alongside HTTP/2 and advertise it via `Alt-Svc`; clients
  upgrade opportunistically and fall back to HTTP/2 cleanly.
- Watch for middleboxes/load balancers in front of nginx that terminate at HTTP/1.1 and
  erase the benefit before traffic reaches you.

## AI Review Checklist

- Is HTTP/2 enabled with the current `http2 on;` directive, not the deprecated `listen`
  parameter?
- Is it on a TLS listener with a valid certificate?
- Have HTTP/1.1-era hacks (sharding, concatenation, sprites) been removed?
- Is Server Push absent (removed feature)?
- Is the negotiated protocol verified end to end, including any upstream proxy?
- Is TLS 1.2+ configured so no cipher forces an HTTP/2 downgrade?

## Related

- `knowledge/nginx/11-http3.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/09-compression.md`
- `knowledge/nginx/03-server-blocks.md`
- `knowledge/nginx/18-performance.md`
