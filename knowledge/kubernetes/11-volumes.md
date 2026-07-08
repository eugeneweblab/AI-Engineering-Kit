---
id: kubernetes/11-volumes
topic: kubernetes
slug: volumes
title: "Volumes"
type: doc
order: 11
status: ready
tags: [kubernetes, volumes]
related: [kubernetes/12-persistent-volumes, kubernetes/13-statefulsets, kubernetes/09-configmaps, kubernetes/10-secrets]
when_to_use: "Read before adding storage to a Pod, sharing files between containers, or deciding whether data must survive a restart."
---
# Volumes

## Purpose

This document defines how storage is attached to Pods with volumes, and — critically —
which volume types survive a restart and which do not. A volume is a directory mounted
into one or more containers in a Pod. It exists to share files between containers, to give
a container scratch space, and to inject config or secrets as files.

A Pod-level volume is not the same as durable storage. For data that must outlive the Pod,
you need a [PersistentVolume](12-persistent-volumes.md) bound via a PersistentVolumeClaim.
This document covers the volume mechanics; persistence guarantees live in that document.

## Why It Matters

The most damaging Kubernetes mistake in this area is writing important data to a volume
that is deleted with the Pod. `emptyDir` and the container's own writable layer are
ephemeral: when the Pod is rescheduled — a routine event during any rollout or node
drain — the data is gone with no warning. Conversely, using node-local `hostPath` for
"persistence" ties a Pod to one node and exposes the host filesystem, breaking scheduling
and security. Choosing the wrong volume type silently trades away either your data or your
portability.

## Core Principles

- **`emptyDir` lives and dies with the Pod.** It is created empty when the Pod is
  scheduled and deleted when the Pod is removed. Use it for scratch and cache only, never
  for data you need to keep.
- **The container's writable layer is not storage.** Anything written outside a volume
  vanishes on restart and bloats the node. Treat container filesystems as read-only.
- **Persistent data requires a PVC → PersistentVolume.** Only a
  [PersistentVolume](12-persistent-volumes.md) backed by real storage survives Pod
  rescheduling. A bare volume does not.
- **`hostPath` is not persistence and is a security risk.** It mounts a node directory
  into the Pod, pinning the Pod to that node and exposing the host. Avoid it outside of
  specific node-agent workloads.
- **Access mode dictates sharing.** `ReadWriteOnce` binds to one node at a time; sharing
  across nodes needs `ReadWriteMany`, which not every storage backend supports.

## Best Practices

- Run containers with a read-only root filesystem (`readOnlyRootFilesystem: true`) and
  mount a small `emptyDir` for any paths that genuinely need to be writable (temp, cache).
- Use `emptyDir` only for scratch, caches, and inter-container handoff within one Pod;
  document that its contents are disposable.
- For durable data, declare a PersistentVolumeClaim and mount it; use a
  [StatefulSet](13-statefulsets.md) when each replica needs its own stable volume.
- Mount [ConfigMaps](09-configmaps.md) and [Secrets](10-secrets.md) as volumes to deliver
  config and credentials as files, with `readOnly: true` and restrictive `defaultMode`.
- Set `emptyDir.sizeLimit` so a runaway writer cannot exhaust node disk and evict
  neighbors.
- Avoid `hostPath`; if a node-level agent truly needs it, mount the narrowest path
  possible, `readOnly`, and constrain it with Pod Security Admission.
- Match the volume's access mode to the workload — do not assume `ReadWriteMany` is
  available; check the storage class.

## Examples

**Good Example** — read-only root, scratch `emptyDir`, durable data on a PVC

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: report-worker
spec:
  containers:
    - name: worker
      image: report-worker:2.3.0
      securityContext:
        readOnlyRootFilesystem: true   # container FS is immutable
      volumeMounts:
        - name: scratch
          mountPath: /tmp              # disposable scratch space
        - name: output
          mountPath: /data             # durable results
  volumes:
    - name: scratch
      emptyDir:
        sizeLimit: 1Gi                 # bounded so it cannot fill the node
    - name: output
      persistentVolumeClaim:
        claimName: report-output       # survives Pod rescheduling
```

**Bad Example** — important data on `emptyDir`, node-pinning `hostPath`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: report-worker
spec:
  containers:
    - name: worker
      image: report-worker:2.3.0
      volumeMounts:
        - name: data
          mountPath: /data     # writes "durable" reports here...
        - name: host
          mountPath: /host
  volumes:
    - name: data
      emptyDir: {}             # ...but emptyDir is DELETED with the Pod → data lost on any reschedule
    - name: host
      hostPath:
        path: /var/lib/reports # pins Pod to one node and exposes the host filesystem
```

## Common Mistakes

- Storing data that must persist in an `emptyDir` or the container's writable layer, then
  losing it on the next rollout or reschedule.
- Using `hostPath` as a persistence mechanism, coupling the Pod to a single node.
- Mounting `hostPath` into ordinary app Pods, opening a path to the host filesystem.
- Assuming `ReadWriteMany` works when the storage backend only supports `ReadWriteOnce`.
- Unbounded `emptyDir` filling node disk and triggering evictions of other Pods.
- Writing to a read-only-root container without providing a writable scratch volume,
  causing runtime failures.

## Production Tips

- Enforce `readOnlyRootFilesystem` and forbid `hostPath` cluster-wide via Pod Security
  Admission or a policy engine; grant exceptions only to audited node agents.
- Monitor node ephemeral-storage usage; `emptyDir` and image layers consume it and cause
  evictions when exhausted.
- For anything stateful, prefer a StatefulSet with `volumeClaimTemplates` so each replica
  gets its own durable volume with stable identity.

## AI Review Checklist

- Is any data that must survive a restart on a PersistentVolumeClaim, not `emptyDir` or
  the container layer?
- Is `emptyDir` used only for scratch/cache, and is `sizeLimit` set?
- Is `hostPath` avoided (or, for a genuine node agent, narrow and `readOnly`)?
- Do containers run with a read-only root filesystem plus a writable scratch mount where
  needed?
- Are ConfigMaps and Secrets mounted `readOnly` with a restrictive `defaultMode`?
- Does the requested access mode (`ReadWriteOnce`/`ReadWriteMany`) match what the storage
  class actually supports?

## Related

- `knowledge/kubernetes/12-persistent-volumes.md`
- `knowledge/kubernetes/13-statefulsets.md`
- `knowledge/kubernetes/09-configmaps.md`
- `knowledge/kubernetes/10-secrets.md`
- `knowledge/kubernetes/04-pods.md`
