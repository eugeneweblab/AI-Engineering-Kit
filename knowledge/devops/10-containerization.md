---
id: devops/10-containerization
topic: devops
slug: containerization
title: "Containerization"
type: doc
order: 10
status: ready
tags: [devops, containerization, ENTRYPOINT, COPY, CMD, WORKDIR, alpine, EXPOSE]
related: [devops/11-orchestration, devops/09-configuration-management, devops/16-security, devops/05-build-pipelines, devops/07-deployment-strategies]
when_to_use: "Read before writing or reviewing a Dockerfile, container image, or anything that packages an app to run in a container."
---
# Containerization

## Purpose

This document defines how to package an application into a container image that is small,
secure, reproducible, and safe to run in production. It is written so an agent can author
or review a Dockerfile without shipping a bloated, root-running, or secret-leaking image.

Containerization is about the **image and how a single container runs**. Scheduling many
containers across hosts is [orchestration](11-orchestration.md); supplying their settings
is [configuration management](09-configuration-management.md). This doc stops at the
boundary of one well-built image.

## Why It Matters

The container image is the deployable artifact — the thing promoted from staging to
production. A poorly built image is a liability that ships with every deploy: a 2 GB
image slows every rollout and scale-up, a root-running container turns one app bug into
host compromise, and a secret baked into a layer is exposed to anyone who can pull the
image. These are not runtime problems you can patch later; they are frozen into the
artifact at build time, so getting the Dockerfile right is the cheapest place to fix them.

## Core Principles

- **Immutable and reproducible.** An image is built once and never mutated; the same
  Dockerfile + pinned inputs should produce a functionally identical image. No installing
  things at runtime.
- **Minimal surface.** Ship only what the app needs to run. Every extra package is
  attack surface, download weight, and a potential CVE.
- **Least privilege.** Run as a non-root user; the container should not be able to do
  more than the app requires.
- **One concern per container.** A container runs one main process; let the orchestrator
  compose many. Do not cram a whole stack into one image.
- **Config and secrets come from outside.** They are injected at runtime, never baked
  into layers — layers are cached, shared, and inspectable.

## Best Practices

- Use **multi-stage builds**: compile/build in a fat stage, copy only the artifact into a
  slim runtime stage. This keeps build tools (and their CVEs) out of the shipped image.
- Start from a **minimal, pinned base** (`-slim`, `distroless`, or `alpine` where libc
  allows). Pin by digest or specific tag, never `latest` — `latest` makes builds
  non-reproducible.
- **Run as non-root.** Create a dedicated user and `USER` to it; a root container that is
  breached can attack the host and other containers.
- **Never `COPY` secrets or `.env` into the image**, and never pass them as build args
  (build args persist in history). Add a `.dockerignore` to keep credentials, `.git`, and
  local files out of the build context.
- Order layers by change frequency: copy dependency manifests and install *before*
  copying source, so a code change does not bust the dependency cache.
- Add a **`HEALTHCHECK`** (or rely on orchestrator probes) so the platform knows when the
  container is actually serving, not merely started.
- Set an explicit, non-root-friendly `WORKDIR`, `EXPOSE`, and a direct `ENTRYPOINT`
  (exec form) so signals (SIGTERM) reach the app for graceful shutdown.

## Examples

**Good Example** — multi-stage, pinned, non-root, no secrets

```dockerfile
# --- build stage: has the toolchain, none of which ships to production ---
FROM node:22.11-bookworm-slim AS build
WORKDIR /app
COPY package*.json ./          # copy manifests first → dependency layer stays cached
RUN npm ci                     # on code-only changes this layer is reused
COPY . .
RUN npm run build

# --- runtime stage: minimal, only the built artifact + prod deps ---
FROM node:22.11-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER node                      # non-root: a breach can't own the host
HEALTHCHECK CMD node dist/health.js || exit 1
# exec form → SIGTERM reaches node for graceful shutdown/draining
ENTRYPOINT ["node", "dist/server.js"]
```

**Bad Example** — fat, root, secret baked in, unpinned

```dockerfile
FROM node:latest              # unpinned → today's and next week's build differ
WORKDIR /app
COPY . .                      # copies .env, .git, node_modules, everything in context
ENV API_KEY=sk-live-abc123    # secret frozen into a layer, visible to anyone who pulls
RUN npm install               # dev + build deps shipped to prod = bloat + CVEs
# runs as root by default: a container escape becomes a host compromise
CMD npm start                 # shell form: SIGTERM goes to the shell, not node → no drain
```

## Common Mistakes

- Basing on `latest` (or any moving tag), making builds non-reproducible.
- Single-stage builds that ship compilers, package managers, and dev dependencies.
- Running as root because it "just works."
- Baking secrets via `ENV`, `COPY .env`, or build args — all persist in image layers.
- No `.dockerignore`, so `.git`, credentials, and local junk enter the build context.
- Shell-form `CMD`/`ENTRYPOINT`, which breaks signal delivery and graceful shutdown.
- Copying source before installing dependencies, busting the layer cache on every change.

## Production Tips

- Scan images for CVEs in CI (Trivy, Grype) and fail the build on high-severity findings.
- Push by immutable digest and reference that digest in deployment for true reproducibility.
- Keep images small — smaller images pull faster, which directly speeds up scale-up and
  rollout during incidents.
- Sign images and verify signatures at deploy time to prevent tampered artifacts running.

## AI Review Checklist

- Is the base image pinned (not `latest`) and minimal (slim/distroless)?
- Is a multi-stage build used so build tooling and dev deps stay out of the runtime image?
- Does the container run as a non-root `USER`?
- Are there zero secrets in `ENV`, `COPY`, or build args, and a `.dockerignore` present?
- Is `ENTRYPOINT`/`CMD` in exec form so SIGTERM reaches the app for graceful shutdown?
- Are dependency layers ordered before source copy to preserve caching?

## Related

- `knowledge/devops/11-orchestration.md`
- `knowledge/devops/09-configuration-management.md`
- `knowledge/devops/16-security.md`
- `knowledge/devops/05-build-pipelines.md`
- `knowledge/devops/07-deployment-strategies.md`
