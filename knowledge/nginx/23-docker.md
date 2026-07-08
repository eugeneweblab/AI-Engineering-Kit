---
id: nginx/23-docker
topic: nginx
slug: docker
title: "Docker"
type: doc
order: 23
status: ready
tags: [nginx, docker]
related: [nginx/19-proxying-applications, nginx/05-reverse-proxy, nginx/12-ssl-tls, nginx/16-logging, nginx/25-production]
when_to_use: "Read before building an nginx container image or wiring nginx into a docker-compose or Kubernetes deployment."
---
# Docker

## Purpose

This document defines how to run nginx in a container correctly: how to build the image,
how to get config and TLS certs into it, how to resolve backend service names, and how to
log and reload without fighting the container lifecycle. Running nginx in Docker changes
several defaults — DNS resolution, log destinations, signal handling — and each one has a
specific containerized answer.

The proxying, TLS, and performance rules from the rest of this topic all still apply; this
doc is about the container-specific traps that make an otherwise-correct config fail inside
Docker, plus the image hygiene that keeps it small and secure.

## Why It Matters

nginx configs that work on a host break subtly in a container. `proxy_pass http://api;`
resolves the backend once at startup — fine on a static host, broken in Docker where a
service restart gives it a new IP and nginx keeps sending traffic to the dead one. Logs
written to `/var/log/nginx/access.log` vanish because Docker collects `stdout`/`stderr`,
not files inside the container. A `docker stop` sends `SIGTERM`, which nginx interprets as
a *fast, connection-dropping* shutdown rather than a graceful one. Each of these is a
container-specific default, not a bug — and each produces an outage that looks like an
application problem.

## Core Principles

- **Resolve backends at request time, not startup.** In dynamic environments, use a
  variable in `proxy_pass` plus a `resolver` so nginx re-resolves the service name instead
  of caching one IP forever.
- **Log to stdout/stderr.** The official image already symlinks the logs to Docker's
  streams; keep it that way so `docker logs` and the platform's log pipeline see them.
- **Config and secrets come from outside the image.** Bake app-agnostic defaults into the
  image; inject environment-specific config and TLS certs via mounts, configmaps, or
  templated entrypoints. Never bake a private key into a layer.
- **Handle SIGTERM gracefully.** Ensure the orchestrator's stop signal reaches nginx as
  `SIGQUIT` (graceful) or give it time; a bare `SIGTERM` drops in-flight connections.
- **Keep the image minimal and unprivileged.** Start from the official pinned `nginx`
  image, add only what you need, and prefer the `nginx-unprivileged` variant so the process
  does not run as root.

## Best Practices

- Base on a pinned official tag (`nginx:1.27-alpine`), not `latest`, so builds are
  reproducible and you control upgrades.
- Mount config read-only: `-v ./nginx.conf:/etc/nginx/conf.d/default.conf:ro`, or copy it
  in at build time for immutable images. Never edit config inside a running container.
- For dynamic backends, set `resolver 127.0.0.11 valid=10s;` (Docker's embedded DNS) and
  proxy through a variable so the name is re-resolved.
- Use the image's `/docker-entrypoint.d/` template mechanism (`envsubst` on `*.template`
  files) to inject environment variables at container start instead of hardcoding.
- Run TLS termination with certs mounted from a secret/volume, never copied into an image
  layer where they persist in history.
- Add a `HEALTHCHECK` (or Kubernetes readiness probe) hitting a lightweight `location` so
  the orchestrator knows when nginx is actually ready.
- Set `stopSignal`/`STOPSIGNAL SIGQUIT` so orchestrated shutdown drains connections.

## Examples

**Good Example** — pinned base, runtime DNS, stdout logs, graceful stop

```dockerfile
FROM nginx:1.27-alpine            # pinned, minimal, reproducible
COPY default.conf.template /etc/nginx/templates/   # envsubst'd at container start
STOPSIGNAL SIGQUIT                 # graceful drain on docker stop, not a hard drop
HEALTHCHECK CMD wget -qO- http://localhost/healthz || exit 1
# no certs, no secrets baked in — they are mounted at runtime
```

```nginx
# default.conf.template — resolved at request time so a restarted backend is picked up
resolver 127.0.0.11 valid=10s;     # Docker's embedded DNS, short TTL

server {
    listen 80;

    location / {
        set $upstream http://api:3000;   # variable forces per-request re-resolution
        proxy_pass $upstream;            # a new backend IP is picked up within 10s
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location = /healthz { return 200 "ok\n"; }  # probe target
}
```

**Bad Example** — cached IP, lost logs, secrets in the image

```dockerfile
FROM nginx:latest                  # unpinned: silent upgrades break builds
COPY tls/privkey.pem /etc/nginx/certs/   # secret baked into a layer, kept in image history
COPY app.log /var/log/nginx/       # writing to a file Docker never collects
```

```nginx
server {
    location / {
        proxy_pass http://api:3000;   # literal name resolved ONCE at startup
        # api restarts → new IP → nginx keeps hitting the dead one until reload → 502s
    }
    access_log /var/log/nginx/access.log;  # file inside container, invisible to `docker logs`
}
```

## Common Mistakes

- Using a literal service name in `proxy_pass` (resolved once at startup), so a restarted
  backend yields persistent 502s until nginx is reloaded.
- Writing logs to files inside the container, so `docker logs` and the platform's log
  aggregation see nothing.
- Baking TLS keys or config secrets into image layers, where they persist in history even
  after a later `rm`.
- Pinning to `nginx:latest`, making builds non-reproducible and upgrades uncontrolled.
- Editing config inside a running container (`docker exec`), losing the change on the next
  redeploy.
- Ignoring the stop signal, so `docker stop` / pod eviction drops in-flight requests.
- Running as root when the `nginx-unprivileged` image would drop the privilege.

## Production Tips

- In Kubernetes, prefer an Ingress controller or a `resolver` pointing at the cluster DNS;
  the same per-request-resolution rule applies to `Service` names.
- Send access logs as JSON to stdout (see [logging](16-logging.md)) so the platform's
  pipeline can parse them without a custom parser.
- Give nginx a `terminationGracePeriodSeconds` (K8s) or `stop_grace_period` (compose)
  longer than your longest request, so `SIGQUIT` can drain cleanly.
- Keep a separate lightweight `location` for readiness vs liveness so a busy backend does
  not fail the liveness probe and trigger a restart loop.
- Reload config with `nginx -s reload` via a sidecar or rolling redeploy — do not `kill -HUP`
  a PID you assume; in a container nginx is usually PID 1.

## AI Review Checklist

- Is the base image a pinned official tag, not `latest`?
- Do dynamic backends use a `resolver` plus a variable in `proxy_pass` for per-request resolution?
- Do logs go to stdout/stderr rather than files inside the container?
- Are TLS certs and secrets mounted at runtime, never copied into image layers?
- Is config injected via mount or template, not edited in a running container?
- Is the stop signal `SIGQUIT` (or grace period set) so shutdown drains connections?
- Is there a health/readiness endpoint, and does the process avoid running as root?

## Related

- `knowledge/nginx/19-proxying-applications.md`
- `knowledge/nginx/05-reverse-proxy.md`
- `knowledge/nginx/12-ssl-tls.md`
- `knowledge/nginx/16-logging.md`
- `knowledge/nginx/25-production.md`
