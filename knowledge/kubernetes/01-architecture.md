---
id: kubernetes/01-architecture
topic: kubernetes
slug: architecture
title: "Kubernetes Architecture"
type: doc
order: 1
status: ready
tags: [kubernetes, architecture]
related: [kubernetes/00-overview, kubernetes/02-cluster, kubernetes/03-nodes, kubernetes/04-pods, kubernetes/18-rbac]
when_to_use: "Read before reasoning about how the control plane reconciles state, or when debugging why an object is not converging."
---
# Kubernetes Architecture

## Purpose

This document explains the moving parts of a Kubernetes cluster — the control plane
and the node components — and how they cooperate to turn a declared manifest into a
running workload. Understand this before debugging why an object "isn't doing anything":
almost always a specific component in this reconciliation loop is the answer.

## Why It Matters

Kubernetes has no central "run this" command. When you `kubectl apply` a Deployment,
you are only writing a record to a database. A chain of independent controllers then
notices the record and acts. If you do not know which component owns which step, you
cannot diagnose failures — you will restart the wrong thing, blame the wrong layer, or
"fix" a symptom while the real controller keeps reconciling your change away. Knowing the
architecture turns guesswork into a directed search.

## Core Principles

- **etcd is the single source of truth.** All cluster state lives in etcd. Lose it without
  a backup and you lose the cluster. Everything else is reconstructable.
- **The API server is the only writer.** No component talks to etcd directly except the
  API server. Every read and write — including between controllers — goes through the API.
- **Controllers watch and reconcile.** The controller-manager runs control loops
  (Deployment, ReplicaSet, Node, Job, …) that watch desired state and drive actual state
  toward it. This loop never stops.
- **The scheduler only places, it does not run.** The scheduler assigns a pod to a node by
  writing `nodeName`; the node's kubelet is what actually starts containers.
- **Nodes are semi-autonomous.** The kubelet on each node reconciles the pods assigned to
  it even if it briefly loses contact with the control plane.

## Best Practices

- Back up etcd on a schedule and test restores — it is the only irreplaceable component
  (see [disaster recovery](28-disaster-recovery.md)).
- Run the control plane highly available: 3 or 5 etcd members (odd number, for quorum) and
  multiple API server replicas behind a load balancer.
- Restrict who can reach the API server and with what verbs via [RBAC](18-rbac.md); the API
  server is the cluster's front door.
- When debugging, follow the reconciliation chain in order — API object exists? controller
  created children? scheduler assigned a node? kubelet pulled and started? Do not skip steps.

## Examples

**Good Example** — trace a rollout through the components, in order

```bash
# 1. Control plane: did the object land in etcd via the API server?
kubectl get deployment web -o wide
# 2. controller-manager: did the Deployment controller create a ReplicaSet + Pods?
kubectl get rs,pods -l app=web
# 3. scheduler: was each pod assigned a node? (nodeName set)
kubectl get pod -l app=web -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName
# 4. kubelet: is the container actually running on that node?
POD=$(kubectl get pod -l app=web -o name | head -1)
kubectl describe "$POD"   # Events show pull/start on the assigned node
```

**Bad Example** — assuming one command "runs" the app and mis-diagnosing

```bash
kubectl apply -f deploy.yaml
# Pod is Pending. Restarting the API server or scheduler here fixes nothing:
sudo systemctl restart kube-apiserver   # wrong layer — the API object already exists
# The real cause is often node-side (no schedulable node, taints, insufficient
# resources). Pending means the *scheduler* found no fit — investigate nodes, not the API.
```

## Common Mistakes

- Treating `kubectl apply` as "start the container" — it only records desired state; a
  controller and kubelet do the work asynchronously.
- Not backing up etcd, then discovering the cluster is unrecoverable after a disk failure.
- Running an even number of etcd members, which cannot form a quorum on a split.
- Editing objects a controller owns (e.g. a ReplicaSet under a Deployment) and being
  confused when the controller reverts the change.
- Exposing the API server without tight RBAC and network restrictions.

## Production Tips

- Monitor control-plane health explicitly: API server latency, etcd fsync/leader changes,
  scheduler and controller-manager leader election. These predict cluster-wide failures.
- Keep control-plane and node component versions within the supported skew (kubelet may
  trail the API server, never lead it) — see [upgrades](25-upgrades.md).

## AI Review Checklist

- Is etcd backed up on a schedule with a tested restore procedure?
- Is the control plane HA with an odd number of etcd members?
- Is access to the API server governed by least-privilege [RBAC](18-rbac.md)?
- Does the debugging approach follow the reconciliation chain rather than guessing a layer?

## Related

- `knowledge/kubernetes/00-overview.md`
- `knowledge/kubernetes/02-cluster.md`
- `knowledge/kubernetes/03-nodes.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/18-rbac.md`
