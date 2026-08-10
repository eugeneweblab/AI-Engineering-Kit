---
id: kubernetes/02-cluster
topic: kubernetes
slug: cluster
title: "Kubernetes Cluster"
type: doc
order: 2
status: ready
tags: [kubernetes, cluster, ResourceQuota, LimitRange, provisioning, making, configuring]
related: [kubernetes/01-architecture, kubernetes/03-nodes, kubernetes/18-rbac, kubernetes/25-upgrades, kubernetes/28-disaster-recovery]
when_to_use: "Read before provisioning, configuring, or making cluster-wide changes such as namespaces, upgrades, or multi-tenancy."
---
# Kubernetes Cluster

## Purpose

This document covers the cluster as a whole: how it is provisioned, how workloads are
partitioned with namespaces, and the cluster-wide concerns — versioning, tenancy, and
resource governance — that individual manifests cannot address. Read it before any change
that affects more than one team or workload.

## Why It Matters

A cluster is shared infrastructure. A single misconfiguration at this level — an unbounded
namespace, a missing quota, a version skew, an over-broad default service account — degrades
every tenant at once, not one app. Cluster-level decisions are also the hardest to reverse:
you can redeploy a pod in seconds, but re-partitioning namespaces or upgrading a control
plane touches everything. This is where a small amount of upfront rigor prevents cluster-wide
outages.

## Core Principles

- **Namespaces are for isolation and governance, not just naming.** Use them to scope RBAC,
  quotas, network policy, and limits per team or environment.
- **Prefer many small clusters or firm namespace boundaries over one flat shared space.**
  Hard multi-tenancy on a single cluster is difficult; namespaces are a soft boundary, not a
  security boundary by themselves.
- **Every namespace needs guardrails.** A namespace with no `ResourceQuota` or `LimitRange`
  lets one workload starve the rest of the cluster.
- **The cluster has a version, and it constrains everything.** Node, add-on, and client
  versions must stay within the supported skew of the control plane.

## Best Practices

- Provision clusters as code (managed services like EKS/GKE/AKS, or IaC such as Terraform);
  never click-configure production. The cluster definition belongs in git.
- Give each team/environment its own namespace with a `ResourceQuota` and a `LimitRange` so
  no tenant can consume the whole cluster or omit resource requests.
- Do not deploy into `default`; it has no quotas or ownership and becomes an untracked dumping
  ground.
- Combine namespaces with [RBAC](18-rbac.md) (scoped `RoleBindings`) and
  [NetworkPolicies](17-network-policies.md) to make the boundary real, not cosmetic.
- Plan upgrades deliberately, one minor version at a time, draining nodes gracefully — see
  [upgrades](25-upgrades.md).

## Examples

**Good Example** — a governed namespace with quota and default limits

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-payments      # per-team boundary, not the shared default
---
apiVersion: v1
kind: ResourceQuota
metadata: { name: quota, namespace: team-payments }
spec:
  hard:                    # caps total consumption so one team can't starve others
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    pods: "100"
---
apiVersion: v1
kind: LimitRange
metadata: { name: defaults, namespace: team-payments }
spec:
  limits:
    - type: Container
      default:            # applied when a pod omits limits, so nothing runs unbounded
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
```

**Bad Example** — everything in `default`, no guardrails

```yaml
# No namespace field → lands in "default", which has no quota, no ownership,
# no network policy. One runaway pod can consume every node's CPU and memory,
# and there is no way to attribute cost or revoke access per team.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web            # ends up in default, unbounded and untracked
spec:
  selector: { matchLabels: { app: web } }
  replicas: 50
  template:
    metadata: { labels: { app: web } }
    spec:
      containers:
        - name: web
          image: web:latest
          # ...no ResourceQuota constrains this; 50 unbounded pods can drain the cluster
```

## Common Mistakes

- Deploying real workloads into the `default` namespace.
- Creating namespaces with no `ResourceQuota`/`LimitRange`, letting workloads run unbounded.
- Treating namespaces as a hard security boundary — pods can still reach each other without
  a [NetworkPolicy](17-network-policies.md).
- Upgrading across multiple minor versions at once, breaking API and skew compatibility.
- Hand-building clusters through a console so the configuration exists nowhere in git.

## Production Tips

- Label namespaces with owner, environment, and cost-center for attribution and policy.
- Enforce cluster-wide policy (no privileged pods, required labels, disallowed registries)
  with an admission policy engine (Kyverno or built-in ValidatingAdmissionPolicy).
- Keep a documented, tested restore path for the whole cluster, not just etcd — see
  [disaster recovery](28-disaster-recovery.md).

## AI Review Checklist

- Is every workload in a purpose-scoped namespace rather than `default`?
- Does each namespace have a `ResourceQuota` and a `LimitRange`?
- Is namespace isolation reinforced with scoped RBAC and NetworkPolicies?
- Is the cluster provisioned as code and within supported version skew?

## Related

- `knowledge/kubernetes/01-architecture.md`
- `knowledge/kubernetes/03-nodes.md`
- `knowledge/kubernetes/18-rbac.md`
- `knowledge/kubernetes/25-upgrades.md`
- `knowledge/kubernetes/28-disaster-recovery.md`
