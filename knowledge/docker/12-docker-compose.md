---
id: docker/12-docker-compose
topic: docker
slug: docker-compose
title: "Docker Compose"
type: doc
order: 12
status: ready
tags: [docker, docker-compose]
related: [docker/13-environment-variables, docker/14-secrets, docker/15-healthchecks, docker/17-resource-limits, docker/07-networks]
when_to_use: "Read before writing or reviewing a compose.yaml that wires multiple containers together for local dev or single-host deployment."
---
# Docker Compose

## Purpose

This document defines how to describe a multi-container application declaratively
with Docker Compose: services, networks, volumes, dependencies, and startup order.
It is written so an agent can author or review a `compose.yaml` that is reproducible,
readable, and safe to run from a fresh checkout.

Compose is for a *single host* — one machine running a set of related containers. It
is the standard tool for local development and small single-node deployments. It is
not an orchestrator; for multi-node scheduling, failover, and rolling updates, see
[orchestration](23-orchestration.md).

## Why It Matters

The compose file is the executable contract for how the whole system fits together.
When it is correct, a new developer runs `docker compose up` and gets a working stack
in one command. When it is wrong — a hardcoded secret, an unpinned image, a missing
health gate — the failure is reproduced on every machine that runs it, and the file
becomes the canonical source of a bad pattern that spreads by copy-paste. A compose
file is read far more often than it is written; treat it as documentation that also
happens to run.

## Core Principles

- **Declare, do not script.** The file states the desired end state. If a service
  needs setup steps, put them in the image or an entrypoint, not in a README.
- **Pin every image to a specific tag or digest.** `latest` makes the stack
  non-reproducible; the same file yields different behavior on different days.
- **Depend on readiness, not on start.** `depends_on` only orders container starts.
  To wait until a dependency actually serves traffic, gate it on a healthcheck.
- **Keep secrets and environment out of the committed file.** Reference `.env` and
  `secrets`; never inline a password or API key into `compose.yaml`.
- **One concern per service.** A service is one process family (app, db, cache). Do
  not bundle unrelated processes behind a shell script in one container.

## Best Practices

- Name the file `compose.yaml` (the current canonical name) and omit the obsolete
  top-level `version:` key — the Compose Specification ignores it.
- Pin images: `postgres:16.4` or a digest, never `postgres` or `postgres:latest`,
  because unpinned tags break reproducibility and let a bad upstream push in.
- Use `depends_on` with `condition: service_healthy` so an app does not start
  querying a database that has not finished booting.
- Define explicit named `volumes` for state (databases, uploads). Data in the
  container layer is destroyed on `docker compose down`.
- Put configuration in `env_file: .env` and commit a `.env.example` with dummy
  values so the required keys are documented without leaking real ones.
- Set `restart: unless-stopped` for long-running services so a crash recovers, but
  a deliberate stop stays stopped.
- Bind-mount source in dev with a separate `compose.override.yaml`; keep the base
  file production-shaped so the two environments do not drift.
- Publish only the ports you need with `"127.0.0.1:8080:8080"` in dev to avoid
  exposing services on all interfaces.

## Examples

**Good Example** — pinned images, health-gated startup, named volume, external env

```yaml
# compose.yaml — no `version:` key; Compose Spec ignores it
services:
  db:
    image: postgres:16.4          # pinned tag → reproducible across machines
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password  # secret, not inline value
    secrets: [db_password]
    volumes:
      - db-data:/var/lib/postgresql/data                # state survives `down`
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 3s
      retries: 5

  app:
    image: myorg/app:1.4.2         # pinned; not `latest`
    restart: unless-stopped
    env_file: .env                 # config lives outside the committed file
    depends_on:
      db:
        condition: service_healthy # wait until db actually accepts connections
    ports:
      - "127.0.0.1:8080:8080"      # bound to loopback in dev, not 0.0.0.0

volumes:
  db-data:                          # named volume, explicitly declared

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

**Bad Example** — unpinned, secret inlined, start-order race, ephemeral data

```yaml
services:
  db:
    image: postgres                 # unpinned → different version every pull
    environment:
      POSTGRES_PASSWORD: hunter2     # secret committed into version control
    # no volume → all data lost on `docker compose down`

  app:
    image: myorg/app:latest          # `latest` is not a version
    depends_on:
      - db                           # only waits for START, not readiness
    ports:
      - "8080:8080"                  # exposed on every interface
```

## Common Mistakes

- Assuming `depends_on` waits for readiness — it waits only for the container to
  start, so the app races the database and fails intermittently.
- Using `latest` or unpinned tags, making the stack non-reproducible.
- Committing real secrets or `.env` files instead of a sanitized `.env.example`.
- Forgetting a named volume for stateful services, so `down` silently deletes data.
- Keeping the obsolete top-level `version:` key and mistaking it for the app version.
- Cramming dev-only bind mounts and overrides into the base file, so production
  and development configurations drift apart.

## Production Tips

- Use `docker compose config` in CI to validate and fully render the file (variable
  interpolation, merges) before it ever runs — it catches typos and missing vars.
- Keep the base file production-shaped and layer local changes in
  `compose.override.yaml`, which Compose merges automatically.
- Set resource limits (see [resource limits](17-resource-limits.md)) so one runaway
  service cannot starve the host.
- Prefer `docker compose up --wait`, which blocks until services are healthy and
  exits non-zero on failure — ideal for smoke tests.

## AI Review Checklist

- Is every `image` pinned to a specific tag or digest, never `latest`?
- Are cross-service dependencies gated on `condition: service_healthy`, not bare
  `depends_on`?
- Are secrets referenced via `secrets:` or `.env`, never inlined in the file?
- Does every stateful service have a named volume so `down` does not lose data?
- Is the obsolete top-level `version:` key removed?
- Are published ports scoped (loopback in dev) rather than exposed on all interfaces?
- Is `restart: unless-stopped` set on long-running services?

## Related

- `knowledge/docker/13-environment-variables.md`
- `knowledge/docker/14-secrets.md`
- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/07-networks.md`
