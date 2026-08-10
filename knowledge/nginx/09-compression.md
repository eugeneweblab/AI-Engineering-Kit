---
id: nginx/09-compression
topic: nginx
slug: compression
title: "Compression"
type: doc
order: 9
status: ready
tags: [nginx, compression, Accept-Encoding, gzip_comp_level, being, responses, enabling]
related: [nginx/07-static-files, nginx/08-caching, nginx/12-ssl-tls, nginx/10-http2, nginx/18-performance]
when_to_use: "Read before enabling gzip/brotli or debugging why responses are not being compressed."
---
# Compression

## Purpose

This document defines how to compress responses in nginx with gzip and Brotli: which
content types to compress, when to pre-compress versus compress on the fly, and the
security pitfalls of compressing dynamic, secret-bearing responses. Compression trades a
little CPU for large bandwidth and latency wins on text.

Compression answers "can I send fewer bytes for the same content?". The traps are
compressing things that do not benefit (already-compressed media), compressing at a cost
that hurts latency, and compressing secret-bearing responses in a way that enables the
BREACH attack.

## Why It Matters

Text assets — HTML, CSS, JS, JSON — dominate page weight, and compressing them typically
cuts transfer size by 70-80%, directly improving load time and bandwidth cost. But
compression is not free or always safe: compressing responses that mix attacker-controlled
input with secrets over TLS opens the BREACH side channel, and compressing already-
compressed formats (images, video, zip) wastes CPU for zero gain. Because the defaults are
conservative (gzip off, or only `text/html`), most sites under-compress; a careless config
over-compresses. Both are easy to ship silently.

## Core Principles

- **Compress text, never re-compress media.** gzip/Brotli help HTML/CSS/JS/JSON/SVG/fonts;
  JPEG, PNG, WebP, MP4, and zip are already compressed and only cost CPU.
- **Prefer pre-compressed static assets.** For files that do not change per request,
  compress once at build time and serve the `.gz`/`.br` with `gzip_static`/`brotli_static`
  at the highest ratio; do not burn CPU compressing the same file on every request.
- **Mind BREACH on dynamic, secret-bearing responses.** If a response is served over TLS,
  contains a secret (CSRF token, session data), and reflects user input, compressing it can
  leak the secret. Disable compression there or separate secrets from reflected input.
- **Pick a level that fits the workload.** High gzip levels give diminishing size wins at
  rising CPU cost; on-the-fly compression should use a moderate level, pre-compression a
  maximal one.
- **Honor client capability.** Only compress when the client sends `Accept-Encoding`;
  nginx handles this, but a broken proxy in front can strip it — verify end to end.

## Best Practices

- Enable `gzip on` with an explicit `gzip_types` list covering text formats; the default
  only compresses `text/html`, leaving CSS/JS/JSON uncompressed.
- Add Brotli (`brotli on`) when the module is available — it beats gzip on text at similar
  CPU — but keep gzip as the fallback for clients that do not advertise `br`.
- Set `gzip_min_length 1024` so tiny responses are not compressed (the overhead exceeds the
  saving below ~1 KB).
- Use `gzip_static on;`/`brotli_static on;` for build assets and generate `.gz`/`.br`
  files in CI; serve those instead of compressing per request.
- Set `gzip_comp_level` to a moderate value (4-6) for on-the-fly text; reserve level 9 / 11
  for pre-compressed static files.
- Add `gzip_vary on;` so caches key correctly on `Accept-Encoding` and do not serve a
  compressed body to a client that cannot decode it.
- Set `gzip_proxied` appropriately (e.g. `any` or specific tokens) when nginx sits behind
  another proxy, or proxied responses will not be compressed.
- Do not compress responses that combine secrets and reflected user input over TLS; scope
  compression off for those endpoints.

## Examples

**Good Example** — text-only types, pre-compressed statics, safe defaults

```nginx
# On-the-fly compression for dynamic text responses.
gzip on;
gzip_vary on;                        # caches must vary on Accept-Encoding
gzip_min_length 1024;                # don't compress tiny payloads
gzip_comp_level 5;                   # moderate CPU for on-the-fly
gzip_proxied any;
gzip_types text/plain text/css application/json application/javascript
           text/xml application/xml image/svg+xml font/woff2;

# Serve pre-built .br/.gz for static assets instead of compressing each request.
brotli_static on;
gzip_static on;

# JPEG/PNG/MP4 are omitted from gzip_types on purpose: already compressed.
```

**Bad Example** — compresses everything, wrong level, BREACH risk

```nginx
gzip on;
gzip_comp_level 9;                   # max CPU on every dynamic request -> latency hit
gzip_types *;                        # invalid intent: also compresses images/video for no gain
# gzip_vary missing -> a shared cache may serve a gzipped body to a non-gzip client.
# Compression left ON for an authenticated page that reflects a query param and
# embeds a CSRF token over HTTPS -> BREACH oracle leaks the token.
```

## Common Mistakes

- Relying on the default `gzip_types` (`text/html` only), leaving CSS/JS/JSON uncompressed.
- Compressing already-compressed media (images, video, archives), spending CPU for nothing.
- Compressing on the fly at level 9, adding latency instead of using `gzip_static`.
- Omitting `gzip_vary`, causing caches to serve a compressed body to a client that cannot
  read it.
- Leaving compression on for TLS responses that mix a secret with reflected input (BREACH).
- Forgetting `gzip_proxied`, so compression silently does nothing behind another proxy.

## Production Tips

- Verify with `curl -H 'Accept-Encoding: br,gzip' -I https://site/...` and check the
  `Content-Encoding` response header — do not assume compression is happening.
- Generate `.br`/`.gz` in the build pipeline so the runtime never compresses static bytes.
- Measure: compression is a CPU/bandwidth trade. On CPU-bound origins, lower the on-the-fly
  level or push compression to a CDN edge.

## AI Review Checklist

- Does `gzip_types` cover CSS, JS, JSON, SVG, and fonts — not just `text/html`?
- Are already-compressed media types excluded?
- Are static assets served pre-compressed (`gzip_static`/`brotli_static`) rather than
  compressed per request?
- Is `gzip_vary on` set so caches key on `Accept-Encoding`?
- Is compression disabled for TLS responses that reflect user input alongside secrets
  (BREACH)?
- Is the on-the-fly `gzip_comp_level` moderate rather than maxed?

## Related

- `knowledge/nginx/07-static-files.md`
- `knowledge/nginx/08-caching.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/10-http2.md`
- `knowledge/nginx/18-performance.md`
