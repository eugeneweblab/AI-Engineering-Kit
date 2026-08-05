---
id: kubernetes/06-replicasets
topic: kubernetes
slug: replicasets
title: "Replicasets"
type: doc
order: 6
status: ready
tags: [kubernetes, replicasets]
related: [kubernetes/05-deployments, kubernetes/04-pods, kubernetes/13-statefulsets, kubernetes/07-services, kubernetes/19-resource-management]
when_to_use: "Read before creating a ReplicaSet directly or debugging why a Deployment's Pod count is wrong."
---
# Replicasets

## Purpose

This document defines what a ReplicaSet is, what guarantee it provides, and — most
importantly — when you must *not* create one directly. A ReplicaSet keeps a stable set
of identical Pod replicas running at any given time. It is the controller that watches
the cluster, counts matching Pods, and creates or deletes Pods until the observed count
equals the desired `replicas`.

You almost never author a ReplicaSet yourself. A [Deployment](05-deployments.md) creates
and owns ReplicaSets for you and adds rolling updates and rollback on top. Understand the
ReplicaSet so you can read what a Deployment produces and debug it.

## Why It Matters

The ReplicaSet is the mechanism behind self-healing. When a node dies or a Pod crashes,
the ReplicaSet controller notices the replica count dropped and schedules a replacement.
If you get its selector wrong, the controller can *adopt* Pods you never intended it to
manage, or fight another controller over the same Pods — either way it deletes or
duplicates running workloads. Because the controller acts continuously and silently, a
misconfigured selector corrupts your fleet without any error message.

## Core Principles

- **Prefer a Deployment; do not hand-write ReplicaSets.** A bare ReplicaSet cannot do a
  rolling update — changing its Pod template does nothing to existing Pods. The cost of a
  raw ReplicaSet is that every version change becomes a manual delete-and-recreate.
- **The selector is a contract, not a label.** A ReplicaSet owns every Pod matching its
  selector, whether or not it created it. Overlapping selectors across controllers cause
  Pods to be adopted, orphaned, or deleted.
- **`selector` must match the Pod template's labels.** The API server rejects a
  ReplicaSet whose `spec.selector` does not match `spec.template.metadata.labels`.
- **Replica count is desired state, not a one-time command.** Deleting a Pod by hand
  triggers an immediate recreate. Scale via the object, never by killing Pods.
- **ReplicaSets assume Pods are interchangeable.** If Pods need stable identity or
  storage, you need a [StatefulSet](13-statefulsets.md), not a ReplicaSet.

## Best Practices

- Create Deployments, not ReplicaSets. Let the Deployment name and manage its ReplicaSets.
- Give every replica set of Pods a unique, specific selector (for example
  `app: checkout` plus `pod-template-hash`) so no two controllers overlap.
- Never reuse label values across unrelated workloads in the same namespace; overlap is
  how selectors collide.
- Scale with `kubectl scale` or by editing `replicas` in the manifest — the two must
  agree, or the next `apply` reverts a manual scale.
- Set resource `requests` and `limits` and readiness probes on the Pod template so the
  controller replaces only genuinely ready Pods (see
  [resource management](19-resource-management.md)).
- To change the image or config, change the Deployment. Editing a ReplicaSet template
  leaves existing Pods untouched.

## Examples

**Good Example** — a Deployment owns the ReplicaSet; selector matches template labels

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
spec:
  replicas: 3
  selector:
    matchLabels:
      app: checkout          # selector and template labels agree exactly
  template:
    metadata:
      labels:
        app: checkout        # Deployment adds pod-template-hash so ReplicaSets never collide
    spec:
      containers:
        - name: web
          image: registry.example.com/checkout:1.8.2  # pinned tag, never :latest
          readinessProbe:                              # controller waits for readiness
            httpGet: { path: /healthz, port: 8080 }
```

**Bad Example** — bare ReplicaSet with a mismatched, too-broad selector

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: checkout
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web               # too broad: adopts every Pod labelled app=web in the namespace
  template:
    metadata:
      labels:
        app: web             # collides with other workloads sharing app=web
    spec:
      containers:
        - name: web
          image: checkout:latest  # :latest — no way to know or roll back what is running
# No rolling update: changing image here does NOT restart existing Pods.
```

## Common Mistakes

- Creating a raw ReplicaSet instead of a Deployment, then wondering why an image change
  did not roll out.
- A selector broader than intended, so the ReplicaSet adopts unrelated Pods and deletes
  the "extra" ones to hit its replica count.
- `spec.selector` not matching `spec.template.metadata.labels`, so the API server rejects
  the object.
- Scaling by deleting Pods; the controller immediately recreates them.
- Editing a ReplicaSet that a Deployment owns — the Deployment reconciles and reverts it.
- Using a ReplicaSet for stateful Pods that need stable network identity or per-Pod
  storage.

## AI Review Checklist

- Is this a Deployment rather than a hand-written ReplicaSet? If a bare ReplicaSet, is
  there a documented reason?
- Does `spec.selector.matchLabels` exactly match `spec.template.metadata.labels`?
- Is the selector specific enough that no other controller can match the same Pods?
- Is the container image pinned to an explicit tag or digest, not `:latest`?
- Does the Pod template set resource requests/limits and a readiness probe?
- Is scaling done through the object's `replicas`, not by deleting Pods?

## Related

- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/13-statefulsets.md`
- `knowledge/kubernetes/07-services.md`
- `knowledge/kubernetes/19-resource-management.md`
