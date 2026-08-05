---
id: nginx/16-logging
topic: nginx
slug: logging
title: "Nginx Logging"
type: doc
order: 16
status: ready
tags: [nginx, logging, Authorization, access_log, request_time, USR1, log_format, logrotate]
related: [nginx/17-monitoring, nginx/13-security, nginx/24-debugging, nginx/05-reverse-proxy]
when_to_use: "Read before configuring `access_log` / `error_log` in nginx or reviewing what the edge records."
---
# Nginx Logging

## Purpose

This document defines how nginx should log: what the access and error logs are for,
how to design a log format that is machine-parseable, what must never be written, and
how to keep logging from becoming a performance or disk problem. It is written so an
agent produces logs that are useful in an incident without leaking secrets.

The nginx logs are the authoritative record of what actually reached the edge —
status, latency, upstream behavior, client — independent of the application. They are
the first thing anyone opens during an outage.

## Why It Matters

Logs are only valuable if they exist, are parseable, and are safe. A default text
format is unparseable at scale, so during an incident you cannot query "which upstream
was slow for 5xx requests". Logging a full URL or `Authorization` header writes session
tokens, passwords, and API keys to disk and to your log pipeline — a data breach in
plain sight. And unbounded logs fill the disk, at which point nginx stops serving. Each
failure surfaces at the worst moment: mid-incident, or in an audit. Getting logging
right is preparation you cannot do retroactively — the request you needed is already gone.

## Core Principles

- **Log for querying, not reading.** A structured (JSON or strictly delimited) format
  turns logs into data you can filter, aggregate, and alert on.
- **Capture the edge truth.** Record status, request time, upstream time, upstream
  address, and bytes — the facts only nginx knows about each request.
- **Never log secrets.** Query strings, `Authorization`, `Cookie`, and card/PII fields
  do not belong in logs. Assume the log store is broadly readable.
- **Bound the volume.** Rotate, compress, and ship logs; buffer writes so logging does
  not stall request handling.
- **Separate the streams.** Access logs (every request) and error logs (nginx-level
  failures) answer different questions — keep and tune them separately.

## Best Practices

- Define a structured `log_format` (JSON or tab-delimited) including
  `$status`, `$request_time`, `$upstream_response_time`, `$upstream_addr`,
  `$body_bytes_sent`, and a request/trace id — the fields you actually query on.
- Log the request line (`$request`) but strip the query string, or log a sanitized
  path, so tokens in URLs are not persisted.
- Set `error_log` at `warn` in production (`info`/`debug` are noisy and can leak); raise
  temporarily only when actively debugging.
- Enable `access_log ... buffer=32k flush=5s;` so log writes batch instead of blocking
  each request.
- Rotate with `logrotate` and a `USR1` reopen signal; never let logs grow unbounded.
- Propagate/generate a request id (`$request_id`) and pass it upstream so edge and app
  logs correlate.
- Disable access logging for high-volume, low-value paths (health checks, static assets)
  with `access_log off;` where it adds only noise.

## Examples

**Good Example** — structured, correlated, secret-free, buffered

```nginx
http {
    # JSON so every field is queryable in the log pipeline.
    log_format json escape=json
      '{"ts":"$time_iso8601","status":$status,"method":"$request_method",'
      '"path":"$uri",'                          # $uri, not $request → no query string/tokens
      '"rt":$request_time,"urt":"$upstream_response_time",'
      '"upstream":"$upstream_addr","bytes":$body_bytes_sent,'
      '"rid":"$request_id","ip":"$remote_addr"}';

    # Buffer writes so logging does not block each request; flush at least every 5s.
    access_log /var/log/nginx/access.json json buffer=32k flush=5s;
    error_log  /var/log/nginx/error.log warn;   # warn: signal without debug noise/leaks

    server {
        add_header X-Request-Id $request_id always;   # hand the id back for correlation
        location = /healthz { access_log off; return 200; }   # drop health-check noise
    }
}
```

**Bad Example** — unparseable, leaks secrets, blocking, no rotation

```nginx
http {
    # Default combined format: logs the FULL request line including query string,
    # so /reset?token=abc123 and ?api_key=... land in plaintext on disk.
    access_log /var/log/nginx/access.log;        # unbuffered → a write per request

    # debug in production: enormous volume, and it dumps headers incl. Authorization.
    error_log /var/log/nginx/error.log debug;

    # No logrotate config anywhere → the file grows until the disk fills and nginx 500s.
}
```

## Common Mistakes

- Keeping the default combined format, which is hard to query and logs full query strings.
- Logging `Authorization`/`Cookie` headers or token-bearing URLs, writing secrets to disk.
- Running `error_log debug` in production — huge volume and it can expose request data.
- Unbuffered `access_log` on a hot path, adding a synchronous write to every request.
- No rotation, so logs fill the disk and take the server down.
- No request id, so an edge log line cannot be tied to the application log for the same request.
- Logging health checks and static assets, drowning the signal in noise.

## Production Tips

- Ship logs off the box (to Loki/ELK/CloudWatch) so they survive an instance dying and
  are searchable centrally; the local file is a buffer, not the archive.
- Alert on log-derived signals (5xx rate, p99 `request_time`) — see [monitoring](17-monitoring.md).
- Redact defensively at the shipping layer too; treat the local file as the last line, not the only one.
- After a format change, confirm the parser/pipeline still ingests it before relying on it.

## AI Review Checklist

- Is the access log a structured, machine-parseable format (JSON or strict delimiters)?
- Does it capture `$status`, `$request_time`, `$upstream_response_time`, `$upstream_addr`, and a request id?
- Are query strings, `Authorization`, and `Cookie` kept out of the logs?
- Is `error_log` at `warn` (or higher) in production, not `debug`/`info`?
- Is `access_log` buffered, and are logs rotated so the disk cannot fill?
- Is a request id propagated upstream for edge-to-app correlation?
- Is logging disabled for health checks and other high-volume, low-value paths?

## Related

- `knowledge/nginx/17-monitoring.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/24-debugging.md`
- `knowledge/nginx/05-reverse-proxy.md`
