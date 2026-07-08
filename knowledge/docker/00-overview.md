---
id: docker/00-overview
topic: docker
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [docker, overview]
related: [docker/02-docker-architecture, docker/03-images, docker/04-containers, docker/08-dockerfile, docker/12-docker-compose]
when_to_use: "Read first when starting any Docker work, to orient yourself and find the right deep-dive doc."
---
# Overview

## Purpose

This document is the map of the Docker topic. It orients an agent to what Docker
is, the mental model behind it, and which sibling doc to open for a specific task.
It is not a tutorial — each concept has its own dedicated doc. Read this to route
yourself, then follow the links.

Docker packages an application and everything it needs to run — code, runtime,
system libraries, configuration — into an **image**, then runs that image as an
isolated **container**. The promise is "build once, run anywhere the Docker Engine
runs," which removes the "works on my machine" class of bugs.

## Why It Matters

An agent writing Docker configuration is writing the boundary between the app and
the operating system. Mistakes here do not surface as compile errors; they surface
as bloated images, containers that leak secrets, data lost on restart, or a build
that passes in CI and fails in production. Because a Dockerfile and a Compose file
are the executable definition of your deployment environment, they are held to the
same rigor as production code, not treated as throwaway scripts.

## Core Principles

- **Images are immutable; containers are disposable.** Never store state or fix
  data inside a running container. Rebuild the image or mount a volume instead.
- **A container is a process, not a virtual machine.** It shares the host kernel.
  Treat it as one main process with a clear lifecycle, not a place to run an init
  system and many daemons.
- **Reproducibility over convenience.** Pin versions, order build steps for cache
  reuse, and keep the build declarative so the same input yields the same image.
- **Least privilege by default.** Run as a non-root user, drop capabilities, keep
  images minimal. Every extra package or privilege is attack surface.

## How the Docs Fit Together

Read them roughly in order; jump to the one matching your task.

- **[01-installation](01-installation.md)** — set up the Docker Engine / Desktop and
  verify the install. Start here on a fresh machine.
- **[02-docker-architecture](02-docker-architecture.md)** — the client, daemon,
  registry, and how a `docker run` actually flows through the system. Read this to
  build a correct mental model before anything else.
- **[03-images](03-images.md)** — what an image is, layers, tags, digests, and how
  the build cache works. Foundational for every build task.
- **[04-containers](04-containers.md)** — the container lifecycle, PID 1, signals,
  and stateless design.
- **[05-volumes](05-volumes.md)** — how to persist data that must outlive a
  container. Pairs with **[06-bind-mounts](06-bind-mounts.md)** for local dev.
- **[07-networks](07-networks.md)** — how containers reach each other and the world.
- **[08-dockerfile](08-dockerfile.md)** — authoring the build recipe correctly.
  Then **[11-multi-stage-builds](11-multi-stage-builds.md)** and
  **[09-image-optimization](09-image-optimization.md)** to make it small and fast,
  with **[10-buildkit](10-buildkit.md)** as the modern build engine.
- **[12-docker-compose](12-docker-compose.md)** — defining and running multi-service
  stacks locally, alongside **[13-environment-variables](13-environment-variables.md)**
  and **[14-secrets](14-secrets.md)** for configuration.
- **[15-healthchecks](15-healthchecks.md)**, **[16-logging](16-logging.md)**,
  **[17-resource-limits](17-resource-limits.md)**, and **[18-security](18-security.md)**
  — the operational concerns for running containers safely.
- **[22-production](22-production.md)**, **[26-best-practices](26-best-practices.md)**,
  and the **[98-production-checklist](98-production-checklist.md)** /
  **[99-ai-review-checklist](99-ai-review-checklist.md)** — pull it together before
  shipping. **[100-common-antipatterns](100-common-antipatterns.md)** lists the
  traps to avoid.

## Best Practices

- Open the specific doc for the task instead of guessing — Docker's failure modes
  are subtle and each doc encodes the non-obvious rules.
- When authoring a build, read **03-images** and **08-dockerfile** together; layers
  and cache behavior explain most "why is my image huge / slow" questions.
- When something must survive `docker rm`, stop and read **05-volumes** first —
  data loss is the most common and least reversible Docker mistake.

## Common Mistakes

- Treating a container as a persistent server you SSH into and patch, rather than a
  rebuildable artifact — see **04-containers**.
- Writing a Dockerfile without reading how the build cache works, producing slow
  builds and bloated images — see **03-images**, **09-image-optimization**.
- Storing database files inside the container's writable layer, losing them on the
  next deploy — see **05-volumes**.
- Baking secrets into image layers, where they persist forever — see **14-secrets**.

## AI Review Checklist

- Does the change reference the correct dedicated doc rather than improvising Docker
  rules from memory?
- Is state persisted via a volume (**05-volumes**), not the container layer?
- Is the image built for reproducibility and least privilege (**03-images**,
  **08-dockerfile**, **18-security**)?
- Are secrets and config kept out of image layers (**14-secrets**)?

## Related

- `knowledge/docker/02-docker-architecture.md`
- `knowledge/docker/03-images.md`
- `knowledge/docker/04-containers.md`
- `knowledge/docker/08-dockerfile.md`
- `knowledge/docker/12-docker-compose.md`
