---
id: docker/18-security
topic: docker
slug: security
title: "Security"
type: doc
order: 18
status: ready
tags: [docker, security]
related: [docker/14-secrets, docker/03-images, docker/17-resource-limits, docker/22-production, docker/09-image-optimization]
when_to_use: "Read before writing a Dockerfile or running any container that will reach staging or production."
---
# Security

## Purpose

This document defines how to build and run containers that do not widen your attack
surface: which base image to trust, which user to run as, which Linux capabilities to
drop, and how to keep secrets out of images. It is written so an agent can harden a
container without breaking it.

A container is not a security boundary the way a VM is — it shares the host kernel. The
default `docker run` is convenient and dangerous: root inside the container is root on
the host if anything escapes. Treat every container as internet-facing until proven
otherwise.

## Why It Matters

Container images are shipped, cached, and re-run thousands of times. A vulnerability
baked into a base layer, or a secret committed to an image, propagates to every
environment that pulls it — silently, because the container still runs perfectly. A
single container running as root with `--privileged` turns a minor app bug into full
host compromise. The blast radius is the whole node and everything scheduled on it, so
container hardening is held to a higher bar than the application code inside it.

## Core Principles

- **Run as a non-root user.** Root in the container maps to root on the host under the
  default runtime. A dropped privilege cannot be abused.
- **Minimize what is in the image.** Every package, shell, and tool is attack surface.
  A distroless or `-slim` base has almost nothing to exploit.
- **Drop everything, add back only what is needed.** Default capabilities are broad;
  start from zero and grant the few the process actually requires.
- **Never bake secrets into an image.** Layers are immutable and cached; a secret in a
  layer is permanent even after a later `RM`.
- **Make the root filesystem read-only.** A process that cannot write cannot persist a
  payload or tamper with binaries.
- **Pin and scan.** Pin base images by digest and scan every build; "latest" is a moving,
  unaudited target.

## Best Practices

- Set `USER` to a non-root UID in the Dockerfile, and run with `--user 10001:10001`.
  Prefer a numeric UID so the host can reason about it without `/etc/passwd`.
- Pin the base image by digest (`FROM node:22-slim@sha256:...`), not a mutable tag.
- Run with `--read-only` and mount `--tmpfs /tmp` for the paths that must be writable.
- Drop all capabilities (`--cap-drop=ALL`) and add back only specifics
  (e.g. `--cap-add=NET_BIND_SERVICE` to bind port 80).
- Add `--security-opt=no-new-privileges` so no child process can gain privileges via
  setuid binaries.
- Never use `--privileged`. It disables almost all isolation. If you need one device,
  pass it with `--device`.
- Scan images in CI (Trivy, Grype, `docker scout`) and fail the build on fixable
  high/critical CVEs.
- Use BuildKit secret mounts (`--mount=type=secret`) for build-time credentials so they
  never land in a layer. See [secrets](14-secrets.md).

## Examples

**Good Example** — non-root, pinned, minimal, hardened

```dockerfile
# Pinned by digest so the base cannot change under you between builds.
FROM gcr.io/distroless/nodejs22-debian12@sha256:abc123...
WORKDIR /app
COPY --chown=10001:10001 . .
USER 10001                       # non-root: an escape lands as an unprivileged user
CMD ["server.js"]                # distroless has no shell to exploit
```

```bash
docker run \
  --read-only --tmpfs /tmp \     # nothing can be written to the image filesystem
  --cap-drop=ALL \               # start from zero Linux capabilities
  --security-opt=no-new-privileges \
  --user 10001:10001 \
  myapp:1.4.2
```

**Bad Example** — root, mutable base, full privileges

```dockerfile
FROM node:latest                 # mutable tag: contents change unpredictably
COPY . .
ENV DB_PASSWORD=hunter2          # secret baked into an immutable, cached layer
CMD ["node", "server.js"]        # runs as root by default
```

```bash
# --privileged disables seccomp, AppArmor, and capability limits at once.
docker run --privileged myapp:latest
```

## Common Mistakes

- Running as root because "it works" — the default, and the most common escalation path.
- Using `latest` or an unpinned tag, so a rebuild silently pulls new, unaudited code.
- Baking API keys or passwords into `ENV` or `COPY`, where they persist in image layers
  and registry history forever.
- Reaching for `--privileged` to fix a permission error instead of granting one
  `--cap-add` or `--device`.
- A fat base image (full `ubuntu`) shipping a shell, `curl`, and compilers an attacker
  can use for lateral movement.
- Never scanning images, so known CVEs ship to production.

## Production Tips

- Enforce a default seccomp and AppArmor/SELinux profile; do not run with
  `--security-opt seccomp=unconfined`.
- Gate deploys on image signing and provenance (Sigstore/cosign) so only built-and-scanned
  images run.
- Re-scan running images on a schedule — a CVE disclosed after build still affects you.
- Set resource limits (see [resource limits](17-resource-limits.md)) so a compromised
  container cannot exhaust the node.

## AI Review Checklist

- Does the container run as a non-root `USER` / `--user`?
- Is the base image pinned by digest and scanned in CI?
- Are secrets kept out of layers (BuildKit secret mounts, not `ENV`/`COPY`)?
- Is `--cap-drop=ALL` used with a minimal `--cap-add` set, and no `--privileged`?
- Is the root filesystem read-only with an explicit writable `tmpfs` where needed?
- Is `no-new-privileges` set?
- Is the base image minimal (distroless/`-slim`), not a full OS?

## Related

- `knowledge/docker/14-secrets.md`
- `knowledge/docker/03-images.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/09-image-optimization.md`
