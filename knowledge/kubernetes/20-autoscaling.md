---
id: kubernetes/20-autoscaling
topic: kubernetes
slug: autoscaling
title: "Autoscaling"
type: doc
order: 20
status: ready
tags: [kubernetes, autoscaling]
related: [kubernetes/19-resource-management, kubernetes/05-deployments, kubernetes/23-monitoring, kubernetes/26-production]
when_to_use: "Read before adding an HPA, VPA, or cluster/node autoscaler, or when a workload flaps, thrashes, or fails to scale under load."
---
# Autoscaling

## Purpose

This document defines the three layers of Kubernetes autoscaling and how they interact:
the **Horizontal Pod Autoscaler** (more replicas), the **Vertical Pod Autoscaler**
(bigger pods), and the **Cluster/Node Autoscaler** (more nodes). It is written so an
agent can pick the right layer and configure it without causing thrashing or capacity
gaps.

Autoscaling only works if [resource requests](19-resource-management.md) are set
correctly — the HPA computes utilization as *usage ÷ request*. Wrong requests produce
wrong scaling decisions, so read that document first.

## Why It Matters

Autoscaling trades manual capacity planning for automated reactions to load, but a
misconfigured autoscaler is worse than none: it can thrash replicas up and down every
minute, amplify an outage by scaling a broken service, or scale pods that no node has
room for. Scaling is inherently laggy — pulling images and warming caches takes time —
so the configuration must account for reaction delay, not assume instant capacity.

## Core Principles

- **Horizontal first, vertical second.** Scale stateless services out with the HPA;
  reserve the VPA for right-sizing or workloads that cannot be parallelized.
- **Never run HPA and VPA on the same metric.** Both reacting to CPU on one Deployment
  fight each other. Use VPA in `recommendation`-only mode alongside HPA, or split by
  resource.
- **Pod scaling needs node scaling.** An HPA that adds replicas is useless if the
  Cluster Autoscaler (or Karpenter) cannot add nodes to place them. Configure both.
- **Scale up fast, down slow.** Aggressive scale-down thrashes and drops warm capacity
  right before the next spike. Use stabilization windows.
- **Requests are the denominator.** HPA target utilization is relative to the request;
  garbage requests produce garbage scaling.

## Best Practices

- Use `autoscaling/v2` HPA (the current, stable API) so you can scale on multiple and
  custom/external metrics, not just CPU.
- Set a `minReplicas` that survives one AZ failure (≥ 2 for anything user-facing) and a
  `maxReplicas` that a node pool can actually satisfy.
- Add a `behavior.scaleDown.stabilizationWindowSeconds` (e.g. 300s) to damp flapping;
  keep scale-up responsive.
- Scale user-facing services on a saturation signal that tracks user pain — requests per
  second or queue depth via custom metrics — rather than CPU alone, which lags.
- Run the VPA in `updateMode: "Off"` first to read its recommendations before letting it
  mutate pods; VPA eviction restarts pods.
- Pair the Cluster Autoscaler / Karpenter with `PodDisruptionBudgets` so scale-down does
  not evict below your availability floor.
- Ensure readiness probes are accurate — the HPA and Service route to Ready pods, so a
  lying probe sends traffic to cold replicas.

## Examples

**Good Example** — v2 HPA with sane bounds and a scale-down damper

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 3            # survives one AZ loss; not 1
  maxReplicas: 20           # a value the node pool can actually place
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65   # % of the CPU *request*, so requests must be right
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300   # slow, damped scale-down avoids thrashing
    scaleUp:
      stabilizationWindowSeconds: 0     # react to spikes immediately
```

**Bad Example** — flappy HPA on a deployment that also runs VPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: web }
  minReplicas: 1                     # single replica: no HA, cold-starts on every scale-up
  maxReplicas: 100                   # no node pool can place 100 → pods stay Pending
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 90 }  # too high; scales up too late
  # no behavior block → default scale-down thrashes; and a VPA also targets this
  # Deployment's CPU, so the two autoscalers oscillate against each other
```

## Common Mistakes

- Running HPA and VPA on the same CPU/memory metric so they fight.
- `minReplicas: 1`, giving no headroom and a cold start on every scale event.
- `maxReplicas` larger than any node pool can place, leaving pods Pending.
- Scaling pods without a node autoscaler, so replicas never schedule.
- No scale-down stabilization, causing replica flapping every reconcile.
- Wrong resource requests, so utilization percentages are meaningless.
- Scaling on CPU when the real bottleneck is a queue, DB, or I/O.

## Production Tips

- Load-test the full path (pod scale → node scale → Ready) and measure end-to-end
  reaction time; that lag drives your minReplicas headroom.
- Alert when an HPA sits at `maxReplicas` or `minReplicas` for long — it means the bounds
  are wrong or the metric is saturated.
- Watch for Pending pods; they signal the node autoscaler cannot keep up.

## AI Review Checklist

- Is the HPA using `autoscaling/v2`, not a deprecated version?
- Are `minReplicas` (≥ 2 for user-facing) and `maxReplicas` (placeable) both sane?
- Is there a scale-down stabilization window to prevent thrashing?
- Are HPA and VPA prevented from fighting over the same metric?
- Is a Cluster Autoscaler / Karpenter present to place new replicas?
- Are resource requests set correctly, since utilization depends on them?
- Are PodDisruptionBudgets in place so scale-down respects availability?

## Related

- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/23-monitoring.md`
- `knowledge/kubernetes/26-production.md`
