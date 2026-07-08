---
id: docker/25-performance
topic: docker
slug: performance
title: "Performance"
type: doc
order: 25
status: ready
tags: [docker, performance]
related: [docker/09-image-optimization, docker/10-buildkit, docker/17-resource-limits, docker/11-multi-stage-builds, docker/24-monitoring]
when_to_use: "Read when builds are slow, images are bloated, or containers run slower than the same process on the host."
---
# Performance

## Purpose

This document defines how to make Docker fast along the two axes that matter:
build time (how long from source to image) and runtime (how efficiently the
container executes). It is written so an agent can diagnose and fix a slow build
or a throttled container without guessing.

Performance here is distinct from [image optimization](09-image-optimization.md),
which is about size. Small images help performance (faster pulls, faster starts)
but a small image can still build slowly or run throttled. Treat build speed,
image size, and runtime efficiency as three related but separate targets.

## Why It Matters

Slow builds tax every developer and every CI run, compounding across a team all
day. Bloated or misconfigured containers cost real money in cloud spend and slow
every deploy through longer image pulls. And a container that hits a
[resource limit](17-resource-limits.md) does not fail loudly — the kernel
silently throttles CPU or OOM-kills the process, so the app just gets mysteriously
slow. Because these costs are continuous and hidden, performance is not a one-time
tune; it is a property you protect with every Dockerfile and run configuration.

## Core Principles

- **Order layers by change frequency.** Put stable steps (dependency install)
  before volatile ones (copying source) so the cache survives ordinary edits.
- **Cache is the cheapest speedup.** A build that reuses layers is 10-100x faster
  than one that rebuilds them. Protect the cache before optimizing anything else.
- **Match limits to reality.** A CPU limit below what the app needs causes CFS
  throttling; a memory limit below the working set causes OOM kills. Measure, then
  set.
- **Smaller ships faster.** Every megabyte is pulled on every node on every deploy.
  Runtime start time is dominated by image pull, not process boot.
- **Right base image, right job.** `alpine` is small but its musl libc and slow
  DNS can hurt some workloads; `slim` variants are often the better default.

## Best Practices

- Use [BuildKit](10-buildkit.md) (default in modern Docker) and cache mounts
  (`RUN --mount=type=cache`) for package managers so downloads persist across
  builds without bloating the final image.
- Structure the Dockerfile so `COPY` of dependency manifests and the install step
  come before `COPY` of application source. Editing app code should not invalidate
  the dependency layer.
- Use [multi-stage builds](11-multi-stage-builds.md) to keep compilers and build
  tools out of the final image — faster pulls, smaller attack surface.
- Add a well-scoped `.dockerignore` so the build context excludes `.git`,
  `node_modules`, and build artifacts. A fat context slows every build before the
  first instruction runs.
- Set CPU and memory [limits](17-resource-limits.md) from measured usage, then
  [monitor](24-monitoring.md) `container_cpu_cfs_throttled_seconds_total` to catch
  throttling.
- Prefer `--cache-from`/registry cache in CI so ephemeral runners reuse layers from
  a previous build.
- Pin base images by digest so a rebuild is reproducible and a cache hit is real,
  not a silent upstream change.

## Examples

**Good Example** — cache-friendly layer order and a cache mount

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-slim AS build

WORKDIR /app

# Copy only manifests first: this layer's cache survives every source edit.
COPY package.json package-lock.json ./
# Cache mount keeps the npm cache across builds without shipping it in the image.
RUN --mount=type=cache,target=/root/.npm \
    npm ci --no-audit --no-fund

# Source changes here do NOT bust the dependency layer above.
COPY . .
RUN npm run build

FROM node:22-slim                    # slim runtime, no build toolchain
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

**Bad Example** — cache-busting order, no cache mount, tools in final image

```dockerfile
FROM node:22                         # full image: ~1GB pulled every deploy

WORKDIR /app
COPY . .                             # any file change invalidates everything below
RUN npm install                      # re-downloads all deps on every source edit
RUN npm run build
# build toolchain, dev deps, and .git all ship to production and every node
CMD ["node", "dist/server.js"]
```

## Common Mistakes

- Copying the whole source tree before installing dependencies, so every edit
  triggers a full dependency reinstall.
- Missing or incomplete `.dockerignore`, sending hundreds of MB of context to the
  daemon on every build.
- Setting a CPU limit like `0.5` on a latency-sensitive service and then blaming
  the app for tail-latency caused by CFS throttling.
- Setting a memory limit below the app's working set, causing intermittent OOM
  kills that look like random crashes.
- Chasing image size with `alpine` and inheriting musl DNS/compat problems that
  cost more than the megabytes saved.
- Disabling BuildKit or not using cache in CI, so every pipeline rebuilds from
  scratch.

## Production Tips

- Measure before tuning: `docker build --progress=plain` shows which step is slow;
  `docker history` shows which layer is fat.
- Use a persistent registry cache in CI so cold runners still get warm caches.
- Profile the running container's actual CPU/memory over a representative load
  window, then set limits with headroom rather than guessing.
- Watch pull time in deploys — if it dominates, the win is in image size, not app
  code.

## AI Review Checklist

- Are dependency-install layers ordered before source `COPY` so the cache survives
  edits?
- Is a scoped `.dockerignore` present to keep the build context lean?
- Are build tools excluded from the final image via [multi-stage](11-multi-stage-builds.md)?
- Are BuildKit cache mounts or registry cache used for package managers?
- Are CPU/memory [limits](17-resource-limits.md) set from measured usage, not
  guessed?
- Is throttling/OOM [monitored](24-monitoring.md) so limit mistakes surface?
- Are base images pinned so cache hits are real and reproducible?

## Related

- `knowledge/docker/09-image-optimization.md`
- `knowledge/docker/10-buildkit.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/docker/24-monitoring.md`
