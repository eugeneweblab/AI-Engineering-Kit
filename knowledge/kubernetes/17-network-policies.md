---
id: kubernetes/17-network-policies
topic: kubernetes
slug: network-policies
title: "Network Policies"
type: doc
order: 17
status: ready
tags: [kubernetes, network-policies]
related: [kubernetes/07-services, kubernetes/22-security, kubernetes/18-rbac, kubernetes/04-pods, kubernetes/26-production]
when_to_use: "Read before securing pod-to-pod traffic, isolating a namespace, or reviewing any cluster's east-west network security."
---
# Network Policies

## Purpose

This document defines how to control which pods may talk to which, using a **NetworkPolicy**.
By default, Kubernetes networking is wide open: every pod can reach every other pod in the
cluster, across all namespaces. A NetworkPolicy is a namespaced firewall that restricts
**ingress** (who may connect to a pod) and **egress** (where a pod may connect) based on pod
labels, namespaces, and IP blocks.

This is east-west (pod-to-pod) security. It complements, but does not replace,
[RBAC](18-rbac.md) (who may call the Kubernetes API) and application-level authz. Think of
it as network segmentation for the microsegmented world inside the cluster.

## Why It Matters

The default-open network means a single compromised pod — a vulnerable image, a leaked
credential, an SSRF — can reach *every* database, secret store, and internal API in the
cluster. Lateral movement is how a small breach becomes a total one, and without
NetworkPolicies there is nothing to stop it. Worse, the absence of a policy is invisible:
the app works identically whether or not the blast radius is contained, so the gap is never
noticed until an attacker exploits it. Network segmentation is a load-bearing control for
compliance (PCI, SOC 2) and for blast-radius reduction. Because the failure mode is "silent,
until catastrophic breach," this is held to the same bar as authentication.

## Core Principles

- **Policies are additive and default-allow until one selects a pod.** A pod with *no*
  policy selecting it allows all traffic. The moment *any* policy selects it for a direction,
  that direction becomes default-deny except what the policies explicitly allow.
- **You need a CNI that enforces them.** NetworkPolicy is an API, not an implementation.
  Flannel (default) ignores it; you need Calico, Cilium, or an equivalent. Applying policies
  under a non-enforcing CNI gives a false sense of security.
- **Ingress and egress are independent.** Locking down ingress does nothing to egress. A
  compromised pod with open egress can exfiltrate data or call a C2 server.
- **Selectors are label-based.** Policies match pods and namespaces by labels, so correct
  labeling is a security control. A mislabeled pod is an unprotected pod.
- **Allow-list, don't deny-list.** Start from deny-all and open exactly what is needed;
  enumerate-what-to-block is always incomplete.

## Best Practices

- Apply a **default-deny** policy (ingress *and* egress) per namespace, then add narrow
  allow rules. This is the only posture that fails safe.
- Always allow **DNS egress** (UDP/TCP 53 to kube-dns/CoreDNS) when you default-deny egress,
  or every name lookup — and thus nearly everything — breaks.
- Scope allow rules with both `podSelector` **and** `namespaceSelector`; an empty
  `namespaceSelector: {}` means "all namespaces," which is usually too broad.
- Combine peer selectors carefully: within one `from`/`to` array element, `podSelector` +
  `namespaceSelector` is an **AND**; separate array elements are an **OR**. This distinction
  is the most common source of accidental over-permission.
- Label namespaces (e.g. `kubernetes.io/metadata.name`, or your own `tier`, `env`) so
  policies can select them reliably.
- Restrict egress to databases and third-party APIs by `ipBlock` (with `except` for
  metadata endpoints like `169.254.169.254`) to prevent SSRF and metadata theft.
- Test policies in a staging namespace; a wrong default-deny can black-hole production
  traffic instantly.

## Examples

**Good Example** — default-deny plus explicit allow (with DNS)

```yaml
# 1) Default-deny ALL ingress and egress in the namespace: fail safe.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: payments }
spec:
  podSelector: {}                 # selects every pod in the namespace
  policyTypes: [Ingress, Egress]  # both directions locked down
---
# 2) Allow the api pods to reach postgres, and allow DNS so name lookups work.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api-egress, namespace: payments }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Egress]
  egress:
    - to:
        - podSelector: { matchLabels: { app: postgres } }  # only the DB, nothing else
      ports: [{ protocol: TCP, port: 5432 }]
    - to:                          # DNS is mandatory once egress is denied by default
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
      ports:
        - { protocol: UDP, port: 53 }
        - { protocol: TCP, port: 53 }
```

**Bad Example** — over-broad allow that isolates nothing

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-all-ingress, namespace: payments }
spec:
  podSelector: {}
  policyTypes: [Ingress]
  ingress:
    - {}                          # BUG: empty rule = allow from ANY pod, ANY namespace
  # No egress policy at all → a compromised pod can call out anywhere and exfiltrate data.
  # Net effect: looks like "security exists" but the pod is fully open.
```

## Common Mistakes

- Assuming policies are enforced when the CNI (e.g. Flannel) ignores them entirely.
- Locking down ingress but leaving egress wide open, permitting data exfiltration and SSRF.
- Applying a default-deny egress without a DNS allow rule, breaking every name lookup.
- Confusing AND vs OR in peer selectors and accidentally allowing all namespaces.
- Relying on IP-based rules for pod peers — pod IPs are ephemeral; use label selectors.
- Forgetting to label namespaces, so `namespaceSelector` matches nothing (or everything).
- Treating NetworkPolicy as a substitute for RBAC or app authz; they secure different layers.

## Production Tips

- Roll out default-deny in **audit/log mode** first if your CNI supports it (Cilium
  policy-audit, Calico staged policies) to see what would break before it does.
- Alert on denied-flow metrics from the CNI; a spike is either an attack or a missing allow rule.
- Keep a small library of reusable policies (default-deny, allow-DNS, allow-same-namespace)
  and apply them via your platform tooling so every namespace starts locked down.
- Pair egress restrictions with blocking the cloud metadata IP (`169.254.169.254`) to defend
  the credential-theft path that turns SSRF into cluster compromise.

## AI Review Checklist

- Does each sensitive namespace have a **default-deny** policy for both ingress and egress?
- Is the cluster CNI one that actually enforces NetworkPolicy (Calico, Cilium, …)?
- When egress is denied by default, is DNS (port 53 to kube-system) explicitly allowed?
- Are allow rules scoped by specific pod *and* namespace selectors, not empty `{}` peers?
- Is egress to external systems restricted, including blocking the metadata endpoint?
- Are the pods and namespaces referenced by selectors actually labeled to match?
- Is NetworkPolicy used alongside [RBAC](18-rbac.md), not as a replacement for it?

## Related

- `knowledge/kubernetes/07-services.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/18-rbac.md`
- `knowledge/kubernetes/04-pods.md`
- `knowledge/kubernetes/26-production.md`
