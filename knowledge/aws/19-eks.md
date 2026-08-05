---
id: aws/19-eks
topic: aws
slug: eks
title: "EKS"
type: doc
order: 19
status: ready
tags: [aws, eks, cluster-admin, "@sha", ServiceAccount, Role, ClusterRole, resources.requests]
related: [aws/18-ecs, aws/20-ecr, aws/02-iam, aws/06-vpc, aws/11-auto-scaling]
when_to_use: "Read before provisioning an EKS cluster, node group, or workload IAM binding."
---
# EKS

## Purpose

This document defines how to run Kubernetes on AWS with Amazon EKS correctly: cluster
setup, node compute, pod-level IAM, networking, and upgrades. It is written so an agent
can provision a cluster and schedule workloads without granting cluster-wide privilege,
running unpatched nodes, or falling behind on unavoidable version upgrades.

EKS gives you a managed Kubernetes control plane; you bring the workloads and (usually)
the nodes. Choose EKS over [ECS](18-ecs.md) when you need the Kubernetes ecosystem
(Helm, operators, portability across clouds). The cost is real operational complexity —
do not pick EKS for a handful of containers that ECS Fargate would run.

## Why It Matters

EKS multiplies both the power and the failure surface of Kubernetes with AWS-specific
sharp edges. The dangerous mistakes are structural: giving every pod the node's IAM role
means one compromised pod inherits the node's AWS access; skipping IRSA or Pod Identity
means credentials leak through instance metadata; and ignoring the version-support clock
means the control plane force-upgrades under you. Kubernetes upgrades are mandatory and
frequent — EKS supports each minor version for a limited window, so a cluster you forget
about becomes an unsupported, auto-upgraded liability.

## Core Principles

- **Grant AWS permissions per pod, not per node.** Use **EKS Pod Identity** (preferred)
  or **IRSA** so a pod's service account maps to a scoped IAM role. Never let workloads
  ride the node instance role — that is account access for anything scheduled there.
- **Least privilege inside the cluster too.** RBAC on `Role`/`ClusterRole` binds users
  and service accounts to only what they need. `cluster-admin` is for humans in a break-
  glass, not for controllers.
- **Nodes are cattle; patch by replacement.** Use managed node groups or Fargate
  profiles so nodes are recreated from patched AMIs, not manually patched in place.
- **Stay inside the supported version window.** Plan minor-version upgrades on a cadence;
  an unsupported cluster is upgraded for you, on AWS's schedule, not yours.
- **The API server is a control plane you must protect.** Restrict public endpoint
  access or make the endpoint private; anyone who reaches it with credentials owns your
  workloads.

## Best Practices

- Map IAM to cluster access with **EKS access entries** (the current API) rather than
  hand-editing the legacy `aws-auth` ConfigMap, which is error-prone and easy to lock
  yourself out of.
- Use **managed node groups** or **Fargate profiles** so AWS handles node provisioning,
  draining, and AMI updates. Self-managed nodes mean you own that toil.
- Restrict the cluster API endpoint: private-only, or public with a CIDR allowlist.
  Never leave it open to `0.0.0.0/0` with only credentials as the gate.
- Attach a scoped IAM role to each workload via Pod Identity / IRSA, and set
  `automountServiceAccountToken: false` on pods that need no Kubernetes API access.
- Run the **cluster autoscaler** or **Karpenter** for node scaling and the
  **Horizontal Pod Autoscaler** for pod scaling; do not fix replica counts by hand.
- Set pod `resources.requests` and `limits` so the scheduler can bin-pack and the
  kubelet can protect nodes from a runaway pod.
- Enable **control plane audit logging** to CloudWatch and encrypt Kubernetes secrets
  at rest with a KMS key (`encryptionConfig`).
- Keep add-ons (VPC CNI, CoreDNS, kube-proxy) as **managed EKS add-ons** so they upgrade
  with the cluster instead of drifting.

## Examples

**Good Example** — pod-scoped IAM via a service account (IRSA/Pod Identity)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: orders-api
  namespace: orders
  annotations:
    # Binds this service account to a scoped IAM role — pods get only these AWS perms.
    eks.amazonaws.com/role-arn: arn:aws:iam::111122223333:role/orders-api-s3-read
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders-api, namespace: orders }
spec:
  template:
    spec:
      serviceAccountName: orders-api          # not the node role
      containers:
        - name: api
          image: 111122223333.dkr.ecr.eu-west-1.amazonaws.com/orders@sha256:9c4f...
          resources:
            requests: { cpu: "250m", memory: "512Mi" }  # lets the scheduler bin-pack
            limits:   { cpu: "500m", memory: "512Mi" }  # caps a runaway pod
```

**Bad Example** — pods inherit the node role, no resource bounds

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders-api, namespace: orders }
spec:
  template:
    spec:
      # No serviceAccountName -> pods use the node instance role, which can read
      # every AWS resource the node can. One RCE = account-wide AWS access.
      containers:
        - name: api
          image: .../orders:latest        # mutable tag: unknowable version
          # no resources -> one pod can starve every other pod on the node
```

## Common Mistakes

- Relying on the node instance role for pod AWS access instead of Pod Identity / IRSA.
- Leaving the cluster API endpoint public with no CIDR restriction.
- Letting the cluster fall out of the supported version window and getting force-upgraded.
- Editing `aws-auth` by hand and locking all admins out of the cluster.
- Omitting resource requests/limits, so the scheduler over-packs nodes and pods get OOM-
  killed unpredictably.
- Running unmanaged add-ons that drift and break during a control-plane upgrade.
- Handing `cluster-admin` to CI or application service accounts.

## Production Tips

- Test upgrades in a non-prod cluster first; upgrade the control plane, then node groups,
  then add-ons, and drain nodes with `PodDisruptionBudget`s in place.
- Use **Karpenter** for fast, cost-aware node provisioning that picks instance types from
  pending pod requirements instead of pre-sized node groups.
- Ship control-plane audit logs and pod logs to CloudWatch or a SIEM; audit logs are your
  record of who did what to the cluster.
- Enforce policy (no privileged pods, no `hostPath`, image provenance) with an admission
  controller like Kyverno or OPA Gatekeeper.

## AI Review Checklist

- Do workloads get AWS permissions via Pod Identity/IRSA rather than the node role?
- Is the API server endpoint private or CIDR-restricted, not open to the world?
- Is cluster access managed with access entries, not hand-edited `aws-auth`?
- Are node groups managed/Fargate so patching happens by replacement?
- Does every pod set resource requests and limits?
- Is the cluster within the supported Kubernetes version window with an upgrade plan?
- Are audit logging and KMS secret encryption enabled?

## Related

- `knowledge/aws/18-ecs.md`
- `knowledge/aws/20-ecr.md`
- `knowledge/aws/02-iam.md`
- `knowledge/aws/06-vpc.md`
- `knowledge/aws/11-auto-scaling.md`
