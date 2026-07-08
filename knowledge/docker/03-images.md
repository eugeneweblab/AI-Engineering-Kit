---
id: docker/03-images
topic: docker
slug: images
title: "Images"
type: doc
order: 3
status: ready
tags: [docker, images]
related: [docker/04-containers, docker/08-dockerfile, docker/09-image-optimization, docker/11-multi-stage-builds, docker/19-registry]
when_to_use: "Read before building, tagging, or referencing an image, or when a build is slow, huge, or non-reproducible."
---
# Images

## Purpose

This document defines what a Docker image is, how layers and the build cache work,
and how to reference an image reliably by tag and digest. Understanding images is
the prerequisite for writing a correct [Dockerfile](08-dockerfile.md) and for every
optimization that follows.

An image is a read-only, layered filesystem plus metadata (entrypoint, env, exposed
ports) that becomes a [container](04-containers.md) when run. Images are immutable:
you never edit one, you build a new one.

## Why It Matters

Images are the unit you ship. A poorly built image is slow to build, slow to pull,
expensive to store, and — worst — a security liability, because every file and
secret in every layer travels with it forever. Two facts drive almost all image
mistakes: layers are cached by instruction, and layers are additive (deleting a
file in a later layer does not remove it from the image). An agent that internalizes
these two facts writes small, fast, reproducible images by default.

## Core Principles

- **Layers are cached and additive.** Each Dockerfile instruction is a layer keyed
  on its inputs. A change invalidates that layer and every layer after it. A file
  added then deleted in a later layer still ships in the earlier one.
- **Order for cache reuse.** Put rarely changing steps (install dependencies) before
  frequently changing steps (copy source) so most rebuilds hit the cache.
- **Tags are mutable pointers; digests are immutable.** `node:20` can change under
  you. `node:20@sha256:...` cannot. Pin by digest when reproducibility matters.
- **Smaller is safer and faster.** Fewer packages means less attack surface, faster
  pulls, and lower cost. Start from a minimal base.
- **The image carries everything in it, forever.** Anything written to any layer —
  including secrets — is recoverable from the image even if a later layer removes it.

## Best Practices

- Choose a minimal, current base: `-slim` or distroless for runtime, `alpine` where
  its musl libc is acceptable. Avoid full `ubuntu`/`debian` for runtime images.
- Pin the base image by tag **and** digest so rebuilds are reproducible and supply
  chain is auditable. See [19-registry](19-registry.md).
- Combine related `RUN` commands and clean up in the **same** layer (e.g.
  `apt-get install ... && rm -rf /var/lib/apt/lists/*`) so the cleanup actually
  shrinks the image.
- Use [multi-stage builds](11-multi-stage-builds.md) to keep build tools out of the
  final image — compile in one stage, copy only artifacts into a slim final stage.
- Tag meaningfully: an immutable version tag (`app:1.4.2` or a git SHA) for deploys,
  plus `latest` only as a convenience. Never deploy floating `latest` to production.
- Scan images for vulnerabilities in CI (`docker scout`, Trivy) and rebuild
  regularly to pick up base-image patches. See [18-security](18-security.md).

## Examples

**Good Example** — cache-friendly ordering, cleanup in-layer, pinned base

```dockerfile
# Pinned by tag AND digest → reproducible, auditable base.
FROM node:20.17-slim@sha256:1c1c1c...  # digest truncated for brevity

WORKDIR /app

# Copy only the manifest first. This layer's cache is reused unless deps change,
# so source edits don't trigger a full reinstall.
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Source is copied AFTER deps, so frequent code changes invalidate only from here.
COPY . .

CMD ["node", "server.js"]
```

**Bad Example** — cache-busting order, cleanup in a separate layer

```dockerfile
FROM node:latest                 # floating tag → not reproducible, huge base

WORKDIR /app
COPY . .                         # any source change busts the cache for ALL steps below
RUN npm install                  # reinstalls every dependency on every code edit

# The apt cache is deleted in a NEW layer, so the previous layer still ships it.
RUN apt-get update && apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*  # image is not actually smaller
```

## Common Mistakes

- Deleting files (secrets, caches) in a later `RUN`, believing they leave the image
  — they remain in the earlier layer and are recoverable.
- Copying the whole source before installing dependencies, so every code change
  triggers a full dependency reinstall.
- Using `FROM node:latest` (or any floating tag) and getting different, unpinned
  images across environments.
- Building on a full OS base when a `-slim`/distroless image would run the app just
  as well with a fraction of the attack surface.
- `RUN apt-get install` without cleaning the package lists in the same layer.
- Baking API keys or `.env` files into layers via `COPY . .` — use
  [secrets](14-secrets.md) and `.dockerignore` instead.

## Production Tips

- Deploy by immutable digest or a unique version tag, never `latest`, so rollbacks
  and audits are exact.
- Enable BuildKit cache mounts (`RUN --mount=type=cache`) to speed dependency
  installs without baking the cache into the image. See [10-buildkit](10-buildkit.md).
- Inspect what you shipped with `docker history` and `docker image inspect`; use
  `dive` to find wasted layers.

## AI Review Checklist

- Is the base image minimal and pinned by tag and digest?
- Are dependencies installed before source is copied, for cache reuse?
- Is package/cache cleanup done in the same `RUN` as the install?
- Are build-time tools excluded from the final image (multi-stage)?
- Are deploys pinned to an immutable tag or digest, not `latest`?
- Are secrets kept out of image layers entirely?

## Related

- `knowledge/docker/04-containers.md`
- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/09-image-optimization.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/docker/19-registry.md`
