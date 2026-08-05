---
id: docker/readme
topic: docker
slug: readme
title: "Docker Engineering Standards"
type: index
order: -1
status: ready
tags: [docker, readme]
related: []
when_to_use: "Read first when starting any Docker work, to see how this section's docs fit together."
---
# Docker Engineering Standards

## Purpose

This section defines the engineering standards for packaging and running applications with
Docker. Docker packages an application and everything it needs — code, runtime, system
libraries, configuration — into an image, then runs that image as an isolated container,
removing the "works on my machine" class of bugs.

A Dockerfile and a Compose file are the executable definition of your deployment environment,
so they are held to the same rigor as production code, not treated as throwaway scripts.
Mistakes do not surface as compile errors; they surface as bloated images, leaked secrets,
data lost on restart, or a build that passes in CI and fails in production. The docs move
from the architecture and mental model, through building images correctly, into
configuration, operations, and production readiness.

These standards apply to both human developers and AI coding assistants.

---

## Scope

This documentation covers:

- Docker architecture, images, and containers
- Volumes, bind mounts, and networks
- Dockerfile authoring, image optimization, BuildKit, and multi-stage builds
- Docker Compose, environment variables, and secrets
- Healthchecks, logging, and resource limits
- Security, registries, and container debugging
- Development workflow and production operation
- Orchestration, monitoring, performance, and CI integration

---

## Learning Path

Study the documents in the following order.

## Foundations

- 00. Overview
- 01. Installation
- 02. Docker Architecture
- 30. Engineering Principles

## Images & Containers

- 03. Images
- 04. Containers
- 05. Volumes
- 06. Bind Mounts
- 07. Networks

## Building Images

- 08. Dockerfile
- 09. Image Optimization
- 10. BuildKit
- 11. Multi-Stage Builds

## Configuration

- 12. Docker Compose
- 13. Environment Variables
- 14. Secrets

## Operate & Secure

- 15. Healthchecks
- 16. Logging
- 17. Resource Limits
- 18. Security
- 19. Registry
- 20. Container Debugging

## Deliver

- 21. Development Workflow
- 22. Production
- 23. Orchestration
- 24. Monitoring
- 25. Performance
- 26. Best Practices
- 27. Troubleshooting
- 28. Tooling
- 29. CI Integration

## Verification

- 98. Production Checklist
- 99. AI Review Checklist
- 100. Common Anti-Patterns

---

## Engineering Principles

Every Docker change should satisfy the following principles:

- Treat images as immutable and containers as disposable; never fix data inside a container.
- Treat a container as a single process with a clear lifecycle, not a virtual machine.
- Favor reproducibility over convenience: pin versions and order steps for cache reuse.
- Run as a non-root user, drop capabilities, and keep images minimal.
- Persist anything that must outlive a container in a volume, not the writable layer.
- Keep secrets and config out of image layers, where they persist forever.
- Build small with multi-stage builds and a well-ordered cache.
- Consult the specific doc for the task; Docker's failure modes are subtle.

---

## Intended Audience

These standards are intended for:

- DevOps and Platform Engineers
- Backend and Fullstack Engineers
- SRE Engineers
- Release Engineers
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps images small, reproducible, and least-privilege, so the
boundary between the app and the operating system is defined with production-grade rigor.
