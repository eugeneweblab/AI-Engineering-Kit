---
id: cicd/03-build-stage
topic: cicd
slug: build-stage
title: "Build Stage"
type: doc
order: 3
status: ready
tags: [cicd, build-stage, GIT_SHA, "node:latest"]
related: [cicd/02-pipeline-design, cicd/04-test-stage, cicd/07-artifacts, cicd/08-versioning, cicd/21-docker-integration]
when_to_use: "Read before writing or reviewing the build job that compiles/packages an app in CI."
---
# Build Stage

## Purpose

This document defines how the build stage should compile, bundle, and package an
application into an artifact that later stages test and deploy. It covers reproducibility,
dependency locking, and the "build once, promote everywhere" rule. What the artifact is
and how it is stored is covered in [Artifacts](07-artifacts.md); how it is tagged in
[Versioning](08-versioning.md).

The build stage has one job: turn a specific commit into a deterministic, immutable
artifact — the exact bytes that will run in production.

## Why It Matters

Everything downstream trusts the build. If the build is non-deterministic — unpinned
dependencies, floating base images, machine-specific paths — then "the tests passed" and
"the scan was clean" are claims about an artifact that no longer exists, because the next
build produces something different. Worse, rebuilding per environment means the binary you
tested in staging is not the binary in production; a dependency published in the intervening
minutes can change behavior. A reproducible build is the foundation that makes every later
guarantee meaningful. Get it wrong and every green check is a lie.

## Core Principles

- **Build once, promote the same bytes.** Produce a single artifact in CI and promote that
  identical artifact through every environment. Never rebuild for staging vs production.
- **Reproducible in, reproducible out.** The same commit must produce a functionally
  identical artifact on any runner, at any time. Pin everything the build reads.
- **Install from a lockfile, offline where possible.** Use exact, hash-verified
  dependencies (`npm ci`, `pip install --require-hashes`, `go mod verify`), never a
  resolver that can pick a newer version at build time.
- **No network surprises, no ambient state.** The build must not depend on a service that
  might be down or a file that happens to exist on the runner.
- **Fail the build on any error.** A build that emits warnings and exits 0 while half the
  output is missing is worse than a clean failure.

## Best Practices

- Commit lockfiles and install with the strict, lockfile-respecting command; a build that
  can silently upgrade a dependency is not reproducible.
- Pin the runtime and base image to an exact version or digest (`node:22.11.0`,
  `python@sha256:...`), never a floating tag like `node:latest`.
- Use multi-stage Docker builds so build tooling stays out of the runtime image, keeping
  it small and reducing attack surface. See [Docker Integration](21-docker-integration.md).
- Cache dependency and layer inputs keyed by lockfile hash; invalidate on lockfile change.
- Stamp the artifact with its commit SHA and version so a running binary is traceable.
- Treat build warnings as errors (`-Werror`, `tsc --noEmitOnError`) where the ecosystem
  supports it, so silent degradation cannot ship.

## Examples

**Good Example** — pinned, lockfile-locked, multi-stage, build once

```dockerfile
# Pinned base image by exact version → reproducible across time and machines.
FROM node:22.11.0-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci                      # exact, hash-verified deps from the lockfile
COPY . .
RUN npm run build               # produces /app/dist once

# Runtime stage carries only the built output — no compilers, no dev deps.
FROM node:22.11.0-slim
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
ARG GIT_SHA
# artifact traceable to its commit
LABEL org.opencontainers.image.revision=$GIT_SHA
CMD ["node", "dist/server.js"]
```

**Bad Example** — floating image, unlocked deps, rebuilt per env

```dockerfile
# floating tag → different base every build
FROM node:latest
WORKDIR /app
COPY . .
RUN npm install                # resolver may pick newer versions than were tested
RUN npm run build
# Single stage: ships compilers, dev deps, and source — large and non-reproducible.
# Deploy scripts run this Dockerfile again per environment, so prod != staging.
CMD ["node", "dist/server.js"]
```

## Common Mistakes

- Using `npm install` / unpinned `pip install` instead of a lockfile-strict install.
- Floating base images (`:latest`) that change the runtime out from under you.
- Rebuilding the artifact per environment, breaking the "tested == shipped" guarantee.
- Shipping a single-stage image with build tools and source baked into the runtime.
- Builds that exit 0 on warnings, hiding missing or degraded output.
- No commit stamp, so a production incident cannot be traced to a source revision.

## Production Tips

- Store the built artifact in a registry with an immutable, content-addressed tag (digest),
  and deploy by digest so the reference cannot drift. See [Artifacts](07-artifacts.md).
- Verify reproducibility periodically by rebuilding a known commit and diffing the output.
- Keep a build cache but scope it per lockfile hash so a poisoned or stale cache cannot
  leak an old dependency into a new build.

## AI Review Checklist

- Are dependencies installed strictly from a lockfile (`npm ci`, `--require-hashes`)?
- Is the base image pinned to an exact version or digest, never `:latest`?
- Is the artifact built exactly once and promoted, not rebuilt per environment?
- Does the build fail on warnings/errors rather than exiting 0 with degraded output?
- Is the artifact stamped with its commit SHA/version for traceability?

## Related

- `knowledge/cicd/02-pipeline-design.md`
- `knowledge/cicd/04-test-stage.md`
- `knowledge/cicd/07-artifacts.md`
- `knowledge/cicd/08-versioning.md`
- `knowledge/cicd/21-docker-integration.md`
