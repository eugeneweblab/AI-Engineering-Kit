---
id: nginx/11-http3
topic: nginx
slug: http3
title: "HTTP/3"
type: doc
order: 11
status: ready
tags: [nginx, http3]
related: [nginx/10-http2, nginx/12-ssl-tls, nginx/13-security, nginx/18-performance, nginx/03-server-blocks]
when_to_use: "Read before enabling HTTP/3 (QUIC) or opening UDP/443 for it in your firewall."
---
# HTTP/3

## Purpose

This document defines how to enable HTTP/3 in nginx: the QUIC-over-UDP transport, the
`Alt-Svc` advertisement that gets clients to upgrade, the firewall change UDP/443 requires,
and why HTTP/3 must be offered *alongside* — not instead of — HTTP/2. HTTP/3 runs HTTP over
QUIC, which replaces TCP with UDP and integrates TLS 1.3.

HTTP/3 answers "how do I remove TCP's head-of-line blocking so one lost packet doesn't
stall every stream?". The failures are forgetting HTTP/3 is an *upgrade path* (clients try
it, then fall back), blocking UDP/443, and TLS setup mistakes since QUIC bakes TLS 1.3 in.

## Why It Matters

HTTP/2 multiplexes streams over one TCP connection, so a single dropped packet stalls all
of them (TCP head-of-line blocking) — painful on lossy mobile networks. QUIC moves
multiplexing into the transport so streams are independent, and its 0-RTT/1-RTT handshake
cuts connection setup latency. But HTTP/3 is opt-in and discovered: a client first connects
over HTTP/2, sees your `Alt-Svc` header, and only then tries QUIC. If you block UDP/443,
misconfigure TLS 1.3, or drop the HTTP/2 fallback, clients silently get a worse experience
or none of the benefit — and it looks like everything is working.

## Core Principles

- **HTTP/3 augments HTTP/2, it does not replace it.** Always keep an HTTP/2 (TCP) listener
  as the fallback; not all clients or networks allow QUIC. Offer both from the same server.
- **Advertise with `Alt-Svc` or clients never upgrade.** Discovery is out-of-band: the
  client learns HTTP/3 exists only from the `Alt-Svc: h3=":443"` response header on the
  HTTP/2 connection. Without it, HTTP/3 sits unused.
- **QUIC is UDP — open UDP/443.** HTTP/3 uses UDP, not TCP. Firewalls, security groups, and
  load balancers default to allowing only TCP/443; you must explicitly permit UDP/443.
- **TLS 1.3 is mandatory and built in.** QUIC integrates TLS 1.3; there is no HTTP/3 without
  it. Your certificate and `ssl_protocols` must support TLS 1.3 — see [SSL/TLS](12-ssl-tls.md).
- **Verify the build.** HTTP/3 requires nginx built against a QUIC-capable TLS library
  (e.g. a QUIC-enabled BoringSSL/OpenSSL). A stock build may not have `http3` support even
  if the config parses.

## Best Practices

- Enable QUIC with `listen 443 quic reuseport;` alongside the existing
  `listen 443 ssl; http2 on;` block, sharing the same certificate and `server_name`.
- Add `add_header Alt-Svc 'h3=":443"; ma=86400';` on the TLS server so clients discover and
  cache the HTTP/3 endpoint.
- Use `reuseport` on exactly one listener per address/port to let the kernel distribute UDP
  packets across workers; duplicating it errors on reload.
- Open UDP/443 in every layer: host firewall, cloud security group, and any L4 load balancer
  or proxy in front of nginx.
- Keep TLS 1.3 enabled (`ssl_protocols TLSv1.2 TLSv1.3;`); QUIC will not negotiate without
  it, and 1.2 remains the fallback for the TCP listener.
- Consider disabling 0-RTT early data unless you have made those requests replay-safe;
  0-RTT data can be replayed by an attacker, so restrict it to idempotent requests.
- Confirm your nginx binary reports QUIC support before relying on it in production.

## Examples

**Good Example** — HTTP/3 + HTTP/2 fallback, Alt-Svc, shared cert

```nginx
server {
    listen 443 ssl;                          # HTTP/2 over TCP (fallback)
    listen 443 quic reuseport;               # HTTP/3 over QUIC/UDP
    http2 on;
    server_name example.com;

    ssl_certificate     /etc/ssl/example.com/fullchain.pem;
    ssl_certificate_key /etc/ssl/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;           # TLS 1.3 is required for QUIC

    # Tell clients HTTP/3 exists; without this header they never try QUIC.
    add_header Alt-Svc 'h3=":443"; ma=86400' always;

    location / {
        proxy_pass http://app_pool;
    }
}
```

**Bad Example** — QUIC only, no advertisement, UDP blocked

```nginx
server {
    listen 443 quic reuseport;               # no TCP listener -> clients that can't QUIC get nothing
    server_name example.com;
    ssl_certificate     /etc/ssl/example.com/fullchain.pem;
    ssl_certificate_key /etc/ssl/example.com/privkey.pem;
    # No Alt-Svc header -> clients never discover HTTP/3.
    # No ssl_protocols TLSv1.3 -> QUIC handshake fails.
    # And the firewall still only allows TCP/443, so UDP packets are dropped silently.
}
```

## Common Mistakes

- Dropping the HTTP/2 (TCP) listener, so clients that cannot use QUIC lose connectivity.
- Forgetting the `Alt-Svc` header, so no client ever upgrades to HTTP/3.
- Leaving UDP/443 blocked in a firewall, security group, or upstream load balancer.
- Using `reuseport` on multiple listeners for the same port, breaking the reload.
- Assuming TLS 1.3 is optional; without it QUIC cannot negotiate at all.
- Enabling 0-RTT early data for non-idempotent requests, exposing a replay vulnerability.
- Relying on a stock nginx build without QUIC support.

## Production Tips

- Verify with `curl --http3 -I https://example.com` (needs an HTTP/3-capable curl) or a
  browser's protocol column showing `h3`; then check `Alt-Svc` is present.
- Monitor UDP/443 reachability separately from TCP; network paths that pass TCP can still
  drop UDP, silently disabling HTTP/3.
- Roll out behind the `Alt-Svc` `ma` (max-age) cache: clients fall back to HTTP/2
  automatically if QUIC starts failing, so a QUIC issue degrades rather than breaks.

## AI Review Checklist

- Is an HTTP/2 (TCP) listener kept as a fallback alongside the QUIC listener?
- Is the `Alt-Svc: h3=":443"` header set so clients discover HTTP/3?
- Is UDP/443 opened in every firewall, security group, and upstream proxy?
- Is TLS 1.3 enabled, since QUIC requires it?
- Is `reuseport` set on exactly one listener per port?
- Is 0-RTT early data restricted to replay-safe requests (or disabled)?
- Does the nginx build actually support QUIC/HTTP/3?

## Related

- `knowledge/nginx/10-http2.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/18-performance.md`
- `knowledge/nginx/03-server-blocks.md`
