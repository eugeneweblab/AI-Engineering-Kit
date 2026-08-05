---
id: nginx/99-ai-review-checklist
topic: nginx
slug: ai-review-checklist
title: "Nginx AI Review Checklist"
type: doc
order: 99
status: ready
tags: [nginx, ai-review-checklist]
related: [nginx/30-engineering-principles, nginx/26-best-practices, nginx/13-security, nginx/05-reverse-proxy, nginx/100-common-antipatterns]
when_to_use: "Read before reviewing or approving any nginx config change in a pull request or agent-generated diff."
---
# Nginx AI Review Checklist

## Purpose

This is the checklist an agent runs when reviewing an nginx configuration change. Each item
is a concrete yes/no an agent can confirm by reading the diff and the surrounding blocks —
not a style preference. Its job is to catch the class of nginx mistakes that pass `nginx -t`
but still break, leak, or slow down production.

## Why It Matters

nginx failures are disproportionately caused by things a syntax check cannot see: a header
that silently stops inheriting, a regex `location` that shadows an auth path, a proxy that
drops the client's real IP. Because the config parses, review is the only gate that catches
these before they ship. A reviewer who checks only "does it parse" approves outages. This
list forces the reviewer to reason about inheritance, matching order, and failure modes.

## Correctness and Matching

- [ ] Does the change pass `nginx -t`, and is that verified rather than assumed?
- [ ] Are `location` matches unambiguous — no regex block silently shadowing a prefix/auth path?
- [ ] For redefined `add_header`/`proxy_set_header` in a child block, are all still-needed
      values re-declared (they are replaced, not merged)?
- [ ] Does `proxy_pass` end with `/` (or not) consistently with the intended URI rewriting?
- [ ] Are there no `if` directives inside `location` doing work `try_files`/`map` should do?

## Proxying

- [ ] Are `Host`, `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Proto` set on the proxy?
- [ ] Are explicit `proxy_connect_timeout`/`proxy_read_timeout`/`send_timeout` present?
- [ ] Is `proxy_next_upstream` scoped so non-idempotent (POST/PUT) requests are not retried?
- [ ] For WebSockets, are `Upgrade` and `Connection` headers and a long read timeout set?
- [ ] Is `resolver` configured when `proxy_pass` uses a variable/DNS name that can change?

## Security

- [ ] Is `server_tokens off;` set so the version is not leaked?
- [ ] Does an unknown Host fail closed via a `default_server`, not fall through to a real site?
- [ ] Are TLS settings restricted to 1.2/1.3 with a modern cipher suite?
- [ ] Are security headers present and not dropped by a downstream `add_header`?
- [ ] Are internal/admin/metrics locations IP- or auth-restricted?
- [ ] Is rate limiting applied to abuse-prone endpoints, and no secret committed to the repo?

## Performance and Caching

- [ ] Are timeouts and `worker_connections` sane for the expected load?
- [ ] Is `gzip`/`brotli` enabled for text types without compressing already-compressed assets?
- [ ] Does `proxy_cache`/`fastcgi_cache` honor `Cache-Control` and never cache authenticated
      or `Set-Cookie` responses by accident?
- [ ] Is `keepalive` set on upstreams to reuse backend connections?

## Observability and Change Safety

- [ ] Do access logs include `$request_time` and `$upstream_response_time`?
- [ ] Is `error_log` at `warn`/`error`, not `debug`, for production?
- [ ] Is the change in version control and applied fleet-wide, not one node?
- [ ] Is there a rollback path (revert, `nginx -t`, reload)?

## Examples

**Good** — a diff a reviewer can approve

```nginx
location /api/ {
    include snippets/proxy_params.conf;    # Host + X-Forwarded-* + timeouts, one source
    include snippets/security_headers.conf; # re-included so headers are not dropped here
    proxy_pass http://api_upstream;
    proxy_read_timeout 30s;                 # explicit
}
```

**Bad** — a diff to reject

```nginx
location /api/ {
    add_header X-Api-Version "2";           # REPLACES all inherited security headers
    proxy_pass http://api_upstream;         # no Host / X-Forwarded-* → upstream mis-routes
    # no timeouts → one slow call ties up a worker connection indefinitely
}
```

## AI Review Checklist

- [ ] Verified `nginx -t` passes, not just that syntax looks right.
- [ ] Confirmed no `location`/header inheritance surprise in the diff.
- [ ] Confirmed proxy forwarding headers and timeouts are present.
- [ ] Confirmed version leak, fail-closed default, and TLS restrictions.
- [ ] Confirmed logging, rollback, and fleet-wide application.

## Related

- `knowledge/nginx/30-engineering-principles.md`
- `knowledge/nginx/26-best-practices.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/100-common-antipatterns.md`
