---
id: kubernetes/14-daemonsets
topic: kubernetes
slug: daemonsets
title: "Daemonsets"
type: doc
order: 14
status: ready
tags: [kubernetes, daemonsets, maxUnavailable, RollingUpdate, hostPath, resources.requests, limits, nodeSelector]
related: [kubernetes/05-deployments, kubernetes/03-nodes, kubernetes/19-resource-management, kubernetes/21-observability, kubernetes/22-security]
when_to_use: "Read before deploying a node-level agent — log shipper, metrics exporter, CNI, or storage plugin — that must run one copy per node."
---
# Daemonsets

## Purpose

This document defines how to run exactly one copy of a pod on every (or a selected subset
of) node in the cluster using a **DaemonSet**. Its job is node-local infrastructure: log
collectors (Fluent Bit), metrics exporters (node-exporter), CNI plugins, CSI node drivers,
and security agents. As nodes join the cluster, the DaemonSet controller automatically
schedules a pod onto them; as nodes leave, their pods are garbage-collected.

Use a DaemonSet only when the workload is inherently *per node*. If you want N copies of a
service for capacity or availability, that is a [Deployment](05-deployments.md), not a
DaemonSet.

## Why It Matters

Node agents are the observability and security substrate — the thing that tells you a node
is misbehaving and enforces policy on it. If the agent is missing from even one node, that
node becomes a blind spot: logs vanish, metrics gap, policy goes unenforced, and you learn
about it only during an incident on exactly that node. A DaemonSet is the only controller
that guarantees "one per node, including nodes that don't exist yet." Getting it wrong —
tolerations that skip tainted nodes, resource limits that starve the kubelet, an update
strategy that reboots every node at once — turns cluster-wide infrastructure into a
cluster-wide outage. The blast radius is the entire fleet.

## Core Principles

- **One pod per node, automatically.** The controller reconciles the pod set to node
  membership; you never set `replicas`. Scaling is a property of the cluster, not the spec.
- **Node coverage depends on tolerations.** A DaemonSet does not automatically run on
  tainted nodes (control-plane, GPU pools, `NoSchedule` taints) unless it tolerates them.
  Missing tolerations = silent gaps in coverage.
- **Rollouts are node-disruptive.** Updating a DaemonSet restarts a pod on every node. The
  `updateStrategy` (`RollingUpdate` with `maxUnavailable`/`maxSurge`) controls how many
  nodes are affected at once.
- **Agents share the node's fate and resources.** DaemonSet pods compete with real
  workloads for CPU/memory; unbounded limits can starve the kubelet and take the node down.
- **Node access is privileged.** These pods often mount host paths and use host networking;
  that power must be scoped tightly, not granted blanket.

## Best Practices

- Set explicit `resources.requests` and `limits`. A runaway log shipper must not evict the
  workloads it is meant to observe. Use a `Guaranteed` or tight `Burstable` QoS.
- Add the tolerations needed for full coverage. To truly run *everywhere*, tolerate the
  broad operator `{ operator: "Exists" }` — but do so deliberately, knowing it includes
  control-plane and specialty nodes.
- Constrain scope with `nodeSelector`/`affinity` when the agent is only for some nodes
  (e.g. GPU exporter on GPU nodes).
- Choose `updateStrategy: RollingUpdate` with a small `maxUnavailable` (e.g. 1 or 10%) so a
  bad agent version does not brick the whole fleet at once. Reserve `OnDelete` for agents
  you must roll manually.
- Set `priorityClassName` high (e.g. `system-node-critical` for true infra) so the agent is
  not the first thing evicted under pressure.
- Grant only the host access actually required — specific `hostPath` mounts and a minimal
  `securityContext`, not blanket `privileged: true`.

## Examples

**Good Example** — bounded resources, full-coverage tolerations, safe rollout

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata: { name: fluent-bit, namespace: logging }
spec:
  selector: { matchLabels: { app: fluent-bit } }
  updateStrategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 1 }   # reboot one node's agent at a time
  template:
    metadata: { labels: { app: fluent-bit } }
    spec:
      priorityClassName: system-node-critical  # do not evict the log shipper first
      tolerations:
        - operator: Exists                 # run on EVERY node, incl. tainted/control-plane
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:3.1
          resources:                       # bounded so it can't starve the kubelet
            requests: { cpu: 50m, memory: 64Mi }
            limits:   { cpu: 200m, memory: 128Mi }
          volumeMounts:
            - { name: varlog, mountPath: /var/log, readOnly: true }  # least privilege
      volumes:
        - name: varlog
          hostPath: { path: /var/log }
```

**Bad Example** — Deployment for a node agent, unbounded, no tolerations

```yaml
apiVersion: apps/v1
kind: Deployment          # BUG: gives N random pods, not one-per-node coverage
metadata: { name: node-exporter }
spec:
  selector: { matchLabels: { app: node-exporter } }
  replicas: 3             # BUG: 3 copies somewhere, blind on every other node
  template:
    metadata: { labels: { app: node-exporter } }
    spec:
      # No tolerations → skips tainted/control-plane nodes → silent coverage gaps.
      containers:
        - name: node-exporter
          image: prom/node-exporter:latest   # unpinned tag = non-reproducible rollout
          # No resource limits → can starve the kubelet and crash the node.
```

## Common Mistakes

- Using a Deployment (or a fixed replica count) for a per-node agent, leaving nodes uncovered.
- Omitting tolerations, so the agent silently skips tainted, GPU, or control-plane nodes.
- No resource limits, letting a busy agent starve the kubelet and destabilize the node.
- Updating with a large `maxUnavailable`, restarting the agent on every node simultaneously.
- Running `privileged: true` when a single read-only `hostPath` would do.
- Forgetting a `priorityClassName`, so critical infra is evicted first under pressure.

## Production Tips

- Alert on DaemonSet `numberReady` vs `desiredNumberScheduled` — any gap is an uncovered node.
- Pin image tags/digests; a `latest` agent that fails rolls out to the whole fleet.
- Test agent upgrades on a canary node pool before a fleet-wide `RollingUpdate`.
- For agents that must start before workloads (CNI, CSI), set the appropriate node-critical
  priority so scheduling is not blocked by application pods.

## AI Review Checklist

- Is this genuinely a per-node workload? If it is capacity/HA, use a
  [Deployment](05-deployments.md) instead.
- Are `resources.requests` and `limits` set so the agent cannot starve the kubelet?
- Do tolerations give the intended node coverage (or is skipping tainted nodes intentional)?
- Is `updateStrategy` `RollingUpdate` with a conservative `maxUnavailable`?
- Is host access minimal (specific `hostPath`, no blanket `privileged`)?
- Is a `priorityClassName` set so the agent is not evicted first under pressure?

## Related

- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/03-nodes.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/21-observability.md`
- `knowledge/kubernetes/22-security.md`
