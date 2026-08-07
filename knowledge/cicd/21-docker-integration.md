---
id: cicd/21-docker-integration
topic: cicd
slug: docker-integration
title: "Docker Integration"
type: doc
order: 21
status: ready
tags: [cicd, docker-integration, ARG, GIT_SHA, "@sha", NPM_TOKEN, "myapp:latest", builder]
related: [cicd/03-build-stage, cicd/06-security-scanning, cicd/07-artifacts, cicd/22-kubernetes-integration]
when_to_use: "Read before building, tagging, or pushing container images from a CI/CD pipeline."
---
# Docker Integration

## Purpose

This document defines how to build, tag, scan, and push container images correctly from a
pipeline. It covers reproducible builds, layer caching, immutable tagging, multi-stage
Dockerfiles, registry authentication, and image signing. The goal is an agent that can wire
Docker into CI so the image that gets scanned and tested is byte-for-byte the image that
ships.

A container image is a build [artifact](07-artifacts.md); the same immutability and
provenance rules apply. This doc covers the Docker-specific mechanics that break that chain.

## Why It Matters

The container image is what actually runs in production — not your source, not your
lockfile, the image. If the pipeline builds an image, scans a *different* image, and
deploys a *third*, every [security scan](06-security-scanning.md) and test is meaningless.
The two ways this breaks are non-reproducible builds (unpinned base images, `latest` tags)
and mutable tags (re-pushing `myapp:latest`), and both are silent: nothing fails, you just
can no longer prove what is running. Immutable, digest-addressed images are the foundation
everything downstream trusts.

## Core Principles

- **Pin the base image by digest.** `FROM node:22.11.0-slim@sha256:...` is reproducible;
  `FROM node:latest` is not. The digest guarantees the same bytes every build; the cost is
  a periodic bump via Renovate/Dependabot.
- **Tag immutably, deploy by digest.** Tag with the commit SHA (`myapp:git-<sha>`), never
  reuse a tag, and reference the resulting `@sha256:` digest downstream. A moving `latest`
  tag means "which build?" has no answer.
- **Multi-stage builds ship only what runs.** Compile in a `builder` stage, copy the
  artifact into a minimal runtime stage. This shrinks the image and removes compilers and
  dev dependencies that expand the attack surface.
- **Build once, promote the same image.** Build in one job; the exact same image (by digest)
  flows through test → staging → prod. Never rebuild per environment.
- **Run as non-root.** A container that runs as root is one escape away from host access.
  Set a `USER` and drop capabilities.

## Best Practices

- Use **BuildKit** (`docker buildx`) with a registry cache (`--cache-to`/`--cache-from
  type=registry`) so cache survives across ephemeral CI runners.
- Add a `.dockerignore` to keep `.git`, `node_modules`, and secrets out of the build
  context — a smaller context builds faster and cannot leak files into layers.
- Authenticate to the registry with **short-lived OIDC tokens** where supported, or a
  scoped robot/deploy token — never a personal account or a long-lived root credential.
- Scan the built image (Trivy/Grype) *after build, before push*, and fail on new
  High/Critical CVEs — see [security scanning](06-security-scanning.md).
- Never pass secrets via `ARG` or `ENV`; they persist in image layers and history. Use
  BuildKit `--secret` mounts, which are not written to the final image.
- Sign images (`cosign`) and, in the cluster, verify the signature so only pipeline-built
  images can run.
- Set `HEALTHCHECK`, a non-root `USER`, and a pinned `WORKDIR`; label the image with the
  commit SHA and build time for traceability.

## Examples

**Good Example** — multi-stage, pinned, non-root, immutable tag, BuildKit secret

```dockerfile
# Build stage: has the toolchain; discarded from the final image
FROM node:22.11.0-slim@sha256:<digest> AS builder
WORKDIR /app
COPY package*.json ./
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci                                  # token via secret mount, not baked into a layer
COPY . .
RUN npm run build

# Runtime stage: minimal, no compilers, runs as non-root
FROM node:22.11.0-slim@sha256:<digest>
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
# never run as root
USER node
HEALTHCHECK CMD node healthcheck.js || exit 1
CMD ["node", "dist/server.js"]
```

```bash
# CI: build once, tag by SHA, scan, then push the exact image
docker buildx build --secret id=npmrc,src=$HOME/.npmrc \
  --cache-from type=registry,ref=$REG/myapp:cache \
  --cache-to type=registry,ref=$REG/myapp:cache,mode=max \
  -t $REG/myapp:git-$GIT_SHA .
trivy image --exit-code 1 --severity CRITICAL,HIGH $REG/myapp:git-$GIT_SHA  # gate before push
docker push $REG/myapp:git-$GIT_SHA        # immutable tag; deploy references its digest
```

**Bad Example** — unpinned, secret in a layer, mutable tag, root

```dockerfile
# non-reproducible base
FROM node:latest
# baked into image history → recoverable forever
ARG NPM_TOKEN
RUN echo "//registry/:_authToken=$NPM_TOKEN" > .npmrc && npm install
# no .dockerignore → .git and secrets copied in
COPY . .
# runs as root
CMD ["npm", "start"]
```

```bash
docker build -t myapp:latest . && docker push myapp:latest  # mutable tag; "which build?" is unanswerable
```

## Common Mistakes

- `FROM ...:latest` or an unpinned base, so the image is not reproducible.
- Passing tokens via `ARG`/`ENV`, leaving them recoverable in `docker history`.
- Re-pushing a mutable tag (`latest`, `staging`) instead of an immutable SHA tag.
- Building a fresh image per environment instead of promoting one image by digest.
- Scanning source or a different image than the one that ships.
- Running as root and copying the whole context (no `.dockerignore`).
- Discarding the BuildKit cache each run because it is stored locally on an ephemeral runner.

## Production Tips

- Deploy manifests should reference images by **digest** (`myapp@sha256:...`), not tag, so a
  re-tag cannot silently change what runs.
- Keep base images fresh with automated PRs (Renovate); pinning without updating trades
  drift for staleness.
- Publish an **SBOM** alongside the image so you can answer "are we affected by CVE-X?"
  during a zero-day without rebuilding.
- Enforce signature verification (cosign + admission policy) in the cluster so unsigned or
  externally built images cannot run — see [Kubernetes integration](22-kubernetes-integration.md).

## AI Review Checklist

- Is the base image pinned by digest (or at least an exact tag), never `latest`?
- Are build secrets passed via BuildKit `--secret`, never `ARG`/`ENV`?
- Is the image tagged immutably (commit SHA) and deployed by digest?
- Is it a multi-stage build that ships only the runtime, running as a non-root `USER`?
- Is the same image promoted across environments, not rebuilt per environment?
- Is the image scanned after build and before push, with a High/Critical gate?
- Is there a `.dockerignore` keeping `.git`/secrets out of the build context?

## Related

- `knowledge/cicd/03-build-stage.md`
- `knowledge/cicd/06-security-scanning.md`
- `knowledge/cicd/07-artifacts.md`
- `knowledge/cicd/22-kubernetes-integration.md`
