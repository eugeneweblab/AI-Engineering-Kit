---
id: docker/100-common-antipatterns
topic: docker
slug: common-antipatterns
title: "Docker Common Antipatterns"
type: doc
order: 100
status: ready
tags: [docker, common-antipatterns]
related: [docker/08-dockerfile, docker/09-image-optimization, docker/14-secrets, docker/18-security, docker/30-engineering-principles]
when_to_use: "Read when authoring or reviewing a Dockerfile to recognize and avoid the most common container mistakes."
---
# Docker Common Antipatterns

## Purpose

A catalog of the container mistakes that recur most often, each with *why it is wrong*
and *the fix*. These are the defects that pass build and boot but degrade security,
reproducibility, or reliability in production. An agent should recognize them on sight
and correct them rather than replicate them from an existing bad `Dockerfile`.

## Why It Matters

Antipatterns spread by copy-paste. One team's root-running, `latest`-based image becomes
the template for ten services. Naming the pattern and its fix breaks the chain: a review
that catches the smell once prevents it from propagating.

## Antipatterns

### 1. Floating base image tag

- **Why it is wrong:** `FROM node:latest` (or `:22`) resolves to a different image on
  every rebuild. Builds are non-reproducible, and a base update can silently break or
  compromise you with no diff to review.
- **The fix:** Pin by digest — `FROM node:22.11-slim@sha256:...`. Update it deliberately,
  as a reviewable change.

### 2. Running as root

- **Why it is wrong:** The default `USER` is root. If the process is compromised, the
  attacker has root inside the container and a much shorter path to the host.
- **The fix:** Create and switch to a non-root user (`USER node` or a dedicated
  `useradd` user) before the entrypoint. See [security](18-security.md).

### 3. `COPY . .` before installing dependencies

- **Why it is wrong:** Any source change invalidates the layer cache for the dependency
  install below it, so every build reinstalls everything — slow CI, wasted minutes.
- **The fix:** Copy manifests first, install, then copy source:
  `COPY package*.json ./ && RUN npm ci && COPY . .`.

### 4. Secrets baked into layers

- **Why it is wrong:** `ENV API_KEY=...`, `ARG TOKEN`, or `COPY .env .` persist in image
  layers. Anyone with the image can extract them via `docker history` — deleting them in
  a later layer does not remove them.
- **The fix:** Inject secrets at run time (env, secret mounts) or use BuildKit
  `--secret` for build-time needs. See [secrets](14-secrets.md).

### 5. Fat images with build tooling shipped to prod

- **Why it is wrong:** Compilers, dev headers, and package managers left in the final
  image bloat pulls and expand the attack surface — every tool is a potential CVE.
- **The fix:** Use a [multi-stage build](11-multi-stage-builds.md); copy only runtime
  artifacts into a minimal final stage.

### 6. Shell-form `CMD` / `ENTRYPOINT`

- **Why it is wrong:** `CMD npm start` runs under `/bin/sh -c`, so PID 1 is the shell.
  It does not forward `SIGTERM`, so the app is `SIGKILL`ed after the grace period —
  connections drop, work is lost.
- **The fix:** Use exec form — `CMD ["node", "server.js"]` — so the process is PID 1 and
  receives signals directly.

### 7. Un-chained `RUN` steps that leave cache cruft

- **Why it is wrong:** Separate `apt-get update` and `apt-get install` layers can serve
  stale package indexes, and leaving `/var/lib/apt/lists` bloats the image permanently
  (a later `rm` cannot shrink an earlier layer).
- **The fix:** Chain in one layer and clean within it:
  `RUN apt-get update && apt-get install -y --no-install-recommends pkg && rm -rf /var/lib/apt/lists/*`.

### 8. No `.dockerignore`

- **Why it is wrong:** The entire directory — `.git`, `node_modules`, local secrets — is
  sent as build context. Builds are slow, caches bust needlessly, and secrets can leak
  into the image.
- **The fix:** Add a `.dockerignore` before the first build; exclude VCS, dependencies,
  build output, and env files.

### 9. Multiple services in one container

- **Why it is wrong:** Running app + database + cron under a supervisor breaks
  independent scaling, per-service logs, and clean lifecycle/health signals.
- **The fix:** One primary process per container; compose multiple services with
  [Docker Compose](12-docker-compose.md) or an orchestrator.

### 10. Persisting state in the writable layer

- **Why it is wrong:** Data written inside the container is destroyed when it is
  replaced. Containers are disposable; treating them as durable loses data on every
  redeploy.
- **The fix:** Write state to a named [volume](05-volumes.md) or an external store, and
  verify the container can be killed and replaced with no loss.

### 11. No resource limits

- **Why it is wrong:** An unbounded container can consume all host memory/CPU, getting
  OOM-killed unpredictably or starving its neighbors — a noisy-neighbor outage.
- **The fix:** Set memory and CPU [limits](17-resource-limits.md) in the run/Compose
  config for every service.

### 12. Missing or fake healthcheck

- **Why it is wrong:** With no [`HEALTHCHECK`](15-healthchecks.md), the orchestrator
  routes traffic to a process that is up but not ready. A check that only pings the
  process (not the app) is just as blind.
- **The fix:** Add a healthcheck that exercises real readiness (dependencies reachable,
  endpoint responding).

## AI Review Checklist

- Is the base pinned by digest, not a floating tag?
- Does the image run as a non-root user?
- Are dependencies installed before source is copied?
- Is the image free of baked-in secrets (`docker history` clean)?
- Is build tooling excluded via a multi-stage build?
- Do `CMD`/`ENTRYPOINT` use exec form for correct signal handling?
- Is state written to volumes, and are resource limits and a real healthcheck present?

## Related

- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/09-image-optimization.md`
- `knowledge/docker/14-secrets.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/30-engineering-principles.md`
