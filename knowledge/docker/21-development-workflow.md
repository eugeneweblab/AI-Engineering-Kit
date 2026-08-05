---
id: docker/21-development-workflow
topic: docker
slug: development-workflow
title: "Development Workflow"
type: doc
order: 21
status: ready
tags: [docker, development-workflow, prod, node_modules, depends_on, compose.yaml, compose.override.yaml, DB_PASSWORD]
related: [docker/12-docker-compose, docker/06-bind-mounts, docker/11-multi-stage-builds, docker/13-environment-variables, docker/22-production]
when_to_use: "Read when setting up Docker for local development — compose files, live reload, and dev/prod parity."
---
# Development Workflow

## Purpose

This document defines how to use Docker for day-to-day development: fast rebuilds, live
code reload, a reproducible local stack, and keeping the dev setup close enough to
production to catch bugs early. It is written so an agent can create a developer
experience that is fast without drifting from what actually ships.

The goal is a single `docker compose up` that gives every developer the same database,
cache, and services, with source changes reflected instantly — while the production image
stays lean and separate.

## Why It Matters

The two failure modes pull in opposite directions. A dev setup that rebuilds the whole
image on every keystroke is so slow developers abandon Docker and lose parity. A dev
setup that diverges too far from production — different base image, bind-mounted
`node_modules`, dev-only dependencies baked in — produces "works locally, breaks in prod"
bugs that surface at the worst time. A good workflow is fast *and* faithful: it optimizes
the inner loop while sharing a build definition with production.

## Core Principles

- **Optimize the inner loop, not the image.** In dev, mount source for instant reload; do
  not rebuild the image to see a code change.
- **One Dockerfile, staged.** Use multi-stage builds so `dev` and `prod` targets share a
  base and diverge only where they must. See [multi-stage builds](11-multi-stage-builds.md).
- **Dev/prod parity.** Same base image, same major dependency versions, same service
  topology. Differences you tolerate in dev become surprises in prod.
- **Configuration by environment, not by edit.** Switch behavior with env vars and
  compose overrides, never by hand-editing files inside the container.
- **Reproducible for everyone.** `docker compose up` on a clean checkout must produce a
  working stack with no undocumented host setup.

## Best Practices

- Use `compose.yaml` for the shared stack and `compose.override.yaml` for local-only
  concerns (bind mounts, exposed debug ports); Compose merges them automatically.
- Bind-mount source into the container for live reload, but keep dependency directories
  (`node_modules`, `.venv`) in a named volume or the image so host and container do not
  fight over platform-specific binaries. See [bind mounts](06-bind-mounts.md).
- Target a `dev` build stage that includes hot-reload tooling; the `prod` stage builds
  from the same base without it.
- Pin service dependencies (Postgres, Redis) to the same major versions you run in
  production, with named volumes for data persistence between runs.
- Use `depends_on` with `condition: service_healthy` so the app waits for its database
  to be ready, not merely started.
- Keep secrets and machine-specific values in a git-ignored `.env`; commit a
  `.env.example` documenting every key. See [environment variables](13-environment-variables.md).
- Leverage BuildKit cache mounts so dependency installs are cached across rebuilds.

## Examples

**Good Example** — staged Dockerfile, source-mounted dev, parity kept

```yaml
# compose.yaml — shared, prod-like topology
services:
  app:
    build: { context: ., target: dev }   # dev stage of the SAME Dockerfile
    env_file: .env
    depends_on:
      db: { condition: service_healthy }  # wait for readiness, not just start
  db:
    image: postgres:16                    # same major version as production
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
volumes: { pgdata: {} }
```

```yaml
# compose.override.yaml — local-only live reload
services:
  app:
    volumes:
      - ./src:/app/src         # edits reflect instantly, no rebuild
      - /app/node_modules      # keep container's deps; don't shadow with host's
    command: npm run dev       # hot-reload server, dev stage only
```

**Bad Example** — rebuild on every change, dev/prod drift

```yaml
services:
  app:
    build: .                   # no target: dev tools leak into the prod image
    image: node:18             # dev on 18, prod on 22 -> parity broken
    # No bind mount: every code change requires a full `docker compose build`,
    # so the inner loop is minutes long and developers stop using compose.
    environment:
      - DB_PASSWORD=devpass    # secret hardcoded in a committed file
```

## Common Mistakes

- Rebuilding the whole image to see a code change instead of bind-mounting source,
  making the inner loop unbearably slow.
- Bind-mounting over `node_modules`/`.venv`, so host-built binaries break inside the
  container (or vice versa).
- Different base image or dependency versions in dev vs. prod, hiding bugs until deploy.
- One giant Dockerfile with dev tools baked in, shipping `nodemon` and compilers to prod.
- Undocumented host prerequisites, so a teammate's `compose up` fails on a clean machine.
- `depends_on` without a health condition, so the app starts before the database accepts
  connections and crashes on boot.

## Production Tips

- Build the `prod` target in CI from the exact same Dockerfile developers use, so the
  image is battle-tested locally.
- Run the production image locally (`target: prod`, no bind mount) before release to catch
  parity issues the dev stage masks.
- Keep the dev stack's data in named volumes so `compose down` does not wipe local state
  unless a developer explicitly asks (`down -v`).

## AI Review Checklist

- Is there one multi-stage Dockerfile with distinct `dev` and `prod` targets?
- Does dev use bind mounts for live reload instead of rebuilding on every change?
- Are dependency directories protected from being shadowed by the host mount?
- Do dev and prod share base image and major dependency versions (parity)?
- Are secrets in a git-ignored `.env` with a committed `.env.example`?
- Does `docker compose up` produce a working stack on a clean checkout, with health-gated
  dependencies?

## Related

- `knowledge/docker/12-docker-compose.md`
- `knowledge/docker/06-bind-mounts.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/docker/13-environment-variables.md`
- `knowledge/docker/22-production.md`
