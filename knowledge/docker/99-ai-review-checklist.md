---
id: docker/99-ai-review-checklist
topic: docker
slug: ai-review-checklist
title: "Docker AI Review Checklist"
type: doc
order: 99
status: ready
tags: [docker, ai-review-checklist]
related: [docker/08-dockerfile, docker/09-image-optimization, docker/18-security, docker/26-best-practices, docker/100-common-antipatterns]
when_to_use: "Read when reviewing a Dockerfile, Compose file, or container-related diff, to catch defects before merge."
---
# Docker AI Review Checklist

## Purpose

A focused review pass for container artifacts — `Dockerfile`, `.dockerignore`,
`docker-compose.yml`, and entrypoint scripts. Each item is a defect an agent can detect
by reading the diff, with the reason it matters, so the review flags real problems rather
than style preferences. Use it whenever a change touches how the app is built or run in a
container.

## Why It Matters

Container mistakes are quiet: the build passes, the app boots, tests are green — and the
image still ships as root with a 900 MB attack surface and a secret in layer 4. These
defects surface in production, weeks later, as an incident. A disciplined review at
merge time is the cheapest place to catch them.

## Correctness & Reproducibility

**Rules:** [Dockerfile](08-dockerfile.md) · [Multi Stage Builds](11-multi-stage-builds.md)

- [ ] Is the base image pinned by digest, so rebuilds are byte-reproducible?
- [ ] Are dependencies installed from a committed lockfile (`npm ci`, `pip install -r`
      with hashes), not resolved fresh each build?
- [ ] Does instruction order put least-changing steps first so the layer cache is reused?
- [ ] Is `COPY` scoped to what is needed, rather than `COPY . .` pulling in the whole tree?
- [ ] Does the container avoid runtime installs (`apt-get`, `git pull` in the entrypoint)?

## Security

**Rules:** [Security](18-security.md) · [Secrets](14-secrets.md)

- [ ] Does the image declare a non-root `USER` before the entrypoint?
- [ ] Are there any secrets, tokens, or keys visible in `ENV`, `ARG`, or copied files?
- [ ] Is the build free of `curl ... | sh` and unpinned remote scripts?
- [ ] Are unnecessary tools (shells, `curl`, package managers) kept out of the final stage?
- [ ] Are capabilities dropped and privileges restricted in the run config?

## Image Hygiene

**Rules:** [Image Optimization](09-image-optimization.md) · [Images](03-images.md)

- [ ] Is a [multi-stage build](11-multi-stage-builds.md) used to drop build-time tooling?
- [ ] Is a `.dockerignore` present and does it exclude `.git`, `node_modules`, and env files?
- [ ] Are `RUN` steps chained and caches cleaned in the same layer (e.g.
      `apt-get ... && rm -rf /var/lib/apt/lists/*`) so cruft is not committed?
- [ ] Is the base minimal (`-slim`/distroless) unless a fuller base is justified?

## Runtime Behavior

**Rules:** [Healthchecks](15-healthchecks.md) · [Resource Limits](17-resource-limits.md)

- [ ] Do `ENTRYPOINT`/`CMD` use exec form so PID 1 receives `SIGTERM`?
- [ ] Is there a [`HEALTHCHECK`](15-healthchecks.md) that reflects real readiness?
- [ ] Are [resource limits](17-resource-limits.md) set in the Compose/run config?
- [ ] Does the app log to stdout/stderr rather than files inside the container?
- [ ] Is persistent state written to a volume, never the container's writable layer?

## Configuration

**Rules:** [Environment Variables](13-environment-variables.md) · [Compose](12-docker-compose.md)

- [ ] Is environment-specific config injected at run time, not hardcoded in a layer?
- [ ] Are published ports limited to what the service needs?
- [ ] Does the Compose file avoid `network_mode: host` and `privileged: true` unless
      genuinely required and justified in a comment?

## How to Report

- Cite the file and line, name the defect, and state the consequence
  ("runs as root → container escape owns the host"), not just the rule.
- Rank by blast radius: secret exposure and root execution before cache inefficiency.
- Prefer a concrete fix ("add `USER node` after the final `COPY`") over "improve security".

## Related

- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/09-image-optimization.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/26-best-practices.md`
- `knowledge/docker/100-common-antipatterns.md`
