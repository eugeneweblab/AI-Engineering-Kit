---
id: kubernetes/12-persistent-volumes
topic: kubernetes
slug: persistent-volumes
title: "Persistent Volumes"
type: doc
order: 12
status: ready
tags: [kubernetes, persistent-volumes]
related: [kubernetes/11-volumes, kubernetes/13-statefulsets, kubernetes/19-resource-management, kubernetes/28-disaster-recovery, kubernetes/26-production]
when_to_use: "Read before requesting, provisioning, or reviewing durable storage that must survive pod restarts and rescheduling."
---
# Persistent Volumes

## Purpose

This document defines how to give a pod storage that outlives the pod. A
[Volume](11-volumes.md) is scoped to a pod and dies with it; a **PersistentVolume (PV)**
is a cluster resource with an independent lifecycle. A **PersistentVolumeClaim (PVC)** is
a namespaced request for storage that binds to a PV. A **StorageClass** describes *how* to
provision PVs on demand.

The mental model is a three-part contract: the app asks for storage (PVC), the platform
supplies it (PV, usually created dynamically from a StorageClass), and Kubernetes binds
the two. Get the contract wrong and data is lost silently on the next reschedule.

## Why It Matters

Storage is the one Kubernetes resource that cannot be recreated from a manifest. Delete a
Deployment and reapply it — no harm. Delete a PVC bound to a `Delete`-reclaim PV and the
underlying disk is gone, along with every byte on it. Storage bugs are therefore *data
loss* bugs, and data loss is unrecoverable. Compounding this, the failure is delayed: an
`emptyDir` masquerading as durable storage works perfectly until the first node drain,
then loses everything. Because the blast radius is your customers' data and the failure is
invisible until it is catastrophic, storage manifests are held to a higher bar than
stateless workloads.

## Core Principles

- **Claims, not volumes.** Application manifests reference a PVC, never a PV directly.
  The PVC is the portable, namespaced abstraction; PVs are cluster infrastructure.
- **Access mode is a promise, not a mount option.** `ReadWriteOnce` means one *node* may
  mount it. Most block storage (EBS, PD, Ceph RBD) cannot do `ReadWriteMany`; asking for
  it silently leaves the PVC `Pending`.
- **The reclaim policy decides your data's fate.** `Retain` keeps the disk after the PVC
  is deleted; `Delete` destroys it. Dynamic provisioning defaults to `Delete`.
- **Bind late.** Use `volumeBindingMode: WaitForFirstConsumer` so the volume is created in
  the same zone as the pod that will use it. Immediate binding strands pods in the wrong
  zone.
- **Capacity is a request, not a quota.** The PVC `resources.requests.storage` sizes the
  disk; the app can still fill it. Size for growth and monitor free space.

## Best Practices

- Name a **StorageClass explicitly** in every PVC (`storageClassName`). Relying on the
  cluster default is non-portable — the default differs per cluster and can change.
- Set `reclaimPolicy: Retain` (on the StorageClass or PV) for any data you cannot
  regenerate, so an accidental `kubectl delete pvc` does not erase the disk.
- Enable `allowVolumeExpansion: true` on the StorageClass so you can grow a PVC in place;
  most CSI drivers cannot shrink, so never over-provision expecting to reclaim it.
- Use `WaitForFirstConsumer` binding for zonal/topology-aware storage (the norm on cloud).
- Prefer **CSI drivers** over the removed in-tree cloud providers (`kubernetes.io/aws-ebs`,
  `gce-pd`, etc.), which were fully removed in the 1.31 release train.
- For per-replica storage, let a [StatefulSet](13-statefulsets.md) `volumeClaimTemplates`
  create one PVC per pod rather than sharing one PVC across replicas.
- Back up the *data*, not the PV object. Use CSI `VolumeSnapshot` or an application-level
  backup; the PV/PVC YAML is not a backup.

## Examples

**Good Example** — explicit class, retain policy, late binding, expandable

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-retain
provisioner: ebs.csi.aws.com
reclaimPolicy: Retain            # keep the disk if the PVC is deleted by mistake
allowVolumeExpansion: true       # can grow the PVC later; cannot shrink
volumeBindingMode: WaitForFirstConsumer  # provision in the pod's zone, not eagerly
parameters:
  type: gp3
  encrypted: "true"              # encrypt data at rest
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
spec:
  storageClassName: fast-retain  # explicit, not the cluster default
  accessModes: ["ReadWriteOnce"] # block storage: one node at a time
  resources:
    requests:
      storage: 50Gi
```

**Bad Example** — ephemeral storage mistaken for durable

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: db }
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: db
          image: postgres:17
          volumeMounts:
            - { name: data, mountPath: /var/lib/postgresql/data }
      volumes:
        - name: data
          emptyDir: {}           # BUG: wiped on every reschedule/node drain — total data loss
        # Also wrong even with a PVC: a Deployment shares one PVC across
        # replicas; use a StatefulSet for per-pod durable storage.
```

## Common Mistakes

- Using `emptyDir` or `hostPath` for data that must survive a pod restart.
- Requesting `ReadWriteMany` from block storage that only supports `ReadWriteOnce`,
  leaving the PVC stuck `Pending` with no obvious error.
- Leaving `reclaimPolicy: Delete` on production databases, so deleting the PVC deletes the
  disk.
- Omitting `storageClassName`, then breaking when the cluster's default class changes.
- Sharing one PVC across Deployment replicas and getting multi-writer corruption or
  scheduling deadlock.
- Assuming a PVC will resize automatically — expansion requires `allowVolumeExpansion` and
  a driver that supports it, and often a pod restart.

## Production Tips

- Alert on PV free space, not just PVC capacity — a full disk crashes stateful apps.
- Test restore, not just backup: schedule a periodic drill that restores a snapshot into a
  scratch namespace.
- Label PVs/PVCs with owner and app so orphaned `Retain` volumes can be reconciled and
  cost-attributed; retained disks keep billing after the workload is gone.
- Set a `ResourceQuota` on `requests.storage` per namespace to cap runaway provisioning.

## AI Review Checklist

- Does every stateful pod reference a **PVC**, never `emptyDir`/`hostPath`, for durable data?
- Is `storageClassName` set explicitly rather than relying on the cluster default?
- Is the reclaim policy `Retain` for data that cannot be regenerated?
- Does the requested `accessMode` match what the backing storage actually supports?
- Is `volumeBindingMode: WaitForFirstConsumer` used for zonal storage?
- For per-replica state, is a [StatefulSet](13-statefulsets.md) `volumeClaimTemplates` used
  instead of a shared PVC?
- Is there a snapshot/backup strategy for the data, and has restore been tested?

## Related

- `knowledge/kubernetes/11-volumes.md`
- `knowledge/kubernetes/13-statefulsets.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/28-disaster-recovery.md`
- `knowledge/kubernetes/26-production.md`
