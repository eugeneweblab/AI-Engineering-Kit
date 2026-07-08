---
id: nginx/12-ssl-tls
topic: nginx
slug: ssl-tls
title: "SSL TLS"
type: doc
order: 12
status: ready
tags: [nginx, ssl-tls]
related: [nginx/13-security, nginx/10-http2, nginx/05-reverse-proxy, nginx/25-production]
when_to_use: "Read before terminating HTTPS in nginx or reviewing any `ssl_*` / listen 443 configuration."
---
# SSL TLS

## Purpose

This document defines how to terminate TLS correctly in nginx: which protocols and
ciphers to allow, how to load certificates and keys, and how to make HTTPS the only
way in. It is written so an agent can write or review a `server` block that serves
443 without weakening transport security.

TLS is what makes a request *private* and *authentic* on the wire. nginx is almost
always the process that owns the certificate and the handshake, so its `ssl_*`
directives are the security boundary for the entire site behind it.

## Why It Matters

A single wrong directive here silently downgrades every connection. Leaving TLS 1.0
enabled, allowing an RSA-only cipher without forward secrecy, or omitting HSTS does
not throw an error — nginx starts happily and the site loads. The weakness is
invisible until a downgrade or interception attack exploits it, and by then every
user who ever connected is affected. TLS config is also slow to fix in the field:
certificates expire on a clock, and a lapsed cert takes the whole site down. Treat
this file as a security control, not a checkbox.

## Core Principles

- **TLS 1.2 is the floor, TLS 1.3 is the default.** Disable SSLv3, TLS 1.0, and
  TLS 1.1 — they have known, exploitable weaknesses and no modern client needs them.
- **Forward secrecy is mandatory.** Prefer ECDHE key exchange so a stolen private
  key cannot decrypt past captured traffic.
- **Redirect, do not also serve, plain HTTP.** Port 80 exists only to send a 301 to
  HTTPS; never serve real content on it.
- **HSTS after you are sure.** Once HTTPS is stable, tell browsers to refuse HTTP —
  but only when every subdomain is HTTPS-ready, because HSTS is hard to undo.
- **The private key is a secret.** It is `root`-owned, `chmod 600`, never in the
  repo, never in an image layer, never logged.

## Best Practices

- Set `ssl_protocols TLSv1.2 TLSv1.3;`. Do not list anything older.
- Let TLS 1.3 pick its own suites; for 1.2, use a curated ECDHE list and set
  `ssl_prefer_server_ciphers off` (modern guidance — clients pick best mutual suite).
- Serve the **full chain** (`fullchain.pem`), not just the leaf, or intermediate
  clients fail to validate.
- Enable **OCSP stapling** (`ssl_stapling on;` + a resolver) so clients do not make
  a separate revocation round-trip.
- Reuse sessions with `ssl_session_cache shared:SSL:10m;` and `ssl_session_timeout`;
  keep `ssl_session_tickets off` unless you rotate ticket keys, since static tickets
  break forward secrecy.
- Automate renewal (certbot / ACME) and reload nginx on renew; a cert expiring at
  3 a.m. is an outage, not an alert.
- Add HSTS with `includeSubDomains` and a long `max-age` only after validating every
  subdomain over HTTPS.

## Examples

**Good Example** — modern TLS, HTTP redirects up, key is protected

```nginx
# Port 80 exists only to push clients to HTTPS — no real content served here.
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;   # permanent redirect, preserves path
}

server {
    listen 443 ssl;
    http2 on;                                # multiplex over the same TLS
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;  # full chain
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;    # 0600, root

    ssl_protocols TLSv1.2 TLSv1.3;           # no TLS 1.0/1.1 — known weaknesses
    ssl_prefer_server_ciphers off;           # let modern clients choose best suite
    ssl_session_cache shared:SSL:10m;        # resume handshakes, save CPU
    ssl_stapling on;                         # staple OCSP so clients skip a round-trip
    ssl_stapling_verify on;
    resolver 1.1.1.1 valid=300s;

    # Sent only over HTTPS; tells browsers to refuse plain HTTP for 2 years.
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
}
```

**Bad Example** — obsolete protocols, leaf-only cert, no redirect

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate     /etc/nginx/cert.pem;     # leaf only → intermediate clients fail
    ssl_certificate_key /etc/nginx/key.pem;      # world-readable in most bad setups

    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;   # SSLv3/1.0/1.1 are exploitable
    ssl_ciphers ALL;                             # includes RC4/3DES/no-forward-secrecy
    # No port-80 redirect: the site is happily reachable over plain HTTP too.
    # No HSTS: a downgrade attack can strip HTTPS entirely.
}
```

## Common Mistakes

- Leaving TLS 1.0/1.1 or SSLv3 enabled "for old clients" — they enable downgrade attacks.
- Using `ssl_ciphers ALL` or `HIGH:!aNULL`, which still permits non-forward-secret suites.
- Serving the leaf certificate without its intermediate chain, breaking strict clients.
- Serving real content on port 80 instead of a 301 redirect to HTTPS.
- Committing the private key to git or baking it into a Docker image layer.
- Enabling HSTS with `preload` before every subdomain supports HTTPS, locking users out.
- No automated renewal, so the certificate expires and the site goes dark.

## Production Tips

- Monitor certificate expiry as a metric and alert at 14 days remaining, not on the day.
- After any change, verify externally with an SSL scanner (e.g. Qualys SSL Labs) and
  test with `openssl s_client -connect host:443 -tls1_2` to confirm downgrades fail.
- Keep `ssl_dhparam` at 2048-bit or higher if any non-ECDHE suite is retained.
- Reload, do not restart, nginx on renewal so in-flight connections are not dropped.

## AI Review Checklist

- Is `ssl_protocols` limited to `TLSv1.2 TLSv1.3` (no older protocols)?
- Does every cipher path provide forward secrecy (ECDHE), with no RC4/3DES/NULL?
- Is `ssl_certificate` the full chain, and the key file `root`-owned and `0600`?
- Does port 80 return a 301 to HTTPS rather than serving content?
- Is HSTS present and scoped correctly, added only after HTTPS is proven everywhere?
- Is renewal automated with a reload hook, and is expiry monitored?
- Is OCSP stapling enabled with a working resolver?

## Related

- `knowledge/nginx/13-security.md`
- `knowledge/nginx/10-http2.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/25-production.md`
