---
id: nginx/29-troubleshooting
topic: nginx
slug: troubleshooting
title: "Nginx Troubleshooting"
type: doc
order: 29
status: ready
tags: [nginx, troubleshooting, alias, root, worker_connections, client_max_body_size, proxy_read_timeout, backend]
related: [nginx/24-debugging, nginx/05-reverse-proxy, nginx/16-logging, nginx/12-ssl-tls, nginx/25-production]
when_to_use: "Read when nginx returns a specific error — 502/504, 413, 404, TLS handshake failure, or 'address already in use' — and you need the known cause and fix."
---
# Nginx Troubleshooting

## Purpose

This document is a field guide to nginx's most common failure signatures and their
causes: what a `502` vs `504` actually means, why uploads get `413`, why a valid file
returns `404`, why TLS handshakes fail, and why a reload says "address already in use."
Each entry maps a symptom to the mechanism and the fix, so an agent can resolve the
error instead of guessing.

Troubleshooting is pattern-matching known failure classes; [debugging](24-debugging.md)
is the method you fall back to when the symptom is *not* a known one. Read that for the
general loop; read this for the specific error in front of you.

## Why It Matters

nginx error codes are precise but easily misread — a `502` and a `504` point at
different problems, and fixing the wrong one wastes an outage. Most nginx errors have a
small set of well-known causes; recognizing the signature turns a 30-minute
investigation into a two-minute fix. The cost of misdiagnosis is high: restarting nginx
"to see if it helps" during a `502` does nothing if the real problem is a dead backend,
and drops live connections on top.

## Core Principles

- **Read the error log line for the exact code.** nginx logs the upstream error and
  the failing directive; the code alone is ambiguous, the log line is not.
- **Locate the failing layer first.** Is the error nginx-generated (404 match, 413 body
  limit) or relayed from the upstream (502/504)? `$upstream_status` disambiguates.
- **502 ≠ 504.** 502 = nginx reached the backend and got a bad/closed response;
  504 = the backend did not answer within the timeout. Different fixes.
- **Reproduce on the box, against the origin.** `curl` from the nginx host removes the
  CDN, client network, and browser cache from the diagnosis.
- **Change one thing, re-test.** With `nginx -t && reload` between each change, so you
  know which edit fixed (or broke) it.

## Best Practices

- For **502 Bad Gateway**: the backend is down, crashed, or spoke the wrong protocol.
  Curl the upstream directly; check the backend process; verify `proxy_pass` scheme
  (`http` vs `https`) and that the backend is not returning malformed responses.
- For **504 Gateway Timeout**: the backend is too slow. Raise `proxy_read_timeout` only
  if the slowness is legitimate; otherwise fix the backend — a longer timeout hides the
  real problem and ties up workers.
- For **413 Request Entity Too Large**: raise `client_max_body_size` on the relevant
  `server`/`location` to fit real uploads; the default is 1M.
- For **404 on a file that exists**: check `root` vs `alias` (a classic mismatch), file
  permissions for the nginx user, and `try_files`. `nginx -T` shows the effective `root`.
- For **TLS handshake failures**: verify the full chain is in the cert file (leaf +
  intermediates), the protocol/cipher set matches the client, and SNI resolves to the
  right `server` block. Test with `openssl s_client -connect host:443 -servername host`.
- For **"bind() ... address already in use"**: another process (often a stray nginx or
  another web server) holds the port. `ss -ltnp | grep :80` finds it.
- For **worker connection / "too many open files"**: raise `worker_rlimit_nofile` and
  the systemd `LimitNOFILE`, not just `worker_connections` (see [production](25-production.md)).

## Examples

**Good Example** — diagnose a 502 by isolating the layer

```bash
# 1. Confirm nginx logged it as an upstream failure, not a config 502
tail -n 20 /var/log/nginx/error.log
#   → "connect() failed (111: Connection refused) while connecting to upstream"
#      = backend is down, NOT an nginx config problem

# 2. Curl the upstream directly from the nginx host to confirm
curl -v http://10.0.0.11:8080/healthz     # Connection refused → backend really is down

# 3. Fix the backend (start the process); nginx recovers automatically once the
#    peer answers again — no nginx restart needed.
```

```nginx
# For a legitimate 413 on an upload path, scope the limit — don't raise it globally:
location /uploads/ {
    client_max_body_size 100m;   # sized to the real max upload, only where needed
    proxy_pass http://app;
}
```

**Bad Example** — reacting to the code without reading the cause

```bash
# 502 in the browser → "restart nginx and hope"
sudo systemctl restart nginx     # drops every live connection; backend is still dead
                                 # → 502 persists, and now in-flight requests were killed

# 504 → blindly bump the timeout instead of fixing the slow backend
#   proxy_read_timeout 600s;     # hides a 10-minute query; workers stay blocked at scale
```

## Common Mistakes

- Treating 502 and 504 as the same error and applying the wrong fix.
- Restarting nginx for an upstream failure — it changes nothing and drops connections.
- Raising `proxy_read_timeout` to mask a slow backend instead of fixing the backend.
- Confusing `root` and `alias`, producing 404s on files that exist on disk.
- Raising `worker_connections` for "too many open files" without raising the fd limit.
- Diagnosing in a browser with a warm cache, so you debug a stale response.
- A cert file missing its intermediate chain — works in a browser (which caches CAs) but
  fails for API clients and `curl`.

## Production Tips

- Keep a symptom→cause runbook (this table) next to the on-call docs so triage is
  mechanical during an incident.
- Add `$upstream_status`, `$upstream_response_time`, and `$upstream_addr` to
  `log_format` so 502/504 root cause is in the log before you go looking (see
  [logging](16-logging.md)).
- Alert on 5xx rate and `$upstream_response_time`, not just "nginx is up" — nginx being
  alive while every upstream 502s is the failure mode that pages you at 3am.

## AI Review Checklist

- Is the error attributed to the right layer (nginx-generated vs relayed upstream)?
- For 502/504, was the upstream curled directly before touching nginx config?
- Is `client_max_body_size` scoped to the upload path, not raised globally?
- Is a 404 checked against `root`/`alias` and file permissions via `nginx -T`?
- Are TLS failures checked with the full chain and `openssl s_client`?
- Is "too many open files" fixed at the fd limit, not just `worker_connections`?
- Are upstream fields in the log format so future incidents self-diagnose?

## Related

- `knowledge/nginx/24-debugging.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/16-logging.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/25-production.md`
