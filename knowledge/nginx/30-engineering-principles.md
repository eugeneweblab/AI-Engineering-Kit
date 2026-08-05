---
id: nginx/30-engineering-principles
topic: nginx
slug: engineering-principles
title: "Nginx Engineering Principles"
type: doc
order: 30
status: ready
tags: [nginx, engineering-principles, location, proxy_set_header, add_header, server, proxy_pass, http]
related: [nginx/26-best-practices, nginx/13-security, nginx/18-performance, nginx/25-production, nginx/29-troubleshooting]
when_to_use: "Read before designing, editing, or reviewing any nginx configuration that will serve production traffic."
---
# Nginx Engineering Principles

## Purpose

This document defines the durable principles that govern how nginx configuration is
written, structured, and changed. It is not a feature reference — it is the reasoning an
agent applies before touching a `.conf` file so the result is safe to reload into a
live edge server.

nginx sits in front of everything. A syntactically valid config can still take down every
site on the host, so the bar is correctness under reload, not just "it parses."

## Why It Matters

nginx is usually the single ingress point for all traffic. Unlike an application bug that
degrades one endpoint, an nginx mistake fails globally and instantly: one bad `proxy_pass`,
one missing `ssl_certificate`, one greedy `location` and every request 502s or leaks. The
process reloads gracefully, which is a trap — an operator who ran `nginx -s reload` on a
config that only *parses* can serve wrong or insecure responses without a single error in
the log. Because the blast radius is the whole host and failures are often silent (a
mis-scoped header, a cache serving stale auth), nginx config is held to a higher standard
than application code: validate before reload, and assume every directive inherits context
you did not intend.

## Core Principles

- **Validate before you reload.** Never reload a config you have not run `nginx -t` against.
  A test failure is the last cheap moment to catch the mistake; a runtime failure is not.
- **Understand directive inheritance.** Directives inherit from `http` → `server` →
  `location`, but many (`add_header`, `proxy_set_header`) are *replaced* wholesale, not
  merged, when redefined in a child block. Assume nothing carries down; verify it.
- **Be explicit, not clever.** Prefer exact and prefix `location` matches over regex.
  Regex locations are order-dependent and the first match wins — clever ordering is how
  auth endpoints get bypassed.
- **Fail closed.** Default `server` blocks, unmatched hosts, and upstream errors must deny
  or return a controlled error, never fall through to an arbitrary backend or the wrong site.
- **Configuration is code.** Version it, review it, and template it. A config edited live
  on one node and not the others is an outage waiting for the next deploy.
- **Separate concerns into files.** Split `http`, per-site `server` blocks, and shared
  snippets (TLS, security headers, proxy params) into includes so a change is auditable
  and reusable.

## Best Practices

- Keep a single source of truth in `conf.d/` or `sites-available/` with symlinks, and
  gate every change on `nginx -t` in CI before it reaches a host.
- Factor repeated blocks into `include` snippets (`ssl_params.conf`, `proxy_params.conf`,
  `security_headers.conf`) so TLS and security policy are defined once, not per site.
- Set `proxy_set_header Host`, `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Proto` on
  every proxy — upstreams need the real client context, and defaults drop it.
- Always define explicit timeouts (`proxy_connect_timeout`, `proxy_read_timeout`,
  `send_timeout`). The defaults are long enough to exhaust worker connections under a slow
  backend.
- Pin `worker_processes auto;` and tune `worker_connections` to the host, not a copied value.
- Reference variables and `map` blocks instead of duplicating conditional logic; avoid `if`
  inside `location` — it is evaluated in surprising ways ("if is evil").
- Keep secrets (TLS keys, upstream credentials) out of the repo; reference them by path and
  restrict file permissions to the nginx user.

## Examples

**Good Example** — explicit, testable, fails closed

```nginx
# Default server catches unknown Host headers and refuses them, so a
# misrouted or spoofed request never lands on a real site by accident.
server {
    listen 443 ssl default_server;
    ssl_certificate     /etc/nginx/ssl/default.crt;   # required even for the sink
    ssl_certificate_key /etc/nginx/ssl/default.key;
    return 444;                                        # drop the connection
}

server {
    listen 443 ssl;
    server_name app.example.com;

    include snippets/ssl_params.conf;                  # one source of TLS policy
    include snippets/security_headers.conf;            # headers defined once, reused

    location /api/ {
        include snippets/proxy_params.conf;            # Host + X-Forwarded-* set here
        proxy_pass http://api_upstream;
        proxy_read_timeout 30s;                        # explicit, not the 60s default
    }
}
```

**Bad Example** — implicit inheritance and a regex ordering trap

```nginx
server {
    listen 80;
    server_name _;                                     # matches everything, no TLS

    add_header X-Frame-Options DENY;                   # set at server level...

    location ~ \.php$ {
        add_header Cache-Control "public";             # ...this REPLACES the header above,
                                                       # silently dropping X-Frame-Options
        proxy_pass http://backend;                     # no Host/X-Forwarded-* headers
    }

    location /admin/ {                                 # prefix match, but a regex location
        proxy_pass http://backend;                     # elsewhere may win first → bypass
    }
}
```

## Common Mistakes

- Reloading without `nginx -t`, turning a typo into a site-wide 502.
- Assuming `add_header` or `proxy_set_header` inherits into a child block — redefining one
  in a child discards all parent values.
- Using regex `location` blocks whose order accidentally shadows an auth or admin path.
- Omitting `proxy_set_header Host` so the upstream sees nginx's internal name and routes wrong.
- Relying on default timeouts, so one slow upstream ties up every worker connection.
- Editing config live on one node and forgetting the rest of the fleet.
- Putting TLS keys or upstream passwords in the versioned config.

## Production Tips

- Run `nginx -t && nginx -s reload` as a single guarded command in deploy scripts; never
  reload unconditionally.
- Keep the last known-good config; a reload that fails validation leaves the old workers
  running, so recovery is `git checkout` + re-test, not a restart.
- Log the config version (a comment or `$hostname` + build tag) so you can correlate an
  incident with the exact config that was live.

## AI Review Checklist

- Has the change been validated with `nginx -t` before any reload?
- Does every `location` that redefines `add_header`/`proxy_set_header` re-include all
  headers it still needs?
- Are `location` matches unambiguous, with no regex block shadowing an auth or admin path?
- Does every `proxy_pass` set `Host` and `X-Forwarded-*` and explicit timeouts?
- Is there a `default_server` that fails closed on unknown hosts?
- Are TLS keys and credentials referenced by path, not embedded in the repo?
- Is the change in version control and applied to the whole fleet, not one node?

## Related

- `knowledge/nginx/26-best-practices.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/18-performance.md`
- `knowledge/nginx/25-production.md`
- `knowledge/nginx/29-troubleshooting.md`
