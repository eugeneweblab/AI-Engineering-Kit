---
id: kubernetes/04-pods
topic: kubernetes
slug: pods
title: "Pods"
type: doc
order: 4
status: ready
tags: [kubernetes, pods, securityContext, SIGTERM, runAsNonRoot, RuntimeDefault, topologySpreadConstraints, terminationGracePeriodSeconds]
related: [kubernetes/05-deployments, kubernetes/03-nodes, kubernetes/19-resource-management, kubernetes/22-security, kubernetes/24-debugging]
when_to_use: "Read before writing or reviewing any pod spec — probes, resources, security context, or container layout."
---
# Pods

## Purpose

This document defines the pod: the smallest deployable unit in Kubernetes and the spec that
every controller ultimately renders. Read it before writing any pod template, because the same
fields — probes, resources, `securityContext`, containers — appear inside Deployments,
StatefulSets, Jobs, and everything else. Get the pod right and the workloads above it inherit
correctness.

## Why It Matters

A pod is a group of containers sharing a network namespace and lifecycle. It is also the unit
Kubernetes schedules, restarts, and kills. Nearly every reliability and security property of a
workload is decided in the pod spec: without resource requests the scheduler can't place it
safely; without probes Kubernetes can't tell running from healthy; without a `securityContext`
the container runs as root with more access than it needs. These fields are easy to omit and
their absence is silent — the pod runs fine until the day it doesn't. That is why the pod spec is
held to a high bar.

## Core Principles

- **A pod is ephemeral.** It can be killed and rescheduled at any moment, with a new IP. Never
  store durable state on pod-local disk; never rely on a pod's identity or address.
- **Rarely create bare pods.** A pod created directly is not rescheduled if its node dies. Let a
  controller ([Deployment](05-deployments.md), Job, StatefulSet) own the pod's lifecycle.
- **One concern per container.** Prefer a single main process per container; add sidecars/init
  containers for cross-cutting setup, not to bundle unrelated apps.
- **Running is not healthy.** Kubernetes only knows what your probes tell it. Define liveness,
  readiness, and (for slow starts) startup probes explicitly.
- **Least privilege by default.** Drop capabilities, run as non-root, and mount a read-only root
  filesystem unless a specific need forbids it.

## Best Practices

- Set CPU and memory **requests and limits** on every container so the scheduler can place it and
  the kubelet can bound it — see [resource management](19-resource-management.md).
- Define a **readiness** probe (gates traffic) and a **liveness** probe (triggers restart); use a
  **startup** probe for slow boots so liveness doesn't kill a still-initializing container.
- Set a hardened `securityContext`: `runAsNonRoot`, no privilege escalation, dropped capabilities,
  read-only root FS — see [security](22-security.md).
- Use init containers for ordering-dependent setup and sidecars for logging/proxy concerns; keep
  the main container focused.
- Handle `SIGTERM` and set a sensible `terminationGracePeriodSeconds` so the pod shuts down cleanly
  during rollouts and evictions.

## Examples

**Good Example** — probes, resources, and a hardened security context

```yaml
apiVersion: v1
kind: Pod          # illustrative; in practice a Deployment owns this template
metadata: { name: web, labels: { app: web } }
spec:
  securityContext: { runAsNonRoot: true, seccompProfile: { type: RuntimeDefault } }
  containers:
    - name: web
      image: registry.example.com/web:1.4.2   # pinned tag, not :latest
      resources:
        requests: { cpu: 100m, memory: 128Mi } # scheduler places on these
        limits:   { cpu: 500m, memory: 256Mi } # kubelet enforces these
      readinessProbe:                            # gate traffic until ready
        httpGet: { path: /healthz, port: 8080 }
      livenessProbe:                             # restart if it hangs
        httpGet: { path: /livez, port: 8080 }
        initialDelaySeconds: 10
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities: { drop: ["ALL"] }
```

**Bad Example** — bare pod, no limits, no probes, root

```yaml
apiVersion: v1
kind: Pod
metadata: { name: web }   # bare pod: if the node dies, it is never rescheduled
spec:
  containers:
    - name: web
      image: web:latest   # unpinned → different code on each pull, no rollback
      # no resources  → scheduler can't reason about placement; can starve the node
      # no probes     → traffic sent before ready; hung process never restarts
      # runs as root, writable FS → oversized blast radius if compromised
```

## Common Mistakes

- Creating bare pods instead of letting a controller manage them (no self-healing).
- Using `image: latest` or an unpinned tag, making deploys non-reproducible and rollback impossible.
- Omitting resource requests/limits, so the scheduler misplaces the pod and one container can starve
  the node.
- Missing readiness probes (traffic hits an unready pod) or missing liveness probes (a hung process
  never restarts).
- Running as root with a writable root filesystem and full capabilities.
- Ignoring `SIGTERM`, so the pod is force-killed and drops in-flight requests during rollouts.

## Production Tips

- Debug a bad pod with `kubectl describe pod` (events, restart reasons), `kubectl logs --previous`
  (crash logs), and an ephemeral debug container for distroless images — see [debugging](24-debugging.md).
- Spread pods across nodes/zones with `topologySpreadConstraints` and protect voluntary disruptions
  with a `PodDisruptionBudget` (see [Deployments](05-deployments.md)).

## AI Review Checklist

- Is the pod owned by a controller rather than created bare?
- Are image tags pinned (no `:latest`)?
- Does every container set resource requests and limits?
- Are readiness and liveness probes defined (plus startup for slow boots)?
- Does the `securityContext` run as non-root with dropped capabilities and a read-only root FS?
- Does the container handle `SIGTERM` within the grace period?

## Related

- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/03-nodes.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/24-debugging.md`
