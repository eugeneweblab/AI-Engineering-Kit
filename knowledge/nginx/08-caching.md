---
id: nginx/08-caching
topic: nginx
slug: caching
title: "Caching"
type: doc
order: 8
status: ready
tags: [nginx, caching]
related: [nginx/05-reverse-proxy, nginx/07-static-files, nginx/09-compression, nginx/06-load-balancing, nginx/17-monitoring]
when_to_use: "Read before enabling proxy_cache or setting Cache-Control on responses served through nginx."
---
# Caching

## Purpose

This document defines two related things: how nginx caches *upstream* responses with
`proxy_cache`, and how it should set *client* cache headers (`Cache-Control`, `Expires`,
`ETag`). Both reduce load and latency, but both can serve stale or wrong content to the
wrong user if configured carelessly.

Caching answers "can I reuse a previous response instead of recomputing it, and for how
long?". The dangerous failures are caching private data under a shared key, and caching
something you can never invalidate.

## Why It Matters

A cache sits between truth (your application) and the client, so a caching bug shows the
wrong answer while every component reports healthy. The two worst outcomes are both silent:
caching a *personalized* or *authenticated* response under a shared key leaks one user's
data to another; caching too aggressively pins users to stale content with no way to purge.
Because nginx caches by a key you define, the correctness of the whole system depends on
that key and on which responses you allow to be cached — details that are easy to get
subtly wrong.

## Core Principles

- **Never cache private responses under a shared key.** If a response depends on a cookie,
  `Authorization` header, or user identity, either exclude it from the cache or include the
  distinguishing value in `proxy_cache_key`. Default to *not caching* anything authenticated.
- **The origin controls cacheability; respect it.** Honor upstream `Cache-Control`,
  `Set-Cookie`, and `Vary`. Overriding them with `proxy_ignore_headers` is a deliberate,
  documented choice — not a default.
- **Cache immutable, revalidate mutable, never cache dynamic.** Fingerprinted assets cache
  forever; HTML revalidates; per-user JSON is not cached at all.
- **Always have an invalidation story.** Before you cache something, know how you will
  purge or expire it. A cache you cannot invalidate is a bug waiting to happen.
- **Serve stale on failure, on purpose.** `proxy_cache_use_stale` can keep a site up while
  the origin is down — a feature, but only when the content tolerates staleness.

## Best Practices

- Define `proxy_cache_path` with a bounded `max_size` and `inactive` time so the cache
  cannot fill the disk; put it in `http` context and reference the zone by name.
- Build `proxy_cache_key` explicitly (`$scheme$host$request_uri`) and add any header/cookie
  that changes the response; do not rely on the default key for anything personalized.
- Use `proxy_cache_valid` per status code — cache 200s for minutes/hours, but cache 404s
  briefly (e.g. 1m) so a transient miss does not get pinned.
- Add `proxy_cache_lock on` to collapse a thundering herd: only one request populates the
  cache while others wait, instead of all hitting the origin.
- Skip the cache for logged-in users with `proxy_cache_bypass`/`proxy_no_cache` keyed on
  the session cookie or `Authorization` header.
- Expose `X-Cache-Status: $upstream_cache_status` in responses (at least in staging) so you
  can verify HIT/MISS/BYPASS behavior.
- For client caching, set `Cache-Control: public, max-age=..., immutable` on hashed assets
  and `no-cache` on HTML — see [static files](07-static-files.md).

## Examples

**Good Example** — bounded cache, explicit key, bypass for authenticated users

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app:10m
                 max_size=1g inactive=60m use_temp_path=off;

map $http_authorization $no_cache {
    default 0;
    "~.+"  1;                         # any Authorization header => do not cache
}

server {
    location / {
        proxy_pass http://app_pool;
        proxy_cache app;
        proxy_cache_key "$scheme$host$request_uri";
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;                 # avoid pinning a transient 404
        proxy_cache_lock on;                      # collapse concurrent misses
        proxy_cache_use_stale error timeout updating;

        proxy_cache_bypass $no_cache;             # logged-in users skip the cache
        proxy_no_cache $no_cache;                 # and do not populate it
        add_header X-Cache-Status $upstream_cache_status always;
    }
}
```

**Bad Example** — caches authenticated responses under a shared key

```nginx
proxy_cache_path /var/cache/nginx keys_zone=app:10m;  # no max_size -> can fill the disk

server {
    location / {
        proxy_pass http://app_pool;
        proxy_cache app;
        proxy_cache_valid any 1h;              # caches EVERYTHING, including 500s and private JSON
        proxy_ignore_headers Cache-Control Set-Cookie;  # discards origin's "do not cache"
        # Default key ignores Authorization -> user A's dashboard served to user B.
    }
}
```

## Common Mistakes

- Caching authenticated or cookie-personalized responses under a key that ignores the
  distinguishing value, leaking data between users.
- `proxy_ignore_headers Cache-Control Set-Cookie` used casually, overriding the origin's
  correct instructions.
- `proxy_cache_valid any ...` caching error responses (5xx) and pinning an outage.
- Omitting `max_size`, letting the cache grow until the disk fills and nginx fails.
- No `X-Cache-Status` visibility, so you cannot tell whether caching even works.
- Caching with no plan to purge, then being unable to ship a fix.

## Production Tips

- Track hit ratio via `$upstream_cache_status` in logs; a low HIT rate means your key is
  too specific or your TTLs too short.
- For explicit purging, use `proxy_cache_purge` (nginx Plus) or a keyed
  bypass/versioned-URL strategy in open-source nginx.
- Keep the cache on fast local disk or tmpfs for hot content; `use_temp_path=off` avoids a
  needless copy across filesystems.

## AI Review Checklist

- Are authenticated/personalized responses excluded from the cache or keyed by identity?
- Does `proxy_cache_key` include every value that changes the response?
- Is `proxy_cache_valid` scoped per status, with error/404 handled deliberately (not `any`)?
- Does `proxy_cache_path` have a bounded `max_size` and `inactive`?
- Is there an invalidation/purge strategy?
- Is `$upstream_cache_status` observable to verify HIT/MISS/BYPASS?

## Related

- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/07-static-files.md`
- `knowledge/nginx/09-compression.md`
- `knowledge/nginx/06-load-balancing.md`
- `knowledge/nginx/17-monitoring.md`
