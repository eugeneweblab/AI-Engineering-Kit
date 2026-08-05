---
id: kubernetes/05-deployments
topic: kubernetes
slug: deployments
title: "Deployments"
type: doc
order: 5
status: ready
tags: [kubernetes, deployments, maxUnavailable, maxSurge, PodDisruptionBudget, replicas, RollingUpdate, minReplicas]
related: [kubernetes/04-pods, kubernetes/06-replicasets, kubernetes/07-services, kubernetes/13-statefulsets, kubernetes/20-autoscaling]
when_to_use: "Read before creating or changing a stateless workload's rollout, replica count, or update strategy."
---
# Deployments

## Purpose

This document defines Deployments: the controller for **stateless** workloads that manages
replica count and, critically, safe rolling updates and rollbacks. Read it before shipping or
changing any stateless service. It builds on the [pod](04-pods.md) spec, which supplies the
template a Deployment rolls out.

## Why It Matters

A Deployment is how you change running code without downtime — and how you cause an outage if
its update strategy is wrong. It creates a [ReplicaSet](06-replicasets.md) per template version
and shifts pods between them according to `maxSurge`/`maxUnavailable`. Get those wrong and a
rollout either takes the whole service offline or ships a broken version to every replica before
anyone notices. Because Deployments touch live traffic, their configuration — probes, strategy,
disruption budget — is where availability is won or lost.

## Core Principles

- **Deployments are for stateless pods only.** Anything needing stable identity, ordered startup,
  or per-pod storage belongs in a [StatefulSet](13-statefulsets.md), not a Deployment.
- **Rollouts are gated by readiness probes.** A Deployment only proceeds to the next batch when new
  pods report *Ready*. Without a readiness probe, it declares success on pods that can't serve.
- **The update strategy bounds the blast radius.** `maxUnavailable` caps lost capacity during a
  rollout; `maxSurge` caps extra capacity. These are your downtime and cost dials.
- **Rollbacks are first-class.** Each template change creates a new ReplicaSet, so
  `kubectl rollout undo` restores the previous version instantly. Keep revision history.
- **Desired state lives in the manifest.** Scale and image changes belong in git and CI, not in
  ad-hoc `kubectl scale`/`edit` that drift from source.

## Best Practices

- Use `RollingUpdate` with explicit `maxUnavailable: 0` (or a small value) and a small `maxSurge`
  so capacity never drops during a deploy; the cost is briefly running extra pods.
- Require a **readiness probe** on the pod template — it is what makes a rolling update safe.
- Run at least 2–3 replicas and pair the Deployment with a `PodDisruptionBudget` so voluntary
  disruptions (node drains, upgrades) can't remove too many pods at once.
- Pin image tags (immutable digests ideally) so a rollout is reproducible and `rollout undo` is
  meaningful.
- Scale with the [HorizontalPodAutoscaler](20-autoscaling.md), and set the HPA's floor via
  `minReplicas` rather than editing `replicas` by hand.
- Set `revisionHistoryLimit` deliberately (e.g. 10) so you retain rollback targets without keeping
  unbounded old ReplicaSets.

## Examples

**Good Example** — zero-downtime rolling update, gated on readiness

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: web, labels: { app: web } }
spec:
  replicas: 3
  selector: { matchLabels: { app: web } }
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0   # never drop below desired capacity during a rollout
      maxSurge: 1         # add one extra pod at a time, then retire an old one
  template:
    metadata: { labels: { app: web } }
    spec:
      containers:
        - name: web
          image: registry.example.com/web:1.4.2   # pinned → rollback is well-defined
          readinessProbe:                           # gates the rollout: no Ready, no progress
            httpGet: { path: /healthz, port: 8080 }
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits:   { cpu: 500m, memory: 256Mi }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: web }
spec:
  minAvailable: 2          # node drains/upgrades can't take the service below 2 pods
  selector: { matchLabels: { app: web } }
```

**Bad Example** — recreate strategy, no probe, single replica

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: web }
spec:
  replicas: 1              # single replica → any disruption is a full outage
  selector: { matchLabels: { app: web } }
  strategy: { type: Recreate }  # kills all old pods BEFORE new ones start → downtime
  template:
    metadata: { labels: { app: web } }
    spec:
      containers:
        - name: web
          image: web:latest      # unpinned → rollout not reproducible, undo is meaningless
          # no readiness probe → rollout "succeeds" on pods that can't serve traffic
```

## Common Mistakes

- Using a Deployment for a stateful workload that needs stable identity or storage (use a
  [StatefulSet](13-statefulsets.md)).
- No readiness probe, so a rolling update marches through broken pods and reports success.
- `strategy: Recreate` (or `maxUnavailable` too high) on a user-facing service, causing downtime.
- Running a single replica and no `PodDisruptionBudget`, so a routine node drain is an outage.
- Editing `replicas` by hand while an HPA also manages it — the two fight and thrash.
- Using `:latest`, so `kubectl rollout undo` can't reproduce the previous image.

## Production Tips

- Verify a deploy with `kubectl rollout status deployment/web`; it blocks until the rollout is
  healthy and fails fast on a stuck one. Roll back with `kubectl rollout undo`.
- Set `progressDeadlineSeconds` so a wedged rollout is reported as failed instead of hanging.
- For risk-sensitive changes, layer a canary or blue-green pattern (via a second Deployment and
  [Service](07-services.md) selector shift) on top of the rolling update.

## AI Review Checklist

- Is the workload genuinely stateless (otherwise a StatefulSet)?
- Does the pod template define a readiness probe that gates the rollout?
- Is the strategy `RollingUpdate` with a `maxUnavailable`/`maxSurge` that preserves capacity?
- Are there ≥2 replicas and a `PodDisruptionBudget`?
- Are image tags pinned so rollout/rollback are reproducible?
- Is scaling delegated to the HPA rather than manual `replicas` edits?

## Related

- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/06-replicasets.md`
- `knowledge/kubernetes/07-services.md`
- `knowledge/kubernetes/13-statefulsets.md`
- `knowledge/kubernetes/20-autoscaling.md`
