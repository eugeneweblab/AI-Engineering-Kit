---
id: linux/22-containers
topic: linux
slug: containers
title: "Containers"
type: doc
order: 22
status: ready
tags: [linux, containers]
related: [linux/06-processes, linux/17-security, linux/21-firewall, linux/08-systemd, linux/25-production]
when_to_use: "Read before building, running, or reviewing containerized workloads on a Linux host."
---
# Containers

## Purpose

This document defines how containers work on Linux and how to run them safely: what they
actually are (namespaces and cgroups, not virtual machines), how to build lean images, and
how to avoid the security and resource pitfalls specific to the Linux kernel. It is written
so an agent can containerize a workload without shipping a root-privileged, unbounded, or
bloated image.

A container answers "how do I run this process in an isolated, reproducible slice of the
host?". The isolation is real but shallower than a VM — the container shares the host
kernel, which shapes every security decision.

## Why It Matters

A container is a normal Linux process with a restricted view of the system, not a separate
machine. That distinction is the source of most container security incidents: a process
running as UID 0 inside a container is often UID 0 on the host if it escapes, and a
container with no memory limit can OOM-kill its neighbors. Meanwhile a careless image
bakes in secrets, build tools, and a 2 GB base layer that slows every deploy and widens
the attack surface. Because containers are the default deployment unit, these mistakes
replicate across an entire fleet.

## Core Principles

- **A container shares the host kernel.** It is isolation via namespaces and cgroups, not
  a VM. A kernel vulnerability is a shared risk; container root is close to host root.
- **Run as a non-root user.** Drop from UID 0 inside the container so an escape does not
  hand over host privileges. Root-by-default is the single most common container flaw.
- **Set resource limits.** Without CPU and memory limits, one container can starve every
  other workload on the host. Bound them explicitly.
- **Images are immutable artifacts.** Build once, tag by digest, and never patch a running
  container. Rebuild and redeploy — a mutated container is unreproducible.
- **Minimize the image.** Every package in the image is attack surface and download
  weight. Ship only the runtime and the app.

## Best Practices

- Use a minimal base (`distroless`, `alpine`, or a slim runtime) and multi-stage builds so
  compilers and build deps never reach the final image.
- Add a dedicated user and `USER` directive; never let the default `CMD` run as root.
- Set `--memory` and `--cpus` (or Compose/Kubernetes limits) on every container so cgroups
  enforce a ceiling.
- Drop Linux capabilities you do not need (`--cap-drop ALL`, add back only what is
  required) and run with `--read-only` root filesystem plus explicit writable volumes.
- Never bake secrets into image layers — they persist in the layer history even if later
  "deleted". Inject them at runtime via env or mounted files/secret stores.
- Pin base images by digest (`@sha256:...`), not a floating tag like `latest`, so builds
  are reproducible and cannot silently change.
- Scan images for known CVEs in CI (`trivy`, `grype`) and rebuild to pick up base-image
  patches on a schedule.
- Run one main process per container and let the init system (or `--init`) reap zombies;
  do not cram a service manager inside.

## Examples

**Good Example** — multi-stage, non-root, pinned, minimal

```dockerfile
# Build stage: compilers and dev deps stay here, never shipped.
FROM golang:1.24@sha256:<digest> AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app ./cmd/server

# Runtime stage: distroless, non-root, tiny attack surface.
FROM gcr.io/distroless/static@sha256:<digest>
COPY --from=build /app /app
USER 65532:65532          # nonroot: an escape does not yield host root
ENTRYPOINT ["/app"]
```

```bash
# Run with explicit resource ceilings and dropped privileges.
docker run --read-only --cap-drop ALL \
  --memory 512m --cpus 1.0 --pids-limit 200 \
  myapp@sha256:<digest>
```

**Bad Example** — root, unbounded, secrets baked in, floating tag

```dockerfile
FROM ubuntu:latest                 # floating tag: build is not reproducible
RUN apt-get update && apt-get install -y build-essential python3  # build tools shipped
COPY . /app                        # copies .git, tests, and local files too
ENV API_KEY=sk-live-abc123         # secret persists forever in the image layers
CMD ["python3", "/app/server.py"]  # runs as root, no user, no limits set
# No memory/CPU cap: this container can OOM-kill everything else on the host.
```

## Common Mistakes

- Running the container process as root, so a container escape becomes host compromise.
- Omitting memory/CPU limits, letting one container starve or OOM the whole host.
- Baking secrets or `.env` files into image layers, where they persist in history.
- Using `latest` (or any moving tag), making builds unreproducible and rollbacks unclear.
- Shipping the build toolchain in the final image instead of using a multi-stage build.
- Treating a container like a VM — SSHing in and mutating it live instead of rebuilding.
- Assuming container isolation is VM-strength and running untrusted code without extra
  sandboxing (gVisor, Kata, or a real VM).

## Production Tips

- Manage container lifecycle with systemd units or an orchestrator so containers restart
  on failure and start on boot, rather than a detached `docker run`.
- Centralize container logs to the host journal or a log pipeline; container stdout is
  ephemeral and dies with the container.
- Set health checks so the orchestrator can detect and replace a hung container.
- Remember Docker rewrites host `iptables`; verify published ports against your
  [firewall](21-firewall.md) policy rather than assuming they are covered.

## AI Review Checklist

- Does the container run as a non-root user (`USER` set, not UID 0)?
- Are memory, CPU, and pid limits set on every container?
- Are base images pinned by digest rather than a floating tag?
- Is a multi-stage build used so build tools and dev deps are excluded?
- Are secrets injected at runtime, never baked into image layers?
- Are unneeded Linux capabilities dropped and the root filesystem read-only where possible?
- Are images scanned for CVEs, and is untrusted code given stronger isolation than a plain
  container?

## Related

- `knowledge/linux/06-processes.md`
- `knowledge/linux/17-security.md`
- `knowledge/linux/21-firewall.md`
- `knowledge/linux/08-systemd.md`
- `knowledge/linux/25-production.md`
