---
id: docker/09-image-optimization
topic: docker
slug: image-optimization
title: "Image Optimization"
type: doc
order: 9
status: ready
tags: [docker, image-optimization, distroless, node_modules, dive, ubuntu]
related: [docker/08-dockerfile, docker/11-multi-stage-builds, docker/10-buildkit, docker/03-images, docker/18-security]
when_to_use: "Read when an image is too large, slow to pull, or carries needless attack surface, and you need to shrink it safely."
---
# Image Optimization

## Purpose

This document defines how to make images small, fast to pull, and cheap to rebuild
*without* breaking the app: choosing minimal bases, trimming layers, ordering for cache
reuse, and using a `.dockerignore`. It builds on the [Dockerfile](08-dockerfile.md)
fundamentals and pairs with [multi-stage builds](11-multi-stage-builds.md).

Optimization is not a vanity metric. Image size is pull time on every deploy and scale-up,
disk on every node, and attack surface in every CVE scan. Smaller is faster *and* safer.

## Why It Matters

A 1.2 GB image and a 90 MB image run the same code, but the large one costs minutes per
deploy across a fleet, fills registry and node disk, and ships hundreds of packages you
never call — each a potential CVE. Autoscaling amplifies the cost: every new replica pulls
the image before it can serve traffic, so bloat directly slows your response to a spike.
The fixes are mechanical and low-risk, which is why an unoptimized image is usually a sign
nobody looked, not a considered trade-off.

## Core Principles

- **Every byte in the image is attack surface and pull time.** Ship only what runs in
  production — not compilers, headers, package caches, tests, or docs.
- **Layer cache is your rebuild budget.** Order instructions least- to most-frequently
  changing so a code edit reuses the dependency layers.
- **A file removed in a later layer still weighs in the earlier one.** Clean up in the
  same `RUN` that created the mess, or the image keeps both.
- **The base image sets the floor.** `-slim`, `-alpine`, and `distroless` bases start
  hundreds of MB smaller than the full distro image.
- **The build context is uploaded before the build runs.** A missing `.dockerignore`
  sends `.git` and `node_modules` to the daemon and risks baking them in.

## Best Practices

- Pick the smallest base that runs your app: `distroless` or `-slim` for compiled and
  interpreted apps; `-alpine` when its musl libc is compatible (verify — some native
  wheels and glibc-only binaries break on Alpine).
- Use [multi-stage builds](11-multi-stage-builds.md) so build-time toolchains stay in a
  builder stage and the final stage copies only the artifact.
- Combine `RUN` steps that create-then-clean, and delete package-manager caches in the
  same layer (`rm -rf /var/lib/apt/lists/*`, `npm cache clean`, `pip --no-cache-dir`).
- Install production dependencies only (`npm ci --omit=dev`, `pip install --no-dev`,
  `go build` without test deps).
- Write a `.dockerignore` covering `.git`, `node_modules`, build output, `*.md`, tests,
  and any secrets, so the context is small and nothing sensitive leaks in.
- Use BuildKit `--mount=type=cache` for package downloads to speed rebuilds without adding
  the cache to a layer; see [BuildKit](10-buildkit.md).
- Measure: `docker image ls`, `docker history <image>`, and `dive` show where the bytes
  went. Optimize the biggest layer first.

## Examples

**Good Example** — slim base, single cleanup layer, prod-only deps

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Manifest first → install layer stays cached across code edits.
COPY requirements.txt .
# --no-cache-dir keeps pip's cache out of the layer; build deps removed in the
# same RUN so they never persist in the image.
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY . .
CMD ["python", "-m", "app"]
```

**Bad Example** — full base, caches and build tools retained across layers

```dockerfile
FROM python:3.12            # full image: ~1 GB before your code

WORKDIR /app
COPY . .                    # no .dockerignore → .git and caches shipped in
RUN apt-get update && apt-get install -y build-essential  # never removed
RUN pip install -r requirements.txt                       # cache kept in a layer
# build-essential and pip's cache live in the final image forever, adding
# hundreds of MB of pull time and CVE surface that nothing at runtime uses.
CMD ["python", "-m", "app"]
```

## Common Mistakes

- Basing on the full `python`/`node`/`ubuntu` image when a `-slim` or distroless base runs
  the same code at a fraction of the size.
- Deleting build tools or caches in a *separate* `RUN`, so the bytes stay in the earlier
  layer and nothing is saved.
- Copying source before installing dependencies, busting the cache on every edit.
- Shipping devDependencies, test frameworks, and docs into production images.
- No `.dockerignore`, so the context balloons and secrets/`.git` can be baked in.
- Switching to Alpine blindly and shipping a subtly broken binary due to musl vs glibc.

## Production Tips

- Set an image-size budget in CI and fail the build when it regresses; size creep is easy
  to catch early and painful to unwind later.
- Scan every image for CVEs (`docker scout`, Trivy); a smaller base usually means far fewer
  findings to triage. See [Security](18-security.md).
- Prefer digest-pinned bases so a slim tag cannot silently grow between builds.

## AI Review Checklist

- Is the base the smallest viable image (`-slim`, `-alpine`, or `distroless`)?
- Are build tools and package caches removed in the same `RUN` that created them?
- Are only production dependencies installed?
- Is there a `.dockerignore` excluding VCS, deps, build output, and secrets?
- Is instruction order preserving the dependency cache across code changes?
- Would a [multi-stage build](11-multi-stage-builds.md) remove build-time tooling entirely?

## Related

- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/docker/10-buildkit.md`
- `knowledge/docker/03-images.md`
- `knowledge/docker/18-security.md`
