---
id: nginx/25-production
topic: nginx
slug: production
title: "Nginx Production"
type: doc
order: 25
status: ready
tags: [nginx, production, worker_rlimit_nofile, restart, max_fails, worker_connections, LimitNOFILE, fail_timeout]
related: [nginx/98-production-checklist, nginx/13-security, nginx/18-performance, nginx/27-high-availability, nginx/16-logging]
when_to_use: "Read before putting an nginx config in front of real traffic, or when reviewing whether an existing deployment is production-ready."
---
# Nginx Production

## Purpose

This document defines what separates an nginx config that works on your laptop from
one that is safe to run in front of real users: process and file-descriptor tuning,
graceful reloads, TLS hardening, timeouts, resource limits, and the operational
practices that keep it serving under load and failure. It is the bridge between "the
config parses" and "the config survives a Tuesday afternoon traffic spike."

For a pass/fail gate use the [production checklist](98-production-checklist.md); this
document explains the *why* behind each item.

## Why It Matters

nginx defaults are conservative and generic — they are tuned to start anywhere, not to
perform under your load. Left unchanged, they cap you at a few hundred connections,
leak worker memory across reloads, and hold dead upstreams. The failures do not show
in testing; they show at peak, when file descriptors run out or a backend hangs and
every worker blocks on it. Production readiness means removing the defaults that break
under pressure and adding the limits that fail safely when something goes wrong.

## Core Principles

- **Reload, never restart, for config changes.** `nginx -s reload` starts new workers
  and drains old ones with zero dropped connections. `restart` drops every live request.
- **Size workers to the machine, not by guessing.** `worker_processes auto;` matches
  CPU cores; `worker_connections` must be backed by a matching `worker_rlimit_nofile`.
- **Every upstream interaction needs a timeout.** Without `proxy_read_timeout` and
  friends, one slow backend ties up workers until they are all blocked.
- **Fail safe under limits, not open.** Connection, rate, and body-size limits should
  reject cleanly (429/413), never crash or let an attacker exhaust memory.
- **Pin the version and the config.** Production runs a known nginx version with a
  reviewed, version-controlled config — not whatever the base image shipped.

## Best Practices

- Set `worker_processes auto;` and raise `worker_rlimit_nofile` to at least
  `2 * worker_connections`, and match the systemd `LimitNOFILE`. A high
  `worker_connections` with a low fd limit fails silently at load.
- Give every proxy a full timeout set: `proxy_connect_timeout`, `proxy_send_timeout`,
  `proxy_read_timeout` (and for streaming, disable buffering deliberately). Defaults
  are 60s — often too long for a user-facing path.
- Cap request bodies with `client_max_body_size` to a real limit, not the 1M default
  and not unlimited. Too small breaks uploads; unlimited invites memory abuse.
- Terminate TLS with modern settings only: TLSv1.2+TLSv1.3, `ssl_session_cache`, OCSP
  stapling, HSTS. See [SSL/TLS](12-ssl-tls.md).
- Turn off `server_tokens` so error pages and headers do not advertise your version.
- Run health checks against upstreams and mark them down (`max_fails`,
  `fail_timeout`) so a dead backend is bypassed instead of retried into the ground.
- Rotate logs (logrotate + `USR1` signal) so `access.log` cannot fill the disk and
  take nginx down with it.

## Examples

**Good Example** — tuned worker limits, bounded timeouts, graceful posture

```nginx
worker_processes auto;                 # one worker per core
worker_rlimit_nofile 65536;            # fds must exceed worker_connections

events {
    worker_connections 16384;          # backed by the fd limit above
}

http {
    server_tokens off;                 # do not leak the nginx version
    client_max_body_size 25m;          # a real cap, sized to the largest upload

    upstream app {
        server 10.0.0.11:8080 max_fails=3 fail_timeout=15s;  # eject dead backends
        server 10.0.0.12:8080 max_fails=3 fail_timeout=15s;
        keepalive 64;                  # reuse upstream connections
    }

    server {
        location / {
            proxy_pass http://app;
            proxy_connect_timeout 2s;  # fail fast if the backend is unreachable
            proxy_read_timeout   30s;  # bounded, not the 60s default
            proxy_next_upstream error timeout http_502;  # retry a healthy peer
        }
    }
}
```

**Bad Example** — defaults everywhere, one slow backend blocks everything

```nginx
# worker_processes 1;                  ← implicit: uses a single core
events { worker_connections 1024; }    # tiny, and no matching fd limit

http {
    server {
        location / {
            proxy_pass http://10.0.0.11:8080;  # single backend, no failover
            # no timeouts → a hung backend holds workers until all 1024 are stuck
            # no client_max_body_size cap beyond default → 413s on real uploads
        }
    }
    # server_tokens on (default) → responses advertise "nginx/1.27.4"
}
```

## Common Mistakes

- Using `restart` instead of `reload`, dropping live connections on every deploy.
- Raising `worker_connections` without raising `worker_rlimit_nofile` and systemd
  `LimitNOFILE` — nginx caps out well below the configured number.
- No `proxy_*_timeout`, so a single slow upstream cascades into worker exhaustion.
- Leaving `server_tokens on`, advertising the exact version to attackers.
- One upstream `server` with no `max_fails`/failover — a backend death is an outage.
- Logs never rotated; the disk fills and nginx stops accepting connections.

## Production Tips

- Load-test with the production config (not the dev one) so you discover the fd and
  connection ceilings before users do.
- Keep the config in version control and deploy it immutably; never hand-edit on a box.
- Wire `nginx -t && nginx -s reload` into the deploy so a bad config aborts the rollout
  instead of taking the site down.
- Export metrics via `stub_status` or the Prometheus exporter and alert on
  `active connections`, 5xx rate, and `$upstream_response_time` (see
  [monitoring](17-monitoring.md)).

## AI Review Checklist

- Is `worker_processes auto;` set and `worker_rlimit_nofile` >= `2 * worker_connections`?
- Does every `proxy_pass` have connect/send/read timeouts scoped to the path?
- Is `client_max_body_size` set to a deliberate value?
- Is TLS restricted to 1.2/1.3 with HSTS, and is `server_tokens off`?
- Do upstreams have `max_fails`/`fail_timeout` and more than one peer for critical paths?
- Are config changes applied with `nginx -t` then `reload`, never `restart`?
- Is log rotation configured so the disk cannot fill?

## Related

- `knowledge/nginx/98-production-checklist.md`
- `knowledge/nginx/13-security.md`
- `knowledge/nginx/18-performance.md`
- `knowledge/nginx/27-high-availability.md`
- `knowledge/nginx/16-logging.md`
