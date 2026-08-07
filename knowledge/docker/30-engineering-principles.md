---
id: docker/30-engineering-principles
topic: docker
slug: engineering-principles
title: "Docker Engineering Principles"
type: doc
order: 30
status: ready
tags: [docker, engineering-principles, "@sha", SIGTERM, Dockerfile, compose, tmpfs, EXPOSE]
related: [docker/08-dockerfile, docker/11-multi-stage-builds, docker/18-security, docker/22-production, docker/26-best-practices]
when_to_use: "Read before writing a Dockerfile or shaping how an app is containerized, to internalize the reasoning behind the rules."
---
# Docker Engineering Principles

## Purpose

This document defines the durable engineering principles behind well-built container
images and running containers. The other docs in this topic give specific rules
(a `Dockerfile` instruction, a `compose` field); this one gives the *reasoning* those
rules descend from, so an agent can make a correct call when no rule covers the case.

A container is not a lightweight VM. It is a single process tree sharing the host
kernel, built from an immutable, layered, content-addressed filesystem. Every principle
here follows from that fact. Get the mental model right and the specific rules become
obvious rather than memorized.

## Why It Matters

The Dockerfile is executable infrastructure: it is built once and run thousands of
times, unchanged, across laptops, CI, and production. A sloppy image is not a local
annoyance — it ships a 1.2 GB attack surface, a root process, and irreproducible builds
to every environment at once. Conversely, the discipline compounds: a lean, pinned,
non-root image is faster to pull, cheaper to store, safer to run, and trivial to reason
about during an incident. Because images are the unit you deploy, their quality *is*
your deployment quality.

## Core Principles

- **An image is a build artifact, not a machine.** Bake code and dependencies in at
  build time; inject only configuration at run time. If you `apt-get install` or
  `git pull` when the container starts, you have built the wrong thing.
- **Reproducibility over convenience.** Pin base images by digest and pin dependency
  versions. `FROM node:latest` builds a different image tomorrow — that is a bug, not a
  feature.
- **One concern per container.** A container should run one primary process. Multiple
  services in one image break independent scaling, logging, and lifecycle management.
- **Least privilege by default.** Run as a non-root user, drop capabilities, and mount
  the root filesystem read-only. A container that never needed root cannot be escalated
  to root.
- **Smaller is safer and faster.** Every package you do not install is a CVE you cannot
  ship. Minimize layers, use multi-stage builds, and prefer minimal bases.
- **Treat containers as cattle: immutable and disposable.** Persist state in volumes or
  external stores, never in the container's writable layer. Any container must be
  killable and replaceable at any moment with no data loss.

## Best Practices

- Order `Dockerfile` instructions from least- to most-frequently-changing so the layer
  cache survives code edits (dependencies before source). See
  [image-optimization](09-image-optimization.md).
- Use [multi-stage builds](11-multi-stage-builds.md) to keep compilers, dev headers, and
  test tooling out of the final image.
- Pin the base image by digest (`FROM node:22.11-slim@sha256:...`), not a floating tag,
  so rebuilds are byte-reproducible.
- Add a `.dockerignore` before your first build to keep `.git`, `node_modules`, and
  secrets out of the build context.
- Declare a non-root `USER`, an explicit `EXPOSE`, and a `HEALTHCHECK` in every image
  meant to run a service.
- Make the container log to stdout/stderr and read config from environment/secrets, per
  the twelve-factor model — never write logs to files inside the container.
- Handle `SIGTERM` in the entrypoint (use `exec` form, PID 1 forwarding) so the process
  shuts down gracefully instead of being killed after the grace period.

## Examples

**Good Example** — pinned, staged, non-root, cache-friendly

```dockerfile
# Pinned base by digest → reproducible, auditable builds
FROM node:22.11-slim@sha256:1a2b3c... AS build
WORKDIR /app
# Copy manifests first so `npm ci` is cached until deps actually change
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Final stage carries only runtime artifacts — no compilers, no dev deps
FROM node:22.11-slim@sha256:1a2b3c...
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
# least privilege: never run as root
USER node
EXPOSE 3000
HEALTHCHECK CMD node dist/health.js || exit 1
# exec form → PID 1 gets SIGTERM
ENTRYPOINT ["node", "dist/server.js"]
```

**Bad Example** — floating base, root, mutable, un-cacheable

```dockerfile
# non-reproducible: "latest" drifts every rebuild
FROM node:latest
WORKDIR /app
# any code edit busts the cache for the install below
COPY . .
RUN npm install               # dev deps + compilers shipped to production
# no USER → runs as root; no HEALTHCHECK; shell-form CMD swallows SIGTERM
CMD npm start
```

## Common Mistakes

- Using `latest` or an unpinned tag as the base, making builds non-reproducible.
- Copying the whole context before installing dependencies, destroying layer caching.
- Running as root because "it works" — until a compromised process owns the host.
- Baking secrets or environment-specific config into image layers (they persist and
  leak; see [secrets](14-secrets.md)).
- Installing debug tools, shells, or `curl` "just in case" and shipping them to prod.
- Writing state or logs to the container filesystem, so replacing the container loses
  data.
- Using shell-form `CMD`/`ENTRYPOINT`, so PID 1 is `/bin/sh` and never receives
  `SIGTERM`.

## Production Tips

- Scan every image in CI (Trivy, Grype) and fail the build on fixable HIGH/CRITICAL CVEs.
- Generate and store an SBOM per image so you can answer "are we affected?" the day a
  CVE drops.
- Set `--read-only` with explicit `tmpfs` mounts for the few paths that must be writable.
- Tag images with the immutable git SHA, not just `latest`, so a rollback is a precise,
  reproducible action.

## AI Review Checklist

- Is the base image pinned by digest rather than a floating tag?
- Are build-time tools excluded from the final image via multi-stage builds?
- Does the image declare a non-root `USER`?
- Are dependency install steps ordered before source copy for cache reuse?
- Is all config/secrets injected at run time, with nothing sensitive baked into layers?
- Does the entrypoint use exec form so PID 1 receives `SIGTERM`?
- Is there a `.dockerignore` excluding `.git`, secrets, and local artifacts?

## Related

- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/26-best-practices.md`
