---
id: nginx/98-production-checklist
topic: nginx
slug: production-checklist
title: "Nginx Production Checklist"
type: doc
order: 98
status: ready
tags: [nginx, production-checklist]
related: [nginx/25-production, nginx/12-ssl-tls, nginx/13-security, nginx/17-monitoring, nginx/27-high-availability]
when_to_use: "Read before promoting any nginx configuration to production or signing off a launch/hardening review."
---
# Nginx Production Checklist

## Purpose

This is the pre-flight checklist for putting nginx in front of live traffic. Every item is
a verifiable yes/no you can confirm against the running config or host — not advice, but a
gate. If any box is unchecked, the deployment is not ready.

## Why It Matters

The difference between a config that works on staging and one that survives production is
almost never a feature — it is the hardening, limits, and observability that were skipped
under time pressure. This list captures the items that are invisible until the moment they
matter: the missing timeout that exhausts workers under load, the absent `nginx -t` gate
that turns a typo into an outage, the default TLS that fails an audit. Walk it before every
promotion, not after the incident.

## Validation and Deployment

- [ ] `nginx -t` passes on the exact config being deployed, in CI and on the host.
- [ ] The deploy reloads with `nginx -s reload` (graceful), not `restart` (drops connections).
- [ ] The identical config is applied to every node in the fleet, not just one.
- [ ] The previous known-good config is recoverable via version control.

## TLS and Certificates

- [ ] TLS 1.2 and 1.3 only; SSLv3, TLS 1.0, and 1.1 are disabled.
- [ ] Certificates are valid, cover all served `server_name`s, and auto-renew (ACME/certbot).
- [ ] A monitor alerts on certificates within 21 days of expiry.
- [ ] `ssl_certificate` uses the full chain (leaf + intermediates), not just the leaf.
- [ ] HSTS (`Strict-Transport-Security`) is set with a sensible `max-age`.
- [ ] OCSP stapling is enabled (`ssl_stapling on;`) to cut handshake latency.

## Security Hardening

- [ ] `server_tokens off;` — the nginx version is not advertised in headers or error pages.
- [ ] A `default_server` fails closed (e.g. `return 444;`) on unknown Host headers.
- [ ] Security headers (`X-Frame-Options`/CSP, `X-Content-Type-Options`, `Referrer-Policy`)
      are set and survive every `location` that redefines `add_header`.
- [ ] Rate limiting (`limit_req`) protects login, API, and other abuse-prone endpoints.
- [ ] `client_max_body_size` is set intentionally, not left at the 1 MB default.
- [ ] Internal locations (status, metrics, admin) are IP-restricted or auth-gated.
- [ ] TLS private keys are owned by root, mode `600`, and not in the repo.

## Proxying and Upstreams

- [ ] Every `proxy_pass` sets `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.
- [ ] Explicit `proxy_connect_timeout`, `proxy_read_timeout`, and `send_timeout` are set.
- [ ] Upstreams define health checks / `max_fails` + `fail_timeout` so dead backends drop out.
- [ ] `proxy_next_upstream` is scoped so non-idempotent requests are not silently retried.
- [ ] WebSocket locations set `Upgrade`/`Connection` headers and a long `proxy_read_timeout`.

## Performance

- [ ] `worker_processes auto;` and `worker_connections` are tuned to the host, with a
      matching OS `ulimit -n`.
- [ ] `gzip` (or `brotli`) is enabled for text content types with a sane `gzip_min_length`.
- [ ] `keepalive` is configured on upstream connections to reuse backend sockets.
- [ ] Static assets have `expires`/`Cache-Control` and `sendfile on;` is enabled.
- [ ] HTTP/2 (`http2 on;`) is enabled on TLS listeners.

## Observability

- [ ] Access and error logs are written, rotated (`logrotate`), and shipped off-host.
- [ ] `error_log` level is `warn` or `error` in production, not `debug`.
- [ ] The access log format includes `$request_time` and `$upstream_response_time`.
- [ ] A metrics or status endpoint (stub_status / VTS / exporter) is scraped and dashboarded.
- [ ] Alerts fire on 5xx rate, upstream failures, and worker connection saturation.

## Resilience

- [ ] The host is not a single point of failure (LB pair, keepalived VIP, or multiple AZs).
- [ ] `limit_conn` caps per-client concurrent connections to blunt slow-loris and abuse.
- [ ] A tested rollback path exists: revert config, `nginx -t`, reload.
- [ ] Graceful shutdown drains in-flight requests before a node is removed.

## AI Review Checklist

- [ ] Was `nginx -t` run against the exact deployed config?
- [ ] Are TLS, security headers, and rate limits present and not overridden downstream?
- [ ] Does every proxy set forwarding headers and explicit timeouts?
- [ ] Is `server_tokens off` and a fail-closed `default_server` in place?
- [ ] Are logs shipped and 5xx/upstream alerts wired up?
- [ ] Is there a tested rollback and no single point of failure?

## Related

- `knowledge/nginx/25-production.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/17-monitoring.md`
- `knowledge/nginx/27-high-availability.md`
