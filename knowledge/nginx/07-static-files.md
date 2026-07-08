---
id: nginx/07-static-files
topic: nginx
slug: static-files
title: "Static Files"
type: doc
order: 7
status: ready
tags: [nginx, static-files]
related: [nginx/08-caching, nginx/09-compression, nginx/04-location-blocks, nginx/13-security, nginx/10-http2]
when_to_use: "Read before serving assets, downloads, or a SPA build directly from disk with nginx."
---
# Static Files

## Purpose

This document defines how to serve files from disk with nginx: `root` vs `alias`,
cache-control headers for assets, safe handling of missing files, and the
single-page-app fallback. Serving static content is what nginx is fastest at — a request
never touches your application — but the config has sharp edges around path resolution
and header defaults.

Static file serving answers "send these exact bytes from disk, correctly and cacheably".
The failure modes are path traversal, wrong caching, and accidentally exposing files that
should never be public.

## Why It Matters

Static assets are the highest-volume traffic on most sites, so their config decides both
your bandwidth bill and your page-load time. A missing `expires` header means every
returning visitor re-downloads unchanged CSS. A confused `root`/`alias` can serve the
wrong directory — or leak `.git`, `.env`, or a backup file to anyone who guesses the URL.
Because these directives are terse and inherit across contexts, a small mistake is easy to
ship and hard to notice until it is a data leak or a cache-invalidation nightmare.

## Core Principles

- **Know `root` vs `alias`.** `root` appends the full request URI to the path; `alias`
  replaces the matched `location` prefix. Mixing them up serves the wrong directory.
- **Cache immutable assets aggressively, HTML never.** Fingerprinted files
  (`app.a1b2c3.js`) can be cached for a year; HTML and the SPA entry point must not be,
  or clients pin a stale app.
- **Deny by default what should not be served.** Dotfiles, source maps in production,
  and backup extensions must be explicitly blocked; the filesystem is not an access model.
- **Let nginx handle 404s and ranges.** nginx does missing-file, byte-range, and
  conditional-request handling natively and correctly — do not reinvent it in the app.
- **Serve, don't proxy.** If a file exists on disk at the edge, it should be sent from the
  edge; routing it through the application wastes a whole request cycle.

## Best Practices

- Use `try_files $uri $uri/ =404` for plain static roots; use
  `try_files $uri /index.html` only for SPA routes, and scope that fallback so it does not
  swallow real 404s for missing assets.
- Set `expires` and `Cache-Control: immutable` on build-hashed assets; set
  `Cache-Control: no-cache` (or short max-age) on HTML. See [caching](08-caching.md) for
  the full model.
- Block hidden and sensitive files explicitly with a `location ~ /\.` deny rule (with a
  carve-out for `/.well-known/`).
- Enable `sendfile on`, `tcp_nopush on`, and (for large files) `aio` so the kernel moves
  bytes without copying them through userspace.
- Do not serve source maps (`*.map`) publicly in production unless you intend to expose
  source; return 404 for them.
- Prefer serving pre-compressed assets over compressing on the fly for static content —
  see [compression](09-compression.md).
- Set `open_file_cache` in high-traffic static roots to avoid a `stat()` syscall per
  request.

## Examples

**Good Example** — correct `alias`, immutable asset caching, dotfile deny, SPA fallback

```nginx
server {
    root /var/www/site/dist;

    # Hashed build assets: safe to cache for a year and mark immutable.
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;                 # a missing asset is a real 404, not the app
    }

    # SPA entry: never cache, so a deploy is picked up immediately.
    location / {
        try_files $uri /index.html;
        add_header Cache-Control "no-cache";
    }

    # Never serve dotfiles (.git, .env), but allow ACME/well-known.
    location ~ /\.(?!well-known) {
        deny all;
    }

    sendfile on;
    tcp_nopush on;
}
```

**Bad Example** — `alias` path bug, caches HTML, leaks dotfiles

```nginx
server {
    location /static/ {
        # alias without a trailing slash mismatches root -> serves the wrong path,
        # and can enable traversal when combined with a regex location.
        alias /var/www/assets;
    }

    location / {
        root /var/www/site/dist;
        expires 30d;                 # caches index.html for 30 days -> stale SPA after deploy
        # No dotfile rule: GET /.env or /.git/config is served straight off disk.
    }
}
```

## Common Mistakes

- Swapping `root` and `alias`, or omitting the trailing slash on `alias`, serving the
  wrong directory.
- Caching HTML or the SPA entry point, pinning users to an old build after deploy.
- No dotfile deny rule, exposing `.env`, `.git`, or editor backup files.
- A broad `try_files $uri /index.html` that returns the SPA (200) for genuinely missing
  assets, hiding real 404s from monitoring.
- Proxying static files through the application instead of serving them from disk.
- Shipping production source maps, handing attackers your original source.

## Production Tips

- Put static assets behind a CDN and let nginx set long, immutable cache headers so the
  CDN and browsers both hold them.
- Version assets by content hash in the filename; then "cache forever" is safe because a
  changed file gets a new URL.
- Use `open_file_cache max=10000 inactive=60s;` on busy static servers to cut per-request
  `stat()` overhead.

## AI Review Checklist

- Is `root` vs `alias` used correctly, with matching trailing slashes?
- Are fingerprinted assets cached long/`immutable` while HTML is `no-cache`?
- Is there an explicit deny for dotfiles (with a `/.well-known/` carve-out)?
- Is the SPA `try_files` fallback scoped so it does not mask missing-asset 404s?
- Are production source maps blocked?
- Are `sendfile`/`tcp_nopush` enabled for efficient delivery?

## Related

- `knowledge/nginx/08-caching.md`
- `knowledge/nginx/09-compression.md`
- `knowledge/nginx/04-location-blocks.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/10-http2.md`
