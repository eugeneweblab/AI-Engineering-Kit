---
id: nginx/03-server-blocks
topic: nginx
slug: server-blocks
title: "Server Blocks"
type: doc
order: 3
status: ready
tags: [nginx, server-blocks]
related: [nginx/04-location-blocks, nginx/02-configuration, nginx/12-ssl-tls, nginx/05-reverse-proxy, nginx/13-security]
when_to_use: "Read before defining a virtual host, adding a domain, or debugging which server block handled a request."
---
# Server Blocks

## Purpose

This document defines how nginx selects a `server` block (virtual host) to handle a
request: the roles of `listen` and `server_name`, how the default server is chosen,
and how to prevent a request from landing on the wrong host. An agent that gets this
right routes each hostname to exactly the intended config.

## Why It Matters

The `server` block is the first routing decision nginx makes, and it is easy to get
wrong in ways that are invisible until they bite. A missing default server means an
unmatched `Host` header falls through to whichever block loaded first — often exposing
an internal site or a stale TLS certificate. A too-broad `server_name` can hijack
traffic meant for another host. Because selection happens before any `location`
matching, a mistake here misroutes the entire request.

## Core Principles

- **Selection is by `listen` first, then `server_name`.** nginx narrows to blocks
  listening on the request's IP:port, then matches the `Host` header against
  `server_name` (exact > leading wildcard > trailing wildcard > regex).
- **There is always a default server.** If nothing matches `server_name`, nginx uses
  the block marked `default_server` (or the first one for that port). Define it
  explicitly so unmatched hosts hit a controlled response, not a random site.
- **`server_name` is matched, not trusted.** The `Host` header is client-controlled;
  validate it, and return `444`/`421` for unexpected hosts rather than serving them.
- **TLS is per server block via SNI.** Each HTTPS host needs its `ssl_certificate`
  in its own block; the wrong default server serves the wrong certificate.

## Best Practices

- Give every listening port an explicit `default_server` that returns `444` (close
  connection) for unknown hosts, so probes and misconfigured DNS get nothing useful.
- Use exact `server_name` values for known hosts; reserve wildcards (`*.example.com`)
  for genuine multi-tenant needs. Narrow names are safer and faster.
- Redirect HTTP to HTTPS in a dedicated port-80 block; do not serve real content on 80.
- Keep one `server` block per file (see [configuration](02-configuration.md)) so each
  host is independently reviewable.
- For HTTPS, terminate TLS in the block and set modern protocols/ciphers — see
  [SSL/TLS](12-ssl-tls.md). Add security headers here or in a shared include.
- Set `server_name` before you rely on `$host`/`$server_name` in downstream config.

## Examples

**Good Example** — explicit default, exact host, HTTP->HTTPS redirect

```nginx
# Catch-all default: unmatched Host headers get nothing, not a random vhost
server {
    listen 443 ssl default_server;
    ssl_certificate     /etc/nginx/ssl/default.crt;   # a valid cert so TLS handshake completes
    ssl_certificate_key /etc/nginx/ssl/default.key;
    return 444;                                        # close connection, serve no content
}

# Redirect all plaintext to HTTPS in a dedicated port-80 block
server {
    listen 80;
    server_name app.example.com;
    return 301 https://$host$request_uri;              # preserve host + path on redirect
}

# The real host, exact server_name, its own certificate
server {
    listen 443 ssl;
    server_name app.example.com;                       # exact match, highest priority
    ssl_certificate     /etc/nginx/ssl/app.crt;
    ssl_certificate_key /etc/nginx/ssl/app.key;
    root /var/www/app;
}
```

**Bad Example** — no default, over-broad name, mixed concerns

```nginx
server {
    listen 80;
    listen 443 ssl;                 # serving content on 80 AND 443 — no forced HTTPS
    server_name _;                  # matches everything; silently becomes the fallback host
    ssl_certificate     /etc/nginx/ssl/app.crt;   # wrong cert served to any unknown host
    ssl_certificate_key /etc/nginx/ssl/app.key;
    root /var/www/app;              # unknown Host headers get real app content
}
```

## Common Mistakes

- No explicit `default_server`, so unmatched hosts hit whichever block loaded first.
- Serving content on port 80 instead of redirecting to HTTPS.
- Over-broad `server_name _` or wildcards that swallow traffic meant for other hosts.
- Assuming the `Host` header is trustworthy and using it without validation.
- Putting the wrong certificate in the default server, so probes see a mismatched cert.
- Multiple blocks claiming the same `server_name` on the same port (nginx warns, then
  uses the first — usually not what you meant).

## Production Tips

- Test host routing with `curl -H 'Host: unknown' https://server` and confirm you get
  the `444`/controlled response, not real content.
- Use `nginx -T` to see the fully-resolved set of server blocks and their names.
- Keep certificate paths and security headers in shared includes to avoid drift.
- Log `$host` and `$server_name` during setup to verify which block matched.

## AI Review Checklist

- Does every listening port have an explicit `default_server`?
- Does the default server return a controlled response (e.g. `444`) for unknown hosts?
- Are `server_name` values as narrow as the use case allows?
- Is HTTP (port 80) redirected to HTTPS, not serving content directly?
- Does each HTTPS host have its own correct `ssl_certificate`?
- Is the client-supplied `Host` header validated rather than trusted?

## Related

- `knowledge/nginx/04-location-blocks.md`
- `knowledge/nginx/02-configuration.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/13-security.md`
