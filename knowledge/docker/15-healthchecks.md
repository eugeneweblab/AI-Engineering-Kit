---
id: docker/15-healthchecks
topic: docker
slug: healthchecks
title: "Healthchecks"
type: doc
order: 15
status: ready
tags: [docker, healthchecks]
related: [docker/12-docker-compose, docker/16-logging, docker/22-production, docker/23-orchestration, docker/04-containers]
when_to_use: "Read before adding a HEALTHCHECK to an image or gating one service on another's readiness."
---
# Healthchecks

## Purpose

This document defines how to tell Docker whether a container is actually *working*,
not merely running: what a healthcheck should probe, how to tune its timing, and how
readiness gates dependent services. It is written so an agent can add a `HEALTHCHECK`
or a compose healthcheck that reflects real service health and does not create false
signals.

A running process is not the same as a working service. A web app can be "up" while
its event loop is deadlocked or its database connection is dead. Healthchecks close
that gap by turning "is the process alive?" into "can this service do its job?".

## Why It Matters

Everything downstream trusts the health signal. Compose's `service_healthy` gate,
orchestrator restart and traffic-routing decisions, and load-balancer membership all
key off it. A missing healthcheck means a broken container silently keeps receiving
traffic and returning errors. A *bad* healthcheck is worse: a probe that always
passes hides real outages, and one that is too strict or too slow flaps, triggering
restart loops and evicting healthy containers. The healthcheck is the definition of
"working" for the whole platform, so it must mean exactly that.

## Core Principles

- **Probe readiness, not liveness of the process.** Check that the service can serve
  a request (hit a real endpoint or dependency), not just that PID 1 exists.
- **Keep the check cheap and local.** It runs on every interval; an expensive probe
  adds load and can itself cause the failure it is meant to detect.
- **Do not cascade dependencies into the check.** An app's healthcheck should test
  the app, not fail because a downstream is briefly slow — that turns one outage into
  many restarts.
- **Tune timing to the service.** `start_period` must cover real startup, or the
  container is killed mid-boot; `interval`/`retries` set how fast a failure is caught.
- **Exit codes are the contract.** `0` = healthy, `1` = unhealthy. Nothing else.

## Best Practices

- Add a `HEALTHCHECK` to the image (so it travels everywhere the image runs) or a
  compose `healthcheck:` for stack-specific tuning; prefer the image for portability.
- Point the probe at a dedicated lightweight endpoint (e.g. `/healthz`) that verifies
  the app can handle a request but does not run heavy business logic.
- Set `start_period` generously (e.g. `30s`) so slow-starting apps are not marked
  unhealthy and killed before they finish booting.
- Keep `timeout` shorter than `interval`, and pick `retries` so transient blips do
  not flip state but real failures are caught within an acceptable window.
- Prefer a check tool already in the image. Do not add `curl` just for the probe on a
  minimal/distroless image; use the app's own health binary or a small built-in.
- Use `CMD-SHELL` when you need shell features (pipes, `||`), `CMD` for a direct exec.
- In compose, gate dependents with `depends_on: { db: { condition: service_healthy }}`
  so an app never starts against a not-yet-ready dependency.

## Examples

**Good Example** — cheap local readiness probe, tuned timing, health-gated dependent

```dockerfile
# HEALTHCHECK travels with the image → same signal everywhere it runs
HEALTHCHECK --interval=15s --timeout=3s --start-period=30s --retries=3 \
  CMD wget -qO- http://localhost:8080/healthz || exit 1
#   ^ hits a dedicated endpoint that confirms the app can serve a request
#   ^ start-period covers real boot time so a slow start is not killed
#   ^ exit 1 on failure → Docker marks the container unhealthy
```

```yaml
# compose.yaml — dependent waits for real readiness, not just container start
services:
  app:
    image: myorg/app:1.4.2
    depends_on:
      db:
        condition: service_healthy   # app starts only once db passes its check
```

**Bad Example** — checks nothing real, cascades a dependency, no start grace

```dockerfile
# Passes as long as PID 1 exists — a deadlocked app still reports "healthy"
HEALTHCHECK CMD echo ok

# Or: too strict and cascading — one slow downstream fails THIS service,
# triggering needless restart loops, and no start-period so it dies mid-boot.
HEALTHCHECK --interval=2s --timeout=10s \
  CMD curl -f http://db:5432 && curl -f http://payments/api || exit 1
```

## Common Mistakes

- A trivial check (`echo ok`, `exit 0`) that always passes and hides real outages.
- Probing process liveness instead of request readiness, so a deadlocked app looks
  healthy.
- Omitting `start_period`, so a slow-booting container is killed before it is ready.
- Checking downstream dependencies inside the probe, turning one outage into a
  restart storm across services.
- Relying on `depends_on` alone (start order) and expecting it to wait for readiness.
- Adding heavyweight tooling (installing `curl`) to a minimal image solely for the
  probe, bloating the image and its attack surface.

## Production Tips

- Alert on `unhealthy` transitions and on restart-loop counts; a flapping healthcheck
  usually means a mis-tuned probe, not a broken app.
- Separate *liveness* (restart me) from *readiness* (route traffic to me) in
  orchestrators — Docker's single healthcheck often maps to readiness.
- Keep the health endpoint out of access logs and unauthenticated-but-harmless, so
  probe traffic does not pollute metrics or leak internal state.

## AI Review Checklist

- Does the healthcheck probe real request readiness, not just process existence?
- Is `start_period` long enough to cover the service's real startup time?
- Are `timeout < interval` and `retries` tuned to avoid flapping yet catch failures
  promptly?
- Does the probe avoid checking downstream dependencies (no cascade)?
- Are dependent services gated on `condition: service_healthy`, not bare
  `depends_on`?
- Does the check avoid adding heavy tooling to an otherwise minimal image?

## Related

- `knowledge/docker/12-docker-compose.md`
- `knowledge/docker/16-logging.md`
- `knowledge/docker/22-production.md`
- `knowledge/docker/23-orchestration.md`
- `knowledge/docker/04-containers.md`
