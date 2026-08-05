---
id: kubernetes/03-nodes
topic: kubernetes
slug: nodes
title: "Nodes"
type: doc
order: 3
status: ready
tags: [kubernetes, nodes, Pending, nodeName, NoSchedule, nodeSelector, NotReady, drain]
related: [kubernetes/01-architecture, kubernetes/04-pods, kubernetes/19-resource-management, kubernetes/20-autoscaling, kubernetes/24-debugging]
when_to_use: "Read before scheduling workloads to specific nodes, draining nodes, or debugging Pending pods and node pressure."
---
# Nodes

## Purpose

This document covers nodes — the machines that actually run pods — and the controls that
govern where pods land: labels, taints/tolerations, affinity, and node lifecycle
(cordon, drain, pressure). Read it when a pod is `Pending`, when you need workloads on
particular hardware, or before performing maintenance.

## Why It Matters

Every pod ultimately runs on a node, and the node is where physical reality intrudes on the
declarative model: finite CPU and memory, disk pressure, kernel and kubelet versions, spot
instances that vanish. Most `Pending` pods and mysterious evictions are node-level problems.
If you schedule blindly, the scheduler may pack latency-sensitive and batch workloads onto the
same box, place a GPU job on a CPU node, or leave pods unschedulable while nodes sit idle behind
a taint. Understanding node controls is what makes placement predictable instead of accidental.

## Core Principles

- **The kubelet owns the node.** It reports capacity, runs assigned pods, executes probes, and
  evicts pods under resource pressure. When a pod misbehaves on a node, the kubelet is the actor.
- **Requests drive scheduling; limits drive enforcement.** The scheduler places pods using their
  *requests* against node *allocatable* capacity — not actual usage. Wrong requests cause both
  `Pending` pods and overcommitted nodes.
- **Taints repel, tolerations permit, affinity attracts.** Taints keep pods off a node unless they
  tolerate it; affinity/`nodeSelector` pulls pods toward matching nodes. They are complementary.
- **Nodes fail and get replaced.** Treat nodes as disposable. Drain before maintenance; never
  assume a pod stays on the same node.

## Best Practices

- Select nodes with labels and `nodeAffinity`, not hard-coded `nodeName`; hard-coding removes the
  scheduler's ability to reschedule on failure.
- Reserve special hardware (GPU, high-memory, spot) with taints so only tolerating workloads land
  there, and pull the right workloads in with affinity.
- Always `kubectl drain --ignore-daemonsets` before node maintenance so pods reschedule gracefully
  and [PodDisruptionBudgets](05-deployments.md) are respected. Never power off a node with running
  pods.
- Right-size requests so `allocatable` isn't exhausted by reservations while nodes sit half-idle —
  see [resource management](19-resource-management.md).
- Use the Cluster Autoscaler / Karpenter to add nodes when pods can't be placed, rather than leaving
  them `Pending` — see [autoscaling](20-autoscaling.md).

## Examples

**Good Example** — steer a GPU job with taint toleration + affinity

```yaml
# Nodes tainted: kubectl taint nodes gpu-1 gpu=true:NoSchedule
spec:
  tolerations:
    - key: gpu             # allowed onto the tainted GPU pool...
      operator: Equal
      value: "true"
      effect: NoSchedule
  affinity:
    nodeAffinity:          # ...and required to actually land on a GPU node
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: node.kubernetes.io/instance-type
                operator: In
                values: ["g5.xlarge"]
```

**Bad Example** — pinning to one node by name

```yaml
spec:
  nodeName: ip-10-0-1-42   # bypasses the scheduler entirely
  # If this node is drained, cordoned, or dies, the pod is NOT rescheduled —
  # it stays Pending forever. No self-healing, no autoscaling, no HA.
```

## Common Mistakes

- Using `nodeName` to pin a pod, defeating self-healing and rescheduling.
- Setting requests far below or above real usage, causing overcommitted nodes or wasted capacity.
- Powering off / terminating a node without draining it, killing pods and violating PDBs.
- Adding a taint but forgetting the matching toleration, so pods stay `Pending` with no obvious cause.
- Ignoring node conditions (`MemoryPressure`, `DiskPressure`, `NotReady`) when diagnosing evictions.

## Production Tips

- Check node health first when pods are `Pending` or evicted: `kubectl describe node <node>` shows
  conditions, allocatable vs. requested, and taints. `kubectl get events` shows scheduler messages.
- Spread replicas across nodes and zones with `topologySpreadConstraints` so one node/zone loss
  doesn't take the whole service down.
- Keep a small amount of headroom via system-reserved/kube-reserved so the kubelet and OS never
  starve — see [resource management](19-resource-management.md).

## AI Review Checklist

- Is placement driven by labels/affinity rather than a hard-coded `nodeName`?
- Do specialized nodes use taints, with matching tolerations on the intended workloads?
- Are pods spread across nodes/zones for availability?
- Is the node-maintenance path a graceful `drain`, respecting PodDisruptionBudgets?
- Are requests sized so nodes are neither overcommitted nor wastefully idle?

## Related

- `knowledge/kubernetes/01-architecture.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/20-autoscaling.md`
- `knowledge/kubernetes/24-debugging.md`
