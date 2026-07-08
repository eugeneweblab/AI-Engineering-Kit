---
id: kubernetes/00-overview
topic: kubernetes
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [kubernetes, overview]
related: [kubernetes/01-architecture, kubernetes/04-pods, kubernetes/05-deployments, kubernetes/07-services, kubernetes/27-best-practices]
when_to_use: "Read first when starting any Kubernetes task, to see how the topic's docs fit together and where to go next."
---
# Overview

## Purpose

This document orients an agent to the Kubernetes knowledge base: what Kubernetes
is, the mental model it demands, and how the sibling docs connect. It is a map, not
a tutorial. Read it to decide *which* doc to open for the task at hand.

Kubernetes is a declarative control plane for running containers. You describe the
desired state of your workloads in YAML manifests; controllers continuously reconcile
the live cluster toward that state. Almost every mistake in Kubernetes traces back to
misunderstanding that one idea — you do not run containers, you declare intent and let
controllers converge.

## Why It Matters

Kubernetes is powerful because it self-heals, scales, and rolls out changes without
downtime — but only if the manifests are written correctly. The same declarative engine
that recovers a crashed pod will also faithfully roll out a broken image to every replica,
evict a stateful workload that never set a `PodDisruptionBudget`, or run a container as
root with the whole node's filesystem mounted. Kubernetes does exactly what you declare.
The cost of a vague or wrong manifest is a production incident, so the bar for correctness
is high and the reasoning behind each field must be understood, not copied.

## Core Principles

- **Declarative, not imperative.** Define desired state in manifests checked into git;
  never fix production with live `kubectl edit`. The cluster's truth must live in source.
- **Controllers reconcile continuously.** Every object is watched by a controller whose
  only job is to close the gap between desired and actual. Design for convergence, not for
  one-shot commands.
- **Pods are cattle, not pets.** Any pod can be killed and rescheduled at any moment.
  Workloads must tolerate restarts, rescheduling, and IP changes.
- **The API is the contract.** Everything — nodes, pods, secrets, policies — is an API
  object with a schema. Understanding the object model is understanding Kubernetes.

## Best Practices

- Start from the workload, not the cluster: pick the right controller
  ([Deployments](05-deployments.md) for stateless, [StatefulSets](13-statefulsets.md) for
  stateful, [Jobs](15-jobs.md) for batch) before writing any YAML.
- Keep manifests in version control and apply them through CI, not from a laptop.
- Read the doc for the specific object you are touching; do not generalize across kinds.
- Always set resource requests/limits, probes, and a non-root `securityContext` — these
  are covered in [resource management](19-resource-management.md) and [security](22-security.md).

## How the docs fit together

- **Foundations** — start here. [Architecture](01-architecture.md) explains the control
  plane; [Cluster](02-cluster.md) and [Nodes](03-nodes.md) cover where workloads run.
- **Workloads** — the objects you write daily. [Pods](04-pods.md) is the atom;
  [Deployments](05-deployments.md), [ReplicaSets](06-replicasets.md),
  [StatefulSets](13-statefulsets.md), [DaemonSets](14-daemonsets.md),
  [Jobs](15-jobs.md), and [CronJobs](16-cronjobs.md) manage pods.
- **Networking** — [Services](07-services.md), [Ingress](08-ingress.md), and
  [NetworkPolicies](17-network-policies.md) route and isolate traffic.
- **Configuration and storage** — [ConfigMaps](09-configmaps.md), [Secrets](10-secrets.md),
  [Volumes](11-volumes.md), and [PersistentVolumes](12-persistent-volumes.md).
- **Operations and safety** — [RBAC](18-rbac.md), [resource management](19-resource-management.md),
  [autoscaling](20-autoscaling.md), [observability](21-observability.md),
  [security](22-security.md), [debugging](24-debugging.md), [upgrades](25-upgrades.md),
  and [disaster recovery](28-disaster-recovery.md).
- **Guardrails** — [production checklist](98-production-checklist.md),
  [AI review checklist](99-ai-review-checklist.md), and
  [common anti-patterns](100-common-antipatterns.md) gate anything shipping to production.

## Common Mistakes

- Treating Kubernetes imperatively — patching live objects instead of updating manifests,
  so the cluster and git drift apart.
- Reaching for the wrong controller (a Deployment for a database that needs stable identity
  and storage — use a StatefulSet).
- Copying a manifest without understanding its fields, then shipping missing probes,
  requests, or a root container.
- Assuming a pod is durable; building state into pod-local disk that vanishes on reschedule.

## AI Review Checklist

- Is the desired state expressed in a version-controlled manifest, not a live edit?
- Is the workload matched to the correct controller kind for its lifecycle?
- Does the change reference the specific sibling doc for the object being modified?
- Are the production and security guardrail docs consulted before shipping?

## Related

- `knowledge/kubernetes/01-architecture.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/07-services.md`
- `knowledge/kubernetes/27-best-practices.md`
