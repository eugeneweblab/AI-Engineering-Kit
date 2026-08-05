---
id: docker/22-production
topic: docker
slug: production
title: "Docker Production"
type: doc
order: 22
status: ready
tags: [docker, production]
related: [docker/15-healthchecks, docker/17-resource-limits, docker/18-security, docker/16-logging, docker/23-orchestration]
when_to_use: "Read before shipping any container to a production environment or reviewing a production deployment config."
---
# Docker Production

## Purpose

This document defines what a container must have before it runs in production: pinned
images, resource limits, healthchecks, graceful shutdown, non-root execution, and
externalized configuration. It is written so an agent can promote a container from "runs
on my laptop" to "safe to schedule under load."

Production is where every shortcut taken earlier comes due. The runtime is hostile:
nodes get rescheduled, memory is contended, traffic spikes, and the orchestrator will
kill and restart your container without warning. A production-ready container survives all
of that without corrupting data or dropping requests.

## Why It Matters

A container that starts is not a container that is production-ready. Without a memory
limit, one container OOM-kills its neighbors. Without a healthcheck, the load balancer
routes traffic to a hung process. Without graceful shutdown, every deploy drops in-flight
requests and can corrupt writes. These are not edge cases — they happen on the first
rollout under real traffic. The cost of getting production hardening wrong is measured in
outages and data loss, so the bar is the highest in this topic.

## Core Principles

- **Pin everything.** Deploy images by digest, not by tag, so every replica runs
  identical bytes. See [registry](19-registry.md).
- **Bound every resource.** Set memory and CPU limits so one container cannot starve the
  node. Unbounded is a latent outage. See [resource limits](17-resource-limits.md).
- **Be observable and probeable.** Expose a healthcheck and structured logs so the
  orchestrator and operators can see the container's true state.
- **Shut down gracefully.** Trap `SIGTERM`, stop accepting work, drain in-flight requests,
  then exit before the kill timeout.
- **Externalize configuration.** Config and secrets come from the environment at runtime,
  never baked into the image. See [environment variables](13-environment-variables.md).
- **Assume restarts.** The container will be killed and rescheduled routinely; it must be
  stateless or persist state to a volume/service.

## Best Practices

- Reference the image by digest in the deployment manifest; never `latest`.
- Set both memory and CPU limits (and requests, under an orchestrator) sized from
  observed usage plus headroom, not guesses.
- Define a `HEALTHCHECK` (or orchestrator liveness/readiness probe) that checks real
  readiness — dependencies reachable — not just "process alive." See [healthchecks](15-healthchecks.md).
- Handle `SIGTERM`: stop the listener, finish in-flight requests, close DB connections,
  exit 0. Keep it under the platform's grace period (default 10s in Docker, 30s in k8s).
- Run as a non-root user with a read-only root filesystem and dropped capabilities. See
  [security](18-security.md).
- Write logs to stdout/stderr as structured JSON; let the platform collect them. See
  [logging](16-logging.md).
- Set a restart policy (`unless-stopped` / `on-failure` with backoff) so transient crashes
  self-heal without hammering dependencies.

## Examples

**Good Example** — bounded, probeable, graceful, non-root

```yaml
services:
  app:
    image: registry.example.com/myapp@sha256:abc123...   # pinned by digest
    user: "10001:10001"                                   # non-root
    read_only: true
    tmpfs: [/tmp]
    stop_grace_period: 30s                                # time to drain before SIGKILL
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8080/ready"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 20s
    deploy:
      resources:
        limits: { memory: 512M, cpus: "1.0" }             # cannot starve the node
    restart: unless-stopped
    env_file: .env.production                             # config from environment
```

```js
// Graceful shutdown: drain in-flight work on SIGTERM before the grace period ends.
process.on("SIGTERM", async () => {
  server.close();                 // stop accepting new connections
  await inflight.drain();         // finish current requests
  await db.end();                 // release pooled connections cleanly
  process.exit(0);
});
```

**Bad Example** — unbounded, unprobeable, abrupt

```yaml
services:
  app:
    image: myapp:latest       # mutable tag: replicas may run different code
    # No memory limit -> a leak OOM-kills every other container on the node.
    # No healthcheck -> the LB sends traffic to a hung process.
    # No SIGTERM handling in the app -> every deploy drops in-flight requests.
    restart: always
```

## Common Mistakes

- Deploying `latest`, so a rollback target is ambiguous and replicas drift.
- No memory limit, letting one container's leak take down the whole node.
- A healthcheck that only pings the port, reporting "healthy" while the app can't reach its
  database.
- No `SIGTERM` handler, so every rolling deploy severs live connections and risks partial
  writes.
- Running as root with a writable filesystem — a small bug becomes host compromise.
- Baking config/secrets into the image, forcing a rebuild for every environment and
  leaking secrets into layers.
- Storing state on the container's writable layer, losing it on every reschedule.

## Production Tips

- Roll out with health-gated strategies (rolling/blue-green/canary) so an unhealthy image
  never fully replaces a healthy one. See [orchestration](23-orchestration.md).
- Emit metrics (RED/USE) and traces, not just logs, so you can see saturation before it
  becomes an outage.
- Test the SIGTERM path in CI: send the signal and assert the process drains and exits 0
  within the grace period.
- Record the deployed digest and config version so any incident is traceable to exact
  artifacts.

## AI Review Checklist

- Is the image pinned by digest, not a mutable tag?
- Are memory and CPU limits set from observed usage?
- Is there a readiness-aware healthcheck (dependencies checked, not just process alive)?
- Does the app handle `SIGTERM` and drain in-flight work within the grace period?
- Does it run non-root, read-only, with dropped capabilities?
- Are logs structured to stdout and config/secrets sourced from the environment?
- Is all persistent state written to a volume or external service, not the container layer?

## Related

- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/18-security.md`
- `knowledge/docker/16-logging.md`
- `knowledge/docker/23-orchestration.md`
