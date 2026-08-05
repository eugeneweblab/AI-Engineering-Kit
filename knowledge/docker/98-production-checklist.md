---
id: docker/98-production-checklist
topic: docker
slug: production-checklist
title: "Docker Production Checklist"
type: doc
order: 98
status: ready
tags: [docker, production-checklist]
related: [docker/18-security, docker/15-healthchecks, docker/17-resource-limits, docker/22-production, docker/14-secrets]
when_to_use: "Read before promoting a container image or Compose stack to production, or when reviewing a deployment PR."
---
# Docker Production Checklist

## Purpose

A verifiable, yes/no gate for shipping a container to production. Every item is
observable in the `Dockerfile`, image, or runtime config — no judgment calls. If an item
cannot be checked off, the image is not production-ready. Use it as a pre-merge gate and
during incident review to spot what was skipped.

## Why It Matters

Most container incidents are not exotic — they are a missing `USER`, an unpinned base, a
container OOM-killed with no memory limit, or a secret baked into a layer. These are all
catch-able before deploy. This checklist converts hard-won failure modes into a
mechanical pass that a human or an agent can run in minutes.

## Image Build

**Rules:** [Dockerfile](08-dockerfile.md) · [Multi Stage Builds](11-multi-stage-builds.md)

- [ ] Base image is pinned by digest (`@sha256:...`), not a floating tag like `latest`.
- [ ] Final image is built with a [multi-stage build](11-multi-stage-builds.md); no
      compilers, dev dependencies, or test tooling remain.
- [ ] A `.dockerignore` excludes `.git`, `node_modules`, local env files, and secrets.
- [ ] No secrets, tokens, or private keys appear in any layer (`docker history` is clean).
- [ ] Image size is justified — a minimal or `-slim`/distroless base is used where viable.
- [ ] Dependency versions are pinned (lockfile committed and used, e.g. `npm ci`).
- [ ] Image is tagged with the immutable git SHA, not only `latest`.

## Security

**Rules:** [Security](18-security.md) · [Secrets](14-secrets.md)

- [ ] Container runs as a non-root `USER`.
- [ ] Root filesystem is mounted read-only (`--read-only`) with explicit `tmpfs` for
      writable paths.
- [ ] Linux capabilities are dropped (`--cap-drop ALL`, adding back only what is needed).
- [ ] `no-new-privileges` is set so processes cannot gain privileges via setuid binaries.
- [ ] Image passes a vulnerability scan (Trivy/Grype) with no fixable HIGH/CRITICAL CVEs.
- [ ] An SBOM is generated and stored for the released image.

## Runtime Configuration

**Rules:** [Resource Limits](17-resource-limits.md) · [Environment Variables](13-environment-variables.md)

- [ ] Memory and CPU limits are set; the container will not consume the whole host.
- [ ] A restart policy is defined (`unless-stopped` / `on-failure`, not `always` blindly).
- [ ] Config and [secrets](14-secrets.md) are injected at run time via env/secret mounts,
      not baked into the image.
- [ ] `ENTRYPOINT`/`CMD` use exec form so PID 1 receives `SIGTERM` for graceful shutdown.
- [ ] A `stop_grace_period` allows in-flight work to drain before `SIGKILL`.

## Health & Observability

**Rules:** [Healthchecks](15-healthchecks.md) · [Logging](16-logging.md)

- [ ] A [`HEALTHCHECK`](15-healthchecks.md) is defined and reflects real readiness, not
      just "process alive".
- [ ] Application logs go to stdout/stderr, not to files inside the container.
- [ ] A log-rotation / driver limit is set so logs cannot fill the host disk.
- [ ] Metrics or a metrics endpoint are exposed for the orchestrator/monitoring stack.

## State & Data

**Rules:** [Volumes](05-volumes.md) · [Bind Mounts](06-bind-mounts.md)

- [ ] Persistent state lives in named volumes or external stores, never the writable layer.
- [ ] Volumes containing data are covered by a tested backup and restore procedure.
- [ ] The container can be killed and replaced with zero data loss (verified, not assumed).

## Networking

**Rules:** [Networks](07-networks.md)

- [ ] Only the ports the service actually needs are published; nothing extra is exposed.
- [ ] Inter-service traffic uses a defined [network](07-networks.md), not host networking.
- [ ] TLS terminates at a known boundary (ingress/reverse proxy) with a valid certificate.

## CI/CD

**Rules:** [CI Integration](29-ci-integration.md) · [Registry](19-registry.md)

- [ ] The image is built and scanned in [CI](29-ci-integration.md), not on a laptop.
- [ ] Build is reproducible: same inputs produce the same image digest.
- [ ] A rollback path exists — the previous image tag is retained and deployable.

## AI Review Checklist

- Does every item above have concrete evidence in the Dockerfile, image, or deploy config?
- Are any items marked "N/A" actually justified, or silently skipped?
- Does the running configuration match what the Dockerfile and Compose file declare?
- If this container died right now, would data survive and would it restart cleanly?

## Related

- `knowledge/docker/14-secrets.md`
- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/22-production.md`
