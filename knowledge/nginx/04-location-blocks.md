---
id: nginx/04-location-blocks
topic: nginx
slug: location-blocks
title: "Location Blocks"
type: doc
order: 4
status: ready
tags: [nginx, location-blocks]
related: [nginx/03-server-blocks, nginx/05-reverse-proxy, nginx/07-static-files, nginx/02-configuration, nginx/13-security]
when_to_use: "Read before adding or debugging any location, or when a request matches the wrong path handler."
---
# Location Blocks

## Purpose

This document defines how nginx matches a request URI to a `location` block: the match
modifiers, their precedence, and how `root`, `alias`, and `try_files` resolve to a
file or upstream. Location matching is the single most misunderstood part of nginx
config; getting the order right prevents the majority of routing bugs.

## Why It Matters

Within a chosen `server` block, the `location` decides everything that follows — which
files are served, which requests are proxied, which security rules apply. The match
rules are *not* top-to-bottom for every case: prefix and regex locations follow a
specific precedence that surprises people who assume first-match-wins. A single
mis-ordered regex can shadow a security rule or send an API path to the static-file
handler, and it will look correct on casual reading.

## Core Principles

- **Match precedence is fixed, not source-order for prefixes.** nginx evaluates:
  (1) exact `=`, (2) longest `^~` prefix, (3) first matching regex `~`/`~*` in file
  order, (4) longest plain-prefix match as fallback. Know this order cold.
- **`^~` stops regex evaluation.** A longest-prefix match with `^~` short-circuits the
  regex phase — use it to protect a prefix from being stolen by a later regex.
- **`root` appends the URI; `alias` replaces the matched prefix.** Confusing the two is
  the classic path-traversal or 404 bug. Use `alias` only inside a prefix `location`.
- **`try_files` is the safe resolver.** It tests paths in order and falls back
  explicitly, avoiding the traversal pitfalls of naive `if (-f ...)` checks.

## Best Practices

- Use `=` for hot exact paths (e.g. `= /healthz`) — it is the fastest match and makes
  intent explicit.
- Guard static/asset prefixes with `^~` so a broad regex cannot intercept them.
- Prefer `try_files $uri $uri/ /index.html;` (SPA) or `try_files $uri =404;` over
  chains of `if`; `try_files` is evaluated safely and clearly.
- Use `root` by default; reach for `alias` only when the filesystem path diverges from
  the URI, and always keep a trailing slash consistent between the `location` and
  `alias`.
- Deny access to sensitive paths early and explicitly (`location ~ /\.` for dotfiles).
- Keep regex locations few and specific; each one is evaluated in order on every
  request, so cost and shadowing both grow with count.

## Examples

**Good Example** — deliberate precedence, safe resolution

```nginx
server {
    root /var/www/app;

    location = /healthz { return 200 "ok\n"; }   # exact match, checked first, cheapest

    location ^~ /static/ {                        # ^~ stops regex phase: assets are protected
        expires 30d;                              # long cache for fingerprinted assets
        try_files $uri =404;                      # serve file or a clean 404, no fallthrough
    }

    location ~* \.(js|css)$ {                     # regex only reached for non-/static/ assets
        expires 7d;
    }

    location / {
        try_files $uri $uri/ /index.html;         # SPA fallback, evaluated safely
    }

    location ~ /\. { deny all; }                  # block dotfiles (.git, .env) explicitly
}
```

**Bad Example** — shadowed prefix, alias misuse, unsafe if

```nginx
server {
    location ~* \.(js|css)$ { expires 7d; }       # regex ordered BEFORE /static/ prefix...
    location /static/ {                           # ...so .js/.css under /static never hit this
        alias /var/www/assets;                    # missing trailing slash: /static/x -> /var/www/assetsx
    }

    location / {
        if (-f $request_filename) { expires 1d; } # `if` in location: fragile, use try_files
        proxy_pass http://app;
    }
    # No dotfile guard: /.git/config and /.env are served if present
}
```

## Common Mistakes

- Assuming locations are matched top-to-bottom; forgetting `=` and `^~` take precedence
  over regex, and regex takes precedence over a longer plain prefix.
- Mismatched trailing slashes between a `location` and its `alias`, causing wrong paths.
- Using `alias` where `root` was meant (or vice versa), producing 404s or traversal.
- A broad regex (`\.(js|css)$`) placed before a prefix it should not shadow.
- Replacing `try_files` with `if (-f ...)`, which is slower and error-prone.
- No explicit deny for dotfiles, backups, or `.git`, leaking secrets.

## Production Tips

- Add `location = /healthz` and `location = /favicon.ico` explicitly; they are hot and
  benefit from the exact-match fast path.
- When a request hits the wrong handler, enable debug logging or use `nginx -T` plus a
  test `curl` to trace which `location` matched. See [debugging](24-debugging.md).
- For proxied apps, keep proxy locations and static locations clearly separated so
  neither shadows the other. See [reverse proxy](05-reverse-proxy.md).

## AI Review Checklist

- Is match precedence (`=` > `^~` > regex > prefix) accounted for, not source order?
- Are asset/static prefixes protected with `^~` from later regex locations?
- Is `root` vs `alias` correct, with consistent trailing slashes?
- Is path resolution done with `try_files` rather than `if (-f ...)`?
- Are dotfiles and sensitive paths explicitly denied?
- Are regex locations minimal, specific, and ordered so none shadows another?

## Related

- `knowledge/nginx/03-server-blocks.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/07-static-files.md`
- `knowledge/nginx/02-configuration.md`
- `knowledge/nginx/13-security.md`
