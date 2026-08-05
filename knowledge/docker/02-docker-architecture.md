---
id: docker/02-docker-architecture
topic: docker
slug: docker-architecture
title: "Docker Architecture"
type: doc
order: 2
status: ready
tags: [docker, docker-architecture, node_modules]
related: [docker/00-overview, docker/03-images, docker/04-containers, docker/07-networks, docker/18-security]
when_to_use: "Read before debugging why a Docker command behaves unexpectedly, or before reasoning about build context, sockets, or the daemon."
---
# Docker Architecture

## Purpose

This document explains what actually happens when you run a Docker command: the
client-daemon-registry model, where the build context comes from, and why a
container is an isolated process rather than a virtual machine. An agent that holds
this model correctly avoids a whole category of "why did it do that?" bugs.

## Why It Matters

Almost every confusing Docker behavior — a slow build that ships gigabytes, a
command that runs as root on the host, a path that does not exist inside the
container — comes from not knowing which component is doing the work. The `docker`
CLI is a thin client; the real work happens in a privileged daemon over a socket.
Not seeing that boundary leads to security holes (exposing the socket) and
performance surprises (sending a huge build context). The architecture is the
mental model that makes the rest of Docker predictable.

## Core Principles

- **The client talks to a daemon over an API.** `docker` sends requests to
  `dockerd`; the daemon builds, runs, and manages everything. They can be on
  different hosts.
- **The daemon is root-equivalent.** Anything with access to the Docker socket can
  control the host. The socket is a trust boundary, not a convenience.
- **The build context is sent to the daemon.** `docker build .` uploads the
  directory (minus `.dockerignore`) to the daemon before the first instruction runs.
- **Containers share the host kernel.** Isolation comes from Linux namespaces
  (what a process can see) and cgroups (what it can use), not hardware
  virtualization. This is why containers are lightweight but not a security
  sandbox by themselves.

## Best Practices

- Keep the build context small with a `.dockerignore` (exclude `.git`,
  `node_modules`, build output). A large context slows every build and can leak
  files into images. See [09-image-optimization](09-image-optimization.md).
- Never bind-mount `/var/run/docker.sock` into a container unless you fully accept
  that the container then controls the host. Prefer a proxy or rootless build tools.
- Reason about "where does this path resolve?" — the client's cwd, the daemon's
  filesystem, and the container's filesystem are three different places.
- Use `docker context` to target remote daemons explicitly rather than juggling
  `DOCKER_HOST` env vars ad hoc.
- Pull images from a registry you trust and pin by digest for reproducibility; the
  registry is the third component in the model. See [19-registry](19-registry.md).

## Examples

**Good Example** — small context, explicit remote daemon

```bash
# .dockerignore keeps the context tiny, so the upload to the daemon is fast
# and secrets/junk never reach the build.
cat .dockerignore
# .git
# node_modules
# **/*.env

# Target a named remote daemon explicitly instead of mutating global env.
docker --context staging build -t app:ci .
# The client streams ONLY the filtered context to the staging daemon,
# which runs the build and stores the image on that host.
```

**Bad Example** — huge context and host takeover

```bash
# No .dockerignore: the entire repo, including .git and node_modules, is
# uploaded to the daemon on every build. Slow, and may bake secrets in.
docker build -t app .

# Mounting the daemon socket gives this container root over the whole host.
# Any compromise inside the container is a full host compromise.
docker run -v /var/run/docker.sock:/var/run/docker.sock some/ci-image
```

## Common Mistakes

- Assuming `docker build` reads files from the client at build time — it reads from
  the uploaded context; a file outside the context simply does not exist.
- Treating a container as a VM: expecting a full init system, multiple services, or
  a persistent machine to SSH into and patch.
- Exposing the Docker socket (over TCP without TLS, or bind-mounted) and turning a
  container escape into host root.
- Forgetting `.dockerignore`, then wondering why builds are slow and images are big.
- Confusing paths across the client / daemon / container filesystems when writing
  volume and mount arguments.

## Production Tips

- If you must expose the daemon over the network, require mutual TLS; never open
  `2375/tcp` (plaintext) — it is a well-known target for cryptominers.
- Understand which storage driver the daemon uses (`overlay2` is the current
  default); it governs layer performance and disk usage.
- On multi-tenant CI, give each job an isolated daemon or use rootless/daemonless
  builders (BuildKit) so jobs cannot see each other's images. See
  [10-buildkit](10-buildkit.md).

## AI Review Checklist

- Is a `.dockerignore` present and does it exclude VCS, deps, and secrets?
- Is the Docker socket kept off the network and out of containers?
- Does the code correctly distinguish client, daemon, and container filesystems?
- Are remote daemons targeted via `docker context`, not scattered env vars?
- Is the container relied on for isolation only where namespaces/cgroups actually
  provide it, with hardening added where they do not?

## Related

- `knowledge/docker/00-overview.md`
- `knowledge/docker/03-images.md`
- `knowledge/docker/04-containers.md`
- `knowledge/docker/07-networks.md`
- `knowledge/docker/18-security.md`
