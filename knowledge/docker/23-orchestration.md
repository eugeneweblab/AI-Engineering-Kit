---
id: docker/23-orchestration
topic: docker
slug: orchestration
title: "Orchestration"
type: doc
order: 23
status: ready
tags: [docker, orchestration]
related: [docker/22-production, docker/15-healthchecks, docker/17-resource-limits, docker/24-monitoring, docker/12-docker-compose]
when_to_use: "Read when running containers across multiple hosts — scaling, scheduling, rolling deploys, and self-healing."
---
# Orchestration

## Purpose

This document defines how to run containers at scale across multiple hosts: scheduling,
replication, health-gated rollouts, self-healing, and service discovery. It is written so
an agent can configure an orchestrator (Kubernetes, or Swarm for smaller stacks) that
stays available through failures and deploys.

An orchestrator turns a fleet of hosts into one pool: you declare the desired state
(N replicas of this image, with these limits and probes) and it continuously reconciles
reality toward it — rescheduling on node failure, replacing unhealthy replicas, and
rolling out new versions without downtime.

## Why It Matters

Once traffic outgrows a single host, the failure modes change: nodes die mid-request,
deploys must not drop traffic, and a bad rollout can take down the whole service in
seconds. Orchestration is what makes those events survivable — but only if the workload
is declared correctly. Probes that lie, missing resource requests, and non-graceful
shutdown all defeat the orchestrator's guarantees, turning routine events into outages.
The container contract you define here is what the platform enforces under load.

## Core Principles

- **Declare desired state, don't script actions.** Tell the orchestrator *what* you want
  (replicas, image, limits); let it decide *how* to converge. Imperative fixes drift.
- **Health gates every change.** Rollouts, scaling, and traffic routing all key off
  readiness/liveness probes. Wrong probes make every guarantee hollow.
- **Design for reschedule.** Any replica can be killed and moved at any time. Workloads
  must be stateless or externalize state; startup must be fast and idempotent.
- **Separate liveness from readiness.** Liveness restarts a wedged process; readiness
  gates traffic. Conflating them causes restart loops or traffic to unready pods.
- **Set requests and limits.** The scheduler needs requests to place pods and limits to
  protect nodes. Omitting them causes noisy-neighbor outages and evictions.

## Best Practices

- Run more than one replica of anything that serves traffic, and spread replicas across
  nodes/zones (anti-affinity / spread constraints) so one node loss is survivable.
- Define **liveness** (is the process wedged? restart it) and **readiness** (can it serve
  now? gate traffic) probes separately, with a `startupProbe` for slow boots. See
  [healthchecks](15-healthchecks.md).
- Set resource **requests** (for scheduling) and **limits** (for isolation) on every
  container. See [resource limits](17-resource-limits.md).
- Use rolling updates with `maxUnavailable`/`maxSurge` tuned so capacity never dips below
  demand; keep the previous version ready for instant rollback.
- Configure a `PodDisruptionBudget` (k8s) so voluntary disruptions (node drains) cannot
  take all replicas at once.
- Ensure graceful shutdown: the app handles `SIGTERM` and finishes within
  `terminationGracePeriodSeconds`. See [production](22-production.md).
- Externalize config/secrets via ConfigMaps/Secrets, and use the platform's service
  discovery (DNS) rather than hardcoded IPs.

## Examples

**Good Example** — replicated, probed, resource-bounded, rolling

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: myapp }
spec:
  replicas: 3                       # survive a single node/pod loss
  strategy:
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }  # never dip below capacity
  template:
    spec:
      terminationGracePeriodSeconds: 30                # time to drain on SIGTERM
      containers:
        - name: app
          image: registry.example.com/myapp@sha256:abc123...   # pinned by digest
          resources:
            requests: { cpu: "250m", memory: "256Mi" }  # scheduler placement
            limits:   { cpu: "1",    memory: "512Mi" }  # node protection
          readinessProbe:            # gate traffic until dependencies are reachable
            httpGet: { path: /ready, port: 8080 }
          livenessProbe:             # restart only a genuinely wedged process
            httpGet: { path: /healthz, port: 8080 }
            periodSeconds: 10
```

**Bad Example** — single replica, one probe, unbounded

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 1                        # any node loss = full outage; no rolling headroom
  template:
    spec:
      containers:
        - name: app
          image: myapp:latest        # mutable tag: replicas can diverge, rollback unclear
          # No resource requests/limits -> unschedulable safely, noisy-neighbor evictions.
          livenessProbe:             # reused as readiness -> restart loops on slow boot,
            httpGet: { path: /, port: 8080 }   # and traffic sent before app is ready
```

## Common Mistakes

- One replica for a stateful-feeling service, so any node failure or deploy is a full
  outage.
- Using one probe for both liveness and readiness: a slow dependency triggers restart
  loops instead of just holding traffic.
- No resource requests, so the scheduler over-packs nodes and the kubelet evicts pods
  under pressure.
- `maxUnavailable` too high (or default) so a rollout drops capacity below demand under
  load.
- No graceful shutdown, so every rolling update and node drain severs in-flight requests.
- Deploying `latest`, making rollback ambiguous and replicas non-identical.
- Hardcoding peer IPs instead of using service DNS, breaking on every reschedule.

## Production Tips

- Prefer a managed orchestrator; the control plane is the hardest part to run correctly.
- Use canary or blue-green for risky changes so a bad version takes a fraction of traffic,
  not all of it.
- Enforce policy at admission (require probes, limits, non-root, signed images) so
  unsafe workloads cannot be scheduled.
- Watch scheduler and eviction events plus per-pod saturation (see [monitoring](24-monitoring.md))
  to catch capacity problems before they cascade.

## AI Review Checklist

- Are there multiple replicas spread across nodes/zones for anything serving traffic?
- Are liveness and readiness probes defined separately (plus a startup probe if boot is
  slow)?
- Are resource requests and limits set on every container?
- Is the rollout strategy configured to never drop below required capacity, with easy
  rollback?
- Does the workload handle `SIGTERM` within the grace period?
- Is the image pinned by digest and config/secrets externalized via ConfigMaps/Secrets?
- Is a disruption budget set so drains cannot remove all replicas at once?

## Related

- `knowledge/docker/22-production.md`
- `knowledge/docker/15-healthchecks.md`
- `knowledge/docker/17-resource-limits.md`
- `knowledge/docker/24-monitoring.md`
- `knowledge/docker/12-docker-compose.md`
