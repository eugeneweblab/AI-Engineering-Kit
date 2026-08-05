---
id: kubernetes/18-rbac
topic: kubernetes
slug: rbac
title: "RBAC"
type: doc
order: 18
status: ready
tags: [kubernetes, rbac, ClusterRole, secrets, ServiceAccount, watch, Role, cluster-admin]
related: [kubernetes/22-security, kubernetes/10-secrets, kubernetes/17-network-policies, kubernetes/99-ai-review-checklist]
when_to_use: "Read before granting a user, group, or ServiceAccount any permission in a cluster, or when reviewing Role/RoleBinding manifests."
---
# RBAC

## Purpose

This document defines how to grant Kubernetes API permissions with Role-Based
Access Control (RBAC): what a subject (user, group, or ServiceAccount) may do, to
which resources, in which namespace. It is written so an agent can author or review
RBAC manifests without over-granting access.

RBAC answers "may this subject perform this verb on this resource?". It governs the
Kubernetes API only — it does not control pod-to-pod network traffic (see
[network policies](17-network-policies.md)) or in-container Linux privileges (see
[security](22-security.md)). Do not conflate them.

## Why It Matters

Every pod ships with a ServiceAccount token mounted by default. If that account is
bound to broad permissions, a single compromised container becomes a cluster-wide
foothold: it can read every Secret, create privileged pods, or delete workloads. RBAC
is the boundary that turns "one hacked pod" into "one hacked pod" instead of "the whole
cluster." The failure is silent — an over-permissive Role works perfectly until it is
abused — so RBAC must be reviewed as security-critical code, not boilerplate.

## Core Principles

- **Least privilege by default.** Grant the narrowest verbs on the fewest resources in
  the smallest scope that lets the workload function. Start from zero and add.
- **Namespace-scope over cluster-scope.** Prefer `Role` + `RoleBinding` to
  `ClusterRole` + `ClusterRoleBinding`. Cluster scope is only for genuinely
  cluster-wide needs (nodes, PersistentVolumes, CRDs).
- **Name every subject.** Bind to a specific, purpose-built ServiceAccount — never the
  `default` account and never a wildcard group.
- **No wildcards.** `verbs: ["*"]` or `resources: ["*"]` grants tomorrow's resources
  you have not reviewed. Enumerate what you need.
- **RBAC is additive and permissive-union.** There are no deny rules; a subject's
  permissions are the union of all its bindings. You cannot subtract, only avoid adding.

## Best Practices

- Create one dedicated ServiceAccount per workload and set
  `automountServiceAccountToken: false` on pods that never call the API.
- Grant `get`/`list`/`watch` for read-only controllers; add `create`/`update`/`patch`/
  `delete` only where the code demonstrably writes.
- Never grant `get`, `list`, or `watch` on `secrets` cluster-wide — this leaks every
  credential in the cluster. Scope it to one namespace and, if possible, one Secret via
  `resourceNames`.
- Avoid binding the built-in `cluster-admin` ClusterRole to anything but break-glass
  admin accounts.
- Reuse the built-in aggregated ClusterRoles (`view`, `edit`, `admin`) for human users
  instead of hand-rolling equivalents.
- Audit with `kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa>` before
  shipping; it shows exactly what a subject can do.
- Treat `escalate`, `bind`, and `impersonate` verbs as privileged — they let a subject
  grant itself more access.

## Examples

**Good Example** — a dedicated account with a namespaced, verb-limited Role

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: order-reader
  namespace: shop
automountServiceAccountToken: false   # pod only reads at startup, not per-request
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role                            # namespaced, not ClusterRole
metadata:
  name: config-reader
  namespace: shop
rules:
  - apiGroups: [""]
    resources: ["configmaps"]        # only configmaps, not secrets
    verbs: ["get", "list", "watch"]  # read-only; no create/update/delete
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: order-reader-config
  namespace: shop
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: config-reader
subjects:
  - kind: ServiceAccount
    name: order-reader             # bound to a specific SA, not "default"
    namespace: shop
```

**Bad Example** — cluster-wide wildcards on the default account

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole                    # cluster scope for a namespaced app
metadata:
  name: app-role
rules:
  - apiGroups: ["*"]                 # every API group
    resources: ["*"]                 # includes secrets, nodes, everything
    verbs: ["*"]                     # read AND write AND delete
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: app-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: app-role
subjects:
  - kind: ServiceAccount
    name: default                    # every pod without its own SA inherits this
    namespace: shop
```

## Common Mistakes

- Binding workloads to `cluster-admin` "to make it work," then never narrowing it.
- Granting `secrets` read access cluster-wide, exposing all credentials.
- Using `ClusterRoleBinding` where a namespaced `RoleBinding` would do.
- Leaving the `default` ServiceAccount permissioned and auto-mounted into every pod.
- Wildcard `verbs`/`resources` that silently cover future CRDs and APIs.
- Forgetting `escalate`/`bind` let a subject grant itself higher privileges.
- Assuming RBAC blocks network traffic — it only guards the Kubernetes API.

## Production Tips

- Enable API server audit logging and alert on `secrets` access and any use of
  `impersonate`, `escalate`, or `bind`.
- Run `kubectl auth can-i` checks in CI against rendered manifests to catch
  over-grants before merge.
- Periodically diff live RBAC against source of truth; drift is where privilege creeps.

## AI Review Checklist

- Is every binding scoped to a named, purpose-built ServiceAccount (never `default`)?
- Are verbs limited to what the code actually calls (no gratuitous write/delete)?
- Are there any `*` wildcards in `apiGroups`, `resources`, or `verbs`?
- Is `secrets` access namespaced and, ideally, restricted by `resourceNames`?
- Is `Role`/`RoleBinding` used unless cluster scope is genuinely required?
- Is `automountServiceAccountToken: false` set where the pod never calls the API?
- Are `escalate`, `bind`, and `impersonate` grants intentional and reviewed?

## Related

- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/10-secrets.md`
- `knowledge/kubernetes/17-network-policies.md`
- `knowledge/kubernetes/99-ai-review-checklist.md`
