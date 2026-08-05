---
id: docker/10-buildkit
topic: docker
slug: buildkit
title: "BuildKit"
type: doc
order: 10
status: ready
tags: [docker, buildkit, ARG, NPM_TOKEN, buildx]
related: [docker/08-dockerfile, docker/09-image-optimization, docker/11-multi-stage-builds, docker/14-secrets, docker/29-ci-integration]
when_to_use: "Read before optimizing build speed, caching dependencies, or passing secrets into a build without leaking them into layers."
---
# BuildKit

## Purpose

This document defines how to use **BuildKit**, the modern Docker build engine, to build
faster and more safely: cache mounts for package managers, secret mounts that never touch
a layer, SSH forwarding, and parallel stage execution. BuildKit is the default builder in
current Docker and unlocks capabilities the legacy builder cannot express.

BuildKit changes the build from a strictly linear sequence into a dependency graph. It
runs independent stages in parallel, skips stages nothing depends on, and adds mount types
that solve the two hardest Dockerfile problems: slow rebuilds and secret leakage.

## Why It Matters

Two chronic Dockerfile problems have no clean solution on the legacy builder. First,
package caches: to reuse a download cache you had to bake it into a layer, bloating the
image. Second, secrets: any token passed via `ARG` or `ENV` is permanently recorded in
image history, readable by anyone who pulls it. BuildKit solves both with mounts that
exist only during a single `RUN` and never become a layer. It also parallelizes
multi-stage builds, often cutting cold-build time substantially. Not using BuildKit means
choosing slow builds and leaked secrets on purpose.

## Core Principles

- **BuildKit is enabled by default** in current Docker (via `buildx`); to use its mount
  features a Dockerfile can declare `# syntax=docker/dockerfile:1` at the top.
- **Cache mounts persist between builds but never enter the image.** `--mount=type=cache`
  keeps a package manager's download cache on the build host, not in a layer.
- **Secret mounts expose a secret only during one `RUN`.** `--mount=type=secret` makes the
  value available as a file for that command and leaves nothing in history.
- **Never pass secrets via `ARG`/`ENV`.** Build args are stored in image metadata and
  visible in `docker history`; they are not a secret mechanism.
- **BuildKit builds a graph and runs independent stages in parallel.** Structure stages so
  unrelated work (deps, assets) can proceed concurrently.

## Best Practices

- Add `# syntax=docker/dockerfile:1` as the first line so the frontend supporting mounts is
  used regardless of the daemon's default.
- Use `--mount=type=cache,target=<dir>` for package-manager caches (`~/.npm`,
  `/root/.cache/pip`, `/go/pkg/mod`, `~/.cache/go-build`) to make rebuilds fast without
  adding cache bytes to any layer.
- Pass credentials with `--mount=type=secret,id=<name>` and `docker build --secret
  id=<name>,src=<file>`; read the value inside the `RUN`, never assign it to `ENV`.
- Forward Git/SSH access with `--mount=type=ssh` instead of copying a private key into the
  build context or a layer.
- In CI, use `docker buildx build` with a registry cache (`--cache-to` / `--cache-from`)
  so cache is shared across runners; see [CI Integration](29-ci-integration.md).
- Keep multi-stage graphs shallow and independent so BuildKit can parallelize stages.

## Examples

**Good Example** — cache mount for speed, secret mount that leaves no trace

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./

# Cache mount: npm's download cache lives on the build host, reused across builds,
# and is NOT part of any image layer → fast rebuilds, no bloat.
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev

# Secret mount: the npm token exists only for this RUN and never lands in history.
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN="$(cat /run/secrets/npm_token)" npm run fetch-private
# Build with:
#   docker build --secret id=npm_token,src=./npm_token.txt .
COPY . .
CMD ["node", "server.js"]
```

**Bad Example** — build arg secret and cache baked into a layer

```dockerfile
FROM node:20-slim
WORKDIR /app

# ARG secret is stored in image metadata: `docker history` reveals the token
# to anyone who pulls the image. This is a permanent credential leak.
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > ~/.npmrc \
 && npm ci

# The .npmrc with the token, plus npm's cache, are now permanent layers.
COPY . .
CMD ["node", "server.js"]
```

## Common Mistakes

- Passing tokens or keys via `--build-arg`/`ARG`, which are recorded in image history.
- Copying an SSH private key into the context to clone a private repo, then "deleting" it
  in a later layer where it still persists.
- Baking a package cache into a layer to reuse it, defeating [image
  optimization](09-image-optimization.md).
- Omitting the `# syntax=` directive and finding `--mount` flags unrecognized on an older
  frontend.
- Writing a strictly linear Dockerfile that prevents BuildKit from parallelizing stages.
- Assuming a cache mount is durable state — it can be pruned; it is a speedup, not storage.

## Production Tips

- Share build cache across CI runners with a registry-backed cache (`--cache-to
  type=registry` / `--cache-from`) to keep cold-runner builds fast.
- Prefer BuildKit secret mounts over injecting secrets at build time at all; many secrets
  belong at *runtime* instead — see [Secrets](14-secrets.md).
- Use `docker buildx` for multi-platform builds (`--platform linux/amd64,linux/arm64`),
  which the legacy builder cannot do.

## AI Review Checklist

- Is the Dockerfile's first line `# syntax=docker/dockerfile:1` when mounts are used?
- Are secrets passed via `--mount=type=secret`, never `ARG`/`ENV`/`--build-arg`?
- Are package-manager caches on `--mount=type=cache` rather than baked into layers?
- Is private-repo access done with `--mount=type=ssh`, not a copied key?
- Does `docker history` on the built image reveal no tokens or credentials?
- In CI, is build cache shared across runners for fast cold builds?

## Related

- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/09-image-optimization.md`
- `knowledge/docker/11-multi-stage-builds.md`
- `knowledge/docker/14-secrets.md`
- `knowledge/docker/29-ci-integration.md`
