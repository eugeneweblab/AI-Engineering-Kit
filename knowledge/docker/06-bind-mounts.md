---
id: docker/06-bind-mounts
topic: docker
slug: bind-mounts
title: "Bind Mounts"
type: doc
order: 6
status: ready
tags: [docker, bind-mounts]
related: [docker/05-volumes, docker/04-containers, docker/21-development-workflow, docker/14-secrets, docker/18-security]
when_to_use: "Read before mounting host files or directories into a container for local development, config injection, or debugging."
---
# Bind Mounts

## Purpose

This document defines how to mount a path from the host filesystem directly into a
container using a **bind mount**. It covers when to reach for a bind mount versus a
[volume](05-volumes.md), how to mount safely, and the pitfalls that make bind mounts a
frequent source of "works on my machine" bugs.

A bind mount maps an *exact host path* into the container. The container reads and
writes the real files on the host — there is no copy and no isolation. That directness
is the whole point, and also the whole danger.

## Why It Matters

A bind mount punches a hole between the host and the container. Anything the container
writes lands on the host immediately; anything on the host is visible to the container,
including files you did not intend to share. Get the source path wrong and you either
mount nothing (an empty directory silently appears) or mount your entire home directory
into an untrusted image. Because bind mounts depend on absolute host paths, they make a
compose file non-portable and couple your build to one developer's layout. Used well,
they give a tight edit-reload loop; used carelessly, they leak secrets and corrupt data.

## Core Principles

- **Bind mounts are for development and host integration, not portable state.** For data
  a container owns (databases, uploads), use a named [volume](05-volumes.md) instead — it
  is managed by Docker and portable across hosts.
- **The source path is a host path, and Docker does not create it.** A missing source is
  treated as an empty directory (or an error, depending on syntax), not a warning.
- **Mounts overlay, they do not merge.** Mounting over a directory hides whatever the
  image shipped there. `node_modules` baked into the image disappears if you mount the
  project root over it.
- **Mount the least you need, read-only by default.** A container that only reads config
  should never be able to write it back.
- **Bind mounts inherit host permissions and ownership.** UID/GID mismatches between host
  and container cause "permission denied" that no chmod inside the container can fix.

## Best Practices

- Prefer the explicit `--mount` syntax over the terse `-v` form. `--mount` fails loudly
  on a missing source; `-v` silently creates an empty directory and mounts that.
- Add `,readonly` (or `:ro`) to every mount the container does not need to write. This is
  the cheapest way to stop a compromised or buggy container from altering host files.
- Use relative paths anchored to the compose file (`./src`, not `/Users/me/app/src`) so
  the setup is portable across machines.
- For dependency directories that must stay image-owned, mount an anonymous volume over
  them (e.g. mount `./` then `/app/node_modules`) so the host mount does not clobber them.
- Never bind-mount the Docker socket (`/var/run/docker.sock`) into an application
  container — it grants root-equivalent control of the host. See [Security](18-security.md).
- On macOS and Windows, expect I/O overhead through the VM boundary; use `:cached` /
  `:delegated` consistency hints or scope mounts narrowly to keep builds fast.

## Examples

**Good Example** — explicit, scoped, read-only where possible

```yaml
# docker-compose.yml — relative paths, config mounted read-only,
# deps kept image-owned via an anonymous volume over the host mount.
services:
  web:
    build: .
    volumes:
      - type: bind
        source: ./src          # relative to the compose file → portable
        target: /app/src
      - type: bind
        source: ./nginx.conf   # config the app only reads
        target: /etc/app/nginx.conf
        read_only: true        # container cannot rewrite host config
      - type: volume
        target: /app/node_modules  # anonymous volume shields image-installed deps
```

**Bad Example** — absolute path, writable, clobbers dependencies

```yaml
services:
  web:
    build: .
    volumes:
      # Absolute host path: breaks on every other machine.
      - /Users/alice/projects/app:/app
      # Mounting the project root over /app hides /app/node_modules from the image,
      # so the container starts with no installed dependencies and crashes on import.
      # Everything is writable, so a bug in the app can overwrite source on the host.
```

## Common Mistakes

- Using `-v ./missing/path:/data` and getting a silently created empty directory instead
  of the files you expected.
- Mounting the project root and wondering why `node_modules`, `vendor`, or `target`
  vanished — the mount hid the image's copy.
- Committing absolute host paths into a shared compose file, breaking every teammate.
- Leaving mounts writable, so the container edits or deletes host source and config.
- Bind-mounting the Docker socket "for convenience," handing the container root on the host.
- Blaming the app for "permission denied" that is actually a host/container UID mismatch.

## Production Tips

- Avoid bind mounts in production. They tie a container to a specific host path and
  filesystem, defeating scheduling and portability; use volumes or config/secret stores.
- If a production config must come from the host, mount it read-only and treat the file
  as immutable infrastructure managed by your deployment tooling.
- For secrets, do not bind-mount plaintext files — use [Secrets](14-secrets.md) or a
  secrets manager so values are not left readable on disk.

## AI Review Checklist

- Is this data the container *owns*? If so, should it be a [volume](05-volumes.md) instead?
- Are source paths relative to the compose file rather than absolute host paths?
- Is every mount that only needs reads marked `read_only` / `:ro`?
- Does a root mount accidentally hide image-installed dependencies (`node_modules`, etc.)?
- Is the Docker socket being bind-mounted into an application container? (It must not be.)
- Are any bind mounts carrying secrets that belong in [Secrets](14-secrets.md)?

## Related

- `knowledge/docker/05-volumes.md`
- `knowledge/docker/04-containers.md`
- `knowledge/docker/21-development-workflow.md`
- `knowledge/docker/14-secrets.md`
- `knowledge/docker/18-security.md`
