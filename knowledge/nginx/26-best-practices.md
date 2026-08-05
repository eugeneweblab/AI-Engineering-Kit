---
id: nginx/26-best-practices
topic: nginx
slug: best-practices
title: "Nginx Best Practices"
type: doc
order: 26
status: ready
tags: [nginx, best-practices, location, add_header, proxy_pass, always, try_files, resolver]
related: [nginx/02-configuration, nginx/04-location-blocks, nginx/13-security, nginx/25-production, nginx/100-common-antipatterns]
when_to_use: "Read before writing or reviewing any nginx config, to apply the conventions that keep it correct, secure, and maintainable."
---
# Nginx Best Practices

## Purpose

This document collects the config conventions that make an nginx setup correct,
readable, and safe to change: how to structure files, how to write `location` and
`proxy_pass` so they match what you intend, which defaults to override, and which
directives are traps. It is the "how a senior engineer writes nginx" reference —
concrete rules, each with the reason behind it.

It complements [production](25-production.md) (operational readiness) and
[common anti-patterns](100-common-antipatterns.md) (what not to do); this is the
positive-form playbook.

## Why It Matters

nginx config is a small, unforgiving language where a trailing slash, an `if`, or a
missing `always` on `add_header` changes behavior in ways that pass `nginx -t` and
still route traffic wrong. Because the file is declarative and matching is
priority-based, "looks right" and "is right" diverge constantly. Following
established conventions removes whole classes of subtle bugs and makes the config
reviewable — the next engineer can predict what a block does without running it.

## Core Principles

- **Prefer explicit over clever.** A few clear `location` blocks beat one regex with
  captures. The config is read far more often than it is written.
- **`if` is evil — avoid it.** Inside `location`, most `if` uses are undefined or
  surprising. Use `map`, `try_files`, `return`, or `location` matching instead.
- **Understand `location` priority, not source order.** Exact (`=`) > prefix `^~` >
  regex (`~`, `~*`) > plain prefix. nginx does not match top-to-bottom like a script.
- **Trailing slashes are semantic.** `proxy_pass http://app/` rewrites the path;
  `proxy_pass http://app` preserves it. `location /api` vs `/api/` match differently.
- **Split config into includes.** One giant file is unreadable; per-site files under
  `sites-available` / `conf.d` are diff-friendly and independently testable.

## Best Practices

- Factor shared proxy settings into an `include snippets/proxy.conf;` so every
  backend gets the same headers and timeouts — DRY config, one place to fix.
- Always set the standard proxy headers (`Host`, `X-Real-IP`, `X-Forwarded-For`,
  `X-Forwarded-Proto`) or the backend sees nginx's identity, not the client's.
- Use `try_files $uri $uri/ =404;` for static and SPA routing instead of `if -f`.
  `try_files` is evaluated once and is far cheaper and clearer than `if` chains.
- Add `always` to security-relevant `add_header` (HSTS, CSP) so it is emitted on
  error responses too — without it, headers are dropped on 4xx/5xx.
- Remember `add_header` does not inherit into a block that has its own `add_header`;
  re-declare or use an include, or the parent headers silently vanish.
- Set `resolver` with a `valid=` TTL when using variables in `proxy_pass`, so DNS
  changes for the backend are picked up instead of cached forever.
- Pin `worker_processes auto;`, `sendfile on;`, `tcp_nopush on;`, and `gzip` in
  `http {}` once, rather than repeating per-server.

## Examples

**Good Example** — shared snippet, correct headers, `try_files` over `if`

```nginx
# snippets/proxy.conf — one source of truth for every backend
proxy_set_header Host              $host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;  # appends, not overwrites
proxy_set_header X-Forwarded-Proto $scheme;
proxy_connect_timeout 2s;
proxy_read_timeout   30s;

server {
    root /var/www/app;

    location / {
        try_files $uri $uri/ /index.html;   # SPA fallback, no `if`
    }

    location /api/ {
        include snippets/proxy.conf;         # DRY: same headers/timeouts everywhere
        proxy_pass http://app_backend;       # no trailing slash → keeps /api/ prefix
    }

    add_header Strict-Transport-Security "max-age=63072000" always;  # emitted on errors too
}
```

**Bad Example** — `if`, missing headers, silent header loss

```nginx
server {
    location / {
        if ($request_method = POST) {        # `if` inside location: fragile, undefined edges
            proxy_pass http://app_backend;
        }
        # backend receives no Host/X-Forwarded-* → wrong redirects, wrong client IP
        proxy_pass http://app_backend/;      # trailing slash silently strips the path
    }

    location /secure/ {
        add_header X-Frame-Options DENY;     # this block's add_header hides the parent's HSTS
    }
    add_header Strict-Transport-Security "max-age=63072000";  # no `always` → dropped on errors
}
```

## Common Mistakes

- Using `if` inside `location` for anything but the documented-safe cases; behavior is
  undefined and routing breaks in edge cases.
- Assuming `location` blocks match in file order rather than by priority class.
- Getting the `proxy_pass` trailing slash wrong, mangling the upstream path.
- Forgetting `X-Forwarded-*` headers, so the backend logs nginx's IP and builds wrong URLs.
- Omitting `always` on security headers, dropping them exactly on error responses.
- A child block's `add_header` silently discarding all inherited headers.
- Hardcoding a backend IP in `proxy_pass` with no `resolver`, so DNS changes never apply.

## Production Tips

- Run `nginx -T` (capital T) to dump the fully-resolved config with all includes — review
  that, not the fragments, since inheritance and overrides only appear in the merged view.
- Keep a linter (`gixy` for security, `nginx -t` for syntax) in CI so bad config never merges.
- Standardize on one directory convention (`conf.d/` or `sites-available/` + symlinks) across
  the fleet so every host is navigable the same way.

## AI Review Checklist

- Are `if` directives inside `location` replaced with `map`/`try_files`/`return`?
- Do `location` blocks account for priority (`=`, `^~`, regex, prefix), not source order?
- Is the `proxy_pass` trailing slash intentional and matching the desired path rewrite?
- Are `Host` and `X-Forwarded-*` headers set on every proxied location?
- Do security headers use `always`, and is `add_header` inheritance accounted for?
- Are shared settings factored into includes rather than copy-pasted per server?
- Was the merged config reviewed with `nginx -T`, not just the fragments?

## Related

- `knowledge/nginx/02-configuration.md`
- `knowledge/nginx/04-location-blocks.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/25-production.md`
- `knowledge/nginx/100-common-antipatterns.md`
