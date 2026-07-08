---
id: nginx/18-performance
topic: nginx
slug: performance
title: "Performance"
type: doc
order: 18
status: ready
tags: [nginx, performance]
related: [nginx/08-caching, nginx/09-compression, nginx/10-http2, nginx/05-reverse-proxy, nginx/17-monitoring]
when_to_use: "Read before tuning nginx worker, connection, buffer, or keepalive settings for throughput or latency."
---
# Performance

## Purpose

This document defines how to make nginx serve more requests at lower latency without
sacrificing correctness. It covers the settings that actually move the needle — worker
processes, connection handling, file I/O, buffers, and keepalive — and the ones that
only look like they do. It is written so an agent can tune a config with a reason for
every value, not by copying numbers off a blog.

Performance work here means measured throughput and tail latency, not "feels faster".
Change one thing, measure, keep or revert. Guessing at buffer sizes is how you turn a
fast server into a slow one that also drops connections.

## Why It Matters

nginx sits in front of everything: a bad `worker_connections` limit or a missing
`sendfile` caps the whole system regardless of how fast the backend is. The failures are
quiet — under light load the server looks fine, then at peak it silently queues, times
out, or spikes CPU on gzip. Because nginx is the shared choke point, one wrong directive
degrades every route at once. Getting these values right is high-leverage; getting them
wrong is invisible until traffic arrives.

## Core Principles

- **Measure before and after every change.** Tune against a load test (`wrk`, `k6`) and
  read the numbers. A directive that does not change a measured metric is noise.
- **nginx is rarely the bottleneck — prove it is before tuning it.** Most latency lives
  in the backend, the database, or the network. Confirm with `$upstream_response_time`
  before touching worker settings.
- **Defaults are good; change with intent.** Modern nginx auto-tunes `worker_processes`
  and enables `sendfile`. Override a default only when you can name the reason.
- **Keep connections open.** TCP and TLS handshakes are expensive. Reuse connections to
  clients and to upstreams with keepalive; it is the single biggest win.
- **Do not trade correctness for speed.** Buffering, caching, and timeouts have failure
  modes. A fast server that corrupts or drops requests is not fast.

## Best Practices

- Set `worker_processes auto;` so nginx spawns one worker per CPU core. Pin nothing
  unless you have measured contention.
- Raise `worker_connections` (e.g. `4096`) and `worker_rlimit_nofile` together — each
  connection uses a file descriptor, so the OS limit must exceed the nginx limit.
- Enable `sendfile on;`, `tcp_nopush on;`, and `tcp_nodelay on;`. `sendfile` skips a
  userspace copy for static files; `tcp_nopush` fills packets before sending; `tcp_nodelay`
  flushes the last partial packet without delay.
- Enable client keepalive (`keepalive_timeout 65;`) and, critically, **upstream keepalive**
  (a `keepalive` directive in the `upstream` block) so nginx reuses backend connections.
- Size proxy buffers to the response, not to the maximum. Oversized `proxy_buffers`
  waste memory per connection; undersized ones spill to disk (`proxy_temp_path`) and add
  latency — watch for `an upstream response is buffered to a temporary file` in the log.
- Turn on gzip or Brotli for text responses only, at a moderate level (`gzip_comp_level 5`).
  See [compression](09-compression.md) — level 9 burns CPU for a few percent.
- Cache what you can at the edge with `proxy_cache`; a cache hit is the fastest possible
  response. See [caching](08-caching.md).

## Examples

**Good Example** — deliberate, connection-reuse-focused tuning

```nginx
# nginx.conf
worker_processes auto;              # one worker per core; scales with the box
worker_rlimit_nofile 65535;         # OS fd ceiling, must exceed worker_connections

events {
    worker_connections 4096;        # per worker; total = workers * this
    multi_accept on;                # accept all pending connections at once
}

http {
    sendfile on;                    # kernel-space file send, no userspace copy
    tcp_nopush on;                  # coalesce headers + file into full packets
    tcp_nodelay on;                 # but flush the final partial packet immediately
    keepalive_timeout 65;           # reuse client connections, skip repeat handshakes

    upstream app {
        server 10.0.0.10:3000;
        keepalive 32;               # reuse upstream connections — the biggest single win
    }

    server {
        location / {
            proxy_pass http://app;
            proxy_http_version 1.1;         # required for upstream keepalive
            proxy_set_header Connection "";  # strip "close" so the socket is pooled
        }
    }
}
```

**Bad Example** — cargo-culted numbers that hurt

```nginx
events {
    worker_connections 100000;   # far above worker_rlimit_nofile → fd exhaustion, refused conns
}

http {
    gzip on;
    gzip_comp_level 9;           # max CPU for ~2% smaller output; starves request handling
    proxy_buffers 256 64k;       # 16 MB reserved per connection → OOM under load

    upstream app { server 10.0.0.10:3000; }  # no keepalive → new TCP+TLS per request

    server {
        location / {
            proxy_pass http://app;
            # proxy_http_version defaults to 1.0 → Connection: close → keepalive impossible
        }
    }
}
```

## Common Mistakes

- Setting `worker_connections` above the file-descriptor limit, so nginx refuses
  connections at load with `worker_connections are not enough`.
- Omitting upstream `keepalive` (plus `proxy_http_version 1.1` and empty `Connection`),
  paying a full handshake on every proxied request.
- Cranking `gzip_comp_level` to 9, spending CPU that should be serving requests.
- Compressing already-compressed content (images, video, `.zip`) — pure CPU waste.
- Oversizing `proxy_buffers`, multiplying memory by every concurrent connection.
- Tuning nginx when the real latency is in the backend — chasing the wrong number.
- Enabling `access_log` synchronously on a hot path instead of buffering it.

## Production Tips

- Buffer or sample the access log on high-traffic servers: `access_log ... buffer=64k flush=5s;`
  Disk writes on every request add measurable latency.
- Expose `stub_status` and scrape it; watch active connections, reading/writing/waiting.
  See [monitoring](17-monitoring.md).
- Load-test the actual config, not a synthetic one — TLS, real payload sizes, real
  concurrency. Numbers from `localhost` plaintext lie.
- Track `$request_time` vs `$upstream_response_time` in logs; the gap is nginx overhead
  (buffering, DNS, TLS), the rest is the backend.

## AI Review Checklist

- Is `worker_processes` set to `auto`, and does `worker_rlimit_nofile` exceed `worker_connections`?
- Does every `upstream` used for proxying have `keepalive`, with `proxy_http_version 1.1`
  and `proxy_set_header Connection ""`?
- Are `sendfile`, `tcp_nopush`, and `tcp_nodelay` enabled in the `http` block?
- Is gzip limited to text types at a moderate level, and disabled for compressed content?
- Are `proxy_buffers` sized to typical responses rather than an arbitrary large value?
- Is there a load-test result justifying any non-default value?
- Is the access log buffered or sampled on hot paths?

## Related

- `knowledge/nginx/08-caching.md`
- `knowledge/nginx/09-compression.md`
- `knowledge/nginx/10-http2.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/17-monitoring.md`
