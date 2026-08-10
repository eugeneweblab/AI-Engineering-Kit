---
id: docker/05-volumes
topic: docker
slug: volumes
title: "Docker Volumes"
type: doc
order: 5
status: ready
tags: [docker, volumes, POSTGRES_PASSWORD_FILE, POSTGRES_PASSWORD, outlive, databases, uploads]
related: [docker/04-containers, docker/06-bind-mounts, docker/12-docker-compose, docker/18-security, docker/22-production]
when_to_use: "Read before persisting any data that must outlive a container — databases, uploads, or state."
---
# Docker Volumes

## Purpose

This document defines how to persist data with Docker volumes: what a volume is, how
it differs from a [bind mount](06-bind-mounts.md) and the container's writable layer,
and how to use, back up, and secure volumes. Volumes are the answer to the single
most damaging Docker mistake: losing data when a container is recreated.

A **volume** is Docker-managed storage that lives independently of any container.
The container writes to a mount path; the data lives in the volume and survives
`docker rm`. This is distinct from a bind mount, which maps a host directory into the
container.

## Why It Matters

Containers are disposable ([04-containers](04-containers.md)); their writable layer is
deleted with them. Any data written there — a database's files, user uploads, a
cache you cannot rebuild — is gone on the next deploy, crash, or `docker rm`. This
failure is silent until the day it isn't: everything works in testing, then a
routine redeploy wipes production data. Volumes make persistence explicit and are
the only correct place for stateful data in a containerized system.

## Core Principles

- **Persistence must be explicit.** If data matters, put it in a named volume or an
  external managed service. The container layer is never durable storage.
- **Volumes decouple data lifecycle from container lifecycle.** Recreate the
  container freely; the volume and its data remain.
- **Named volumes for portability, bind mounts for local dev.** Volumes are
  Docker-managed and host-agnostic; bind mounts couple you to a host path and its
  permissions. See [06-bind-mounts](06-bind-mounts.md).
- **A volume is not a backup.** It survives container deletion, not disk failure or
  a bad migration. Back it up separately.
- **Volumes have permissions and are attack surface.** A volume shared with a
  root-writable container, or holding secrets, must be scoped and secured.

## Best Practices

- Use **named volumes** for stateful services (databases, message queues, object
  stores) so data is durable and the mount is declarative.
- Declare volumes in [Compose](12-docker-compose.md) under a top-level `volumes:` key
  and reference them by name, so the persistence contract is versioned in the repo.
- Mount only the specific path that needs to persist (e.g. `/var/lib/postgresql/data`),
  not the whole filesystem, to keep the container otherwise immutable.
- Back up volumes on a schedule by running a throwaway container that tars the volume
  to external storage; test restores.
- For read-only reference data, mount the volume `:ro` so the container cannot alter
  it — least privilege for data.
- Prefer a managed external datastore in production when available; a self-hosted
  database on a single-node volume is a single point of failure. See
  [22-production](22-production.md).
- Clean up unused volumes deliberately (`docker volume prune`) — but never on a host
  with live data you have not backed up.

## Examples

**Good Example** — named volume, scoped mount, declarative in Compose

```yaml
services:
  db:
    image: postgres:16
    volumes:
      # Only the data dir is persisted; the rest of the container stays immutable.
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password

volumes:
  pgdata:            # named, Docker-managed → survives `docker compose down`
```

```bash
# Back up the named volume by mounting it read-only into a throwaway container.
docker run --rm -v pgdata:/data:ro -v "$PWD":/backup alpine \
  tar czf /backup/pgdata-$(date +%F).tar.gz -C /data .
```

**Bad Example** — state on the container layer, data lost on recreate

```yaml
services:
  db:
    image: postgres:16
    # No volume at all. Postgres writes to the container's writable layer.
    # `docker compose down` (or any redeploy) deletes the container — and every
    # row in the database with it. Works in dev, wipes prod.
    environment:
      POSTGRES_PASSWORD: hardcoded-in-plaintext   # also a secrets antipattern
```

## Common Mistakes

- Running a database with no volume, so data lives on the ephemeral layer and
  disappears on the next `docker rm` / redeploy.
- Mounting a bind path in production for portable state, coupling the deploy to a
  specific host directory and its uid/gid permissions.
- Assuming a volume is a backup and skipping real backups, then losing everything to
  a disk failure or bad migration.
- Mounting reference data writable when it should be `:ro`, letting the container
  corrupt it.
- Running `docker volume prune` or `docker system prune --volumes` on a host with
  live, un-backed-up data.
- Sharing one volume across containers without considering concurrent-write and
  permission conflicts.

## Production Tips

- Store volume backups off-host (object storage) and verify restores regularly — an
  untested backup is not a backup.
- Match the volume's directory ownership to the non-root user the container runs as,
  or the process cannot write to it.
- Consider a volume driver that supports snapshots/replication for critical data, or
  offload to a managed database entirely.
- Document, per service, exactly which paths are persisted so the persistence
  contract is reviewable.

## AI Review Checklist

- Is all data that must survive a restart on a named volume or external service?
- Are volumes declared by name (in Compose) rather than implied by container state?
- Is the mount scoped to the specific data path, not the whole filesystem?
- Is a backup-and-restore strategy defined for critical volumes?
- Are read-only mounts (`:ro`) used for data the container should not modify?
- Do volume permissions match the container's non-root user?

## Related

- `knowledge/docker/04-containers.md`
- `knowledge/docker/06-bind-mounts.md`
- `knowledge/docker/12-docker-compose.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/22-production.md`
