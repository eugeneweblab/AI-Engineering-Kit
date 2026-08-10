---
id: docker/08-dockerfile
topic: docker
slug: dockerfile
title: "Dockerfile"
type: doc
order: 8
status: ready
tags: [docker, dockerfile, CMD, ENTRYPOINT, EXPOSE, ARG, COPY, HEALTHCHECK, base, concerns, order]
related: [docker/03-images, docker/11-multi-stage-builds, docker/09-image-optimization, docker/10-buildkit, docker/18-security]
when_to_use: "Read before writing or reviewing any Dockerfile — the instruction order, base image, and user are all correctness concerns."
---
# Dockerfile

## Purpose

This document defines how to write a correct, cacheable, secure Dockerfile: choosing a
base image, ordering instructions for layer caching, running as a non-root user, and
declaring the runtime contract (`ENTRYPOINT`, `CMD`, `EXPOSE`, `HEALTHCHECK`). It is the
foundation for [image optimization](09-image-optimization.md) and
[multi-stage builds](11-multi-stage-builds.md).

A Dockerfile is a build *program*, not a config file. Each instruction produces a layer,
and the order of instructions determines both cache reuse and the final image contents.

## Why It Matters

The Dockerfile fixes three properties that are expensive to change later: how big the
image is, how fast it rebuilds, and what privileges it runs with. A careless instruction
order turns a two-second rebuild into a five-minute one by invalidating the dependency
cache on every source edit. A `latest` base tag makes builds non-reproducible. Running as
root — the default — means a container escape is a host compromise. These are decided in a
dozen lines, and every downstream build inherits them.

## Core Principles

- **Order from least to most frequently changing.** Copy and install dependencies before
  copying source, so a code edit does not invalidate the dependency-install layer.
- **Each `RUN` is a layer; chain related commands.** A file deleted in a later layer still
  occupies space in the earlier one. Clean up within the same `RUN`.
- **Pin the base image.** Use a specific tag or digest (`python:3.12-slim`,
  `@sha256:...`), never `latest`, so builds are reproducible.
- **Run as a non-root user.** The default is root; create and switch to an unprivileged
  user before the runtime `CMD`.
- **Prefer `COPY` over `ADD`.** `ADD` also fetches URLs and auto-extracts archives —
  surprising behavior. Use `COPY`; reach for `ADD` only for deliberate tar extraction.
- **`ENTRYPOINT` + `CMD` define the runtime contract** — use exec form so signals reach
  the process (see below).

## Best Practices

- Start `FROM` a slim, pinned base (`-slim`, `-alpine`, or `distroless`) to shrink attack
  surface and size; see [Image Optimization](09-image-optimization.md).
- Add a `.dockerignore` that excludes `.git`, `node_modules`, build output, and secrets,
  so the build context stays small and secrets never enter the image.
- Combine package installs and cache cleanup in one `RUN` (`apt-get update && install &&
  rm -rf /var/lib/apt/lists/*`) to avoid a stale-cache-plus-bloat layer.
- Copy only the dependency manifest first, install, then copy the rest of the source —
  this keeps the install layer cached across code changes.
- Use the **exec form** (`CMD ["node", "server.js"]`), not the shell form
  (`CMD node server.js`). Exec form makes your process PID 1 so it receives `SIGTERM` and
  shuts down gracefully; shell form wraps it in `/bin/sh` that swallows signals.
- Declare a non-root `USER`, an `EXPOSE` for documentation, and a `HEALTHCHECK` so the
  runtime knows the app's port and liveness.
- Never bake secrets into layers with `ENV` or `ARG`; use BuildKit secret mounts
  (see [BuildKit](10-buildkit.md)) or runtime [Secrets](14-secrets.md).

## Examples

**Good Example** — cache-friendly order, pinned base, non-root, exec form

```dockerfile
# Pinned, slim base → reproducible and small.
FROM node:24-slim

WORKDIR /app

# Copy ONLY the manifest first so `npm ci` stays cached when source changes.
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Now copy source; edits here reuse the cached dependency layer above.
COPY . .

# Create and switch to an unprivileged user before runtime.
RUN useradd --system --uid 10001 appuser
USER appuser

EXPOSE 3000
HEALTHCHECK CMD node healthcheck.js || exit 1
# Exec form → app is PID 1 and receives SIGTERM for graceful shutdown.
CMD ["node", "server.js"]
```

**Bad Example** — cache-busting order, floating tag, root, shell form

```dockerfile
# unpinned → not reproducible, silently changes
FROM node:latest

WORKDIR /app
# copies source first: any edit busts the install below
COPY . .
RUN npm install             # re-runs on every code change; installs devDeps too

# No USER → runs as root; a container escape is a host compromise.
# Shell form → node runs under /bin/sh which does not forward SIGTERM,
# so `docker stop` waits 10s then SIGKILLs, losing in-flight requests.
CMD npm start
```

## Common Mistakes

- Copying the whole source before installing dependencies, so every edit rebuilds deps.
- Using `FROM ...:latest`, making builds non-reproducible and prone to surprise breakage.
- Running `apt-get install` and the cache cleanup in separate `RUN`s, so the cleanup saves
  nothing (the files persist in the earlier layer).
- Leaving `USER` as root.
- Shell-form `CMD`/`ENTRYPOINT`, which breaks signal handling and graceful shutdown.
- Using `ADD` for a local copy and inheriting its URL-fetch / auto-extract behavior.
- No `.dockerignore`, so `.git` and secrets bloat the context and leak into the image.

## Production Tips

- Pin to a digest (`FROM image@sha256:...`) for the strongest reproducibility guarantee.
- Enable BuildKit and add `--mount=type=cache` for package managers to speed CI without
  bloating layers; see [BuildKit](10-buildkit.md).
- Scan the built image for CVEs in CI (`docker scout`, Trivy) and fail on high severity.
- Graduate to [multi-stage builds](11-multi-stage-builds.md) so build tools never ship in
  the runtime image.

## AI Review Checklist

- Is the base image pinned to a specific tag or digest (not `latest`)?
- Are dependencies installed before source is copied, preserving the cache?
- Are package installs and cleanup combined in a single `RUN`?
- Does the image declare and switch to a non-root `USER`?
- Are `ENTRYPOINT`/`CMD` in exec form so signals reach the process?
- Is there a `.dockerignore` excluding VCS, build output, and secrets?
- Are secrets kept out of `ENV`/`ARG` and image layers?

## Related

- `knowledge/docker/03-images.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/docker/09-image-optimization.md`
- `knowledge/docker/10-buildkit.md`
- `knowledge/docker/18-security.md`
