---
id: devops/11-orchestration
topic: devops
slug: orchestration
title: "Orchestration"
type: doc
order: 11
status: ready
tags: [devops, orchestration]
related: [devops/10-containerization, devops/07-deployment-strategies, devops/09-configuration-management, devops/19-high-availability, devops/20-scalability]
when_to_use: "Read before writing or reviewing Kubernetes manifests, or deciding how containers are scheduled, scaled, and kept healthy."
---
# Orchestration

## Purpose

This document defines how many containers are scheduled, kept healthy, scaled, and
networked across a cluster — primarily with Kubernetes. It is written so an agent can
author or review workload manifests without creating pods that cannot be scheduled,
scaled safely, or recovered when a node dies.

Orchestration composes the [container images](10-containerization.md) into a running
system. It relies on those images being well-built and on externalized
[configuration](09-configuration-management.md); it executes the
[deployment strategy](07-deployment-strategies.md) you chose. This doc is about the
cluster-level contract each workload must declare.

## Why It Matters

An orchestrator can only do its job — reschedule failed pods, scale to load, roll out
safely, spread across failure domains — if each workload *tells it the truth* about the
workload's needs. Missing a resource request, a readiness probe, or a replica count does
not fail loudly at deploy time; it fails at 3 a.m. when a node dies and the scheduler
makes the wrong call because you never gave it the information. Most Kubernetes outages
are self-inflicted by manifests that omit the signals the platform needs.

## Core Principles

- **Declare desired state; the controller reconciles.** You describe what should be true
  (N healthy replicas of this image); the orchestrator continuously drives reality toward
  it. Do not imperatively `kubectl` your way to a state you cannot reproduce from manifests.
- **Design for pods to die.** Pods are cattle: any pod can be killed or rescheduled at any
  time. Workloads must be stateless (or explicitly stateful with a StatefulSet + volumes)
  and tolerate restarts.
- **Tell the scheduler the truth.** Resource requests/limits, probes, and affinity are how
  the platform makes correct placement and scaling decisions. Omissions cause bad ones.
- **Health is defined by the app, checked by the platform.** Readiness gates traffic;
  liveness restarts wedged processes. The orchestrator only knows what the probes report.
- **Spread across failure domains.** Replicas concentrated on one node or one zone give
  you the cost of redundancy with none of the protection.

## Best Practices

- Set **resource `requests` and `limits`** on every container. Requests drive scheduling
  and let the autoscaler work; limits prevent one pod from starving neighbors. A pod with
  no requests can land anywhere and get evicted first under pressure.
- Define **readiness and liveness probes** (and `startupProbe` for slow starters).
  Readiness that just returns 200 statically is useless — check real dependencies.
- Run **multiple replicas** behind a Deployment and add a **PodDisruptionBudget** so
  voluntary disruptions (node drains, upgrades) cannot take all replicas at once.
- Spread replicas with **`topologySpreadConstraints`** or anti-affinity across nodes and
  zones so a single-node or single-zone failure does not take the whole service down.
- Inject config via **ConfigMaps** and secrets via **Secrets** (backed by a real secrets
  manager); never bake them into the image. Mount them; changing config should not require
  a rebuild.
- Autoscale with an **HPA** on a meaningful metric (CPU, or custom/queue depth), and
  size **requests** correctly — the HPA scales off requests, so wrong requests break
  autoscaling.
- Set a **graceful `terminationGracePeriodSeconds`** and handle SIGTERM so pods drain
  connections during rollouts and scale-downs.
- Apply the **least-privilege security context**: `runAsNonRoot`, drop capabilities,
  read-only root filesystem where possible.

## Examples

**Good Example** — declares its needs so the scheduler can act correctly

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 3                          # survive a node loss; not a single point of failure
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      securityContext: { runAsNonRoot: true }   # least privilege
      topologySpreadConstraints:                 # don't stack all replicas in one zone
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: api } }
      terminationGracePeriodSeconds: 30          # time to drain in-flight requests
      containers:
        - name: api
          image: registry.example.com/api:2.4.0-a1b2c3d   # immutable, pinned
          resources:                             # scheduler + autoscaler depend on these
            requests: { cpu: "250m", memory: "256Mi" }
            limits:   { cpu: "500m", memory: "512Mi" }
          readinessProbe:                        # gates traffic until deps are ready
            httpGet: { path: /ready, port: 8080 }
          livenessProbe:                         # restarts a wedged process
            httpGet: { path: /healthz, port: 8080 }
```

**Bad Example** — hides its needs, so the platform decides badly

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 1                          # single pod: any node failure = full outage
  template:
    spec:
      containers:
        - name: api
          image: registry.example.com/api:latest   # mutable tag: not reproducible
          # No resource requests → scheduler places blindly, HPA can't scale on nothing.
          # No probes → traffic hits a not-ready pod; a hung process is never restarted.
          # No graceful termination → every rollout drops in-flight requests.
```

## Common Mistakes

- No resource requests/limits, breaking scheduling, autoscaling, and fair sharing.
- Missing or trivial readiness probes, so traffic reaches pods that cannot serve.
- Running a single replica for a service that is supposed to be highly available.
- Concentrating replicas on one node/zone, negating redundancy.
- Referencing mutable image tags (`latest`) instead of immutable digests/versions.
- Baking config/secrets into images instead of ConfigMaps/Secrets.
- No PodDisruptionBudget, so a routine node drain takes the whole service down.
- Ignoring SIGTERM, so scale-downs and rollouts sever active connections.

## Production Tips

- Enforce required fields (requests, probes, non-root) with an admission policy (Kyverno,
  OPA/Gatekeeper) so a manifest missing them cannot be applied.
- Watch for `OOMKilled` and CPU throttling — they signal wrong limits, not just load.
- Keep manifests in git and apply via GitOps (Argo CD, Flux); the cluster state should be
  reconciled from the repo, not hand-edited.
- Test node-failure and rollout scenarios in a game day; probes and PDBs only prove out
  under real disruption.

## AI Review Checklist

- Does every container declare resource `requests` and `limits`?
- Are readiness and liveness probes defined and checking real health, not static 200s?
- Are there multiple replicas plus a PodDisruptionBudget for availability-sensitive services?
- Are replicas spread across nodes/zones via topology spread or anti-affinity?
- Are images pinned to immutable references, and config/secrets injected (not baked in)?
- Is `terminationGracePeriodSeconds` set with SIGTERM handling for graceful drain?
- Is a least-privilege security context applied (`runAsNonRoot`, dropped capabilities)?

## Related

- `knowledge/devops/10-containerization.md`
- `knowledge/devops/07-deployment-strategies.md`
- `knowledge/devops/09-configuration-management.md`
- `knowledge/devops/19-high-availability.md`
- `knowledge/devops/20-scalability.md`
