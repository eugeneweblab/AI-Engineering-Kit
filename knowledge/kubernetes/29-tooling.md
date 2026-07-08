---
id: kubernetes/29-tooling
topic: kubernetes
slug: tooling
title: "Tooling"
type: doc
order: 29
status: ready
tags: [kubernetes, tooling]
related: [kubernetes/27-best-practices, kubernetes/24-debugging, kubernetes/22-security, kubernetes/26-production, kubernetes/21-observability]
when_to_use: "Read before choosing how to template, apply, secure, or observe Kubernetes manifests in a project."
---
# Tooling

## Purpose

This document defines the standard tooling around Kubernetes: how to template
manifests, apply them safely, catch bad config before it reaches the cluster, and
manage secrets and packages. It is written so an agent picks tools that reinforce the
declarative, reproducible workflow instead of undermining it.

The goal is not a long tool list but a coherent chain: author with a templating tool,
gate with linters and policy in CI, deploy with GitOps, and observe with a standard
stack. Each link enforces a rule the previous doc set out.

## Why It Matters

Tool choices decide whether the cluster stays in sync with Git or drifts, whether an
insecure manifest is caught in review or in production, and whether the next engineer
can reproduce a deploy. The wrong chain — hand-run `kubectl apply` from laptops,
copied YAML per environment, secrets pasted into ConfigMaps — recreates every problem
the [best-practices](27-best-practices.md) doc warns against. The right chain makes the
correct thing the easy thing: CI rejects bad manifests, GitOps reverts drift, and
policy blocks privilege creep automatically. Tooling is where principles become
enforced.

## Core Principles

- **Template one source, overlay per environment.** Helm or Kustomize with a single
  base; never fork full copies of manifests that drift.
- **Shift validation left.** Lint, schema-check, and policy-scan manifests in CI so
  failures happen in the PR, not the cluster.
- **Deploy via GitOps, not by hand.** A controller (Argo CD/Flux) reconciles the cluster
  to Git continuously; `kubectl apply` from a laptop is for debugging only.
- **Secrets get purpose-built tools.** Encrypt-at-rest or external secret stores; never
  plaintext Secrets in Git (see [security](22-security.md)).
- **Standardize observability.** One metrics/logs/traces stack cluster-wide so every
  workload is debuggable the same way (see [observability](21-observability.md)).

## Best Practices

- Use **Kustomize** (built into `kubectl`) for overlay-style config or **Helm** for
  packaged, parameterized releases — pick one per repo and stay consistent.
- Gate every PR in CI with a schema validator (**kubeconform**) and a best-practice
  linter (**kube-linter**/**kube-score**) so invalid or unsafe manifests fail the build.
- Enforce cluster-wide rules with an admission policy engine (**Kyverno** or **Gatekeeper**):
  require probes, resources, non-root, pinned images (see [production](26-production.md)).
- Manage secrets with **Sealed Secrets**, **SOPS**, or an **External Secrets Operator**
  backed by a vault — encrypted in Git or fetched at runtime, never plaintext.
- Deploy with **Argo CD** or **Flux** so Git is the single source of truth and manual
  drift is auto-reverted.
- Use `kubectl` productively: `-o yaml`, `--dry-run=server`, `explain`, and context
  tools (**kubectx/kubens**) to avoid acting on the wrong cluster.
- Scan images and manifests for vulnerabilities (**Trivy**) in CI (see
  [security](22-security.md)).

## Examples

**Good Example** — validated, policy-gated, GitOps-deployed pipeline

```yaml
# CI: fail the PR before anything reaches the cluster.
steps:
  - run: kubeconform -strict -summary manifests/    # schema-valid against the API
  - run: kube-linter lint manifests/                # probes, resources, non-root
  - run: trivy config manifests/                    # misconfig + CVE scan
# Deploy: Argo CD watches Git and reconciles — no human runs `apply`.
# Secrets: committed as SealedSecrets (encrypted), decrypted only in-cluster.
```

```bash
# Always confirm the target context/namespace before any manual action.
kubectx prod-cluster && kubens shop-prod
kubectl apply --dry-run=server -k overlays/prod   # server-side validate, no mutation
```

**Bad Example** — ad-hoc, unvalidated, drift-prone

```bash
# Applies straight from a laptop with no lint, no policy, no dry-run:
# an insecure or invalid manifest lands directly in production.
kubectl apply -f prod-copy.yaml

# 'prod-copy.yaml' is a hand-forked copy of staging that has silently drifted,
# so environments no longer match and nobody can reproduce the deploy.

# Secret pasted straight into a ConfigMap in Git, in plaintext.
kubectl create configmap db --from-literal=password=s3cr3t
```

## Common Mistakes

- Running `kubectl apply` from developer machines instead of GitOps, causing drift Git
  cannot see.
- Forking full manifests per environment rather than templating one base with overlays.
- No CI validation, so schema errors and insecure config are caught only in the cluster.
- Storing secrets as plaintext ConfigMaps/Secrets in Git.
- No admission policy, so privilege creep and missing probes ship freely.
- Acting on the wrong context/namespace because the current context was not checked.

## Production Tips

- Pin tool versions (Helm, Kustomize, policy bundles) in CI so the pipeline itself is
  reproducible; a floating tool version is another form of drift.
- Run policy in `audit` mode first to find violations, then flip to `enforce` once the
  fleet is clean — blocking on day one stalls every deploy.
- Standardize a single observability stack (e.g. Prometheus + Loki + a tracing backend)
  so on-call debugging is uniform (see [observability](21-observability.md)).

## AI Review Checklist

- Is there one templated base (Helm/Kustomize) with per-environment overlays, not forks?
- Do CI checks schema-validate, lint, and scan manifests before merge?
- Is deployment via GitOps, with manual `kubectl apply` reserved for debugging?
- Are secrets encrypted (Sealed Secrets/SOPS/ESO), never plaintext in Git?
- Is an admission policy engine enforcing probes, resources, and non-root?
- Are tool versions pinned so the pipeline is reproducible?

## Related

- `knowledge/kubernetes/27-best-practices.md`
- `knowledge/kubernetes/24-debugging.md`
- `knowledge/kubernetes/22-security.md`
- `knowledge/kubernetes/26-production.md`
- `knowledge/kubernetes/21-observability.md`
