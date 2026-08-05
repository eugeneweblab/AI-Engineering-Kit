---
id: docker/26-best-practices
topic: docker
slug: best-practices
title: "Docker Best Practices"
type: doc
order: 26
status: ready
tags: [docker, best-practices]
related: [docker/08-dockerfile, docker/18-security, docker/11-multi-stage-builds, docker/15-healthchecks, docker/100-common-antipatterns]
when_to_use: "Read before authoring or reviewing any Dockerfile or container run configuration."
---
# Docker Best Practices

## Purpose

This document collects the load-bearing rules for writing Dockerfiles and running
containers correctly: what to pin, what to exclude, how to run as a non-root user,
and how to structure an image so it is small, reproducible, and safe. It is the
distilled default an agent should follow unless a specific doc says otherwise.

It is a synthesis, not a replacement, for the detail docs: [Dockerfile](08-dockerfile.md),
[security](18-security.md), [multi-stage builds](11-multi-stage-builds.md), and
[image optimization](09-image-optimization.md). When this doc and a topic doc
appear to conflict, the topic doc wins.

## Why It Matters

Docker's defaults optimize for "works on my machine", not for production. Left
alone, they give you images that run as root, pull `latest` non-reproducibly, bake
in secrets, and grow without bound. Each of these is a production incident waiting
for a trigger. The practices here are the difference between an image you can
audit, reproduce, and trust and one that merely happens to run today. The cost of
ignoring them is paid later, under pressure, during an outage or a CVE response.

## Core Principles

- **Reproducible over convenient.** Pin base images by digest and dependencies by
  version. `latest` is a moving target that makes a green build unreproducible.
- **Least privilege by default.** Run as a non-root `USER`; add capabilities only
  when proven necessary. A container breakout inherits whatever the process had.
- **One concern per image.** A container should run one primary process. Bundling a
  DB, a cron, and an app in one image defeats scaling, health, and restart logic.
- **Build context is code.** What you `COPY` and what `.dockerignore` excludes is a
  security and performance decision, not an afterthought.
- **Immutable images, external config.** Bake the code; inject config and
  [secrets](14-secrets.md) at runtime. The same image must run in every
  environment.

## Best Practices

- Pin the base image by digest (`FROM node:22-slim@sha256:...`) so a rebuild
  produces the same bytes and cannot silently change under you.
- Use [multi-stage builds](11-multi-stage-builds.md) to keep compilers, dev
  dependencies, and secrets out of the final image.
- Create and switch to a non-root user with a fixed UID; make the app directory
  owned by it. Never leave the final `USER` as root.
- Maintain a `.dockerignore` that excludes `.git`, `node_modules`, local env files,
  and build output — for speed and to avoid leaking secrets into layers.
- Prefer the exec form of `CMD`/`ENTRYPOINT` (`["node", "server.js"]`) so signals
  reach PID 1 and the container shuts down cleanly.
- Add a [healthcheck](15-healthchecks.md) so orchestrators can tell "running" from
  "healthy".
- Never place secrets in `ENV`, build args, or `RUN` commands — they persist in
  image layers and history. Use [secret mounts](14-secrets.md) at build time and
  injected env/files at runtime.
- Set explicit resource [limits](17-resource-limits.md); an unbounded container can
  starve its neighbors.
- Combine related `RUN` steps and clean package caches in the same layer so the
  cleanup actually reduces image size.

## Examples

**Good Example** — pinned, non-root, minimal, signal-safe

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-slim@sha256:<digest> AS build   # pinned: reproducible builds
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

FROM node:22-slim@sha256:<digest>
WORKDIR /app
# Create an unprivileged user and own the app dir.
RUN useradd --uid 10001 --create-home app && chown -R app /app
COPY --from=build --chown=app /app/dist ./dist
COPY --from=build --chown=app /app/node_modules ./node_modules
USER app                                     # drop root before running
HEALTHCHECK CMD wget -qO- http://localhost:8080/healthz || exit 1
CMD ["node", "dist/server.js"]               # exec form: signals reach PID 1
```

**Bad Example** — root, unpinned, secret baked in, shell form

```dockerfile
FROM node:latest                             # unpinned: not reproducible
WORKDIR /app
COPY . .                                     # no .dockerignore → .git, secrets ship
RUN npm install
ENV API_KEY=sk_live_9f3c...                  # secret persists in every layer forever
# runs as root; no healthcheck; shell form swallows SIGTERM → slow, dirty shutdown
CMD npm start
```

## Common Mistakes

- Using `FROM ...:latest` and expecting reproducible builds.
- Leaving the container running as root because "it worked".
- Putting secrets in `ENV` or `--build-arg`, where they live in image history.
- Shell-form `CMD` that makes the shell PID 1, so `SIGTERM` never reaches the app
  and shutdown hangs until the kill timeout.
- No `.dockerignore`, leaking `.git` and local credentials into the image.
- One image doing many jobs, so you cannot scale, health-check, or restart any of
  them independently.
- Cleaning package caches in a *later* layer than the install, so the bytes are
  already committed and nothing shrinks.

## Production Tips

- Scan images in CI ([tooling](28-tooling.md)) and fail the build on high-severity,
  fixable CVEs.
- Generate an SBOM at build time so you can answer "are we affected?" the next time
  a CVE lands.
- Keep a golden base image per language, pinned and scanned, and rebuild downstream
  images when it updates.

## AI Review Checklist

- Is the base image pinned by digest (or at least an explicit version, never
  `latest`)?
- Does the final stage run as a non-root `USER`?
- Are build tools and dev dependencies excluded via [multi-stage](11-multi-stage-builds.md)?
- Is there a `.dockerignore` covering `.git`, deps, and env files?
- Are `CMD`/`ENTRYPOINT` in exec form so signals reach PID 1?
- Are secrets injected at runtime, never baked into `ENV` or build args?
- Is a [healthcheck](15-healthchecks.md) and resource
  [limits](17-resource-limits.md) defined?

## Related

- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/100-common-antipatterns.md`
