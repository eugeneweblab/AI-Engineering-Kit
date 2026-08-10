---
id: kubernetes/28-disaster-recovery
topic: kubernetes
slug: disaster-recovery
title: "Kubernetes Disaster Recovery"
type: doc
order: 28
status: ready
tags: [kubernetes, disaster-recovery, VolumeSnapshot, posture, procedures, backups]
related: [kubernetes/25-upgrades, kubernetes/12-persistent-volumes, kubernetes/13-statefulsets, kubernetes/26-production, kubernetes/23-monitoring]
when_to_use: "Read before designing backups, recovery procedures, or reviewing a cluster's DR posture."
---
# Kubernetes Disaster Recovery

## Purpose

This document defines how to survive and recover from the loss of Kubernetes state:
a corrupted etcd, a deleted namespace, a failed upgrade, or an entire cluster or region
going down. It is written so an agent can design backups that actually restore and a
recovery procedure that has been proven, not assumed.

Disaster recovery on Kubernetes has two distinct halves: the *cluster state* (etcd — every
object the API server knows about) and the *application data* (PersistentVolumes backing
databases and stateful apps). A backup that covers only one half cannot bring a service
back.

## Why It Matters

Kubernetes is self-healing for node and pod failures, which lulls teams into thinking it
protects data. It does not: a `kubectl delete namespace`, an etcd corruption, or a
control-plane failure can erase the definition of every workload, and a lost PV erases
the data itself. Recovery is only as good as the last *tested* restore — untested
backups routinely turn out to be empty, unreadable, or missing the volumes. Recovery
objectives (how much data you can lose, how long you can be down) must be decided *before*
the incident, because during one there is no time to design a procedure. The cost of
getting this wrong is permanent data loss.

## Core Principles

- **Back up both halves.** etcd (cluster state) *and* PersistentVolumes (app data).
  Either alone leaves you unable to restore a working service.
- **A backup you have not restored does not exist.** Rehearse restores on a schedule;
  measure how long they take.
- **Define RPO and RTO first.** How much data loss is tolerable (RPO) and how long you
  may be down (RTO) drive backup frequency and topology — not the reverse.
- **Store backups off-cluster and off-region.** A backup inside the cluster it protects
  dies with it.
- **Reproduce the cluster from Git.** Manifests in Git (GitOps) mean you rebuild
  workloads by re-syncing; backups then only need state and data, not YAML.

## Best Practices

- Snapshot **etcd** on a schedule (`etcdctl snapshot save`) or use the managed
  provider's control-plane backup; store snapshots encrypted and off-region.
- Back up **PersistentVolumes** with a Kubernetes-aware tool (Velero, or the CSI
  driver's `VolumeSnapshot`) so volume and object metadata are captured together (see
  [persistent-volumes](12-persistent-volumes.md)).
- Use application-consistent snapshots for databases — quiesce or use the DB's own
  backup — since a raw volume snapshot of a running DB can be torn/unrecoverable (see
  [statefulsets](13-statefulsets.md)).
- Keep all manifests in Git so the cluster's *desired state* is reproducible without a
  backup; back up only what Git cannot hold (etcd secrets state, PV data).
- Test restores end-to-end into a scratch cluster/namespace at a fixed cadence; record
  the actual RTO achieved.
- Take an etcd snapshot immediately before every upgrade (see [upgrades](25-upgrades.md))
  as the rollback anchor.
- Monitor backup jobs and alert on failure (see [monitoring](23-monitoring.md)); a
  silently failing backup is the classic DR trap.

## Examples

**Good Example** — scheduled, verified, application-consistent backups

```bash
# Cluster state: snapshot etcd, store the snapshot OFF-cluster and encrypted.
etcdctl --endpoints=$ETCD snapshot save /backup/etcd-$(date +%F).db
aws s3 cp /backup/etcd-$(date +%F).db s3://dr-backups/ --sse aws:kms

# App data: schedule Velero to back up namespace + its PVs together, off-region.
velero schedule create prod-daily \
  --schedule="0 2 * * *" \
  --include-namespaces shop-prod \
  --snapshot-volumes --ttl 720h

# PROVE it: restore into a scratch namespace and validate data before trusting it.
velero restore create --from-backup prod-daily-20260707 \
  --namespace-mappings shop-prod:dr-test
```

**Bad Example** — partial, in-cluster, never tested

```bash
# Backs up ONLY etcd -> restores object definitions but every PV is empty:
# the database comes back with no data.
etcdctl snapshot save /mnt/data/etcd.db     # and PVs are never captured

# Stores the snapshot on a PVC INSIDE the same cluster it protects:
# a cluster/region loss destroys the backup too.
kubectl cp etcd.db backup-pod:/data/etcd.db

# The restore path is never exercised, so nobody knows the snapshot is
# unreadable until the real disaster.
```

## Common Mistakes

- Backing up etcd but not PersistentVolumes (or vice versa), so a restore has structure
  without data or data without structure.
- Storing backups inside the same cluster/region they protect.
- Never running a restore, so the first real attempt fails on an empty or corrupt
  snapshot.
- Volume-snapshotting a running database without quiescing, producing a torn,
  unrecoverable image.
- No defined RPO/RTO, so backup frequency and topology are arbitrary.
- Silent backup-job failures with no alerting.

## Production Tips

- Automate a monthly game-day: restore prod into a scratch cluster and time it against
  your RTO target; treat a miss as a defect.
- Keep an infrastructure-as-code definition of the cluster itself (Terraform/eksctl) so
  a lost control plane is rebuilt reproducibly, then re-hydrated from backups.
- Encrypt backups and manage keys separately from the cluster, so a compromised cluster
  does not expose its own recovery data.

## AI Review Checklist

- Are both etcd (cluster state) and PersistentVolumes (app data) backed up?
- Are backups stored off-cluster and off-region, and encrypted?
- Are database backups application-consistent, not raw snapshots of a live volume?
- Are restores tested end-to-end on a schedule, with the measured RTO recorded?
- Are defined RPO/RTO targets driving backup frequency and topology?
- Is an etcd snapshot taken immediately before every upgrade?
- Do backup jobs alert on failure?

## Related

- `knowledge/kubernetes/25-upgrades.md`
- `knowledge/kubernetes/12-persistent-volumes.md`
- `knowledge/kubernetes/13-statefulsets.md`
- `knowledge/kubernetes/26-production.md`
- `knowledge/kubernetes/23-monitoring.md`
