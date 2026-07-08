---
id: nginx/100-common-antipatterns
topic: nginx
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [nginx, common-antipatterns]
related: [nginx/30-engineering-principles, nginx/05-reverse-proxy, nginx/13-security, nginx/04-location-blocks, nginx/08-caching]
when_to_use: "Read before writing or reviewing nginx config to recognize the failure patterns that pass nginx -t but break production."
---
# Common Antipatterns

## Purpose

This document catalogs the recurring nginx mistakes that survive a syntax check and reach
production. Each entry states the anti-pattern, why it is wrong (the concrete failure it
causes), and the fix. Use it as a pattern-matcher while writing or reviewing config.

## Why It Matters

nginx anti-patterns are dangerous precisely because `nginx -t` accepts them. They do not
crash on reload; they route to the wrong backend, drop a security header, cache a private
response, or exhaust workers under load. The symptoms appear later, in production, far from
the line that caused them. Learning the shapes here lets an agent reject them on sight
instead of debugging them at 3 a.m.

## Anti-Patterns

### 1. Redefining `add_header` in a child block

- **Why it is wrong:** `add_header` does not merge. The moment any `location` (or nested
  block) declares its own `add_header`, every header inherited from the parent is discarded.
  A single `add_header Cache-Control ...` in one location can silently remove your HSTS and
  `X-Frame-Options`.
- **The fix:** Define headers once in an `include` snippet and re-include it in every block
  that also needs to add a header. Verify with `curl -I` that the headers actually appear.

### 2. Using `if` inside `location`

- **Why it is wrong:** `if` in a `location` context is evaluated at request-processing time
  in ways that break `try_files`, `alias`, and other directives ("if is evil"). It commonly
  produces wrong routing or an internal error that only shows under specific request shapes.
- **The fix:** Replace conditional logic with `try_files`, `map`, `limit_except`, or separate
  `location` blocks. Reserve `if` for the few safe cases (e.g. `return`/`rewrite` at server level).

```nginx
# Bad: fragile, breaks try_files
location / {
    if ($http_user_agent ~* bot) { return 403; }
    try_files $uri $uri/ =404;
}
# Good: map decides once, cleanly
map $http_user_agent $is_bot { default 0; ~*bot 1; }
server { location / { if ($is_bot) { return 403; } try_files $uri $uri/ =404; } }
```

### 3. Missing forwarding headers on a proxy

- **Why it is wrong:** Without `proxy_set_header Host` and `X-Forwarded-*`, the upstream sees
  nginx's internal upstream name and loses the real client IP and scheme. Virtual-host routing
  breaks, redirects point at the wrong host, and logs/rate-limits see one IP for everyone.
- **The fix:** Set `Host`, `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Proto` on every
  proxy — centralize them in a `proxy_params` snippet.

### 4. Relying on default timeouts

- **Why it is wrong:** The default `proxy_read_timeout` is 60s. Under a slow or hung upstream,
  workers hold connections for a full minute each, and `worker_connections` is exhausted long
  before the timeout — a slow backend becomes a total outage.
- **The fix:** Set explicit `proxy_connect_timeout`, `proxy_read_timeout`, and `send_timeout`
  sized to the endpoint's real latency budget.

### 5. Ambiguous or shadowing `location` order

- **Why it is wrong:** Regex `location` blocks are matched in file order and the first match
  wins, overriding prefix matches you expected to handle a path. An admin or auth path can be
  silently captured by an earlier regex like `~ \.(php|json)$`, bypassing its intended handler.
- **The fix:** Prefer exact (`=`) and prefix (`^~`) matches for sensitive paths, keep regex
  blocks minimal and ordered deliberately, and test each critical path with `curl`.

### 6. Caching authenticated or `Set-Cookie` responses

- **Why it is wrong:** A `proxy_cache` that ignores `Cache-Control`/`Set-Cookie` will store one
  user's private response and serve it to the next visitor — an account-takeover-grade data leak.
- **The fix:** Do not cache responses with `Set-Cookie`, respect upstream `Cache-Control`, and
  add `proxy_no_cache`/`proxy_cache_bypass` on the auth cookie. Cache only truly public content.

```nginx
# Good: never serve one user's response to another
proxy_no_cache      $http_authorization $cookie_sessionid;
proxy_cache_bypass  $http_authorization $cookie_sessionid;
```

### 7. Leaking the nginx version and falling through on unknown hosts

- **Why it is wrong:** `server_tokens on` (the default) advertises the exact version in headers
  and error pages, handing attackers a CVE shortlist. With no `default_server`, a request with
  an unknown or spoofed Host lands on whichever server block is first — often the wrong site.
- **The fix:** Set `server_tokens off;` and add a `default_server` that fails closed
  (`return 444;`) for unmatched hosts.

### 8. Reloading without validating

- **Why it is wrong:** `nginx -s reload` on an untested config that happens to fail will keep
  old workers but a config that merely *parses* yet is semantically wrong ships instantly.
  Skipping `nginx -t` turns a typo into a site-wide 502.
- **The fix:** Always `nginx -t && nginx -s reload` as one guarded step; gate merges on
  `nginx -t` in CI.

### 9. Editing config live on one node

- **Why it is wrong:** A hand-edit on a single server drifts from the rest of the fleet and
  from version control. The next automated deploy overwrites it, or a load balancer serves
  inconsistent behavior depending on which node answers.
- **The fix:** Treat config as code — change it in the repo, review, `nginx -t` in CI, and
  roll it to every node.

### 10. Enabling `non_idempotent` retries on `proxy_next_upstream`

- **Why it is wrong:** Since nginx 1.9.13 the default will not retry a request already sent
  upstream when the method is non-idempotent (POST/LOCK/PATCH). Adding the `non_idempotent`
  flag overrides that safety, so a `POST` that timed out after reaching one backend gets
  resent to another, causing duplicate charges, duplicate emails, or double writes.
- **The fix:** Do not add `non_idempotent`. Keep `proxy_next_upstream` scoped to safe
  conditions (`error timeout http_502`); the default already excludes non-idempotent methods.
  Use `proxy_next_upstream off;` for write endpoints to disable retries entirely.

## AI Review Checklist

- [ ] No child block redefines `add_header` without re-including required headers.
- [ ] No `if` inside `location` doing routing that `try_files`/`map` should do.
- [ ] Every proxy sets forwarding headers and explicit timeouts.
- [ ] `location` order does not shadow sensitive/auth paths.
- [ ] Cache never stores authenticated or `Set-Cookie` responses.
- [ ] `server_tokens off` and a fail-closed `default_server` are present.
- [ ] Config is validated with `nginx -t`, versioned, and rolled fleet-wide.

## Related

- `knowledge/nginx/30-engineering-principles.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/04-location-blocks.md`
- `knowledge/nginx/08-caching.md`
