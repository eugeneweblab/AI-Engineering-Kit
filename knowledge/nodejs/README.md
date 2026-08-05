---
id: nodejs/readme
topic: nodejs
slug: readme
title: "Node.js Engineering Standards"
type: index
order: -1
status: ready
tags: [nodejs, readme, engines, package.json]
related: []
when_to_use: "Read first when starting any Node.js work, to see how this section's docs fit together."
---
# Node.js Engineering Standards

## Purpose

This section defines the engineering standards, mental models, and best practices for
building backend services, CLIs, and tooling on the Node.js runtime. Node.js is a
single-threaded, event-driven JavaScript runtime built on V8: work is fast when it stays
non-blocking, and the whole process stalls when it does not. Most Node defects are not
logic errors but model errors — blocking the event loop, leaking file descriptors,
mixing module systems, or trusting the network to be fast.

The objective is a consistent path to production-safe code: code that keeps I/O
asynchronous, fails loud and closed, pins its runtime and dependencies, and treats all
external input as hostile. From the execution model through concurrency, operability, and
delivery, these docs keep an agent on the path that survives production rather than the
one that only works on a laptop.

These standards are written for both human engineers and AI coding assistants, so that
either can build, review, and operate Node.js code to the same bar.

---

## Scope

This documentation covers:

- The runtime, event loop, and module systems (ESM and CommonJS)
- Package management and reproducible installs
- File system, streams, buffers, events, and HTTP
- Process control, child processes, worker threads, and clustering
- Environment and configuration
- Error handling, logging, security, performance, and memory management
- Testing, debugging, and CLI development
- Background jobs, microservices, deployment, and monitoring
- Tooling, best practices, and engineering principles

---

## Learning Path

Study the documents in the following order.

### Foundations
- [00. Overview](00-overview.md)
- [01. Node.js Runtime](01-nodejs-runtime.md)
- [02. Event Loop](02-event-loop.md)
- [03. Modules](03-modules.md)

### Project Setup
- [04. Package Management](04-package-management.md)
- [14. Environment](14-environment.md)
- [15. Configuration](15-configuration.md)

### I/O Building Blocks
- [05. File System](05-file-system.md)
- [06. Streams](06-streams.md)
- [07. Buffers](07-buffers.md)
- [08. Events](08-events.md)
- [09. HTTP](09-http.md)

### Concurrency & Processes
- [10. Process](10-process.md)
- [11. Child Process](11-child-process.md)
- [12. Worker Threads](12-worker-threads.md)
- [13. Cluster](13-cluster.md)

### Operability
- [16. Error Handling](16-error-handling.md)
- [17. Logging](17-logging.md)
- [18. Security](18-security.md)
- [19. Performance](19-performance.md)
- [20. Memory Management](20-memory-management.md)
- [27. Monitoring](27-monitoring.md)

### Delivery
- [21. Testing](21-testing.md)
- [22. Debugging](22-debugging.md)
- [23. CLI Development](23-cli-development.md)
- [24. Background Jobs](24-background-jobs.md)
- [25. Microservices](25-microservices.md)
- [26. Deployment](26-deployment.md)
- [28. Best Practices](28-best-practices.md)
- [29. Tooling](29-tooling.md)
- [30. Engineering Principles](30-engineering-principles.md)

### Verification
- [98. Production Checklist](98-production-checklist.md)
- [99. AI Review Checklist](99-ai-review-checklist.md)
- [100. Common Anti-Patterns](100-common-antipatterns.md)

---

## Engineering Principles

Every Node.js change should satisfy the following principles:

- Never block the event loop; keep CPU-bound work off the request path.
- Treat all I/O as asynchronous; reserve `*Sync` APIs for startup only.
- Fail loud and fail closed — surface unhandled rejections and crash for a supervisor to restart.
- Target an Active LTS version and pin it in `.nvmrc` and `package.json` `engines`.
- Reproduce installs from a committed lockfile so every environment runs the same tree.
- Keep the module system (ESM vs CommonJS) consistent across the project.
- Prefer the standard library before adding a dependency.
- Keep processes stateless so they can be restarted and scaled horizontally.
- Treat all external input as hostile; the runtime has real file, network, and process access.
- Design for observability — structured logs, metrics, and health checks — from the start.

---

## Intended Audience

These standards are intended for:

- Backend Engineers
- Fullstack Engineers
- Platform and DevOps Engineers
- Tech Leads
- Software Architects
- AI Coding Assistants
- Code Reviewers

---

## Summary

Following these standards keeps Node.js code non-blocking, reproducible, and
production-safe as it grows from a single script into a fleet of services.
