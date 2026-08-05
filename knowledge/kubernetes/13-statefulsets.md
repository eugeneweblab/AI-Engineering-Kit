---
id: kubernetes/13-statefulsets
topic: kubernetes
slug: statefulsets
title: "Statefulsets"
type: doc
order: 13
status: ready
tags: [kubernetes, statefulsets, volumeClaimTemplates, PodDisruptionBudget, partition, terminationGracePeriodSeconds, StatefulSet, Ready]
related: [kubernetes/05-deployments, kubernetes/12-persistent-volumes, kubernetes/07-services, kubernetes/14-daemonsets, kubernetes/28-disaster-recovery]
when_to_use: "Read before deploying databases, queues, or any workload where pods need stable identity and per-pod durable storage."
---
# Statefulsets

## Purpose

This document defines when and how to run stateful workloads — databases, message
brokers, consensus clusters — using a **StatefulSet**. Unlike a
[Deployment](05-deployments.md), which treats pods as interchangeable cattle, a
StatefulSet gives each pod a **stable identity**: a fixed ordinal name, a stable network
hostname, and its own [PersistentVolumeClaim](12-persistent-volumes.md) that follows the
ordinal across rescheduling.

Reach for a StatefulSet only when identity or per-pod storage actually matters. Most
workloads do not need one; a Deployment plus a shared object store is simpler and safer.

## Why It Matters

Stateful systems encode assumptions about identity into their protocols. A Postgres
replica knows it is `replica-2` and expects to reconnect to *its* disk and *its* primary.
If Kubernetes reschedules it as a random pod with a fresh empty volume, replication breaks
or, worse, the cluster splits brain and silently diverges. A Deployment cannot provide
these guarantees — its pods have random names and, if given a PVC, all share the same one.
Choosing the wrong controller for a database is a data-integrity bug that surfaces weeks
later as corruption. StatefulSets exist precisely to make identity and storage stable, and
using them correctly is the difference between a resilient database and a time bomb.

## Core Principles

- **Stable identity is the whole point.** Pods are named `<name>-0`, `<name>-1`, … and keep
  that name, hostname, and PVC across restarts and reschedules. If you do not need stable
  identity, you do not need a StatefulSet.
- **Ordered, one-at-a-time lifecycle.** By default pods are created/scaled up in order
  `0..N-1` and terminated in reverse. This lets clustered software bootstrap deterministically.
- **Each replica owns its storage.** `volumeClaimTemplates` creates one PVC *per pod*.
  These PVCs are **not deleted** when the StatefulSet is deleted — that is a safety feature.
- **A headless Service provides DNS.** A `clusterIP: None` Service gives each pod a stable
  DNS name (`<pod>.<svc>.<ns>.svc.cluster.local`) for direct, peer-to-peer addressing.
- **Kubernetes manages the pods, not the clustering.** It will not join replicas, elect a
  leader, or reshard for you. That logic lives in the application or an operator.

## Best Practices

- Pair every StatefulSet with a **headless Service** (`clusterIP: None`) named in
  `serviceName`; without it, pods get no stable DNS.
- Use `volumeClaimTemplates` for per-pod storage — never a single shared PVC across
  replicas (that is multi-writer corruption or a scheduling deadlock).
- Set a `PodDisruptionBudget` (e.g. `maxUnavailable: 1`) so voluntary disruptions (node
  drains, upgrades) cannot take down quorum.
- Use `podManagementPolicy: Parallel` only when the app has no bootstrap ordering
  requirement (e.g. shard-nothing). Keep the default `OrderedReady` for quorum systems.
- Prefer `updateStrategy: RollingUpdate` with `partition` for canary upgrades of one
  ordinal at a time; test the new version on the highest ordinal first.
- For anything beyond simple bootstrapping (failover, backups, reshard), use a mature
  **operator** (CloudNativePG, Strimzi, etc.) rather than hand-rolling lifecycle logic.
- Set `terminationGracePeriodSeconds` generously so the database can flush and shut down
  cleanly instead of being killed mid-write.

## Examples

**Good Example** — headless Service, per-pod PVCs, ordered rollout

```yaml
apiVersion: v1
kind: Service
metadata: { name: pg }
spec:
  clusterIP: None                 # headless: gives each pod stable DNS (pg-0.pg, pg-1.pg)
  selector: { app: pg }
  ports: [{ port: 5432 }]
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: pg }
spec:
  serviceName: pg                 # must match the headless Service name
  replicas: 3
  selector: { matchLabels: { app: pg } }
  updateStrategy: { type: RollingUpdate }
  template:
    metadata: { labels: { app: pg } }
    spec:
      terminationGracePeriodSeconds: 60   # let Postgres checkpoint and stop cleanly
      containers:
        - name: pg
          image: postgres:17
          volumeMounts:
            - { name: data, mountPath: /var/lib/postgresql/data }
  volumeClaimTemplates:           # one durable PVC per pod, follows the ordinal
    - metadata: { name: data }
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-retain
        resources: { requests: { storage: 50Gi } }
```

**Bad Example** — Deployment with a shared PVC for a database

```yaml
apiVersion: apps/v1
kind: Deployment              # BUG: random pod names, no stable identity for replication
metadata: { name: pg }
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: pg
          image: postgres:17
          volumeMounts:
            - { name: data, mountPath: /var/lib/postgresql/data }
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: pg-data  # BUG: all 3 replicas mount the SAME disk → corruption
```

## Common Mistakes

- Using a Deployment for a database and getting no stable identity or per-pod storage.
- Forgetting the headless Service (or mismatching `serviceName`), so pods have no stable DNS.
- Scaling down and expecting the orphaned PVCs to be cleaned up — they are intentionally
  retained; you must delete them explicitly if you truly want the data gone.
- Assuming Kubernetes handles failover or leader election — it does not.
- Setting `podManagementPolicy: Parallel` on a quorum database, breaking ordered bootstrap.
- No `PodDisruptionBudget`, so a routine node drain evicts enough replicas to lose quorum.

## Production Tips

- Spread replicas across zones with `topologySpreadConstraints` so a zone outage cannot
  take the whole cluster.
- Treat scale-down as dangerous: it deletes the highest-ordinal pod but keeps its PVC —
  document whether operators should reclaim or preserve that disk.
- Monitor replication lag and quorum health at the application layer; pod `Ready` does not
  mean the cluster is healthy.
- Use the `partition` rolling-update knob to canary one replica and validate before the
  full rollout.

## AI Review Checklist

- Does this workload genuinely need stable identity or per-pod storage? If not, use a
  [Deployment](05-deployments.md).
- Is there a headless Service (`clusterIP: None`) whose name matches `serviceName`?
- Does storage come from `volumeClaimTemplates` (per pod), not a shared PVC?
- Is there a `PodDisruptionBudget` protecting quorum during drains and upgrades?
- Is `terminationGracePeriodSeconds` long enough for a clean shutdown/flush?
- Is failover/backup handled by the app or an operator, not assumed from Kubernetes?

## Related

- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/12-persistent-volumes.md`
- `knowledge/kubernetes/07-services.md`
- `knowledge/kubernetes/14-daemonsets.md`
- `knowledge/kubernetes/28-disaster-recovery.md`
