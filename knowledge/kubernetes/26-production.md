---
id: kubernetes/26-production
topic: kubernetes
slug: production
title: "Kubernetes Production"
type: doc
order: 26
status: ready
tags: [kubernetes, production]
related: [kubernetes/19-resource-management, kubernetes/20-autoscaling, kubernetes/22-security, kubernetes/23-monitoring, kubernetes/98-production-checklist]
when_to_use: "Read before promoting any workload to a production cluster or reviewing a production readiness gate."
---
# Kubernetes Production

## Purpose

This document defines what makes a Kubernetes workload *production-ready*: the
health checks, resource contracts, availability guarantees, and safety rails a
Deployment must have before it serves real traffic. It is written so an agent can
turn a workload that "runs on my cluster" into one that survives node failures,
rollouts, and traffic spikes.

Production readiness is a set of explicit declarations — probes, requests/limits,
replica counts, disruption budgets — that let the control plane keep the workload
healthy without a human watching. A missing declaration is not a default; it is a
gap that fails at the worst time.

## Why It Matters

Kubernetes only protects what you tell it about. Without a readiness probe it routes
traffic to a pod that is still booting; without resource requests the scheduler
overcommits a node and the kernel OOM-kills neighbors; without a PodDisruptionBudget a
node drain can take every replica down at once. Each of these is invisible on a quiet
day and catastrophic during a rollout, an upgrade, or a spike — precisely when
production is under stress. The cost of the missing field is a user-facing outage; the
cost of adding it is a few lines of YAML.

## Core Principles

- **Declare health, don't assume it.** Liveness, readiness, and startup probes tell
  Kubernetes when to route, restart, and wait. No probe means "always ready", which is
  wrong during boot and crashes.
- **Every container states its resources.** `requests` drive scheduling; `limits` cap
  blast radius. Omitting requests makes scheduling a gamble (see
  [resource-management](19-resource-management.md)).
- **Design for disruption.** Nodes die and drain constantly. Run multiple replicas,
  spread them, and set a PodDisruptionBudget so voluntary evictions keep a quorum.
- **Roll forward safely.** Use rolling updates with `maxUnavailable`/`maxSurge` and a
  readiness gate so a bad version cannot replace a good one all at once.
- **No single point of failure.** One replica, one node, one zone is not production.

## Best Practices

- Set a **readiness** probe (gates traffic), a **liveness** probe (restarts a hung
  process), and a **startup** probe for slow boots so liveness does not kill a
  still-initializing container. Make readiness reflect real dependencies (DB reachable),
  liveness reflect only "the process is alive".
- Set CPU and memory **requests** on every container; set a **memory limit** to bound
  the OOM blast radius. Be cautious with CPU limits — they throttle; prefer requests +
  headroom (see [resource-management](19-resource-management.md)).
- Run **>= 2 replicas** and spread with `topologySpreadConstraints` across nodes/zones
  so one failure domain cannot take the service down.
- Define a **PodDisruptionBudget** (`minAvailable`) so drains and upgrades (see
  [upgrades](25-upgrades.md)) cannot evict the whole set.
- Configure **HorizontalPodAutoscaler** on a real signal (see
  [autoscaling](20-autoscaling.md)); pair with `requests` since HPA scales off them.
- Drop the security defaults in place: non-root, read-only root FS, dropped
  capabilities (see [security](22-security.md)).
- Add a `preStop` hook or `terminationGracePeriod` so the pod drains in-flight requests
  before SIGTERM completes.

## Examples

**Good Example** — a Deployment with the production contract declared

```yaml
spec:
  replicas: 3                       # survives a node loss
  template:
    spec:
      topologySpreadConstraints:    # don't stack all replicas on one node/zone
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: api } }
      containers:
        - name: api
          image: registry.example.com/api:1.8.3   # pinned digest/tag, never :latest
          resources:
            requests: { cpu: "250m", memory: "256Mi" }  # scheduler needs these
            limits:   { memory: "512Mi" }                # cap OOM blast radius
          readinessProbe:            # gate traffic until dependencies are up
            httpGet: { path: /readyz, port: 8080 }
          livenessProbe:             # restart only a truly hung process
            httpGet: { path: /healthz, port: 8080 }
            initialDelaySeconds: 20
```

**Bad Example** — no probes, no resources, single replica

```yaml
spec:
  replicas: 1                       # one node drain = full outage
  template:
    spec:
      containers:
        - name: api
          image: api:latest         # unpinned: rollout is non-reproducible
          # no requests  -> scheduler overcommits the node, neighbors OOM-killed
          # no readiness -> traffic sent to a pod that is still booting -> 502s
          # no liveness  -> a hung process is never restarted
```

## Common Mistakes

- Shipping without a readiness probe, so rollouts send traffic to unready pods.
- A liveness probe with no startup probe, killing slow-booting containers in a loop.
- No resource requests, letting the scheduler pack nodes until the kernel OOM-kills.
- Running one replica and calling it highly available.
- No PodDisruptionBudget, so a routine node drain evicts the entire service.
- Using `image: latest`, making the running version unknown and rollback impossible.
- CPU limits set aggressively, causing throttling and latency spikes.

## Production Tips

- Enforce the contract in CI with a policy engine (Kyverno/Gatekeeper): reject any pod
  missing probes, requests, or a non-root securityContext.
- Wire alerts on restart rate, OOMKills, and readiness flapping (see
  [monitoring](23-monitoring.md)) — these predict outages.
- Load-test at expected peak with HPA enabled to confirm scale-up happens before
  saturation, not after.

## AI Review Checklist

- Does every container declare CPU/memory requests and a memory limit?
- Are readiness, liveness, and (for slow boots) startup probes present and meaningful?
- Are there >= 2 replicas spread across nodes/zones?
- Is there a PodDisruptionBudget protecting a minimum available count?
- Is the image pinned to a specific tag/digest, never `latest`?
- Is a securityContext (non-root, dropped caps) applied?
- Is graceful shutdown handled via preStop / terminationGracePeriodSeconds?

## Related

- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/20-autoscaling.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/23-monitoring.md`
- `knowledge/kubernetes/98-production-checklist.md`
