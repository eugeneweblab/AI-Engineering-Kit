---
id: kubernetes/27-best-practices
topic: kubernetes
slug: best-practices
title: "Kubernetes Best Practices"
type: doc
order: 27
status: ready
tags: [kubernetes, best-practices]
related: [kubernetes/26-production, kubernetes/22-security, kubernetes/18-rbac, kubernetes/19-resource-management, kubernetes/09-configmaps]
when_to_use: "Read before authoring or reviewing any Kubernetes manifest for correctness and maintainability."
---
# Kubernetes Best Practices

## Purpose

This document collects the cross-cutting conventions that make Kubernetes manifests
correct, reviewable, and reproducible — how to declare, name, configure, and secure
resources regardless of which specific object you are writing. It is the baseline an
agent applies to *every* manifest, on top of the object-specific docs.

These are not style preferences; each rule prevents a concrete failure mode: drift,
non-reproducible deploys, privilege creep, or an un-debuggable resource. Where a rule
belongs to a dedicated doc (security, resources), this links to it rather than
repeating it.

## Why It Matters

Manifests are the source of truth for a live, self-healing system. A sloppy manifest
does not just look bad — it drifts from Git, deploys a different image each time, grants
more access than needed, or cannot be traced back to an owner during an incident. Small
conventions (labels, pinned images, declared resources) compound into a cluster that is
auditable and recoverable; their absence compounds into one that nobody can reason
about. The rules below are cheap at authoring time and expensive to retrofit after an
outage.

## Core Principles

- **Declarative and in Git.** Every resource is a versioned manifest applied by CI/CD.
  Never `kubectl edit` live state; the change must live in the repo or it is lost on the
  next reconcile.
- **Pin everything.** Image tags to digests or immutable versions, chart versions,
  API versions. `latest` makes deploys non-reproducible and rollback impossible.
- **Least privilege by default.** Minimal RBAC (see [rbac](18-rbac.md)), non-root
  containers, dropped capabilities (see [security](22-security.md)), scoped namespaces.
- **Configuration is external.** App config in ConfigMaps/Secrets (see
  [configmaps](09-configmaps.md)), not baked into the image. Secrets are never in Git in
  plaintext.
- **Name and label consistently.** Use the recommended `app.kubernetes.io/*` labels so
  selectors, dashboards, and cost tooling can find resources.

## Best Practices

- Apply the standard labels — `app.kubernetes.io/name`, `.../instance`,
  `.../version`, `.../part-of`, `.../managed-by` — on every object; selectors and
  observability depend on them.
- Set a namespace explicitly on every namespaced resource; never rely on the caller's
  current context defaulting to `default`.
- Pin images to a digest (`image: app@sha256:...`) or an immutable semver tag; forbid
  `latest` and mutable tags in CI.
- Keep manifests templated (Helm/Kustomize) with one source and per-environment
  overlays — never fork copies per environment that drift apart.
- Declare resource requests/limits and probes on every workload (see
  [production](26-production.md)); a manifest without them is incomplete.
- Store secrets encrypted (Sealed Secrets, SOPS, or an external secrets operator), never
  as plaintext in the repo (see [security](22-security.md)).
- Run `kubectl apply --dry-run=server` and a linter (kubeconform, kube-linter) in CI so
  invalid or insecure manifests fail the build, not the cluster.
- Prefer `Deployment`/`StatefulSet` over bare pods; a bare pod is not rescheduled when
  its node dies.

## Examples

**Good Example** — labeled, namespaced, pinned, config externalized

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
  namespace: shop-prod           # explicit, never inherited from context
  labels:
    app.kubernetes.io/name: checkout
    app.kubernetes.io/version: "2.4.1"
    app.kubernetes.io/part-of: shop
    app.kubernetes.io/managed-by: argocd
spec:
  template:
    spec:
      containers:
        - name: checkout
          image: registry.example.com/checkout@sha256:9f2c...   # pinned by digest
          envFrom:
            - configMapRef: { name: checkout-config }           # config out of image
            - secretRef:    { name: checkout-secrets }          # secret out of Git
```

**Bad Example** — unpinned, unlabeled, config baked in, edited live

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout                 # no namespace -> lands in 'default'
  # no standard labels -> invisible to dashboards, cost, and selectors
spec:
  template:
    spec:
      containers:
        - name: checkout
          image: checkout:latest # non-reproducible; every deploy may differ
          env:
            - name: DB_PASSWORD
              value: "s3cr3t"     # secret in plaintext, committed to Git
# ...then patched by hand with `kubectl edit`, so Git no longer matches reality
```

## Common Mistakes

- Editing live objects with `kubectl edit`/`patch` instead of changing the manifest in
  Git, causing drift that reverts on the next sync.
- Using `latest` or mutable tags, so the running version is unknown and rollback is
  impossible.
- Hardcoding config and secrets into images or plaintext manifests.
- Omitting namespaces and standard labels, breaking selectors and observability.
- Copy-pasting manifests per environment instead of one templated source with overlays.
- Deploying bare pods that are never rescheduled after a node failure.

## Production Tips

- Adopt GitOps (Argo CD / Flux) so the cluster continuously reconciles to Git; manual
  changes are reverted automatically, eliminating drift.
- Enforce conventions with an admission policy (Kyverno/Gatekeeper): reject unlabeled,
  unpinned, or root-running workloads at apply time.
- Keep a single shared library of base charts/overlays so a fix propagates to every
  service instead of being reapplied by hand.

## AI Review Checklist

- Is the resource fully declarative and stored in Git (no live edits)?
- Are images pinned to a digest or immutable tag, never `latest`?
- Are standard `app.kubernetes.io/*` labels and an explicit namespace present?
- Is configuration in ConfigMaps/Secrets rather than baked into the image?
- Are secrets encrypted at rest, never plaintext in the repo?
- Do workloads use a controller (Deployment/StatefulSet), not a bare pod?
- Does CI lint and server-dry-run the manifest before it reaches the cluster?

## Related

- `knowledge/kubernetes/26-production.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/18-rbac.md`
- `knowledge/kubernetes/19-resource-management.md`
- `knowledge/kubernetes/09-configmaps.md`
