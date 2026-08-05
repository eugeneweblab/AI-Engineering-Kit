---
id: kubernetes/25-upgrades
topic: kubernetes
slug: upgrades
title: "Upgrades"
type: doc
order: 25
status: ready
tags: [kubernetes, upgrades, drain, only, PodDisruptionBudgets, NotReady, Ready, kubectl]
related: [kubernetes/26-production, kubernetes/28-disaster-recovery, kubernetes/05-deployments, kubernetes/03-nodes, kubernetes/13-statefulsets]
when_to_use: "Read before upgrading a cluster control plane, node pool, or any API-version-sensitive workload."
---
# Upgrades

## Purpose

This document defines how to upgrade Kubernetes safely: the control plane, worker
nodes, and the workloads whose manifests depend on API versions that change across
releases. It is written so an agent can plan and sequence an upgrade without breaking
running services or stranding resources on a removed API.

Two upgrades are in scope: the *cluster* (Kubernetes itself, one minor version at a
time) and the *workloads* (Deployments, Services, add-ons) that must stay compatible
with the new API surface. Getting the order wrong takes an application down mid-upgrade.

## Why It Matters

Kubernetes ships a new minor version roughly every three to four months and supports
only the last three. Falling behind forces a rushed multi-version jump, exactly the
riskiest kind. Each release deprecates and eventually *removes* APIs; a manifest that
applied fine last year can be silently rejected after an upgrade, so a Deployment fails
to reconcile in the middle of an incident. Control-plane and node skew is bounded (a
kubelet may trail the API server by at most three minors, never lead it), and violating
skew makes nodes go `NotReady`. The blast radius is the whole cluster, so upgrades are
planned, staged, and reversible — never applied straight to production.

## Core Principles

- **One minor version at a time.** Never skip minors (1.30 -> 1.32). Each hop has its
  own migration notes; skipping them compounds breaking changes.
- **Control plane first, then nodes.** The API server must be at or ahead of every
  kubelet. Upgrade masters, verify, then roll node pools.
- **Read the removal notices before you touch anything.** Every release removes APIs;
  check the deprecation guide and scan your manifests with `kubectl` /
  `kubent`/`pluto`.
- **Drain, don't kill.** Cordon and `drain` a node so pods reschedule gracefully under
  their PodDisruptionBudgets before the node reboots.
- **Have a rollback and a backup.** Snapshot etcd (see
  [disaster-recovery](28-disaster-recovery.md)) and know the downgrade path before you
  start.

## Best Practices

- Upgrade a staging cluster on the same version first; treat its result as a gate.
- Scan for removed/deprecated APIs and migrate manifests *before* the control-plane
  hop, so nothing is stranded on a gone API.
- Define PodDisruptionBudgets (see [production](26-production.md)) so `drain` respects
  minimum availability instead of evicting every replica at once.
- Cordon -> drain -> upgrade -> uncordon each node, one at a time (or in small
  surge batches on managed pools), verifying `Ready` before the next.
- Upgrade cluster add-ons (CNI, CoreDNS, CSI drivers, ingress controller) to versions
  the target Kubernetes release supports — they are not covered by the core upgrade.
- Pause and validate between phases: control plane healthy, then one node, then the
  rest. Watch [monitoring](23-monitoring.md) between steps.
- For StatefulSets, confirm the update strategy and PVC behavior
  (see [statefulsets](13-statefulsets.md)) before draining their nodes.

## Examples

**Good Example** — staged, skew-safe node upgrade with graceful eviction

```bash
# 1. BEFORE upgrading: catch manifests on APIs the new version removes.
kubectl deprecations 2>/dev/null || pluto detect-all-in-cluster   # e.g. removed batch/v1beta1

# 2. Upgrade control plane FIRST, one minor only (managed cluster shown).
gcloud container clusters upgrade prod --master --cluster-version=1.31

# 3. Roll nodes one at a time: cordon, drain (respects PDBs), then upgrade.
kubectl cordon node-3
kubectl drain node-3 --ignore-daemonsets --delete-emptydir-data --timeout=10m
# ... node-3 upgraded & rejoined ...
kubectl uncordon node-3     # verify Ready before moving to node-4
```

**Bad Example** — skips versions and force-kills workloads

```bash
# Jumps two minors: skips 1.31's migration notes and removed-API checks.
gcloud container clusters upgrade prod --cluster-version=1.32

# Force-deletes pods instead of draining: ignores PodDisruptionBudgets,
# so every replica of a service can vanish at once -> outage.
kubectl delete pods --all --grace-period=0 --force

# No etcd snapshot, no staging run, no rollback plan: if the API server
# fails to come up, there is nothing to restore to.
```

## Common Mistakes

- Skipping minor versions and hitting multiple breaking changes at once.
- Upgrading kubelets ahead of the API server, violating version skew.
- Applying manifests that still use a removed API version, so Deployments silently fail
  to reconcile after the hop.
- Draining without PodDisruptionBudgets, evicting every replica simultaneously.
- Forgetting add-ons (CNI/CoreDNS/CSI), which then break on the new version.
- Starting with no etcd backup or rollback path.

## Production Tips

- Subscribe to the release calendar and budget a quarterly upgrade cadence; do not let
  the cluster drift out of support.
- On managed clusters (EKS/GKE/AKS), prefer surge upgrades on node pools with a
  maxUnavailable of 1 and a PDB, so capacity is preserved.
- Gate every upgrade behind a green staging run and a fresh etcd snapshot recorded in
  the change ticket.

## AI Review Checklist

- Is the upgrade a single minor-version hop, not a skip?
- Were removed/deprecated APIs scanned and manifests migrated before the control plane?
- Is the control plane upgraded before any kubelet, keeping skew within bounds?
- Are nodes cordoned and drained (not force-killed), respecting PodDisruptionBudgets?
- Are add-ons (CNI, CoreDNS, CSI, ingress) upgraded to compatible versions?
- Is there a recent etcd backup and a documented rollback before starting?

## Related

- `knowledge/kubernetes/26-production.md`
- `knowledge/kubernetes/28-disaster-recovery.md`
- `knowledge/kubernetes/05-deployments.md`
- `knowledge/kubernetes/03-nodes.md`
- `knowledge/kubernetes/13-statefulsets.md`
